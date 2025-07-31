using Microsoft.EntityFrameworkCore;
using DotNetSample.Data;
using DotNetSample.Services;
using DotNetSample.Hubs;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add Entity Framework
var useInMemory = builder.Configuration.GetValue<bool>("UseInMemoryDatabase", false);

if (useInMemory)
{
    builder.Services.AddDbContext<ApplicationDbContext>(options =>
        options.UseInMemoryDatabase("InMemoryDb"));
}
else
{
    var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
        ?? "Server=mysql;Database=dotnet_sample;User=root;Password=password;";
    
    builder.Services.AddDbContext<ApplicationDbContext>(options =>
        options.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString)));
}

// Add custom services
builder.Services.AddScoped<IHealthService, HealthService>();
builder.Services.AddScoped<IUserService, UserService>();

// Add SignalR
builder.Services.AddSignalR();

// Add CORS for SignalR and real-time communication
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
    
    // Specific policy for SignalR (credentials require specific origins)
    options.AddPolicy("SignalRPolicy", builder =>
    {
        builder.WithOrigins("http://localhost:3000", "http://localhost:5000", "https://localhost:5001")
               .AllowAnyMethod()
               .AllowAnyHeader()
               .AllowCredentials();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("SignalRPolicy");
app.UseAuthorization();
app.MapControllers();

// Map SignalR Hub with CORS
app.MapHub<ChatHub>("/hub").RequireCors("SignalRPolicy");

// Add real-time communication info
Console.WriteLine("🔄 Real-time Communication Endpoints:");
Console.WriteLine("   SignalR Hub: /hub");
Console.WriteLine("   Long Polling: /api/realtime/long-polling");
Console.WriteLine("   Server-Sent Events: /api/realtime/sse");
Console.WriteLine("   Hub Simulation: /api/realtime/hub");

// Initialize database
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    try
    {
        await context.Database.EnsureCreatedAsync();
        Console.WriteLine("✅ Database connection successful!");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ Database connection failed: {ex.Message}");
    }
}

// Enable static files for test HTML
app.UseStaticFiles();

Console.WriteLine("🚀 .NET Core 8 Sample API is starting in Production...");
Console.WriteLine("📊 Datadog APM monitoring enabled");
Console.WriteLine("🔗 Swagger UI: http://localhost:5000/swagger");
Console.WriteLine("🧪 Real-time Test UI: http://localhost:5000/realtime-test.html");

app.Run(); 