import httpx
from typing import Optional

from app.config import settings


class RingCentralService:
    def __init__(self):
        self.client_id = settings.ringcentral_client_id
        self.client_secret = settings.ringcentral_client_secret
        self.base_url = "https://platform.ringcentral.com"
    
    def get_oauth_url(self, redirect_uri: str) -> str:
        return (
            f"{self.base_url}/restapi/oauth/authorize"
            f"?response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&client_id={self.client_id}"
            f"&state=random_state_string"
        )
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/restapi/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            return response.json()
    
    async def get_call_history(self, access_token: str, user_id: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/restapi/v1.0/account/~/extension/~/call-log",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("records", [])
    
    async def get_call_recording(self, access_token: str, recording_id: str) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/restapi/v1.0/account/~/recording/{recording_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.content
