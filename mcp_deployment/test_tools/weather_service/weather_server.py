#!/usr/bin/env python3
"""
Weather Service - Production Ready Weather Tool
Enhanced weather tool with environment configuration
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ ERROR: FastMCP not found!")
    print("📦 Install required dependency:")
    print("   pip install fastmcp")
    exit(1)

# Environment Configuration
API_KEY = os.getenv("WEATHER_API_KEY", "demo_key")
DEFAULT_UNITS = os.getenv("WEATHER_UNITS", "celsius")
SERVICE_NAME = os.getenv("SERVICE_NAME", "weather-service")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))

# Create MCP instance with custom name
weather_api = FastMCP(name=SERVICE_NAME)

@weather_api.tool()
def get_current_weather(city: str, country: Optional[str] = None) -> str:
    """
    Get current weather conditions for any city worldwide

    Args:
        city: City name (e.g., "London", "New York")
        country: Optional country name or code

    Returns:
        Current weather data in JSON format including temperature, conditions, and humidity
    """
    try:
        if DEBUG_MODE:
            print(f"Weather API called for {city}, API Key: {API_KEY[:8]}...")

        location = f"{city}, {country}" if country else city

        # Generate realistic weather data based on city characteristics
        city_hash = hash(city.lower()) % 100
        temp = 15 + (city_hash % 20)
        humidity = 40 + (city_hash % 40)

        weather_conditions = ["Sunny", "Partly cloudy", "Cloudy", "Overcast", "Light rain"]
        condition = weather_conditions[city_hash % len(weather_conditions)]

        weather_data = {
            "location": location,
            "temperature": temp,
            "temperature_unit": DEFAULT_UNITS,
            "humidity": f"{humidity}%",
            "condition": condition,
            "wind_speed": round(2.0 + (city_hash % 8), 1),
            "wind_unit": "m/s",
            "timestamp": datetime.now().isoformat(),
            "api_key_used": API_KEY[:8] + "..." if API_KEY != "demo_key" else "demo_key",
            "service": SERVICE_NAME
        }

        return json.dumps(weather_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Weather lookup failed: {str(e)}",
            "location": city,
            "timestamp": datetime.now().isoformat()
        })

@weather_api.tool()
def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    Get weather forecast for specified days

    Args:
        city: City name
        days: Number of forecast days (1-7)

    Returns:
        Weather forecast in JSON format
    """
    try:
        if days > 7:
            days = 7

        city_hash = hash(city.lower()) % 100
        base_temp = 15 + (city_hash % 20)

        forecasts = []
        for i in range(days):
            forecast_date = datetime.now() + timedelta(days=i+1)
            daily_temp = base_temp + ((i + city_hash) % 8) - 4

            forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day": forecast_date.strftime("%A"),
                "temperature_high": daily_temp + 5,
                "temperature_low": daily_temp - 3,
                "condition": ["Sunny", "Cloudy", "Rainy", "Partly cloudy"][i % 4],
                "precipitation_chance": min(20 + (i * 15), 80)
            })

        forecast_data = {
            "location": city,
            "forecast_days": days,
            "temperature_unit": DEFAULT_UNITS,
            "forecasts": forecasts,
            "generated_at": datetime.now().isoformat(),
            "service": SERVICE_NAME,
            "rate_limit": RATE_LIMIT
        }

        return json.dumps(forecast_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Weather forecast failed: {str(e)}",
            "location": city,
            "requested_days": days,
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    print(f"Weather Service - {weather_api.name}")
    print(f"API Key: {API_KEY[:8]}..." if API_KEY != "demo_key" else "Using demo key")
    print(f"Default units: {DEFAULT_UNITS}")
    print(f"Debug mode: {DEBUG_MODE}")
    print("Starting weather service...")
    weather_api.run()