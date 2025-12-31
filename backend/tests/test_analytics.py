"""Tests for analytics bucketing and aggregation."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytest


class TestTimeSeriesBucketing:
    """Test time-series data bucketing."""

    def test_hourly_bucket_assignment(self):
        """Test assigning timestamps to hourly buckets."""
        timestamps = [
            "2024-01-15T10:05:00Z",
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:55:00Z",
            "2024-01-15T11:15:00Z",
        ]
        
        def get_hourly_bucket(ts: str) -> str:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:00")
        
        buckets = [get_hourly_bucket(ts) for ts in timestamps]
        
        assert buckets[0] == "2024-01-15 10:00"
        assert buckets[1] == "2024-01-15 10:00"
        assert buckets[2] == "2024-01-15 10:00"
        assert buckets[3] == "2024-01-15 11:00"

    def test_daily_bucket_assignment(self):
        """Test assigning timestamps to daily buckets."""
        timestamps = [
            "2024-01-15T08:00:00Z",
            "2024-01-15T20:00:00Z",
            "2024-01-16T10:00:00Z",
        ]
        
        def get_daily_bucket(ts: str) -> str:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        
        buckets = [get_daily_bucket(ts) for ts in timestamps]
        
        assert buckets[0] == "2024-01-15"
        assert buckets[1] == "2024-01-15"
        assert buckets[2] == "2024-01-16"

    def test_aggregate_by_bucket(self):
        """Test aggregating counts by bucket."""
        calls = [
            {"created_at": "2024-01-15T10:00:00Z"},
            {"created_at": "2024-01-15T10:30:00Z"},
            {"created_at": "2024-01-15T11:00:00Z"},
            {"created_at": "2024-01-15T11:15:00Z"},
            {"created_at": "2024-01-15T11:45:00Z"},
        ]
        
        def get_hourly_bucket(ts: str) -> str:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:00")
        
        buckets: Dict[str, int] = {}
        for call in calls:
            bucket = get_hourly_bucket(call["created_at"])
            buckets[bucket] = buckets.get(bucket, 0) + 1
        
        assert buckets["2024-01-15 10:00"] == 2
        assert buckets["2024-01-15 11:00"] == 3


class TestOutcomeDistribution:
    """Test outcome distribution calculations."""

    def test_count_outcomes(self):
        """Test counting call outcomes."""
        calls = [
            {"outcome": "success"},
            {"outcome": "success"},
            {"outcome": "no_answer"},
            {"outcome": "busy"},
            {"outcome": "success"},
            {"outcome": "voicemail"},
        ]
        
        outcomes: Dict[str, int] = {}
        for call in calls:
            outcome = call["outcome"]
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        assert outcomes["success"] == 3
        assert outcomes["no_answer"] == 1
        assert outcomes["busy"] == 1
        assert outcomes["voicemail"] == 1

    def test_calculate_percentages(self):
        """Test calculating outcome percentages."""
        outcomes = {"success": 60, "no_answer": 25, "busy": 10, "failed": 5}
        total = sum(outcomes.values())
        
        percentages = {k: round(v / total * 100, 1) for k, v in outcomes.items()}
        
        assert percentages["success"] == 60.0
        assert percentages["no_answer"] == 25.0
        assert percentages["busy"] == 10.0
        assert percentages["failed"] == 5.0


class TestKPICalculations:
    """Test KPI calculations."""

    def test_success_rate(self):
        """Test calculating success rate."""
        total_calls = 100
        successful_calls = 75
        
        success_rate = (successful_calls / total_calls) * 100
        
        assert success_rate == 75.0

    def test_average_duration(self):
        """Test calculating average call duration."""
        calls = [
            {"duration_seconds": 120},
            {"duration_seconds": 180},
            {"duration_seconds": 90},
            {"duration_seconds": 150},
        ]
        
        total_duration = sum(c["duration_seconds"] for c in calls)
        avg_duration = total_duration / len(calls) if calls else 0
        
        assert avg_duration == 135.0

    def test_calls_per_hour(self):
        """Test calculating calls per hour rate."""
        # 120 calls over 8 hours
        total_calls = 120
        hours = 8
        
        calls_per_hour = total_calls / hours
        
        assert calls_per_hour == 15.0

    def test_conversion_rate(self):
        """Test calculating conversion rate."""
        calls = [
            {"outcome": "success", "booked": True},
            {"outcome": "success", "booked": True},
            {"outcome": "success", "booked": False},
            {"outcome": "no_answer", "booked": False},
            {"outcome": "success", "booked": True},
        ]
        
        total = len(calls)
        conversions = sum(1 for c in calls if c.get("booked"))
        conversion_rate = (conversions / total) * 100 if total else 0
        
        assert conversion_rate == 60.0


class TestDateFiltering:
    """Test date range filtering."""

    def test_filter_by_date_range(self):
        """Test filtering calls by date range."""
        calls = [
            {"created_at": "2024-01-10T10:00:00Z"},
            {"created_at": "2024-01-15T10:00:00Z"},
            {"created_at": "2024-01-20T10:00:00Z"},
            {"created_at": "2024-01-25T10:00:00Z"},
        ]
        
        start = datetime(2024, 1, 14)
        end = datetime(2024, 1, 21)
        
        def parse_date(ts: str) -> datetime:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        
        filtered = [
            c for c in calls 
            if start <= parse_date(c["created_at"]) < end
        ]
        
        assert len(filtered) == 2

    def test_filter_today(self):
        """Test filtering for today's calls."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        calls = [
            {"created_at": (today - timedelta(days=1)).isoformat() + "Z"},
            {"created_at": (today + timedelta(hours=2)).isoformat() + "Z"},
            {"created_at": (today + timedelta(hours=10)).isoformat() + "Z"},
        ]
        
        def parse_date(ts: str) -> datetime:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        
        today_calls = [
            c for c in calls 
            if today <= parse_date(c["created_at"]) < tomorrow
        ]
        
        assert len(today_calls) == 2

    def test_empty_range_returns_empty(self):
        """Test that impossible range returns empty."""
        calls = [
            {"created_at": "2024-01-15T10:00:00Z"},
        ]
        
        # End before start
        start = datetime(2024, 1, 20)
        end = datetime(2024, 1, 10)
        
        def parse_date(ts: str) -> datetime:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        
        filtered = [
            c for c in calls 
            if start <= parse_date(c["created_at"]) < end
        ]
        
        assert len(filtered) == 0
