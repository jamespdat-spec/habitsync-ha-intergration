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

    async def close(self):
        """Close the client."""
        if self.client is not None:
            await self.client.aclose()
