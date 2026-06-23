// & "C:\Program Files\dotnet\dotnet.exe" run --project "C:\Users\Barnus\Desktop\Jarvis V2\clients\windows\JarvisClient" -- --host 192.168.1.28 --port 8765 --user barnus --device barnus-pc

using System.Diagnostics;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace JarvisClient;

internal static class Program
{
    public static async Task<int> Main(string[] args)
    {
        var config = ClientConfig.FromArgs(args);
        Console.Title = $"Jarvis Client - {config.DeviceId}";

        Console.WriteLine("Jarvis Windows Client");
        Console.WriteLine($"Server: {config.Host}:{config.Port}");
        Console.WriteLine($"User:   {config.UserId}");
        Console.WriteLine($"Device: {config.DeviceId}");
        Console.WriteLine();

        using var cancellation = new CancellationTokenSource();
        Console.CancelKeyPress += (_, eventArgs) =>
        {
            eventArgs.Cancel = true;
            cancellation.Cancel();
        };

        await using var connection = new PacketConnection(config);

        try
        {
            await connection.ConnectAsync(cancellation.Token);
            Console.WriteLine("Connected.");
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Could not connect: {ex.Message}");
            return 1;
        }

        var receiveTask = ReceiveLoopAsync(connection, cancellation.Token);
        var heartbeatTask = HeartbeatLoopAsync(connection, cancellation.Token);

        await SendEventAsync(connection, "device_online", new
        {
            platform = "windows",
            app = "jarvis-client",
            capabilities = new[] { "push_to_talk_wav", "open_chrome", "echo" },
        }, cancellation.Token);

        Console.WriteLine();
        Console.WriteLine("Controls:");
        Console.WriteLine("  Hold SPACE = push to talk");
        Console.WriteLine("  T          = send text packet");
        Console.WriteLine("  Q          = quit");
        Console.WriteLine();

        try
        {
            await InputLoopAsync(connection, cancellation);
        }
        catch (OperationCanceledException)
        {
            // Ctrl+C or Q is a normal shutdown path.
        }

        cancellation.Cancel();
        await Task.WhenAny(Task.WhenAll(receiveTask, heartbeatTask), Task.Delay(1000));
        return 0;
    }

    private static async Task InputLoopAsync(PacketConnection connection, CancellationTokenSource cancellation)
    {
        var recording = false;
        var recorder = new WaveInWavRecorder();

        while (!cancellation.IsCancellationRequested)
        {
            if (Keyboard.IsKeyDown(ConsoleKey.Spacebar))
            {
                if (!recording)
                {
                    Console.WriteLine("Recording...");
                    try
                    {
                        recorder.Start();
                        recording = true;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Recorder start failed: {ex.Message}");
                        recorder.Cancel();
                    }
                }

                await Task.Delay(30, cancellation.Token).ConfigureAwait(false);
                continue;
            }

            if (recording)
            {
                recording = false;
                try
                {
                    Console.WriteLine("Sending audio packet...");
                    var wavBytes = recorder.Stop();
                    var payload = Convert.ToBase64String(wavBytes);
                    await connection.SendAsync(Packet.Input(connection.Config, payload, "wav"), cancellation.Token);
                    Console.WriteLine($"Sent {wavBytes.Length:N0} bytes.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Recorder/send failed: {ex.Message}");
                    recorder.Cancel();
                }
            }

            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(intercept: true);
                if (key.Key == ConsoleKey.Q)
                {
                    await SendEventAsync(connection, "device_offline", new { reason = "client_quit" }, cancellation.Token);
                    cancellation.Cancel();
                    break;
                }

                if (key.Key == ConsoleKey.T)
                {
                    Console.Write("Text> ");
                    var text = Console.ReadLine();
                    if (!string.IsNullOrWhiteSpace(text))
                    {
                        await connection.SendAsync(Packet.Input(connection.Config, text, "utf-8"), cancellation.Token);
                    }
                }
            }

            await Task.Delay(30, cancellation.Token).ConfigureAwait(false);
        }

