#!/usr/bin/env python3
"""
MCP Weather Server - A production-ready FastMCP server with simulated weather data.

Provides weather tools, resources, and prompts via the Model Context Protocol.
Supports both stdio and Streamable HTTP transports.
"""

import sys
import argparse
import logging
from typing import Any
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP, Context

# Configure logging to stderr (critical for stdio transport)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("mcp-weather")

# ─── Simulated Weather Data ────────────────────────────────────────────
# No API key required - realistic simulated data for demonstration
US_STATES = {
    "CA": "California", "TX": "Texas", "NY": "New York",
    "FL": "Florida", "IL": "Illinois", "WA": "Washington",
    "CO": "Colorado", "AZ": "Arizona", "OR": "Oregon",
    "MA": "Massachusetts", "DC": "District of Columbia",
}

FORECAST_DATA = {
    "CA": {"temp": 72, "condition": "Sunny", "humidity": 45, "wind": 8},
    "TX": {"temp": 95, "condition": "Hot and Dry", "humidity": 30, "wind": 12},
    "NY": {"temp": 58, "condition": "Partly Cloudy", "humidity": 65, "wind": 10},
    "FL": {"temp": 85, "condition": "Thunderstorms", "humidity": 80, "wind": 15},
    "IL": {"temp": 62, "condition": "Cloudy", "humidity": 70, "wind": 9},
    "WA": {"temp": 55, "condition": "Rain", "humidity": 78, "wind": 11},
    "CO": {"temp": 68, "condition": "Clear", "humidity": 35, "wind": 14},
    "AZ": {"temp": 102, "condition": "Extreme Heat", "humidity": 15, "wind": 5},
    "OR": {"temp": 60, "condition": "Drizzle", "humidity": 72, "wind": 7},
    "MA": {"temp": 54, "condition": "Overcast", "humidity": 68, "wind": 13},
    "DC": {"temp": 70, "condition": "Humid", "humidity": 75, "wind": 6},
}

ALERTS_DATA = {
    "CA": [{"type": "Heat Advisory", "severity": "Moderate", "area": "Southern California"}],
    "TX": [{"type": "Extreme Heat Warning", "severity": "Severe", "area": "Central Texas"}],
    "FL": [{"type": "Flood Watch", "severity": "Moderate", "area": "Coastal Florida"},
           {"type": "Thunderstorm Warning", "severity": "Severe", "area": "Miami-Dade"}],
    "NY": [{"type": "Wind Advisory", "severity": "Minor", "area": "New York City Metro"}],
    "CO": [{"type": "Winter Weather Advisory", "severity": "Moderate", "area": "Rocky Mountains"}],
    "WA": [{"type": "Flood Watch", "severity": "Moderate", "area": "Western Washington"}],
    "AZ": [{"type": "Excessive Heat Warning", "severity": "Severe", "area": "Phoenix Metro"}],
    "IL": [{"type": "Air Quality Alert", "severity": "Moderate", "area": "Chicago Metro"}],
}

# ─── Initialize FastMCP Server ─────────────────────────────────────────
mcp = FastMCP(
    "Weather Server",
    description="Provides weather forecasts, alerts, and current conditions for US states. Uses simulated data for demonstration.",
    version="1.0.0",
)


# ─── Tools ─────────────────────────────────────────────────────────────
@mcp.tool(description="Get weather alerts for a US state (2-letter code)")
def get_alerts(state: str) -> list[dict[str, Any]]:
    """Get active weather alerts for a specified US state.
    
    Args:
        state: Two-letter US state code (e.g., 'CA', 'TX', 'NY')
        
    Returns:
        List of alert objects with type, severity, and affected area
    """
    state = state.upper()
    if state not in US_STATES:
        return [{"error": f"Unknown state code: {state}. Valid codes: {', '.join(sorted(US_STATES.keys()))}"}]
    
    alerts = ALERTS_DATA.get(state, [])
    if not alerts:
        return [{"message": f"No active alerts for {US_STATES[state]} ({state})"}]
    return alerts


