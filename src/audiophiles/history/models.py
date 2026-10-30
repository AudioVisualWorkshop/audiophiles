from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from audiophiles.core.rename_plan import RenamePlan

@dataclass (frozen=True)
class RenameHistoryEntry:
    #Record a successfully completed rename operation

    plan: RenamePlan
    timestamp: datetime

    @property
    def count(self) -> int:
        #Return number of rename operations in the plan
        return self.plan.count

    @property
    def renamed_files(self) -> list[tuple[Path, Path]]:
        #Return the original and destination paths for each rename

        return [
            (operation.source, operation.destination)
            for operation in self.plan.operations
        ]

