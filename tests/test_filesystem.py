import pytest
from pathlib import Path
from audiophiles.filesystem.operations import (
    RenameExecutor, 
    rename_file,
    find_blocked_operations,
    create_temp_path,
)
from audiophiles.core.rename_plan import RenameOperation, RenamePlan


def test_rename_file(tmp_path):
    source = tmp_path / "Door.wav"
    destination = tmp_path / "SFX_Door.wav"

    source.touch()

    rename_file(source, destination)

    assert source.exists() is False
    assert destination.exists() is True


def test_rename_executor(tmp_path):
    source_1 = tmp_path / "Door.wav"
    source_2 = tmp_path / "Metal.wav"

    destination_1 = tmp_path / "SFX_Door.wav"
    destination_2 = tmp_path / "SFX_Metal.wav"

    source_1.touch()
    source_2.touch()

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

    executor = RenameExecutor()
    executor.execute(plan)

    assert source_1.exists() is False
    assert source_2.exists() is False

    assert destination_1.exists() is True
    assert destination_2.exists() is True


def test_create_temp_path(tmp_path):
    source = tmp_path / "Door.wav"

    temp_path = create_temp_path(source, 1)

    assert temp_path == tmp_path / ".audiophiles_tmp_1.wav"


def test_create_temp_path_uses_unique_indexes(tmp_path):
    source = tmp_path / "Door.wav"

    temp_path_1 = create_temp_path(source, 1)
    temp_path_2 = create_temp_path(source, 2)

    assert temp_path_1 != temp_path_2


def test_find_blocked_operations(tmp_path):
    operation_1 = RenameOperation(
        source = tmp_path / "A.wav",
        destination = tmp_path / "B.wav",
    )

    operation_2 = RenameOperation(
        source = tmp_path / "B.wav",
        destination = tmp_path / "A.wav",
    )

    operation_3 = RenameOperation(
        source = tmp_path / "C.wav",
        destination = tmp_path / "D.wav",
    )

    plan = RenamePlan(
        operations = [
            operation_1,
            operation_2,
            operation_3,
        ]
    )

    blocked = find_blocked_operations(plan)

    assert blocked == [0, 1]


def test_find_blocked_operations_returns_empty_for_normal_renames(tmp_path):
    operation_1 = RenameOperation(
        source = tmp_path / "A.wav",
        destination = tmp_path / "B.wav",
    )

    operation_2 = RenameOperation(
        source = tmp_path / "C.wav",
        destination = tmp_path / "D.wav",
    )

    plan = RenamePlan(
        operations = [
            operation_1,
            operation_2,
        ]
    )

    blocked = find_blocked_operations(plan)

    assert blocked == []


def test_stage_blocked_operations(tmp_path):
    source_1 = tmp_path / "A.wav"
    source_2 = tmp_path / "B.wav"

    source_1.write_text("A")
    source_2.write_text("B")

    operation_1 = RenameOperation(
        source = source_1,
        destination = source_2,
    )

    operation_2 = RenameOperation(
        source = source_2,
        destination = source_1,
    )

    plan = RenamePlan(
        operations = [
            operation_1,
            operation_2,
        ]
    )

    executor = RenameExecutor()

    temporary_paths = executor.stage_blocked_operations(plan)

    assert source_1.exists() is False
    assert source_2.exists() is False

    assert temporary_paths[0].exists() is True
    assert temporary_paths[1].exists() is True

    assert temporary_paths[0].read_text() == "A"
    assert temporary_paths[1].read_text() == "B"


def test_create_temp_path_avoids_existing_file(tmp_path):
    source = tmp_path / "Door.wav"

    existing_temp = tmp_path / ".audiophiles_tmp_1.wav"
    existing_temp.touch()

    temp_path = create_temp_path(source, 1)

    assert temp_path == tmp_path / ".audiophiles_tmp_2.wav"


def test_create_temp_path_skips_multiple_existing_files(tmp_path):
    source = tmp_path / "Door.wav"

    (tmp_path / ".audiophiles_tmp_1.wav").touch()
    (tmp_path / ".audiophiles_tmp_2.wav").touch()
    (tmp_path / ".audiophiles_tmp_3.wav").touch()

    temp_path = create_temp_path(source, 1)
    
    assert temp_path == tmp_path / ".audiophiles_tmp_4.wav"


def test_executor_performs_simple_rename(tmp_path):
    source = tmp_path / "old.wav"
    destination = tmp_path / "new.wav"

    source.write_text("audio data")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = source,
                destination = destination,
            )
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    assert not source.exists()
    assert destination.exists()
    assert destination.read_text() == "audio data"


def test_executor_handles_two_file_swap(tmp_path):
    file_a = tmp_path / "A.wav"
    file_b = tmp_path / "B.wav"

    file_a.write_text("audio A")
    file_b.write_text("audio B")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = file_a,
                destination = file_b,
            ),
            RenameOperation(
                source = file_b,
                destination = file_a,
            ),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    assert file_a.exists()
    assert file_b.exists()

    assert file_a.read_text() == "audio B"
    assert file_b.read_text() == "audio A"