@mcp.tool(description="Get 5-day weather forecast for coordinates")
def get_forecast(latitude: float, longitude: float) -> list[dict[str, Any]]:
    """Get a 5-day weather forecast for given latitude/longitude coordinates.
    
    Uses the closest simulated US state weather station based on coordinates.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        
    Returns:
        5-day forecast with date, temp, condition, humidity, wind
    """
    # Simple proximity mapping for demonstration
    # Real implementation would call weather.gov API
    state = _coords_to_state(latitude, longitude)
    base = FORECAST_DATA.get(state, {"temp": 65, "condition": "Fair", "humidity": 50, "wind": 8})
    
    forecast = []
    for day in range(5):
        date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        temp_var = (day * 3) % 15 - 5  # Varied temperature within range
        forecast.append({
            "date": date,
            "temperature_f": base["temp"] + temp_var,
            "condition": base["condition"],
            "humidity_pct": min(100, base["humidity"] + day * 2),
            "wind_mph": base["wind"] + day,
            "state": state,
        })
    return forecast


# ─── Resources ─────────────────────────────────────────────────────────
@mcp.resource("weather://{state}/current")
def get_current_weather(state: str) -> str:
    """Get current weather conditions for a state as a formatted string."""
    state = state.upper()
    if state not in US_STATES:
        return f"Unknown state: {state}"
    
    data = FORECAST_DATA.get(state, {"temp": 65, "condition": "Fair", "humidity": 50, "wind": 8})
    alerts = ALERTS_DATA.get(state, [])
    
    result = f"""# Current Weather - {US_STATES[state]} ({state})
**As of:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

| Metric | Value |
|---------|-------|
| Temperature | {data['temp']}°F |
| Condition | {data['condition']} |
| Humidity | {data['humidity']}% |
| Wind | {data['wind']} mph |
"""
    if alerts:
        result += "\n## Active Alerts\n"
        for alert in alerts:
            result += f"- **{alert['type']}** ({alert['severity']}): {alert['area']}\n"
    
    return result


# ─── Prompts ───────────────────────────────────────────────────────────
@mcp.prompt(description="Weather assistant prompt template for a specific state")
def weather_assistant(state: str) -> str:
    """Create a tailored prompt for a weather analysis assistant.
    
    Args:
        state: Two-letter US state code
    """
    state = state.upper()
    state_name = US_STATES.get(state, state)
    return f"""You are a weather analysis assistant specializing in {state_name} ({state}) weather.

Your capabilities:
1. Current conditions: Temperature, humidity, wind, and sky conditions
2. Active weather alerts and advisories
3. 5-day forecast trends and patterns
4. Historical weather context for the region

When responding:
- Use simple, clear language suitable for the general public
- Highlight any active alerts or warnings first
- Note significant weather events (heat waves, storms, etc.)
- Include humidity and wind data when relevant (comfort index, fire risk, etc.)

Always lead with safety information if there are active alerts."""


# ─── Helper Functions ──────────────────────────────────────────────────
def _coords_to_state(lat: float, lon: float) -> str:
    """Simple coordinate-to-state mapping for demonstration.
    
    This is a simplified grid - real implementation would use reverse geocoding.
    """
    # US continental rough bounding box
    if 25 <= lat <= 49 and -125 <= lon <= -67:
        if lat > 42: return "WA" if lon < -120 else "NY"
        if lon < -110: return "CA" if lat < 38 else "OR" if lat < 45 else "WA"
        if lon < -100: return "AZ" if lat < 35 else "CO" if lat < 40 else "IL"
        if lon < -90: return "TX" if lat < 33 else "IL"
        if lat < 28: return "FL"
        return "NY"
    return "CA"  # Default


# ─── CLI Entry Point ───────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MCP Weather Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for Streamable HTTP transport (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for Streamable HTTP transport (default: 0.0.0.0)"
    )
    args = parser.parse_args()
    
    logger.info(f"Starting MCP Weather Server (transport={args.transport})")
    
    if args.transport == "streamable-http":
        logger.info(f"Listening on http://{args.host}:{args.port}")
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
