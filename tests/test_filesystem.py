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