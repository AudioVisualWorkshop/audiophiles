import pytest
from pathlib import Path

from audiophiles.core.tokens import RenameContext, resolve_token, resolve_template
from audiophiles.models import AudioFile


def test_rename_context_properties():
    path = Path("/Users/test/Audio/Door_Large.wav")
    audio_file = AudioFile(path)

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    assert context.filename == "Door_Large.wav"
    assert context.stem == "Door_Large"
    assert context.extension == ".wav"
    assert context.folder == "Audio"


def test_rename_context_preserves_index_and_total():
    path = Path("Users/test/Audio/Door.wav")
    audio_file = AudioFile(path)

    context = RenameContext(
        audio_file = audio_file,
        index = 2,
        total = 5,
    )

    assert context.index == 2
    assert context.total == 5


def test_resolve_filename_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    assert resolve_token("$filename", context) == "Door_Large.wav"


def test_resolve_stem_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    assert resolve_token("$stem", context) == "Door_Large"


def test_resolve_extension_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )   

    assert resolve_token("$extension", context) == ".wav"


def test_resolve_folder_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )   

    assert resolve_token("$folder", context) == "Audio"


def test_resolve_index_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 7,
        total = 10,
    )   

    assert resolve_token("$index", context) == "7"


def test_resolve_unknown_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )   

    with pytest.raises(ValueError, match="Unknown rename token"):
        resolve_token("$banana", context)


def test_resolve_formatted_index_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 7,
        total = 10,
    )

    assert resolve_token("$index:02", context) == "07"
    assert resolve_token("$index:03", context) == "007"
    assert resolve_token("$index:04", context) == "0007"


def test_formatted_index_can_exceed_width():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 123,
        total = 200,
    )

    assert resolve_token("$index:02", context) == "123"


def test_invalid_index_format_raises_error():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    with pytest.raises(ValueError, match="Invalid index format"):
        resolve_token("$index:abc", context)


def test_zero_width_index_raises_error():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    with pytest.raises(ValueError, match="Invalid index format"):
        resolve_token("$index:0", context)


def test_resolve_template():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    result = resolve_template(
        "SFX_$index:03_$filename",
        context,
    )

    assert result == "SFX_001_Door.wav"


def test_resolve_template_with_multiple_tokens():
    audio_file = AudioFile(Path("/Users/test/Audio/Door_Large.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 12,
        total = 20,
    )

    result = resolve_template(
        "$folder_$index:03_$stem$extension",
        context,
    )

    assert result == "Audio_012_Door_Large.wav"


def test_resolve_template_without_tokens():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    result = resolve_template(
        "My_Custom_Name.wav",
        context,
    )

    assert result == "My_Custom_Name.wav"


def test_resolve_template_with_unknown_token():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    context = RenameContext(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    result = resolve_template(
        "SFX_$index:03_$filename",
        context,
    )

    with pytest.raises(ValueError, match="Unknown rename token"):
        resolve_template(
            "SFX_$banana",
            context,
        )