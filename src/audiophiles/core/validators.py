from audiophiles.core.rename_plan import RenamePlan
from dataclasses import dataclass

INVALID_FILENAME_CHARACTERS = set('<>:"/\\|?*')

@dataclass (frozen = True)
class ValidationResult:
    #Contains results of validatin a rename plan

    duplicate_destinations: list[str]
    existing_destinations: list[str]
    noop_operations: list[str]
    invalid_destinations: list[str]

    @property
    def is_valid(self) -> bool:
        #Returns True if plan contains no validation errors
        return not (
            self.duplicate_destinations
            or self.existing_destinations
            or self.noop_operations
            or self.invalid_destinations
        )


def find_invalid_destinations(plan: RenamePlan) -> list[str]:
    #Return destination paths containing invalid filename characters

    invalid = []

    for operation in plan.operations:
        filename = operation.destination.name

        if not filename:
            invalid.append(str(operation.destination))
            continue

        if any(character in INVALID_FILENAME_CHARACTERS for character in filename):
            invalid.append(str(operation.destination))

    return invalid

def find_duplicate_destinations(plan: RenamePlan) -> list[str]:
    #Return destination paths that appear more than once in a plan

    destinations = [operation.destination for operation in plan.operations]

    duplicates = []

    for destination in destinations:
        if destinations.count(destination) > 1:
            if str(destination) not in duplicates:
                duplicates.append(str(destination))

    return duplicates


def find_existing_destinations(plan: RenamePlan) -> list[str]:
    #Return destination paths that already exist outside the plan

    sources = {
        operation.source
        for operation in plan.operations
    }

    existing = []

    for operation in plan.operations:
        if (
            operation.destination.exists()
            and operation.destination not in sources
        ):
            if str(operation.destination) not in existing:
                existing.append(str(operation.destination))

    return existing


def find_noop_operations(plan: RenamePlan) -> list[str]:
    #Return source paths for operations that make no change

    noops = []

    for operation in plan.operations:
        if operation.is_noop:
            noops.append(str(operation.source))

    return noops


def validate_plan(plan: RenamePlan) -> ValidationResult:
    #Validate a rename plan and return all detected problems

    return ValidationResult(
        duplicate_destinations = find_duplicate_destinations(plan),
        existing_destinations = find_existing_destinations(plan),
        noop_operations = find_noop_operations(plan),
        invalid_destinations = find_invalid_destinations(plan),
    )