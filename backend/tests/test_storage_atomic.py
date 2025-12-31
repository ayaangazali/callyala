"""Tests for atomic storage operations."""

import asyncio
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest

from app.core.files import atomic_write_json, read_json, append_jsonl, read_jsonl


class TestAtomicWrites:
    """Test atomic JSON write operations."""

    def test_atomic_write_creates_file(self, temp_data_dir: Path):
        """Test that atomic_write_json creates a new file."""
        file_path = temp_data_dir / "test.json"
        data = {"key": "value", "number": 42}
        
        atomic_write_json(file_path, data)
        
        assert file_path.exists()
        with open(file_path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_atomic_write_overwrites(self, temp_data_dir: Path):
        """Test that atomic_write_json overwrites existing file."""
        file_path = temp_data_dir / "test.json"
        
        # Write initial data
        atomic_write_json(file_path, {"old": "data"})
        
        # Overwrite with new data
        new_data = {"new": "data", "updated": True}
        atomic_write_json(file_path, new_data)
        
        loaded = read_json(file_path)
        assert loaded == new_data

    def test_atomic_write_creates_parent_dirs(self, temp_data_dir: Path):
        """Test that atomic_write_json creates parent directories."""
        file_path = temp_data_dir / "nested" / "deep" / "test.json"
        data = {"nested": True}
        
        atomic_write_json(file_path, data)
        
        assert file_path.exists()
        assert read_json(file_path) == data

    def test_read_json_returns_none_for_missing(self, temp_data_dir: Path):
        """Test read_json returns None for missing file."""
        file_path = temp_data_dir / "nonexistent.json"
        
        result = read_json(file_path)
        
        assert result is None


class TestJSONLOperations:
    """Test JSONL append and read operations."""

    def test_append_jsonl_creates_file(self, temp_data_dir: Path):
        """Test append_jsonl creates new file."""
        file_path = temp_data_dir / "test.jsonl"
        record = {"id": "1", "value": "first"}
        
        append_jsonl(file_path, record)
        
        assert file_path.exists()
        records = read_jsonl(file_path)
        assert len(records) == 1
        assert records[0] == record

    def test_append_jsonl_appends(self, temp_data_dir: Path):
        """Test append_jsonl appends to existing file."""
        file_path = temp_data_dir / "test.jsonl"
        
        append_jsonl(file_path, {"id": "1"})
        append_jsonl(file_path, {"id": "2"})
        append_jsonl(file_path, {"id": "3"})
        
        records = read_jsonl(file_path)
        assert len(records) == 3
        assert [r["id"] for r in records] == ["1", "2", "3"]

    def test_read_jsonl_empty_for_missing(self, temp_data_dir: Path):
        """Test read_jsonl returns empty list for missing file."""
        file_path = temp_data_dir / "nonexistent.jsonl"
        
        records = read_jsonl(file_path)
        
        assert records == []


class TestConcurrentWrites:
    """Test concurrent write safety."""

    def test_concurrent_json_writes(self, temp_data_dir: Path):
        """Test multiple concurrent JSON writes don't corrupt file."""
        file_path = temp_data_dir / "concurrent.json"
        num_writes = 20
        
        def write_data(i: int):
            data = {"iteration": i, "data": f"value-{i}"}
            atomic_write_json(file_path, data)
            return i
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(write_data, i) for i in range(num_writes)]
            results = [f.result() for f in futures]
        
        # File should exist and be valid JSON
        assert file_path.exists()
        loaded = read_json(file_path)
        assert loaded is not None
        assert "iteration" in loaded
        assert "data" in loaded

    def test_concurrent_jsonl_appends(self, temp_data_dir: Path):
        """Test multiple concurrent JSONL appends don't lose records."""
        file_path = temp_data_dir / "concurrent.jsonl"
        num_appends = 50
        
        def append_record(i: int):
            record = {"id": str(i), "thread": i % 5}
            append_jsonl(file_path, record)
            return i
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(append_record, i) for i in range(num_appends)]
            [f.result() for f in futures]
        
        # All records should be present
        records = read_jsonl(file_path)
        assert len(records) == num_appends
        
        # Check all IDs present
        ids = {r["id"] for r in records}
        expected_ids = {str(i) for i in range(num_appends)}
        assert ids == expected_ids
