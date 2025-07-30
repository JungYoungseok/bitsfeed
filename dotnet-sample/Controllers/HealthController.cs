using Microsoft.AspNetCore.Mvc;
using DotNetSample.Services;
using DotNetSample.Models;
using Datadog.Trace;
using System.Diagnostics;

namespace DotNetSample.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    private readonly IHealthService _healthService;
    private readonly ILogger<HealthController> _logger;

    public HealthController(IHealthService healthService, ILogger<HealthController> logger)
    {
        _healthService = healthService;
        _logger = logger;
    }

    /// <summary>
    /// 기본 헬스 체크 - 빠른 응답
    /// </summary>
    [HttpGet]
    public IActionResult Get()
    {
        using var scope = Tracer.Instance.StartActive("health.quick_check");
        
        return Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            service = "dotnet-sample",
            version = "1.0.1",
            environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Development",
            build_info = "GitHub Actions Build Test 🔧"
        });
    }

    /// <summary>
    /// 상세 헬스 체크 - 데이터베이스 연결 포함
    /// </summary>
    [HttpGet("detailed")]
    public async Task<IActionResult> GetDetailed()
    {
        using var scope = Tracer.Instance.StartActive("health.detailed_check");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var healthCheck = await _healthService.PerformHealthCheckAsync();
            
            scope.Span.SetTag("health.status", healthCheck.Status);
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            var statusCode = healthCheck.Status switch
            {
                "Healthy" => 200,
                "Unhealthy" => 503,
                "Critical" => 503,
                _ => 500
            };

            return StatusCode(statusCode, healthCheck);
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Health check failed");
            
            return StatusCode(500, new
            {
                status = "error",
                message = ex.Message,
                timestamp = DateTime.UtcNow
            });
        }
    }

    /// <summary>
    /// 시스템 메트릭 조회
    /// </summary>
    [HttpGet("metrics")]
    public async Task<IActionResult> GetMetrics()
    {
        using var scope = Tracer.Instance.StartActive("health.metrics");
        
        try
        {
            var metrics = await _healthService.GetSystemMetricsAsync();
            
            return Ok(new
            {
                timestamp = DateTime.UtcNow,
                metrics = metrics,
                service = "dotnet-sample"
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to retrieve metrics");
            
            return StatusCode(500, new
            {
                error = "Failed to retrieve metrics",
                message = ex.Message
            });
        }
    }

    /// <summary>
    /// 데이터베이스 연결 상태 확인
    /// </summary>
    [HttpGet("database")]
    public async Task<IActionResult> CheckDatabase()
    {
        using var scope = Tracer.Instance.StartActive("health.database_check");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var isHealthy = await _healthService.CheckDatabaseConnectionAsync();
            
            scope.Span.SetTag("database.status", isHealthy ? "connected" : "disconnected");
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            return Ok(new
            {
                database_status = isHealthy ? "connected" : "disconnected",
                response_time_ms = stopwatch.ElapsedMilliseconds,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Database health check failed");
            
            return StatusCode(503, new
            {
                database_status = "error",
                error = ex.Message,
                timestamp = DateTime.UtcNow
            });
        }
    }

    /// <summary>
    /// 의도적으로 지연시간을 생성하여 APM 테스트
    /// </summary>
    [HttpGet("slow")]
    public async Task<IActionResult> SlowEndpoint([FromQuery] int delayMs = 1000)
    {
        using var scope = Tracer.Instance.StartActive("health.slow_operation");
        scope.Span.SetTag("delay.ms", delayMs);
        
        // 최대 5초로 제한
        delayMs = Math.Min(delayMs, 5000);
        
        _logger.LogInformation("Simulating slow operation with {DelayMs}ms delay", delayMs);
        
        await Task.Delay(delayMs);
        
        return Ok(new
        {
            message = $"Slow operation completed after {delayMs}ms",
            timestamp = DateTime.UtcNow,
            delay_ms = delayMs
        });
    }

    /// <summary>
    /// 의도적으로 에러를 발생시켜 APM 에러 추적 테스트
    /// </summary>
    [HttpGet("error")]
    public IActionResult ErrorEndpoint([FromQuery] string? type = "general")
    {
        using var scope = Tracer.Instance.StartActive("health.error_simulation");
        scope.Span.SetTag("error.type", type);
        
        _logger.LogWarning("Simulating error of type: {ErrorType}", type);
        
        Exception exception = type?.ToLower() switch
        {
            "database" => new InvalidOperationException("Simulated database connection error"),
            "validation" => new ArgumentException("Simulated validation error"),
            "timeout" => new TimeoutException("Simulated timeout error"),
            "null" => new NullReferenceException("Simulated null reference error"),
            _ => new Exception("Simulated general error for APM testing")
        };
        
        scope.Span.SetException(exception);
        throw exception;
    }
} 