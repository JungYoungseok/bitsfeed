using Microsoft.EntityFrameworkCore;
using DotNetSample.Data;
using DotNetSample.Models;
using Datadog.Trace;
using System.Diagnostics;

namespace DotNetSample.Services;

public class UserService : IUserService
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UserService> _logger;

    public UserService(ApplicationDbContext context, ILogger<UserService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<IEnumerable<User>> GetAllUsersAsync()
    {
        using var scope = Tracer.Instance.StartActive("user.get_all");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var users = await _context.Users
                .OrderBy(u => u.CreatedAt)
                .ToListAsync();
            
            scope.Span.SetTag("user.count", users.Count);
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            _logger.LogInformation("Retrieved {UserCount} users in {Duration}ms", 
                users.Count, stopwatch.ElapsedMilliseconds);
            
            return users;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to retrieve users");
            throw;
        }
    }

    public async Task<User?> GetUserByIdAsync(int id)
    {
        using var scope = Tracer.Instance.StartActive("user.get_by_id");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var user = await _context.Users.FindAsync(id);
            
            scope.Span.SetTag("user.found", user != null ? "true" : "false");
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            if (user != null)
            {
                _logger.LogInformation("User {UserId} found in {Duration}ms", 
                    id, stopwatch.ElapsedMilliseconds);
            }
            else
            {
                _logger.LogWarning("User {UserId} not found", id);
            }
            
            return user;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to retrieve user {UserId}", id);
            throw;
        }
    }

    public async Task<User> CreateUserAsync(User user)
    {
        using var scope = Tracer.Instance.StartActive("user.create");
        scope.Span.SetTag("user.email", user.Email);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            user.CreatedAt = DateTime.UtcNow;
            _context.Users.Add(user);
            await _context.SaveChangesAsync();
            
            scope.Span.SetTag("user.id", user.Id);
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            _logger.LogInformation("User {UserId} created with email {Email} in {Duration}ms", 
                user.Id, user.Email, stopwatch.ElapsedMilliseconds);
            
            return user;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to create user with email {Email}", user.Email);
            throw;
        }
    }

    public async Task<User?> UpdateUserAsync(int id, User user)
    {
        using var scope = Tracer.Instance.StartActive("user.update");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var existingUser = await _context.Users.FindAsync(id);
            if (existingUser == null)
            {
                scope.Span.SetTag("user.found", "false");
                return null;
            }
            
            existingUser.Name = user.Name;
            existingUser.Email = user.Email;
            existingUser.UpdatedAt = DateTime.UtcNow;
            
            await _context.SaveChangesAsync();
            
            scope.Span.SetTag("user.found", "true");
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            _logger.LogInformation("User {UserId} updated in {Duration}ms", 
                id, stopwatch.ElapsedMilliseconds);
            
            return existingUser;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to update user {UserId}", id);
            throw;
        }
    }

    public async Task<bool> DeleteUserAsync(int id)
    {
        using var scope = Tracer.Instance.StartActive("user.delete");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
            {
                scope.Span.SetTag("user.found", "false");
                return false;
            }
            
            _context.Users.Remove(user);
            await _context.SaveChangesAsync();
            
            scope.Span.SetTag("user.found", "true");
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            _logger.LogInformation("User {UserId} deleted in {Duration}ms", 
                id, stopwatch.ElapsedMilliseconds);
            
            return true;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to delete user {UserId}", id);
            throw;
        }
    }

    public async Task<int> GetUserCountAsync()
    {
        using var scope = Tracer.Instance.StartActive("user.count");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var count = await _context.Users.CountAsync();
            
            scope.Span.SetTag("user.total_count", count);
            scope.Span.SetTag("operation.duration_ms", stopwatch.ElapsedMilliseconds);
            
            _logger.LogInformation("User count retrieved: {Count} in {Duration}ms", 
                count, stopwatch.ElapsedMilliseconds);
            
            return count;
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to get user count");
            throw;
        }
    }
} 