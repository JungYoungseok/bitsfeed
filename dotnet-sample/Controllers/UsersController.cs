using Microsoft.AspNetCore.Mvc;
using DotNetSample.Services;
using DotNetSample.Models;
using Datadog.Trace;
using System.Diagnostics;

namespace DotNetSample.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IUserService userService, ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    /// <summary>
    /// 모든 사용자 조회
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetUsers()
    {
        using var scope = Tracer.Instance.StartActive("users.get_all");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var users = await _userService.GetAllUsersAsync();
            var userList = users.ToList();
            
            scope.Span.SetTag("users.count", userList.Count);
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            return Ok(new
            {
                users = userList,
                count = userList.Count,
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to retrieve users");
            return StatusCode(500, new { error = "Failed to retrieve users", message = ex.Message });
        }
    }

    /// <summary>
    /// 특정 사용자 조회
    /// </summary>
    [HttpGet("{id}")]
    public async Task<IActionResult> GetUser(int id)
    {
        using var scope = Tracer.Instance.StartActive("users.get_by_id");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var user = await _userService.GetUserByIdAsync(id);
            
            scope.Span.SetTag("user.found", user != null ? "true" : "false");
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            if (user == null)
            {
                return NotFound(new { error = $"User with ID {id} not found" });
            }

            return Ok(new
            {
                user = user,
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to retrieve user {UserId}", id);
            return StatusCode(500, new { error = "Failed to retrieve user", message = ex.Message });
        }
    }

    /// <summary>
    /// 새 사용자 생성
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateUser([FromBody] User user)
    {
        using var scope = Tracer.Instance.StartActive("users.create");
        scope.Span.SetTag("user.email", user.Email);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var createdUser = await _userService.CreateUserAsync(user);
            
            scope.Span.SetTag("user.id", createdUser.Id);
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            return CreatedAtAction(
                nameof(GetUser), 
                new { id = createdUser.Id }, 
                new
                {
                    user = createdUser,
                    message = "User created successfully",
                    timestamp = DateTime.UtcNow,
                    response_time_ms = stopwatch.ElapsedMilliseconds
                });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to create user");
            return StatusCode(500, new { error = "Failed to create user", message = ex.Message });
        }
    }

    /// <summary>
    /// 사용자 정보 업데이트
    /// </summary>
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateUser(int id, [FromBody] User user)
    {
        using var scope = Tracer.Instance.StartActive("users.update");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var updatedUser = await _userService.UpdateUserAsync(id, user);
            
            scope.Span.SetTag("user.found", updatedUser != null ? "true" : "false");
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            if (updatedUser == null)
            {
                return NotFound(new { error = $"User with ID {id} not found" });
            }

            return Ok(new
            {
                user = updatedUser,
                message = "User updated successfully",
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to update user {UserId}", id);
            return StatusCode(500, new { error = "Failed to update user", message = ex.Message });
        }
    }

    /// <summary>
    /// 사용자 삭제
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        using var scope = Tracer.Instance.StartActive("users.delete");
        scope.Span.SetTag("user.id", id);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var deleted = await _userService.DeleteUserAsync(id);
            
            scope.Span.SetTag("user.deleted", deleted ? "true" : "false");
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            if (!deleted)
            {
                return NotFound(new { error = $"User with ID {id} not found" });
            }

            return Ok(new
            {
                message = $"User {id} deleted successfully",
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to delete user {UserId}", id);
            return StatusCode(500, new { error = "Failed to delete user", message = ex.Message });
        }
    }

    /// <summary>
    /// 사용자 수 조회
    /// </summary>
    [HttpGet("count")]
    public async Task<IActionResult> GetUserCount()
    {
        using var scope = Tracer.Instance.StartActive("users.count");
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            var count = await _userService.GetUserCountAsync();
            
            scope.Span.SetTag("users.total_count", count);
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            return Ok(new
            {
                count = count,
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to get user count");
            return StatusCode(500, new { error = "Failed to get user count", message = ex.Message });
        }
    }

    /// <summary>
    /// 대량 사용자 생성 (성능 테스트용)
    /// </summary>
    [HttpPost("bulk")]
    public async Task<IActionResult> CreateBulkUsers([FromQuery] int count = 10)
    {
        using var scope = Tracer.Instance.StartActive("users.create_bulk");
        scope.Span.SetTag("users.bulk_count", count);
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            // 최대 100개로 제한
            count = Math.Min(count, 100);
            
            var users = new List<User>();
            for (int i = 0; i < count; i++)
            {
                var user = new User
                {
                    Name = $"Bulk User {i + 1}",
                    Email = $"bulk{i + 1}@example.com"
                };
                
                users.Add(await _userService.CreateUserAsync(user));
            }
            
            scope.Span.SetTag("users.created_count", users.Count);
            scope.Span.SetTag("response.time_ms", stopwatch.ElapsedMilliseconds);
            
            return Ok(new
            {
                message = $"Created {users.Count} users successfully",
                users = users,
                timestamp = DateTime.UtcNow,
                response_time_ms = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            scope.Span.SetException(ex);
            _logger.LogError(ex, "Failed to create bulk users");
            return StatusCode(500, new { error = "Failed to create bulk users", message = ex.Message });
        }
    }
} 