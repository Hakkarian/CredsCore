import httpx
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = await client.post(url, json=json)
        response.raise_for_status()
        return response.json()

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def __del__(self):
        if self._client and not self._client.is_closed:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(self._client.aclose())
                else:
                    asyncio.run(self._client.aclose())
            except RuntimeError:
                pass