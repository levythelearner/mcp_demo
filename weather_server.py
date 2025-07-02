#!/usr/bin/env python3
"""
Demo MCP Server: Weather Server
Provides weather forecast and current conditions tools via MCP protocol using FastMCP.
"""

import argparse
import requests
from fastmcp import FastMCP

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Headers for API requests
headers = {
    'User-Agent': USER_AGENT
}

mcp = FastMCP("Weather")

@mcp.tool()
def get_weather_forecast(latitude: float, longitude: float, location_name: str = "Location") -> str:
    """Get weather forecast for a given location using latitude and longitude"""
    try:
        # Step 1: Get grid information
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        response = requests.get(points_url, headers=headers, timeout=10)
        response.raise_for_status()
        points_data = response.json()
        
        # Extract forecast URL
        forecast_url = points_data['properties']['forecast']
        office = points_data['properties']['gridId']
        grid_x = points_data['properties']['gridX']
        grid_y = points_data['properties']['gridY']
        
        # Step 2: Get forecast
        forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Format forecast
        periods = forecast_data['properties']['periods']
        result = f"Weather Forecast for {location_name}\n"
        result += f"Weather Office: {office}, Grid: ({grid_x}, {grid_y})\n\n"
        
        for period in periods[:5]:  # Show first 5 periods
            result += f"{period['name']}: {period['temperature']}°{period['temperatureUnit']}\n"
            result += f"  Conditions: {period['shortForecast']}\n"
            result += f"  Details: {period['detailedForecast'][:150]}...\n\n"
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except KeyError as e:
        return f"Error parsing weather data: {e}"

@mcp.tool()
def get_current_conditions(latitude: float, longitude: float, location_name: str = "Location") -> str:
    """Get current weather conditions for a given location"""
    try:
        # Get grid information
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        response = requests.get(points_url, headers=headers, timeout=10)
        response.raise_for_status()
        points_data = response.json()
        
        # Get current conditions from stations
        stations_url = points_data['properties']['observationStations']
        stations_response = requests.get(stations_url, headers=headers, timeout=10)
        stations_response.raise_for_status()
        stations_data = stations_response.json()
        
        if stations_data['features']:
            # Get observations from the first station
            station_url = stations_data['features'][0]['id']
            obs_url = f"{station_url}/observations/latest"
            
            obs_response = requests.get(obs_url, headers=headers, timeout=10)
            obs_response.raise_for_status()
            obs_data = obs_response.json()
            
            props = obs_data['properties']
            
            result = f"Current Conditions for {location_name}\n"
            result += f"Station: {stations_data['features'][0]['properties']['name']}\n"
            result += f"Time: {props.get('timestamp', 'N/A')}\n"
            
            # Temperature
            if props.get('temperature', {}).get('value'):
                temp_c = props['temperature']['value']
                temp_f = (temp_c * 9/5) + 32
                result += f"Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)\n"
            
            # Other conditions
            if props.get('textDescription'):
                result += f"Conditions: {props['textDescription']}\n"
            
            if props.get('windSpeed', {}).get('value'):
                wind_ms = props['windSpeed']['value']
                wind_mph = wind_ms * 2.237
                result += f"Wind Speed: {wind_mph:.1f} mph\n"
            
            if props.get('windDirection', {}).get('value'):
                result += f"Wind Direction: {props['windDirection']['value']}°\n"
            
            if props.get('relativeHumidity', {}).get('value'):
                result += f"Humidity: {props['relativeHumidity']['value']:.1f}%\n"
            
            return result
        else:
            return f"No observation stations found for {location_name}"
            
    except Exception as e:
        return f"Error getting current conditions: {e}"

@mcp.tool()
def get_weather_alerts(latitude: float, longitude: float, location_name: str = "Location") -> str:
    """Get weather alerts for a given location"""
    try:
        # Get alerts for the point
        alerts_url = f"{NWS_API_BASE}/alerts/active?point={latitude},{longitude}"
        response = requests.get(alerts_url, headers=headers, timeout=10)
        response.raise_for_status()
        alerts_data = response.json()
        
        features = alerts_data.get('features', [])
        
        if not features:
            return f"No active weather alerts for {location_name}"
        
        result = f"Active Weather Alerts for {location_name}\n"
        result += "=" * 50 + "\n\n"
        
        for alert in features[:5]:  # Show up to 5 alerts
            props = alert['properties']
            result += f"Alert: {props.get('event', 'Unknown')}\n"
            result += f"Severity: {props.get('severity', 'Unknown')}\n"
            result += f"Urgency: {props.get('urgency', 'Unknown')}\n"
            result += f"Areas: {', '.join(props.get('areaDesc', '').split(';')[:3])}\n"
            
            if props.get('headline'):
                result += f"Headline: {props['headline']}\n"
            
            if props.get('description'):
                result += f"Description: {props['description'][:200]}...\n"
            
            result += "\n" + "-" * 30 + "\n\n"
        
        return result
        
    except Exception as e:
        return f"Error getting weather alerts: {e}"

@mcp.tool()
def get_city_weather(city_name: str) -> str:
    """Get weather for common US cities by name"""
    # Common city coordinates
    cities = {
        "san francisco": (37.7749, -122.4194),
        "new york": (40.7128, -74.0060),
        "los angeles": (34.0522, -118.2437),
        "chicago": (41.8781, -87.6298),
        "houston": (29.7604, -95.3698),
        "phoenix": (33.4484, -112.0740),
        "philadelphia": (39.9526, -75.1652),
        "san antonio": (29.4241, -98.4936),
        "san diego": (32.7157, -117.1611),
        "dallas": (32.7767, -96.7970),
        "miami": (25.7617, -80.1918),
        "atlanta": (33.7490, -84.3880),
        "boston": (42.3601, -71.0589),
        "seattle": (47.6062, -122.3321),
        "denver": (39.7392, -104.9903)
    }
    
    city_lower = city_name.lower()
    if city_lower in cities:
        lat, lon = cities[city_lower]
        return get_weather_forecast(lat, lon, city_name.title())
    else:
        available = ", ".join(sorted(cities.keys()))
        return f"City '{city_name}' not found. Available cities: {available}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument("--transport", default="stdio", help="Transport type (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=6001, help="Port number (default: 6001)")
    
    args = parser.parse_args()
    print("🌤️ Starting Weather MCP Server...")
    print(f"📡 Transport: {args.transport}")

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)