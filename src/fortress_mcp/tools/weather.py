"""Open-Meteo live weather tool."""

from collections.abc import Mapping

import httpx


class WeatherTool:
    """Fetch current weather from the selected free live API."""

    name = "weather_lookup"

    endpoint = "https://api.open-meteo.com/v1/forecast"

    def execute(self, arguments: Mapping[str, object]) -> object:
        """Validate coordinates and fetch current weather."""
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")

        if not isinstance(latitude, (int, float)):
            raise ValueError("latitude must be numeric")

        if not isinstance(longitude, (int, float)):
            raise ValueError("longitude must be numeric")

        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "UTC",
        }

        try:
            response = httpx.get(
                self.endpoint,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("Weather provider request failed.") from exc

        payload = response.json()

        current = payload.get("current")

        if not isinstance(current, dict):
            raise RuntimeError("Weather provider returned an invalid response.")

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": payload.get("timezone"),
            "current": current,
        }