        if (recording)
        {
            recorder.Cancel();
        }
    }

    private static async Task ReceiveLoopAsync(PacketConnection connection, CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            Packet? packet;
            try
            {
                packet = await connection.ReceiveAsync(cancellationToken).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Receive stopped: {ex.Message}");
                break;
            }

            if (packet is null)
            {
                Console.WriteLine("Server closed the connection.");
                break;
            }

            if (packet.Type == "tool_call")
            {
                _ = Task.Run(() => HandleToolCallAsync(connection, packet, cancellationToken), cancellationToken);
                continue;
            }

            Console.WriteLine($"<- {packet.Type}: {packet.Payload.GetRawText()}");
        }
    }

    private static async Task HandleToolCallAsync(PacketConnection connection, Packet packet, CancellationToken cancellationToken)
    {
        ToolResult result;

        try
        {
            var toolCall = packet.Payload.Deserialize<ToolCall>(ProgramJson.Options)
                ?? throw new InvalidOperationException("Tool payload was empty.");

            result = toolCall.Name switch
            {
                "open_chrome" => OpenChrome(toolCall),
                "echo" => ToolResult.Success(toolCall.CallId, toolCall.Name, toolCall.Arguments),
                _ => ToolResult.Failure(toolCall.CallId, toolCall.Name, $"Unsupported tool: {toolCall.Name}"),
            };
        }
        catch (Exception ex)
        {
            result = ToolResult.Failure(packet.RequestId, "unknown", ex.Message);
        }

        await connection.SendAsync(Packet.ToolResult(connection.Config, packet.RequestId, result), cancellationToken);
    }

    private static ToolResult OpenChrome(ToolCall toolCall)
    {
        var url = "https://www.google.com";

        if (toolCall.Arguments.TryGetProperty("url", out var urlElement)
            && urlElement.ValueKind == JsonValueKind.String
            && !string.IsNullOrWhiteSpace(urlElement.GetString()))
        {
            url = urlElement.GetString()!;
        }

        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = url,
                UseShellExecute = true,
            });

            return ToolResult.Success(toolCall.CallId, toolCall.Name, new { opened = url });
        }
        catch (Exception ex)
        {
            return ToolResult.Failure(toolCall.CallId, toolCall.Name, ex.Message);
        }
    }

    private static async Task HeartbeatLoopAsync(PacketConnection connection, CancellationToken cancellationToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(20));

        while (await timer.WaitForNextTickAsync(cancellationToken).ConfigureAwait(false))
        {
            await SendEventAsync(connection, "heartbeat", new
            {
                machine = Environment.MachineName,
                os = RuntimeInformation.OSDescription,
            }, cancellationToken);
        }
    }

    private static Task SendEventAsync(PacketConnection connection, string eventName, object payload, CancellationToken cancellationToken)
    {
        return connection.SendAsync(Packet.Event(connection.Config, new
        {
            name = eventName,
            data = payload,
        }), cancellationToken);
    }
}

internal sealed class PacketConnection : IAsyncDisposable
{
    private readonly TcpClient _tcpClient = new();
    private StreamReader? _reader;
    private StreamWriter? _writer;

    public PacketConnection(ClientConfig config)
    {
        Config = config;
    }

    public ClientConfig Config { get; }

    public async Task ConnectAsync(CancellationToken cancellationToken)
    {
        await _tcpClient.ConnectAsync(Config.Host, Config.Port, cancellationToken).ConfigureAwait(false);
        var stream = _tcpClient.GetStream();
        _reader = new StreamReader(stream, Encoding.UTF8);
        _writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true };
    }

    public async Task SendAsync(Packet packet, CancellationToken cancellationToken)
    {
        if (_writer is null)
        {
            throw new InvalidOperationException("Client is not connected.");
        }

        var json = JsonSerializer.Serialize(packet, ProgramJson.Options);
        await _writer.WriteLineAsync(json.AsMemory(), cancellationToken).ConfigureAwait(false);
    }

    public async Task<Packet?> ReceiveAsync(CancellationToken cancellationToken)
    {
        if (_reader is null)
        {
            throw new InvalidOperationException("Client is not connected.");
        }

        var line = await _reader.ReadLineAsync(cancellationToken).ConfigureAwait(false);
        return line is null ? null : JsonSerializer.Deserialize<Packet>(line, ProgramJson.Options);
    }

    public async ValueTask DisposeAsync()
    {
        _reader?.Dispose();
        if (_writer is not null)
        {
            await _writer.DisposeAsync().ConfigureAwait(false);
        }

        _tcpClient.Dispose();
    }
}

