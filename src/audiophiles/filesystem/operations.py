from pathlib import Path
from audiophiles.core.rename_plan import RenamePlan


def rename_file(source: Path, destination: Path) -> None:
    #Rename one file from source to destination
    return source.rename(destination)


def create_temp_path(source: Path, index: int) -> Path:
    #Create an unused temporary path in the source file's directory

    counter = index

    #Simple collision avoidance
    while True:
        temporary_path = source.with_name(
            f".audiophiles_tmp_{counter}{source.suffix}"
    )

        if not temporary_path.exists():
            return temporary_path

        counter += 1

def find_blocked_operations(plan: RenamePlan) -> list[int]:
    #Return indexes of operations whose destinations are occupied by another

    sources = {
        operation.source
        for operation in plan.operations
    }

    blocked = []

    for index, operation in enumerate(plan.operations):
        if (
            operation.destination in sources
            and operation.destination != operation.source
        ):
            blocked.append(index)

    return blocked


class RenameExecutor:
    #Execute rename plans on the filesystem

    def execute(self, plan: RenamePlan) -> None:
        #Execute a rename plan safely, including cycles

        temporary_paths = self.stage_blocked_operations(plan)

        for index, operation in enumerate(plan.operations):
            source = temporary_paths.get(
                index,
                operation.source,
            )
        
            rename_file(
                source = source,
                destination = operation.destination,
            )

    def stage_blocked_operations(self, plan:RenamePlan) -> dict[int, Path]:
        #Temporarily move blocked source files out of the way

        blocked = find_blocked_operations(plan)
        temporary_paths = {}

        for index in blocked:
            operation = plan.operations[index]

            temporary_path = create_temp_path(
                operation.source,
                index + 1,
            )

            rename_file(
                source = operation.source,
                destination = temporary_path,
            )

            temporary_paths[index] = temporary_path

        return temporary_paths
