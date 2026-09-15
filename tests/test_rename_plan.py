from pathlib import Path
from audiophiles.core.rename_plan import RenameOperation, RenamePlan
from audiophiles.core.validators import (
    find_duplicate_destinations, 
    find_existing_destinations,
    find_noop_operations,
    find_invalid_destinations,
    validate_plan,
)


def test_rename_operation():
    source = Path("/Audio/Door.wav")
    destination = Path("/Audio/SFX_Door.wav")

    operation = RenameOperation(
        source = source,
        destination = destination,
    )

    assert operation.source == source
    assert operation.destination == destination
    assert operation.source_name == "Door.wav"
    assert operation.destination_name == "SFX_Door.wav"
    assert operation.is_noop is False


def test_rename_operation_noop():
    path = Path("/Audio/Door.wav")

    operation = RenameOperation(
        source = path,
        destination = path,
    )

    assert operation.is_noop is True


def test_rename_plan():
    operation_1 = RenameOperation(
        source = Path("/Audio/Door.wav"),
        destination = Path("/Audio/SFX_Door.wav"),
    )

    operation_2 = RenameOperation(
        source = Path("/Audio/Metal.wav"),
        destination = Path("/Audio/SFX_Metal.wav"),
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    assert plan.operations == [operation_1, operation_2]
    assert plan.count == 2


def test_find_duplicate_destinations():
    operation_1 = RenameOperation(
        source = Path("/Audio/Door.wav"),
        destination = Path("/Audio/SFX.wav"),
    )

    operation_2 = RenameOperation(
        source = Path("/Audio/Metal.wav"),
        destination = Path("/Audio/SFX.wav"),
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    duplicates = find_duplicate_destinations(plan)

    assert duplicates == ["/Audio/SFX.wav"]


def test_find_duplicate_destinations_returns_empty_for_unique_destinations():
    operation_1 = RenameOperation(
        source = Path("/Audio/Door.wav"),
        destination = Path("/Audio/SFX_Door.wav"),
    )

    operation_2 = RenameOperation(
        source = Path("/Audio/Metal.wav"),
        destination = Path("/Audio/SFX_Metal.wav"),
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    duplicates = find_duplicate_destinations(plan)

    assert duplicates == []


def test_find_existing_destinations(tmp_path):
    existing_file = tmp_path / "SFX.wav"
    existing_file.touch()

    operation_1 = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = existing_file,
    )

    operation_2 = RenameOperation(
        source = tmp_path / "Metal.wav",
        destination = tmp_path / "SFX_Metal.wav",
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    existing = find_existing_destinations(plan)

    assert existing == [str(existing_file)]


def test_find_existing_destinations_returns_empty_when_none_exists(tmp_path):
    operation = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "SFX_Door.wav",
    )

    plan = RenamePlan(
        operations = [operation],
    )

    existing = find_existing_destinations(plan)

    assert existing == []


def test_find_noop_operations(tmp_path):
    path = tmp_path / "Door.wav"

    operation_1 = RenameOperation(
        source = path,
        destination = path,
    )

    operation_2 = RenameOperation(
        source = tmp_path / "Metal.wav",
        destination = tmp_path / "SFX_Metal.wav",
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    noops = find_noop_operations(plan)
    
    assert noops == [str(path)]


def test_find_noop_operations_returns_empty_when_none_exist(tmp_path):
    operation = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "SFX_Door.wav",
    )

    plan = RenamePlan(
        operations = [operation],
    )

    noops = find_noop_operations(plan)

    assert noops == []


def test_find_invalid_destinations(tmp_path):
    #Test for single invalid character
    operation_1 = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "SFX:Door.wav",
    )

    operation_2 = RenameOperation(
        source = tmp_path / "Metal.wav",
        destination = tmp_path / "SFX_Metal.wav",
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    invalid = find_invalid_destinations(plan)

    assert invalid == [str(tmp_path / "SFX:Door.wav")]


def test_find_invalid_destinations_detects_multiple_invalid_characters(tmp_path):
    operations = [
        RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "Door?.wav",
        ),
        RenameOperation(
            source = tmp_path / "Metal.wav",
            destination = tmp_path / "Metal*.wav",
        ),
        RenameOperation(
            source = tmp_path / "Glass.wav",
            destination = tmp_path / "Glass|Large.wav",
        ),
    ]

    plan = RenamePlan(operations=operations)

    invalid = find_invalid_destinations(plan)

    assert invalid == [
        str(tmp_path / "Door?.wav"),
        str(tmp_path / "Metal*.wav"),
        str(tmp_path / "Glass|Large.wav"),
    ]


def test_find_invalid_destinations_returns_empty_for_valid_names(tmp_path):
    operations = [
        RenameOperation(
            source = tmp_path / "Door.wav",
            destination = tmp_path / "SFX_Door.wav",
        ),
        RenameOperation(
            source = tmp_path / "Metal.wav",
            destination = tmp_path / "Metal-Large_01.wav",
        ),
        RenameOperation(
            source = tmp_path / "Glass.wav",
            destination = tmp_path / "Glass (Large).wav",
        ),
    ]

    plan = RenamePlan(operations=operations)

    invalid = find_invalid_destinations(plan)

    assert invalid == []


def test_validate_plan_with_valid_operations(tmp_path):
    operation_1 = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "SFX_Door.wav",
    )

    operation_2 = RenameOperation(
        source = tmp_path / "Metal.wav",
        destination = tmp_path / "SFX_Metal.wav",
    )

    plan = RenamePlan(
        operations = [operation_1, operation_2],
    )

    result = validate_plan(plan)

    assert result.is_valid is True
    assert result.duplicate_destinations == []
    assert result.existing_destinations == []
    assert result.noop_operations == []
    assert result.invalid_destinations == []


def test_validate_plan_detects_problems(tmp_path):
    existing_file = tmp_path / "Existing.wav"
    existing_file.touch()

    operation_1 = RenameOperation(
        source = tmp_path / "Door.wav",
        destination = tmp_path / "Duplicate.wav",
    )

    operation_2 = RenameOperation(
        source = tmp_path / "Metal.wav",
        destination = tmp_path / "Duplicate.wav",
    )

    operation_3 = RenameOperation(
        source = tmp_path / "Glass.wav",
        destination = existing_file
    )

    operation_4 = RenameOperation(
        source = tmp_path / "Wood.wav",
        destination = tmp_path / "Wood.wav",
    )

    operation_5 = RenameOperation(
        source = tmp_path / "Stone.wav",
        destination = tmp_path / "Stone?.wav",
    )

    plan = RenamePlan(
        operations = [
            operation_1,
            operation_2,
            operation_3,
            operation_4,
            operation_5,
        ],
    )

    result = validate_plan(plan)

    assert result.is_valid is False
    assert result.duplicate_destinations == [
        str(tmp_path / "Duplicate.wav")
    ]
    assert result.existing_destinations == [
        str(existing_file)
    ]
    assert result.noop_operations == [
        str(tmp_path / "Wood.wav")
    ]
    assert result.invalid_destinations == [
        str(tmp_path / "Stone?.wav")
    ]