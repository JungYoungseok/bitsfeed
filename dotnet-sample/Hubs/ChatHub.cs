using Microsoft.AspNetCore.SignalR;

namespace DotNetSample.Hubs;

/// <summary>
/// SignalR Hub for real-time communication
/// Similar to the /hub endpoint that shows long execution times
/// </summary>
public class ChatHub : Hub
{
    public async Task JoinRoom(string roomName)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, roomName);
        await Clients.Group(roomName).SendAsync("UserJoined", $"User {Context.ConnectionId} joined room {roomName}");
    }

    public async Task SendMessage(string roomName, string message)
    {
        await Clients.Group(roomName).SendAsync("ReceiveMessage", Context.ConnectionId, message);
    }

    public async Task SendHeartbeat()
    {
        // Simulate a heartbeat that could cause long-running connections
        await Clients.Caller.SendAsync("Heartbeat", DateTime.UtcNow);
    }

    public override async Task OnConnectedAsync()
    {
        Console.WriteLine($"📱 SignalR Client connected: {Context.ConnectionId}");
        await base.OnConnectedAsync();
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        Console.WriteLine($"📱 SignalR Client disconnected: {Context.ConnectionId}");
        await base.OnDisconnectedAsync(exception);
    }
}