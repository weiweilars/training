#!/usr/bin/env python3
"""
Simple Weather Tool - Training Example
Single-page MCP tool for basic weather information
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
    print("💡 Or run: pip install -r requirements.txt")
    exit(1)

# Configuration
DEFAULT_UNITS = os.getenv("WEATHER_UNITS", "celsius")
stateless_mode = os.getenv("STATELESS_HTTP", "true").lower() == "true"

# Create MCP instance
mcp = FastMCP(name="simple-weather-tool")

@mcp.tool()
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
        # Generate realistic weather data based on city characteristics
        location = f"{city}, {country}" if country else city
        
        # Create consistent data based on city name
        city_hash = hash(city.lower()) % 100
        temp = 15 + (city_hash % 20)  # Temperature between 15-35°C
        humidity = 40 + (city_hash % 40)  # Humidity between 40-80%
        
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
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(weather_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Weather lookup failed: {str(e)}",
            "location": city,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    Get weather forecast for specified days (mock data for demo)
    
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
            
            # Vary temperature slightly for each day
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
            "note": "This is mock data for training purposes"
        }
        
        return json.dumps(forecast_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Weather forecast failed: {str(e)}",
            "location": city,
            "requested_days": days,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
def convert_temperature(temperature: float, from_unit: str, to_unit: str) -> str:
    """
    Convert temperature between units
    
    Args:
        temperature: Temperature value to convert
        from_unit: Source unit (celsius, fahrenheit, kelvin)
        to_unit: Target unit (celsius, fahrenheit, kelvin)
        
    Returns:
        Converted temperature
    """
    try:
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Convert to Celsius first
        if from_unit == "fahrenheit":
            celsius = (temperature - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = temperature - 273.15
        else:  # celsius
            celsius = temperature
        
        # Convert from Celsius to target unit
        if to_unit == "fahrenheit":
            result = celsius * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:  # celsius
            result = celsius
        
        conversion_data = {
            "original_value": temperature,
            "original_unit": from_unit,
            "converted_value": round(result, 2),
            "converted_unit": to_unit,
            "conversion_formula": f"{from_unit} → celsius → {to_unit}",
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(conversion_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Temperature conversion failed: {str(e)}",
            "input": {
                "temperature": temperature,
                "from_unit": from_unit,
                "to_unit": to_unit
            }
        })

if __name__ == "__main__":
    print(f"Simple Weather Tool - {mcp.name}")
    print(f"Default units: {DEFAULT_UNITS}")
    print("Starting MCP server...")
    mcp.run(stateless_http=stateless_mode)