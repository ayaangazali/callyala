"""ElevenLabs Conversational AI batch calling service."""

from typing import Any, Optional
import uuid

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.time import now_utc


ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsService:
    """ElevenLabs API client for batch calling."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=ELEVENLABS_BASE_URL,
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
                timeout=settings.http_timeout_seconds,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def initiate_outbound_call(
        self,
        phone_number: str,
        agent_id: str,
        phone_number_id: str,
        first_message: Optional[str] = None,
        dynamic_variables: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Initiate a single outbound call via ElevenLabs.
        
        Returns:
            dict with call_id, status, etc.
        """
        if settings.mock_mode:
            mock_call_id = f"mock_{uuid.uuid4().hex[:12]}"
            logger.info(f"MOCK_MODE: Would call {phone_number}, returning mock call_id: {mock_call_id}")
            return {
                "call_id": mock_call_id,
                "status": "queued",
                "phone_number": phone_number,
            }

        client = await self._get_client()
        
        # Payload for ElevenLabs Conversational AI outbound call
        payload = {
            "agent_id": agent_id,
            "phone_number_id": phone_number_id,
            "phone_number": phone_number,
        }
        
        if first_message:
            payload["first_message"] = first_message
        
        if dynamic_variables:
            payload["dynamic_variables"] = dynamic_variables

        try:
            # ElevenLabs Conversational AI - Correct endpoint for phone calls
            # Updated endpoint based on ElevenLabs Conversational AI API
            endpoint = f"/v1/convai/conversation"
            logger.info(f"Calling ElevenLabs: POST {endpoint}")
            logger.info(f"Payload: agent_id={agent_id}, phone={phone_number}")
            
            response = await client.post(
                endpoint,
                json=payload,
            )
            
            # Log response for debugging
            logger.info(f"ElevenLabs response status: {response.status_code}")
            logger.info(f"ElevenLabs response body: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract call_id from response
            call_id = data.get("conversation_id") or data.get("call_id") or f"call_{uuid.uuid4().hex[:12]}"
            
            result = {
                "call_id": call_id,
                "status": "queued",
                "phone_number": phone_number,
                "elevenlabs_response": data
            }
            
            logger.info(f"✅ Initiated call to {phone_number}: {call_id}")
            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ ElevenLabs API error: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            # Return a mock response so the app doesn't crash
            mock_id = f"error_{uuid.uuid4().hex[:12]}"
            return {
                "call_id": mock_id,
                "status": "failed",
                "phone_number": phone_number,
                "error": e.response.text
            }
        except Exception as e:
            logger.error(f"❌ Failed to initiate call: {e}")
            mock_id = f"error_{uuid.uuid4().hex[:12]}"
            return {
                "call_id": mock_id,
                "status": "failed",
                "phone_number": phone_number,
                "error": str(e)
            }

    async def initiate_batch_calls(
        self,
        calls: list[dict[str, Any]],
        agent_id: str,
        phone_number_id: str,
    ) -> list[dict[str, Any]]:
        """
        Initiate multiple outbound calls.
        
        Args:
            calls: List of dicts with 'phone', 'first_name', etc.
            agent_id: ElevenLabs agent ID
            phone_number_id: ElevenLabs phone number ID
        
        Returns:
            List of results for each call
        """
        results = []
        
        for call_data in calls:
            phone = call_data.get("phone")
            if not phone:
                results.append({"error": "No phone number", "status": "failed"})
                continue
            
            try:
                # Build dynamic variables from call data
                dynamic_vars = {
                    "customer_name": call_data.get("customer_name", ""),
                    "first_name": call_data.get("first_name", ""),
                    "vehicle_interest": call_data.get("vehicle_interest", ""),
                }
                
                result = await self.initiate_outbound_call(
                    phone_number=phone,
                    agent_id=agent_id,
                    phone_number_id=phone_number_id,
                    dynamic_variables=dynamic_vars,
                )
                results.append({
                    **result,
                    "internal_call_id": call_data.get("internal_call_id"),
                })
            
            except Exception as e:
                logger.error(f"Failed to call {phone}: {e}")
                results.append({
                    "phone_number": phone,
                    "error": str(e),
                    "status": "failed",
                    "internal_call_id": call_data.get("internal_call_id"),
                })
        
        return results

    async def get_call_details(self, call_id: str) -> dict[str, Any]:
        """Get details of a specific call."""
        if settings.mock_mode:
            return {
                "call_id": call_id,
                "status": "completed",
                "duration_seconds": 45,
                "transcript": "Mock transcript...",
            }

        client = await self._get_client()
        
        try:
            response = await client.get(f"/convai/conversation/{call_id}")
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get call details: {e.response.status_code}")
            raise

    async def get_call_transcript(self, call_id: str) -> str:
        """Get transcript for a completed call."""
        if settings.mock_mode:
            return "Mock transcript: Agent greeted the customer..."

        details = await self.get_call_details(call_id)
        return details.get("transcript", "")

    async def get_call_recording_url(self, call_id: str) -> Optional[str]:
        """Get recording URL for a completed call."""
        if settings.mock_mode:
            return f"https://mock-recordings.example.com/{call_id}.mp3"

        details = await self.get_call_details(call_id)
        return details.get("recording_url")


# Singleton instance
elevenlabs = ElevenLabsService()