internal static class ProgramJson
{
    public static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        WriteIndented = false,
    };
}

internal sealed record ClientConfig(string Host, int Port, string UserId, string DeviceId)
{
    public static ClientConfig FromArgs(string[] args)
    {
        var host = GetArg(args, "--host") ?? "127.0.0.1";
        var port = int.TryParse(GetArg(args, "--port"), out var parsedPort) ? parsedPort : 8765;
        var userId = GetArg(args, "--user") ?? Environment.UserName;
        var deviceId = GetArg(args, "--device") ?? Environment.MachineName.ToLowerInvariant();

        return new ClientConfig(host, port, userId, deviceId);
    }

    private static string? GetArg(string[] args, string name)
    {
        for (var i = 0; i < args.Length; i++)
        {
            if (args[i] == name && i + 1 < args.Length)
            {
                return args[i + 1];
            }

            if (args[i].StartsWith(name + "=", StringComparison.OrdinalIgnoreCase))
            {
                return args[i][(name.Length + 1)..];
            }
        }

        return null;
    }
}

internal sealed record Packet(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("device_id")] string DeviceId,
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("payload")] JsonElement Payload,
    [property: JsonPropertyName("encoding")] string Encoding,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("timestamp")] long Timestamp)
{
    public static Packet Input(ClientConfig config, object payload, string encoding)
    {
        return Create(config, "input", payload, encoding);
    }

    public static Packet Event(ClientConfig config, object payload)
    {
        return Create(config, "event", payload, "json");
    }

    public static Packet ToolResult(ClientConfig config, string requestId, ToolResult payload)
    {
        return Create(config, "tool_result", payload, "json", requestId);
    }

    private static Packet Create(ClientConfig config, string type, object payload, string encoding, string? requestId = null)
    {
        return new Packet(
            config.UserId,
            config.DeviceId,
            type,
            JsonSerializer.SerializeToElement(payload, ProgramJson.Options),
            encoding,
            requestId ?? Guid.NewGuid().ToString("N"),
            DateTimeOffset.UtcNow.ToUnixTimeSeconds());
    }
}

internal sealed record ToolCall(
    [property: JsonPropertyName("call_id")] string CallId,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("arguments")] JsonElement Arguments);

internal sealed record ToolResult(
    [property: JsonPropertyName("call_id")] string CallId,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("ok")] bool Ok,
    [property: JsonPropertyName("result")] JsonElement? Result,
    [property: JsonPropertyName("error")] string? Error)
{
    public static ToolResult Success(string callId, string name, object result)
    {
        return new ToolResult(callId, name, true, JsonSerializer.SerializeToElement(result, ProgramJson.Options), null);
    }

    public static ToolResult Failure(string callId, string name, string error)
    {
        return new ToolResult(callId, name, false, null, error);
    }
}

internal sealed class WaveInWavRecorder
{
    private const int WaveMapper = -1;
    private const int CallbackFunction = 0x00030000;
    private const uint WimData = 0x03C0;
    private const int BufferCount = 8;
    private const int BufferSize = 8192;

    private readonly object _sync = new();
    private readonly WaveInNative.WaveInProc _callback;
    private readonly List<AudioBuffer> _buffers = [];
    private MemoryStream _pcm = new();
    private IntPtr _handle;
    private volatile bool _recording;
    private volatile bool _stopping;

    public WaveInWavRecorder()
    {
        _callback = OnWaveIn;
    }

