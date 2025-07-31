using Microsoft.AspNetCore.Mvc;
using System.Text;

namespace DotNetSample.Controllers;

/// <summary>
/// Controller to demonstrate different real-time communication patterns
/// and their impact on APM monitoring (similar to the /hub endpoint analysis)
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class RealTimeController : ControllerBase
{
    private static readonly List<string> _messages = new();
    private static readonly SemaphoreSlim _semaphore = new(1, 1);

    /// <summary>
    /// Long Polling endpoint - waits for new messages
    /// This could explain the 5m 37s execution time seen in APM
    /// </summary>
    [HttpGet("long-polling")]
    public async Task<IActionResult> LongPolling([FromQuery] int timeoutSeconds = 300)
    {
        var startTime = DateTime.UtcNow;
        var timeout = TimeSpan.FromSeconds(Math.Min(timeoutSeconds, 300)); // Max 5 minutes
        
        Console.WriteLine($"🔄 Long polling started at {startTime:HH:mm:ss}");

        while (DateTime.UtcNow - startTime < timeout)
        {
            await _semaphore.WaitAsync();
            try
            {
                if (_messages.Any())
                {
                    var messages = _messages.ToList();
                    _messages.Clear();
                    Console.WriteLine($"✅ Long polling completed with {messages.Count} messages after {(DateTime.UtcNow - startTime).TotalSeconds:F1}s");
                    return Ok(new { messages, waitTime = DateTime.UtcNow - startTime });
                }
            }
            finally
            {
                _semaphore.Release();
            }

            // Wait 1 second before checking again
            await Task.Delay(1000);
        }

        Console.WriteLine($"⏰ Long polling timed out after {timeout.TotalSeconds}s");
        return Ok(new { messages = Array.Empty<string>(), waitTime = timeout, timedOut = true });
    }

    /// <summary>
    /// Post a message that will be picked up by long polling clients
    /// </summary>
    [HttpPost("message")]
    public async Task<IActionResult> PostMessage([FromBody] MessageRequest request)
    {
        await _semaphore.WaitAsync();
        try
        {
            _messages.Add($"{DateTime.UtcNow:HH:mm:ss} - {request.Message}");
            Console.WriteLine($"📨 Message added: {request.Message}");
            return Ok(new { success = true, messageCount = _messages.Count });
        }
        finally
        {
            _semaphore.Release();
        }
    }

    /// <summary>
    /// Server-Sent Events endpoint for streaming data
    /// </summary>
    [HttpGet("sse")]
    public async Task ServerSentEvents([FromQuery] int durationSeconds = 30)
    {
        Response.Headers.Add("Content-Type", "text/event-stream");
        Response.Headers.Add("Cache-Control", "no-cache");
        Response.Headers.Add("Connection", "keep-alive");

        var startTime = DateTime.UtcNow;
        var duration = TimeSpan.FromSeconds(Math.Min(durationSeconds, 300));

        Console.WriteLine($"📡 SSE stream started for {duration.TotalSeconds}s");

        while (DateTime.UtcNow - startTime < duration)
        {
            var data = new
            {
                timestamp = DateTime.UtcNow,
                message = $"Server time: {DateTime.UtcNow:HH:mm:ss}",
                elapsed = (DateTime.UtcNow - startTime).TotalSeconds
            };

            var eventData = $"data: {System.Text.Json.JsonSerializer.Serialize(data)}\n\n";
            var bytes = Encoding.UTF8.GetBytes(eventData);
            
            await Response.Body.WriteAsync(bytes);
            await Response.Body.FlushAsync();

            await Task.Delay(2000); // Send event every 2 seconds
        }

        Console.WriteLine($"📡 SSE stream completed after {duration.TotalSeconds}s");
    }

    /// <summary>
    /// Regular HTTP endpoint for comparison
    /// </summary>
    [HttpGet("quick")]
    public IActionResult QuickResponse()
    {
        Console.WriteLine($"⚡ Quick response at {DateTime.UtcNow:HH:mm:ss}");
        return Ok(new { 
            message = "Quick HTTP response", 
            timestamp = DateTime.UtcNow,
            responseTime = "< 100ms"
        });
    }

    /// <summary>
    /// Simulate the /hub endpoint behavior with configurable delay
    /// </summary>
    [HttpGet("hub")]
    public async Task<IActionResult> HubSimulation([FromQuery] int delaySeconds = 337)
    {
        var startTime = DateTime.UtcNow;
        Console.WriteLine($"🔄 Hub simulation started - will delay for {delaySeconds}s");

        // Simulate the long execution time seen in APM traces
        await Task.Delay(TimeSpan.FromSeconds(delaySeconds));

        var endTime = DateTime.UtcNow;
        var actualDuration = endTime - startTime;

        Console.WriteLine($"✅ Hub simulation completed after {actualDuration.TotalSeconds:F1}s");

        return Ok(new
        {
            message = "Hub simulation completed",
            requestedDelay = delaySeconds,
            actualDuration = actualDuration.TotalSeconds,
            startTime,
            endTime
        });
    }
}

public class MessageRequest
{
    public string Message { get; set; } = string.Empty;
}