def test_executor_handles_three_file_cycle(tmp_path):
    source_a = tmp_path / "A.wav"
    source_b = tmp_path / "B.wav"
    source_c = tmp_path / "C.wav"

    source_a.write_text("audio A")
    source_b.write_text("audio B")
    source_c.write_text("audio C")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = source_a,
                destination = source_b,
            ),
            RenameOperation(
                source = source_b,
                destination = source_c,
            ),
            RenameOperation(
                source = source_c,
                destination = source_a,
            ),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    assert source_a.exists()
    assert source_b.exists()
    assert source_c.exists()

    assert source_a.read_text() == "audio C"
    assert source_b.read_text() == "audio A"
    assert source_c.read_text() == "audio B"


def test_executor_handes_rename_chain(tmp_path):
    file_a = tmp_path / "A.wav"
    file_b = tmp_path / "B.wav"
    file_c = tmp_path / "C.wav"
    file_d = tmp_path / "D.wav"

    file_a.write_text("audio A")
    file_b.write_text("audio B")
    file_c.write_text("audio C")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = file_a,
                destination = file_b,
            ),
            RenameOperation(
                source = file_b,
                destination = file_c,
            ),
            RenameOperation(
                source = file_c,
                destination = file_d,
            ),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    assert not file_a.exists()
    assert file_b.exists()
    assert file_c.exists()
    assert file_d.exists()

    assert file_b.read_text() == "audio A"
    assert file_c.read_text() == "audio B"
    assert file_d.read_text() == "audio C"


def test_executor_handles_cycle_and_simple_rename(tmp_path):
    file_a = tmp_path / "A.wav"
    file_b = tmp_path / "B.wav"
    file_c = tmp_path / "C.wav"
    file_d = tmp_path / "D.wav"

    file_a.write_text("audio A")
    file_b.write_text("audio B")
    file_c.write_text("audio C")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = file_a,
                destination = file_b,
            ),
            RenameOperation(
                source = file_b,
                destination = file_a,
            ),
            RenameOperation(
                source = file_c,
                destination = file_d,
            ),
        ]
    )

    executor = RenameExecutor()
    executor.execute(plan)

    assert file_a.read_text() == "audio B"
    assert file_b.read_text() == "audio A"
    assert not file_c.exists()
    assert file_d.read_text() == "audio C"


def test_executor_rejects_invalid_plan_without_changing_files(tmp_path):
    source = tmp_path / "Door.wav"
    destination = tmp_path / "SFX_Door.wav"
    missing_source = tmp_path / "Missing.wav"
    missing_destination = tmp_path / "SFX_Missing.wav"

    source.write_text("original audio placeholder")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = source,
                destination = destination,
            ),
            RenameOperation(
                source = missing_source,
                destination = missing_destination,
            ),
        ]
    )

    executor = RenameExecutor()

    with pytest.raises(ValueError, match = "Invalid rename plan"):
        executor.execute(plan)

    #Verify no files were changed
    assert source.exists()
    assert source.read_text() == "original audio placeholder"
    assert not destination.exists()
    assert not missing_source.exists()
    assert not missing_destination.exists()


def test_executor_failure_during_final_rename(tmp_path, monkeypatch):
    source_1 = tmp_path / "Door.wav"
    source_2 = tmp_path / "Metal.wav"

    source_1.write_text("door audio")
    source_2.write_text("metal audio")

    plan = RenamePlan(
        operations = [
            RenameOperation(
                source = source_1,
                destination = tmp_path / "SFX_Door.wav",
            ),
            RenameOperation(
                source = source_2,
                destination = tmp_path / "SFX_Metal.wav",
            ),
        ]
    )

    executor = RenameExecutor()
    original_rename_file = rename_file
    final_rename_attempts = 0

    def failing_rename_file(source, destination):
        nonlocal final_rename_attempts

        if ".audiophiles_tmp_" in source.name:
            final_rename_attempts += 1

            if final_rename_attempts == 2:
                raise OSError("Simulated rename failure")

        return original_rename_file(source, destination)

    monkeypatch.setattr(
        "audiophiles.filesystem.operations.rename_file",
        failing_rename_file,
    )

    with pytest.raises(OSError, match = "Simulated rename failure"):
        executor.execute(plan)

    #Both files should be restored to their original paths
    assert source_1.exists()
    assert source_2.exists()

    assert source_1.read_text() == "door audio"
    assert source_2.read_text() == "metal audio"

    #Neither final destination should remain
    assert not (tmp_path / "SFX_Door.wav").exists()
    assert not (tmp_path / "SFX_Metal.wav").exists()

    #No temporary files should remain
    assert not list(tmp_path.glob(".audiophiles_tmp_*"))