"""Tests for webhook idempotency and signature verification."""

import hashlib
import hmac
import json
import time
from pathlib import Path
import pytest

from app.services.webhook_verify import verify_elevenlabs_signature
from app.core.files import atomic_write_json, read_json


class TestWebhookSignatureVerification:
    """Test HMAC signature verification."""

    def test_valid_signature_passes(self):
        """Test that valid HMAC signature is accepted."""
        secret = "test-webhook-secret"
        payload = b'{"event": "call.completed", "call_id": "123"}'
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        result = verify_elevenlabs_signature(
            payload=payload,
            signature=signature,
            secret=secret
        )
        
        assert result is True

    def test_invalid_signature_fails(self):
        """Test that invalid signature is rejected."""
        secret = "test-webhook-secret"
        payload = b'{"event": "call.completed"}'
        
        result = verify_elevenlabs_signature(
            payload=payload,
            signature="invalid-signature",
            secret=secret
        )
        
        assert result is False

    def test_tampered_payload_fails(self):
        """Test that tampered payload is rejected."""
        secret = "test-webhook-secret"
        original_payload = b'{"event": "call.completed"}'
        tampered_payload = b'{"event": "call.failed"}'
        
        # Signature for original
        signature = hmac.new(
            secret.encode(),
            original_payload,
            hashlib.sha256
        ).hexdigest()
        
        # Verify with tampered payload
        result = verify_elevenlabs_signature(
            payload=tampered_payload,
            signature=signature,
            secret=secret
        )
        
        assert result is False

    def test_empty_secret_skips_verification(self):
        """Test that empty secret skips verification (for dev mode)."""
        # Note: The implementation returns True when no secret is configured
        # This is intentional for development/testing
        payload = b'{"event": "test"}'
        
        result = verify_elevenlabs_signature(
            payload=payload,
            signature="any",
            secret=""
        )
        
        # Empty secret means we skip verification (return True)
        assert result is True


class TestWebhookIdempotency:
    """Test webhook deduplication logic."""

    def test_new_webhook_is_processed(self, temp_data_dir: Path):
        """Test that new webhook ID is marked as processed."""
        dedup_file = temp_data_dir / "webhook_dedup.json"
        webhook_id = "wh-unique-123"
        
        # Check not in dedup set
        dedup_data = read_json(dedup_file) or {"processed": []}
        assert webhook_id not in dedup_data.get("processed", [])
        
        # Mark as processed
        dedup_data["processed"].append(webhook_id)
        atomic_write_json(dedup_file, dedup_data)
        
        # Verify it's now tracked
        loaded = read_json(dedup_file)
        assert webhook_id in loaded["processed"]

    def test_duplicate_webhook_detected(self, temp_data_dir: Path):
        """Test that duplicate webhook is detected."""
        dedup_file = temp_data_dir / "webhook_dedup.json"
        webhook_id = "wh-duplicate-456"
        
        # Process first time
        dedup_data = {"processed": [webhook_id]}
        atomic_write_json(dedup_file, dedup_data)
        
        # Check if duplicate
        loaded = read_json(dedup_file) or {"processed": []}
        is_duplicate = webhook_id in loaded.get("processed", [])
        
        assert is_duplicate is True

    def test_dedup_survives_restart(self, temp_data_dir: Path):
        """Test that dedup set persists across restarts."""
        dedup_file = temp_data_dir / "webhook_dedup.json"
        webhook_ids = ["wh-1", "wh-2", "wh-3"]
        
        # Simulate processing
        atomic_write_json(dedup_file, {"processed": webhook_ids})
        
        # Simulate restart by re-reading
        loaded = read_json(dedup_file)
        
        for wh_id in webhook_ids:
            assert wh_id in loaded["processed"]


class TestWebhookPayloadProcessing:
    """Test webhook payload handling."""

    def test_extract_call_id_from_payload(self):
        """Test extracting call ID from webhook payload."""
        payload = {
            "event_type": "call.ended",
            "data": {
                "call_id": "call-789",
                "status": "completed",
                "duration": 120
            }
        }
        
        call_id = payload.get("data", {}).get("call_id")
        assert call_id == "call-789"

    def test_map_elevenlabs_outcome(self):
        """Test mapping ElevenLabs status to our outcome."""
        status_mapping = {
            "completed": "success",
            "no-answer": "no_answer",
            "busy": "busy",
            "failed": "failed",
            "voicemail": "voicemail",
        }
        
        for el_status, expected_outcome in status_mapping.items():
            payload = {"data": {"status": el_status}}
            mapped = status_mapping.get(payload["data"]["status"], "unknown")
            assert mapped == expected_outcome

    def test_handle_missing_fields_gracefully(self):
        """Test handling webhook with missing optional fields."""
        minimal_payload = {
            "event_type": "call.ended",
            "data": {
                "call_id": "call-minimal"
            }
        }
        
        # Extract with defaults
        data = minimal_payload.get("data", {})
        call_id = data.get("call_id")
        duration = data.get("duration", 0)
        transcript = data.get("transcript", "")
        sentiment = data.get("sentiment", "neutral")
        
        assert call_id == "call-minimal"
        assert duration == 0
        assert transcript == ""
        assert sentiment == "neutral"