    public void Start()
    {
        if (_recording)
        {
            throw new InvalidOperationException("Recording is already active.");
        }

        _pcm.Dispose();
        _pcm = new MemoryStream();
        _stopping = false;

        var format = WaveFormat.Pcm16Mono(16000);
        Check(WaveInNative.waveInOpen(out _handle, WaveMapper, ref format, _callback, IntPtr.Zero, CallbackFunction), "waveInOpen");

        try
        {
            for (var i = 0; i < BufferCount; i++)
            {
                var buffer = AudioBuffer.Create(BufferSize);
                _buffers.Add(buffer);
                Check(WaveInNative.waveInPrepareHeader(_handle, buffer.HeaderPointer, Marshal.SizeOf<WaveHeader>()), "waveInPrepareHeader");
                Check(WaveInNative.waveInAddBuffer(_handle, buffer.HeaderPointer, Marshal.SizeOf<WaveHeader>()), "waveInAddBuffer");
            }

            _recording = true;
            Check(WaveInNative.waveInStart(_handle), "waveInStart");
        }
        catch
        {
            Cancel();
            throw;
        }
    }

    public byte[] Stop()
    {
        if (!_recording)
        {
            throw new InvalidOperationException("Recording was not started.");
        }

        _stopping = true;
        WaveInNative.waveInStop(_handle);
        WaveInNative.waveInReset(_handle);

        CleanupDevice();
        _recording = false;
        _stopping = false;

        byte[] pcmBytes;
        lock (_sync)
        {
            pcmBytes = _pcm.ToArray();
        }

        return WavFile.FromPcm16Mono(pcmBytes, 16000);
    }

    public void Cancel()
    {
        _stopping = true;
        if (_handle != IntPtr.Zero)
        {
            WaveInNative.waveInStop(_handle);
            WaveInNative.waveInReset(_handle);
            CleanupDevice();
        }

        _recording = false;
        _stopping = false;
        lock (_sync)
        {
            _pcm.SetLength(0);
        }
    }

    private void OnWaveIn(IntPtr waveInHandle, uint message, IntPtr instance, IntPtr param1, IntPtr param2)
    {
        if (message != WimData || param1 == IntPtr.Zero)
        {
            return;
        }

        var header = Marshal.PtrToStructure<WaveHeader>(param1);

        if (header.BytesRecorded > 0)
        {
            var bytes = new byte[header.BytesRecorded];
            Marshal.Copy(header.Data, bytes, 0, bytes.Length);
            lock (_sync)
            {
                _pcm.Write(bytes, 0, bytes.Length);
            }
        }

        if (_recording && !_stopping && _handle != IntPtr.Zero)
        {
            header.BytesRecorded = 0;
            Marshal.StructureToPtr(header, param1, false);
            WaveInNative.waveInAddBuffer(_handle, param1, Marshal.SizeOf<WaveHeader>());
        }
    }

    private void CleanupDevice()
    {
        foreach (var buffer in _buffers)
        {
            WaveInNative.waveInUnprepareHeader(_handle, buffer.HeaderPointer, Marshal.SizeOf<WaveHeader>());
            buffer.Dispose();
        }

        _buffers.Clear();

        if (_handle != IntPtr.Zero)
        {
            WaveInNative.waveInClose(_handle);
            _handle = IntPtr.Zero;
        }
    }

    private static void Check(int result, string operation)
    {
        if (result != 0)
        {
            throw new InvalidOperationException($"{operation} failed with WinMM error code {result}.");
        }
    }
}

internal static class Keyboard
{
    private const short KeyPressed = unchecked((short)0x8000);

    public static bool IsKeyDown(ConsoleKey key)
    {
        return (GetAsyncKeyState((int)key) & KeyPressed) != 0;
    }

    [DllImport("user32.dll")]
    private static extern short GetAsyncKeyState(int virtualKeyCode);
}

internal sealed class AudioBuffer : IDisposable
{
    private AudioBuffer(IntPtr dataPointer, IntPtr headerPointer)
    {
        DataPointer = dataPointer;
        HeaderPointer = headerPointer;
    }

    public IntPtr DataPointer { get; }

    public IntPtr HeaderPointer { get; }

