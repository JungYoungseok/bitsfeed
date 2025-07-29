using Microsoft.EntityFrameworkCore;
using DotNetSample.Data;
using DotNetSample.Models;
using System.Diagnostics;
using Datadog.Trace;

namespace DotNetSample.Services;

public class HealthService : IHealthService
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<HealthService> _logger;

    public HealthService(ApplicationDbContext context, ILogger<HealthService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<HealthCheck> PerformHealthCheckAsync()
    {
        var stopwatch = Stopwatch.StartNew();
        
        using var scope = Tracer.Instance.StartActive("health.check");
        scope.Span.SetTag("service.name", "dotnet-sample");
        scope.Span.SetTag("operation.name", "health_check");
        
        var healthCheck = new HealthCheck
        {
            CheckedAt = DateTime.UtcNow
        };

        try
        {
            // 데이터베이스 연결 확인
            var dbHealthy = await CheckDatabaseConnectionAsync();
            
            // 시스템 메트릭 수집
            var metrics = await GetSystemMetricsAsync();
            
            healthCheck.Status = dbHealthy ? "Healthy" : "Unhealthy";
            healthCheck.DatabaseStatus = dbHealthy ? "Connected" : "Disconnected";
            healthCheck.ResponseTimeMs = stopwatch.Elapsed.TotalMilliseconds;
            healthCheck.ActiveConnections = (int?)metrics.GetValueOrDefault("active_connections", 0);
            healthCheck.Message = dbHealthy 
                ? $"All systems operational. Response time: {healthCheck.ResponseTimeMs:F2}ms" 
                : "Database connection failed";

            scope.Span.SetTag("health.status", healthCheck.Status);
            scope.Span.SetTag("response.time_ms", healthCheck.ResponseTimeMs);
            
            _logger.LogInformation("Health check completed: {Status} in {ResponseTime}ms", 
                healthCheck.Status, healthCheck.ResponseTimeMs);

            // 헬스 체크 결과를 데이터베이스에 저장
            if (dbHealthy)
            {
                _context.HealthChecks.Add(healthCheck);
                await _context.SaveChangesAsync();
            }

            return healthCheck;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Health check failed");
            
            healthCheck.Status = "Critical";
            healthCheck.Message = $"Health check failed: {ex.Message}";
            healthCheck.ResponseTimeMs = stopwatch.Elapsed.TotalMilliseconds;
            
            return healthCheck;
        }
        finally
        {
            stopwatch.Stop();
        }
    }

    public async Task<bool> CheckDatabaseConnectionAsync()
    {
        using var scope = Tracer.Instance.StartActive("database.connection.check");
        
        try
        {
            await _context.Database.ExecuteSqlRawAsync("SELECT 1");
            scope.Span.SetTag("database.status", "connected");
            return true;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            scope.Span.SetTag("database.status", "disconnected");
            _logger.LogError(ex, "Database connection check failed");
            return false;
        }
    }

    public async Task<Dictionary<string, object>> GetSystemMetricsAsync()
    {
        using var scope = Tracer.Instance.StartActive("system.metrics.collection");
        
        var metrics = new Dictionary<string, object>();
        
        try
        {
            // 프로세스 메트릭
            var process = Process.GetCurrentProcess();
            metrics["memory_usage_mb"] = process.WorkingSet64 / 1024 / 1024;
            metrics["thread_count"] = process.Threads.Count;
            metrics["cpu_time_ms"] = process.TotalProcessorTime.TotalMilliseconds;
            
            // GC 메트릭
            metrics["gc_gen0_collections"] = GC.CollectionCount(0);
            metrics["gc_gen1_collections"] = GC.CollectionCount(1);
            metrics["gc_gen2_collections"] = GC.CollectionCount(2);
            metrics["total_memory_kb"] = GC.GetTotalMemory(false) / 1024;
            
            // 데이터베이스 연결 수 (예시)
            var connectionCount = await GetActiveConnectionCountAsync();
            metrics["active_connections"] = connectionCount;
            
            // 커스텀 메트릭을 Datadog에 전송
            foreach (var metric in metrics)
            {
                scope.Span.SetTag($"metric.{metric.Key}", metric.Value?.ToString() ?? "0");
            }
            
            return metrics;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to collect system metrics");
            return metrics;
        }
    }

    private async Task<int> GetActiveConnectionCountAsync()
    {
        try
        {
            // MySQL의 SHOW PROCESSLIST 실행하여 활성 연결 수 확인
            var result = await _context.Database.ExecuteSqlRawAsync(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND != 'Sleep'");
            return Math.Max(1, result); // 최소 1개 (현재 연결)
        }
        catch
        {
            return 1; // 기본값
        }
    }
} 