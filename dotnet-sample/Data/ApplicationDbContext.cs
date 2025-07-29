using Microsoft.EntityFrameworkCore;
using DotNetSample.Models;

namespace DotNetSample.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<HealthCheck> HealthChecks { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User 엔티티 설정
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(100);
            entity.Property(e => e.Email)
                .IsRequired()
                .HasMaxLength(255);
            entity.HasIndex(e => e.Email)
                .IsUnique();
            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)");
        });

        // HealthCheck 엔티티 설정
        modelBuilder.Entity<HealthCheck>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Status)
                .IsRequired()
                .HasMaxLength(50);
            entity.Property(e => e.Message)
                .HasMaxLength(500);
            entity.Property(e => e.CheckedAt)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)");
        });

        // 초기 데이터 시드
        modelBuilder.Entity<User>().HasData(
            new User 
            { 
                Id = 1, 
                Name = "Test User", 
                Email = "test@example.com", 
                CreatedAt = DateTime.UtcNow 
            },
            new User 
            { 
                Id = 2, 
                Name = "Admin User", 
                Email = "admin@example.com", 
                CreatedAt = DateTime.UtcNow 
            }
        );
    }
} 