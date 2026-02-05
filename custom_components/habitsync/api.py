"""API for HabitSync."""
import httpx

class HabitSyncApi:
    """HabitSync API."""

    def __init__(self, host: str, api_key: str):
        """Initialize the API."""
        self.host = host
        self.api_key = api_key
        self.client = None

    async def _ensure_client(self):
        """Ensure the async client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(base_url=self.host, headers={"X-API-Key": self.api_key})

    async def get_habits(self):
        """Get habits from the API."""
        await self._ensure_client()
        response = await self.client.get("/api/habit/list")
        response.raise_for_status()
        return response.json()

    async def get_record(self, habit_id: str, offset: int = 0, time_zone: str | None = None):
        """Get a record for a habit.

        Calls GET /api/record/<habit_id>/simple?offset=...&timeZone=...
        """
        await self._ensure_client()
        params = {"offset": str(offset)}
        if time_zone:
            params["timeZone"] = time_zone
        url = f"/api/record/{habit_id}/simple"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def create_record(self, habit_id: str, value: float = 1.0, offset: int = 0, time_zone: str | None = None):
        """Create a simple record for a habit.

        Calls POST /api/record/<habit_id>/simple?value=...&offset=...&timeZone=...
        """
        await self._ensure_client()
        params = {"value": str(value), "offset": str(offset)}
        if time_zone:
            params["timeZone"] = time_zone
        url = f"/api/record/{habit_id}/simple"
        response = await self.client.post(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client."""
        if self.client is not None:
            await self.client.aclose()
