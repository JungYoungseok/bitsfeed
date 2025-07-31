export default function RealtimeTestPage() {
  return (
    <div>
      <iframe 
        src="/realtime-test.html" 
        style={{ 
          width: '100%', 
          height: '100vh', 
          border: 'none' 
        }}
        title="Real-time Communication Test"
      />
    </div>
  );
}