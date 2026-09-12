from pathlib import Path

from audiophiles.core.rename_engine import RenameEngine
from audiophiles.core.rules import PrefixRule, RemoveRule, ReplaceRule, SuffixRule
from audiophiles.models import AudioFile


def test_engine_without_template():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    engine = RenameEngine()

    result = engine.rename(
        audio_file = audio_file,
        index = 1,
        total = 3,
    )

    assert result == "Door.wav"


def test_engine_with_template():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    engine = RenameEngine()

    result = engine.rename(
        audio_file = audio_file,
        index = 1,
        total = 3,
        template = "SFX_$index:03_$filename",
    )

    assert result == "SFX_001_Door.wav"


def test_engine_with_prefix_rule():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    engine = RenameEngine()

    result = engine.rename(
        audio_file = audio_file,
        index = 1,
        total = 3,
        rules = [PrefixRule("EDIT_")],
    )

    assert result == "EDIT_Door.wav"


def test_engine_with_multiple_rules_in_order():
    audio_file = AudioFile(Path("/Users/test/Audio/Door-FINAL.wav"))

    engine = RenameEngine()

    result = engine.rename(
        audio_file = audio_file,
        index = 1,
        total = 3,
        rules = [
            ReplaceRule("-", "_"),
            RemoveRule("FINAL"),
            SuffixRule("_EDIT"),
        ],
    )

    assert result == "Door__EDIT.wav"


def test_engine_combines_template_and_rules():
    audio_file = AudioFile(Path("/Users/test/Audio/Door.wav"))

    engine = RenameEngine()

    result = engine.rename(
        audio_file = audio_file,
        index = 7,
        total = 10,
        template = "SFX_$index:03_$filename",
        rules = [
            PrefixRule("EDIT_"),
            SuffixRule("_FINAL"),
        ],
    )

    assert result == "EDIT_SFX_007_Door_FINAL.wav"


def test_engine_renames_batch():
    audio_files = [
        AudioFile(Path("/Users/test/Audio/Door.wav")),
        AudioFile(Path("/Users/test/Audio/Footstep.wav")),
        AudioFile(Path("/Users/test/Audio/Impact.wav")),
    ]

    engine = RenameEngine()

    results = engine.rename_batch(
        audio_files = audio_files,
        template = "SFX_$index:03_$filename",
    )

    assert results == [
        "SFX_001_Door.wav",
        "SFX_002_Footstep.wav",
        "SFX_003_Impact.wav",
    ]


def test_engine_renames_batch_with_rules():
    audio_files = [
        AudioFile(Path("/Users/test/Audio/Door-FINAL.wav")),
        AudioFile(Path("/Users/test/Audio/Footstep-FINAL.wav")),
        AudioFile(Path("/Users/test/Audio/Impact-FINAL.wav")),
    ]

    engine = RenameEngine()

    results = engine.rename_batch(
        audio_files = audio_files,
        rules = [
            ReplaceRule("-", "_"),
            RemoveRule("FINAL"),
        ],
    )

    assert results == [
        "Door_.wav",
        "Footstep_.wav",
        "Impact_.wav",
    ]