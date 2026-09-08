import pytest
from audiophiles.filesystem.scanner import AudioScanner


def test_scanner_finds_audio_files(tmp_path):
    (tmp_path / "Door.wav").touch()
    (tmp_path / "Footstep.wav").touch()
    (tmp_path / "Impact.wav").touch()
    (tmp_path / "README.txt").touch()
    (tmp_path / "image.png").touch()

    scanner = AudioScanner()
    files = scanner.scan(tmp_path)

    filenames = [audio_file.filename for audio_file in files]

    assert filenames == [
        "Door.wav",
        "Footstep.wav",
        "Impact.wav",
    ]

def test_scanner_handles_uppercase_extensions(tmp_path):
    (tmp_path / "Door.WAV").touch()
    (tmp_path / "Footstep.FLAC").touch()
    (tmp_path / "Music.MP3").touch()

    scanner = AudioScanner()
    files = scanner.scan(tmp_path)

    filenames = [audio_file.filename for audio_file in files]

    assert filenames == [
        "Door.WAV",
        "Footstep.FLAC",
        "Music.MP3",
    ]

def test_scanner_ignores_directories(tmp_path):
    (tmp_path / "Door.wav").touch()
    (tmp_path / "Fake.wav").mkdir()

    scanner = AudioScanner()
    files = scanner.scan(tmp_path)

    filenames = [audio_file.filename for audio_file in files]

    assert filenames == ["Door.wav"]

def test_scanner_raises_for_missing_directory(tmp_path):
    missing_directory = tmp_path / "does not exist"

    scanner = AudioScanner()

    with pytest.raises(FileNotFoundError):
        scanner.scan(missingdirectory)

def test_scanner_raises_for_file_path(tmp_path):
    file_path = tmp_path / "Door.wav"
    file_path.touch()

    scanner = AudioScanner()

    with pytest.raises(NotADirectoryError):
        scanner.scan(file_path)