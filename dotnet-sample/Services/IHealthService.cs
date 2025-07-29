using DotNetSample.Models;

namespace DotNetSample.Services;

public interface IHealthService
{
    Task<HealthCheck> PerformHealthCheckAsync();
    Task<bool> CheckDatabaseConnectionAsync();
    Task<Dictionary<string, object>> GetSystemMetricsAsync();
} 