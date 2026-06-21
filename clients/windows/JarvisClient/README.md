# Jarvis Windows Client

Minimal Windows kliens a Jarvis V2 packet kommunikacio kiprobalasahoz.

## Funkciok

- TCP JSON-line packet kapcsolat a szerverrel.
- Push-to-talk WAV kuldes: tartsd nyomva a `Space` billentyut.
- Text packet kuldes: `T`.
- Kilepes: `Q`.
- Demo tool call vegrehajtas:
  - `open_chrome`
  - `echo`

## Kovetelmeny

- .NET 10 SDK/runtime Windowsra.

Ha a `dotnet` nincs PATH-on, hasznald teljes utvonallal:

```powershell
& "C:\Program Files\dotnet\dotnet.exe" --info
```

## Futtatas

```powershell
dotnet run --project .\clients\windows\JarvisClient -- --host 127.0.0.1 --port 8765 --user barnus --device barnus-pc
```

PATH nelkul:

```powershell
& "C:\Program Files\dotnet\dotnet.exe" run --project .\clients\windows\JarvisClient -- --host 127.0.0.1 --port 8765 --user barnus --device barnus-pc
```

Alapertelmezett ertekek:

- host: `127.0.0.1`
- port: `8765`
- user: aktualis Windows felhasznalo
- device: gepnev kisbetusitve

## Packet format

A kliens a jelenlegi Python skeleton `Message` modelljehez igazodik:

```json
{
  "user_id": "barnus",
  "device_id": "barnus-pc",
  "type": "input",
  "payload": "base64-wav-vagy-text",
  "encoding": "wav",
  "request_id": "guid",
  "timestamp": 1782030000
}
```

WAV eseten a `payload` base64 string, mert JSON-on keresztul binaris adat nem kuldheto kozvetlenul.

Megjegyzes: ez a WAV kuldes jelenleg prototipus. Roevid push-to-talk parancsokra jo,
de kesobb erdemes lesz az audiot kisebb chunkokra bontani vagy hosszelotagos
packet protokollra valtani.