    public static AudioBuffer Create(int size)
    {
        var dataPointer = Marshal.AllocHGlobal(size);
        var headerPointer = Marshal.AllocHGlobal(Marshal.SizeOf<WaveHeader>());

        var header = new WaveHeader
        {
            Data = dataPointer,
            BufferLength = (uint)size,
            BytesRecorded = 0,
            User = IntPtr.Zero,
            Flags = 0,
            Loops = 0,
            Next = IntPtr.Zero,
            Reserved = IntPtr.Zero,
        };

        Marshal.StructureToPtr(header, headerPointer, false);
        return new AudioBuffer(dataPointer, headerPointer);
    }

    public void Dispose()
    {
        if (HeaderPointer != IntPtr.Zero)
        {
            Marshal.FreeHGlobal(HeaderPointer);
        }

        if (DataPointer != IntPtr.Zero)
        {
            Marshal.FreeHGlobal(DataPointer);
        }
    }
}

[StructLayout(LayoutKind.Sequential)]
internal struct WaveFormat
{
    public ushort FormatTag;
    public ushort Channels;
    public uint SamplesPerSecond;
    public uint AverageBytesPerSecond;
    public ushort BlockAlign;
    public ushort BitsPerSample;
    public ushort Size;

    public static WaveFormat Pcm16Mono(uint sampleRate)
    {
        const ushort channels = 1;
        const ushort bitsPerSample = 16;
        var blockAlign = (ushort)(channels * bitsPerSample / 8);

        return new WaveFormat
        {
            FormatTag = 1,
            Channels = channels,
            SamplesPerSecond = sampleRate,
            AverageBytesPerSecond = sampleRate * blockAlign,
            BlockAlign = blockAlign,
            BitsPerSample = bitsPerSample,
            Size = 0,
        };
    }
}

[StructLayout(LayoutKind.Sequential)]
internal struct WaveHeader
{
    public IntPtr Data;
    public uint BufferLength;
    public uint BytesRecorded;
    public IntPtr User;
    public uint Flags;
    public uint Loops;
    public IntPtr Next;
    public IntPtr Reserved;
}

internal static class WaveInNative
{
    public delegate void WaveInProc(IntPtr waveInHandle, uint message, IntPtr instance, IntPtr param1, IntPtr param2);

    [DllImport("winmm.dll")]
    public static extern int waveInOpen(out IntPtr waveInHandle, int deviceId, ref WaveFormat format, WaveInProc callback, IntPtr instance, int flags);

    [DllImport("winmm.dll")]
    public static extern int waveInPrepareHeader(IntPtr waveInHandle, IntPtr header, int headerSize);

    [DllImport("winmm.dll")]
    public static extern int waveInAddBuffer(IntPtr waveInHandle, IntPtr header, int headerSize);

    [DllImport("winmm.dll")]
    public static extern int waveInStart(IntPtr waveInHandle);

    [DllImport("winmm.dll")]
    public static extern int waveInStop(IntPtr waveInHandle);

    [DllImport("winmm.dll")]
    public static extern int waveInReset(IntPtr waveInHandle);

    [DllImport("winmm.dll")]
    public static extern int waveInUnprepareHeader(IntPtr waveInHandle, IntPtr header, int headerSize);

    [DllImport("winmm.dll")]
    public static extern int waveInClose(IntPtr waveInHandle);
}

internal static class WavFile
{
    public static byte[] FromPcm16Mono(byte[] pcmBytes, int sampleRate)
    {
        using var stream = new MemoryStream();
        using var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true);

        const short channels = 1;
        const short bitsPerSample = 16;
        var byteRate = sampleRate * channels * bitsPerSample / 8;
        var blockAlign = (short)(channels * bitsPerSample / 8);

        writer.Write(Encoding.ASCII.GetBytes("RIFF"));
        writer.Write(36 + pcmBytes.Length);
        writer.Write(Encoding.ASCII.GetBytes("WAVE"));
        writer.Write(Encoding.ASCII.GetBytes("fmt "));
        writer.Write(16);
        writer.Write((short)1);
        writer.Write(channels);
        writer.Write(sampleRate);
        writer.Write(byteRate);
        writer.Write(blockAlign);
        writer.Write(bitsPerSample);
        writer.Write(Encoding.ASCII.GetBytes("data"));
        writer.Write(pcmBytes.Length);
        writer.Write(pcmBytes);
        writer.Flush();

        return stream.ToArray();
    }
}
