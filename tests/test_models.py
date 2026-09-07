from pathlib import Path

from audiophiles.models import AudioFile

def test_audio_file_properties():
    path = Path("/Users/test/Audio/Door.wav")
    audio_file = AudioFile(path)

    assert audio_file.path == path
    assert audio_file.filename == "Door.wav"
    assert audio_file.stem == "Door"
    assert audio_file.extension == ".wav"
    assert audio_file.folder == Path("/Users/test/Audio")

def test_audio_file_preserves_underscores():
    path = Path("Users/test/Audio/Door_Large_Metal_01.wav")
    audio_file = AudioFile(path)

    assert audio_file.filename == "Door_Large_Metal_01.wav"
    assert audio_file.stem == "Door_Large_Metal_01"

def test_audio_file_extension():
    wav = AudioFile(Path("/Audio/test.wav"))
    aiff = AudioFile(Path("/Audio/test.aiff"))
    flac = AudioFile(Path("/Audio/test.flac"))

    assert wav.extension == ".wav"
    assert aiff.extension == ".aiff"
    assert flac.extension == ".flac"