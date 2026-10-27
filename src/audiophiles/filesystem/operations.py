from pathlib import Path
from audiophiles.core.rename_plan import RenamePlan
from audiophiles.core.validators import validate_plan


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
        #Execute a validated plan safely, including cycles and rollback

        validation = validate_plan(plan)

        if not validation.is_valid:
            raise ValueError(
                f"Invalid rename plan: {validation}"
            )

        completed_moves: list[tuple[Path, Path]] = []

        try: 
            temporary_paths = self.stage_blocked_operations(
                plan,
                completed_moves,
            )

            for index, operation in enumerate(plan.operations):
                source = temporary_paths.get(
                    index, 
                    operation.source,
                )

                rename_file(
                    source = source,
                    destination = operation.destination,
                )

                completed_moves.append(
                    (source, operation.destination)
                )
        
        except Exception as error:
            rollback_errors = []

            for source, destination in reversed(completed_moves):
                if not destination.exists():
                    rollback_errors.append(
                        f"Cannot restore {source}: "
                        f"{destination} no longer exists."
                    )
                    continue
            
                if source.exists():
                    rollback_errors.append(
                        f"Cannot restore {source}: "
                        f"the original path is occupied."
                    )
                    continue
                
                try:
                    rename_file(
                        source = destination,
                        destination = source,
                    )
                except Exception as rollback_error:
                    rollback_errors.append(
                        f"Failed to restore {source}: {rollback_error}"
                    )
            
            if rollback_errors:
                details = "; ".join(rollback_errors)

                raise RuntimeError(
                    f"Rename failed: {error}. "
                    f"Rollback also encountered errors: {details}"
                ) from error

            raise
            

    def stage_blocked_operations(
        self, 
        plan:RenamePlan,
        completed_moves: list[tuple[Path, Path]] | None = None,
        ) -> dict[int, Path]:
        #Temporarily move all source files out of the way

        if completed_moves is None:
            completed_moves = []

        temporary_paths = {}

        for index, operation in enumerate(plan.operations):
            temporary_path = create_temp_path(
                operation.source,
                index + 1,
            )

            rename_file(
                source = operation.source,
                destination = temporary_path,
            )

            temporary_paths[index] = temporary_path

            completed_moves.append(
                (operation.source, temporary_path)
            )

        return temporary_paths
