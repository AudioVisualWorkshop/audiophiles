from datetime import datetime
from pathlib import Path

from audiophiles.core.rename_plan import RenameOperation, RenamePlan
from audiophiles.history.models import RenameHistoryEntry
from audiophiles.history.operations import HistoryManager


def test_history_entry_records_rename_plan(tmp_path):
    source_1 = tmp_path / "Door.wav"
    destination_1 = tmp_path / "SFX_Door.wav"

    source_2 = tmp_path / "Metal.wav"
    destination_2 = tmp_path / "SFX_Metal.wav"

    plan = RenamePlan(
        operations = [
            RenameOperation(source_1, destination_1),
            RenameOperation(source_2, destination_2),
        ]
    )

    timestamp = datetime(2026, 10, 27, 12, 0)
    entry = RenameHistoryEntry(plan=plan, timestamp=timestamp)

    assert entry.plan is plan
    assert entry.timestamp == timestamp
    assert entry.count == 2
    assert entry.renamed_files == [
        (source_1, destination_1),
        (source_2, destination_2),
    ]

def test_history_entry_with_empty_plan(tmp_path):
    plan = RenamePlan(operations = [])
    entry = RenameHistoryEntry(
        plan = plan,
        timestamp = datetime(2026, 10, 27, 12, 0),
    )

    assert entry.count == 0
    assert entry.renamed_files == []


def test_history_manager_records_entries(tmp_path):
    plan = RenamePlan(operations=[])
    entry = RenameHistoryEntry(
        plan = plan,
        timestamp = datetime(2026, 10, 27, 12, 0),
    )

    manager = HistoryManager()
    manager.record(entry)

    assert manager.get_all() == [entry]
    assert manager.get_latest() == entry


def test_history_manager_returns_none_when_empty():
    manager = HistoryManager()

    assert manager.get_all() == []
    assert manager.get_latest() is None


def test_history_manager_returns_copy_of_entries():
    manager = HistoryManager()
    manager.record(
        RenameHistoryEntry(
            plan = RenamePlan(operations = []),
            timestamp = datetime(2026, 10, 27, 12, 0),
        )
    )

    entries = manager.get_all()
    entries.clear()

    assert len(manager.get_all()) == 1


def test_history_manager_clear():
    manager = HistoryManager()
    entry = RenameHistoryEntry(
        plan = RenamePlan(operations = []),
        timestamp = datetime(2026, 10, 27, 12, 0),
    )

    manager.record(entry)

    manager.clear()

    assert manager.get_all() == []
    assert manager.get_latest() is None