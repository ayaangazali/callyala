"""Needs attention rules engine."""

from typing import Any

from app.core.files import read_jsonl
from app.core.config import settings
from app.models import CallStatus, CallOutcome


class RulesService:
    """Rules engine for identifying items needing attention."""

    RULES = [
        {
            "id": "multiple_attempts",
            "name": "Multiple Attempts Without Booking",
            "description": "Call attempted 3+ times without successful booking",
            "severity": "high",
        },
        {
            "id": "negative_sentiment",
            "name": "Negative Sentiment",
            "description": "Customer expressed negative sentiment",
            "severity": "high",
        },
        {
            "id": "callback_requested",
            "name": "Callback Requested",
            "description": "Customer requested a callback",
            "severity": "medium",
        },
        {
            "id": "missing_booking_details",
            "name": "Missing Booking Details",
            "description": "Appointment set but missing date/time",
            "severity": "medium",
        },
        {
            "id": "failed_calls",
            "name": "Failed Calls",
            "description": "Call failed due to error",
            "severity": "high",
        },
        {
            "id": "opt_out",
            "name": "Opt Out / Do Not Call",
            "description": "Customer requested to not be called",
            "severity": "low",
        },
    ]

    def evaluate_call(self, call: dict) -> list[dict[str, Any]]:
        """Evaluate a single call against all rules."""
        violations = []

        # Rule: Multiple attempts without booking
        if call.get("retry_count", 0) >= 3 and call.get("outcome") != CallOutcome.APPOINTMENT_SET.value:
            violations.append({
                "rule_id": "multiple_attempts",
                "rule_name": "Multiple Attempts Without Booking",
                "severity": "high",
                "details": f"Attempted {call.get('retry_count', 0)} times",
            })

        # Rule: Negative sentiment
        sentiment = call.get("sentiment", "").lower()
        if sentiment in ["negative", "neg"]:
            violations.append({
                "rule_id": "negative_sentiment",
                "rule_name": "Negative Sentiment",
                "severity": "high",
                "details": f"Sentiment: {sentiment}",
            })

        # Rule: Callback requested
        if call.get("outcome") == CallOutcome.CALLBACK_REQUESTED.value:
            violations.append({
                "rule_id": "callback_requested",
                "rule_name": "Callback Requested",
                "severity": "medium",
                "details": "Customer requested callback",
            })

        # Rule: Missing booking details
        if call.get("outcome") == CallOutcome.APPOINTMENT_SET.value:
            metadata = call.get("metadata", {})
            extracted = call.get("extracted_fields", {})
            has_date = metadata.get("booked_date") or extracted.get("pickup_date")
            has_time = metadata.get("booked_time") or extracted.get("pickup_time")
            if not has_date or not has_time:
                violations.append({
                    "rule_id": "missing_booking_details",
                    "rule_name": "Missing Booking Details",
                    "severity": "medium",
                    "details": f"Missing {'date' if not has_date else ''} {'time' if not has_time else ''}".strip(),
                })

        # Rule: Failed calls
        if call.get("status") == CallStatus.FAILED.value:
            violations.append({
                "rule_id": "failed_calls",
                "rule_name": "Failed Call",
                "severity": "high",
                "details": call.get("error_message", "Unknown error"),
            })

        # Rule: Opt out
        if call.get("outcome") == CallOutcome.DO_NOT_CALL.value:
            violations.append({
                "rule_id": "opt_out",
                "rule_name": "Do Not Call",
                "severity": "low",
                "details": "Customer opted out",
            })

        return violations

    def get_needs_attention(
        self,
        campaign_id: str = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get all calls needing attention."""
        calls = read_jsonl(settings.calls_file)

        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]

        items = []
        for call in calls:
            violations = self.evaluate_call(call)
            if violations:
                for v in violations:
                    items.append({
                        "call_id": call.get("id"),
                        "campaign_id": call.get("campaign_id"),
                        "customer_name": call.get("customer_name", "Unknown"),
                        "phone": call.get("phone"),
                        "rule_id": v["rule_id"],
                        "rule_name": v["rule_name"],
                        "severity": v["severity"],
                        "details": v["details"],
                        "created_at": call.get("created_at"),
                    })

        # Sort by severity (high first)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        items.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        return items[:limit]

    def get_rules(self) -> list[dict[str, Any]]:
        """Get all available rules."""
        return self.RULES


rules = RulesService()
