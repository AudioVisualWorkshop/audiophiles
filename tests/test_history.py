from datetime import datetime
from pathlib import Path
import pytest

from audiophiles.core.rename_plan import RenameOperation, RenamePlan
from audiophiles.history.models import RenameHistoryEntry
from audiophiles.history.operations import HistoryManager
from audiophiles.filesystem.operations import RenameExecutor


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


def test_history_entry_creates_inverse_plan(tmp_path):
    source_1 = tmp_path / "Door.wav"
    destination_1 = tmp_path / "SFX_Door.wav"

    source_2 = tmp_path / "Metal.wav"
    destination_2 = tmp_path / "SFX_Metal.wav"

    plan = RenamePlan(
        operations = [
        RenameOperation(
            source = source_1,
            destination = destination_1,
        ),
        RenameOperation(
            source = source_2,
            destination = destination_2,
        ),
        ]
    )

    entry = RenameHistoryEntry(
        plan = plan,
        timestamp = datetime(2026, 10, 27, 12, 0),
    )

    inverse_plan = entry.create_inverse_plan()

    assert inverse_plan.operations == [
        RenameOperation(destination_2, source_2),
        RenameOperation(destination_1, source_1),
    ]


def test_history_entry_creates_inverse_plan_for_swap(tmp_path):
    door = tmp_path / "Door.wav"
    metal = tmp_path / "Metal.wav"

    plan = RenamePlan(
        operations = [
        RenameOperation(door, metal),
        RenameOperation(metal, door),
        ]
    )

    entry = RenameHistoryEntry(
        plan = plan,
        timestamp = datetime(2027, 10, 27, 12, 0),
    )

    inverse_plan = entry.create_inverse_plan()

    assert inverse_plan.operations == [
        RenameOperation(door, metal),
        RenameOperation(metal, door),
    ]


def test_history_manager_undo_latest(tmp_path):
    source = tmp_path / "Door.wav"
    destination = tmp_path / "SFX_Door.wav"

    source.write_text("door audio")

    plan = RenamePlan(
        operations = [
            RenameOperation(source, destination),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    manager = executor.history_manager

    entry = manager.get_latest()

    assert entry is not None
    assert destination.exists()

    undone_entry = manager.undo_latest(executor)

    assert undone_entry is entry
    assert source.exists()
    assert source.read_text() == "door audio"
    assert not destination.exists()
    assert manager.get_all() == []

def test_history_manager_undo_with_empty_history():
    manager = HistoryManager()
    executor = RenameExecutor()

    with pytest.raises(ValueError, match = "No history available."):
        manager.undo_latest(executor)


def test_history_manager_preserves_history_when_undo_fails(tmp_path):
    source = tmp_path / "Door.wav"
    destination = tmp_path / "SFX_Door.wav"

    source.write_text("door audio")

    plan = RenamePlan(
        operations = [
            RenameOperation(source, destination),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    manager = executor.history_manager
    original_entry = manager.get_latest()

    #Prevent the inverse rename from succeeding

    (tmp_path / "Door.wav").write_text("another file")

    with pytest.raises(ValueError, match = "Invalid rename plan"):
        manager.undo_latest(executor)

    assert manager.get_latest() is original_entry
    assert destination.exists()