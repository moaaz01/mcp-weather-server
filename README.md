# 🌤️ MCP Weather Server

> A production-ready **Model Context Protocol** weather server built with the official [Anthropic FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). Provides weather forecasts, alerts, and current conditions through a standardized AI-agent interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-%3E%3D1.27-green)](https://pypi.org/project/mcp/)

---

## ✨ Features

- **🔧 2 Tools**: `get_alerts` (weather alerts by state) and `get_forecast` (5-day forecast by coordinates)
- **📄 1 Resource**: `weather://{state}/current` — formatted current conditions
- **💬 1 Prompt**: `weather_assistant(state)` — guided weather analysis template
- **🔌 Dual Transport**: stdio (local clients) and Streamable HTTP (remote clients)
- **🪵 Structured Logging**: All server logs go to stderr (compatible with stdio transport)
- **📦 No API Keys Required**: Uses realistic simulated weather data
- **🧪 Test Client Included**: Ready-to-run example client

---

## 🚀 Quick Start

### Option 1: pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python weather_server.py
```

### Option 2: uv (recommended)

```bash
uv venv
source .venv/bin/activate
uv add "mcp[cli]>=1.27,<2" httpx
python weather_server.py
```

### Option 3: Setup script

```bash
chmod +x setup.sh
./setup.sh
python weather_server.py
```

---

## 📋 Usage

### stdio Transport (default)

```bash
python weather_server.py
```

The server listens on stdin/stdout, ready to connect to Claude Desktop, Cursor, or any MCP client.

### Streamable HTTP Transport

```bash
python weather_server.py --transport streamable-http --port 8000
```

Now available at `http://localhost:8000/mcp` for HTTP-based clients.

### Run the Test Client

```bash
# In one terminal:
python weather_server.py

# In another terminal:
source .venv/bin/activate
python client_example.py
```

---

## 🛠️ Tools Reference

### `get_alerts(state: str) -> list[dict]`
Get active weather alerts for a US state.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `state` | `str` | 2-letter US state code | `"CA"`, `"TX"`, `"FL"` |

**Returns:** List of alerts with `type`, `severity`, and `area`.

### `get_forecast(latitude: float, longitude: float) -> list[dict]`
Get a 5-day weather forecast for coordinates.

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | `float` | Decimal degrees (-90 to 90) |
| `longitude` | `float` | Decimal degrees (-180 to 180) |

**Returns:** 5-day forecast with `date`, `temperature_f`, `condition`, `humidity_pct`, `wind_mph`.

---

## 📄 Resources Reference

### `weather://{state}/current`
Returns formatted current weather conditions for a state as markdown.

---

## 💬 Prompts Reference

### `weather_assistant(state: str)`
Creates a weather analysis assistant prompt template.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `str` | 2-letter US state code |

---

## 🔌 Connecting to Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/mcp-weather-server/weather_server.py"]
    }
  }
}
```

### Cursor

In Cursor Settings → Features → MCP Servers, add:

- **Name**: `weather`
- **Type**: `command`
- **Command**: `python /ABSOLUTE/PATH/TO/mcp-weather-server/weather_server.py`

### HTTP Client (Streamable HTTP)

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

---

## 📁 Project Structure

```
mcp-weather-server/
├── weather_server.py      # Main server implementation
├── client_example.py      # Example MCP client
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── README.md             # This file
└── .gitignore
```

---

## 🧠 Architecture

```
┌─────────────┐     stdio/HTTP      ┌──────────────────┐
│  MCP Client  │ ◄──────────────►  │  Weather Server   │
│ (Claude, etc)│                    │  (FastMCP)        │
└─────────────┘                     └──────────────────┘
                                           │
                                    ┌──────┴──────┐
                                    │  Simulated   │
                                    │  Weather Data│
                                    └─────────────┘
```

---

## 📜 License

MIT — see [LICENSE](LICENSE) for details.

## 🙌 Contributing

PRs welcome! Please ensure tools have proper type hints and docstrings.
