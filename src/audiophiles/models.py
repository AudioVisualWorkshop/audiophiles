from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True) #frozen makes objects immutable later
class AudioFile:
    path: Path

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def extension(self) -> str:
        return self.path.suffix

    @property
    def folder(self) -> Path:
        return self.path.parent