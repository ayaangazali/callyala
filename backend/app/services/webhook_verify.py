"""Webhook signature verification for ElevenLabs."""

import hmac
import hashlib
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


def verify_elevenlabs_signature(
    payload: bytes,
    signature: str,
    secret: Optional[str] = None,
) -> bool:
    """
    Verify ElevenLabs webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body bytes
        signature: Signature from X-ElevenLabs-Signature header
        secret: Optional override for webhook secret
    
    Returns:
        True if signature is valid, False otherwise
    """
    secret = secret or settings.elevenlabs_webhook_secret
    
    if not secret:
        logger.warning("No webhook secret configured - skipping verification")
        return True
    
    if not signature:
        logger.warning("No signature provided in request")
        return False
    
    try:
        # Compute expected signature
        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected.lower(), signature.lower())
        
        if not is_valid:
            logger.warning("Webhook signature verification failed")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


def compute_signature(payload: bytes, secret: str) -> str:
    """
    Compute HMAC-SHA256 signature for testing.
    
    Args:
        payload: Request body bytes
        secret: Webhook secret
    
    Returns:
        Hex-encoded signature
    """
    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
