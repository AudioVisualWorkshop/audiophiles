from pathlib import Path
from audiophiles.models import AudioFile

AUDIO_EXTENSIONS = {
    ".wav",
    ".aif",
    ".aiff",
    ".flac",
    ".mp3",
    ".mp4a",
    ".ogg",
}

class AudioScanner:
    # Find audio files in a directory

    def scan(self, directory: Path) -> list[AudioFile]:
        # Scan a directory and return the audio files contained within

        if not directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {directory}"
            )

        if not directory.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {directory}"
            )

        audio_files = []

        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
                audio_files.append(AudioFile(path))

        return audio_files