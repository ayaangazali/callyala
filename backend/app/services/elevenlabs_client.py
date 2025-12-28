"""
Voice Agent Ops - ElevenLabs API Client

Client for interacting with ElevenLabs Agents Platform API.
"""

from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ElevenLabsClient:
    """
    Client for ElevenLabs Agents Platform API.
    
    Handles batch calling and status queries.
    """

    def __init__(self):
        self.base_url = settings.elevenlabs_base_url
        self.api_key = settings.elevenlabs_api_key
        self.timeout = 30.0

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with API key."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_batch_call(
        self,
        campaign_id: str,
        recipients: list[dict[str, Any]],
        script_id: str | None = None,
        voice_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a batch of outbound calls via ElevenLabs.
        
        Args:
            campaign_id: Internal campaign ID for tracking
            recipients: List of recipient dicts with phone_number and metadata
            script_id: Optional script ID for the call
            voice_config: Optional voice configuration
            
        Returns:
            Response with batch_id and status
            
        Note: The actual endpoint and payload structure depends on
        ElevenLabs API documentation. This is a placeholder implementation.
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            raise ValueError("ElevenLabs API key not configured")

        # Prepare payload
        # Note: Adjust this based on actual ElevenLabs API spec
        payload = {
            "campaign_id": campaign_id,
            "recipients": [
                {
                    "phone_number": r["phone_number"],
                    "dynamic_variables": r.get("metadata", {}),
                }
                for r in recipients
            ],
        }

        if script_id:
            payload["agent_id"] = script_id

        if voice_config:
            payload["voice_settings"] = voice_config

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Note: Replace with actual ElevenLabs endpoint
                response = await client.post(
                    f"{self.base_url}/convai/batch-calls",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                logger.info(f"Created batch call: {result.get('batch_id')}")
                return result

            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Failed to create batch call: {e}")
                raise

    async def get_batch_status(self, batch_id: str) -> dict[str, Any]:
        """
        Get status of a batch call.
        
        Args:
            batch_id: ElevenLabs batch ID
            
        Returns:
            Batch status information
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/convai/batch-calls/{batch_id}",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Failed to get batch status: {e}")
                raise

    async def cancel_batch(self, batch_id: str) -> dict[str, Any]:
        """
        Cancel a running batch call.
        
        Args:
            batch_id: ElevenLabs batch ID
            
        Returns:
            Cancellation result
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/convai/batch-calls/{batch_id}/cancel",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                logger.info(f"Cancelled batch: {batch_id}")
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Failed to cancel batch: {e}")
                raise

    async def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        """
        Get conversation details by ID.
        
        Args:
            conversation_id: ElevenLabs conversation ID
            
        Returns:
            Conversation details
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/convai/conversations/{conversation_id}",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Failed to get conversation: {e}")
                raise
