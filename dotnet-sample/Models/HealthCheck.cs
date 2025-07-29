using System.ComponentModel.DataAnnotations;

namespace DotNetSample.Models;

public class HealthCheck
{
    public int Id { get; set; }
    
    [Required]
    [StringLength(50)]
    public string Status { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Message { get; set; }
    
    public DateTime CheckedAt { get; set; }
    
    public double ResponseTimeMs { get; set; }
    
    public string? DatabaseStatus { get; set; }
    
    public int? ActiveConnections { get; set; }
} 