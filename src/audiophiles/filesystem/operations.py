from pathlib import Path
from audiophiles.core.rename_plan import RenamePlan


def rename_file(source: Path, destination: Path) -> None:
    #Rename one file from source to destination
    return source.rename(destination)


class RenameExecutor:
    #Execute rename plans on the filesystem

    def execute(self, plan: RenamePlan) -> None:
        #Execute every operation in the rename plan

        for operation in plan.operations:
            rename_file(
                source = operation.source,
                destination = operation.destination,
            )