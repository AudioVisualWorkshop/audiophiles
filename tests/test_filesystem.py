from pathlib import Path
from audiophiles.filesystem.operations import RenameExecutor, rename_file
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