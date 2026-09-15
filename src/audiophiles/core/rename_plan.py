from dataclasses import dataclass
from pathlib import Path


@dataclass (frozen = True)
class RenameOperation:
    #Represents one proposed file rename

    source: Path
    destination: Path

    @property
    def source_name(self) -> str:
        #Return current filename
        return self.source.name

    @property
    def destination_name(self) -> str:
        #Return proposed name
        return self.destination.name

    @property
    def is_noop(self) -> bool:
        #Return True if rename would not change path
        return self.source == self.destination


@dataclass (frozen = True)
class RenamePlan:
    #Represent a collection of proposed rename operations

    operations: list[RenameOperation]

    @property
    def count(self) -> int:
        #Return number of operations in the plan
        return len(self.operations)