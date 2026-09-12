from audiophiles.core.rules import (
    PrefixRule, 
    SuffixRule, 
    ReplaceRule,
    RemoveRule,
    )


def test_prefix_rule():
    rule = PrefixRule("SFX_")

    result = rule.apply("Door.wav")

    assert result == "SFX_Door.wav"


def test_prefix_rule_with_underscore_filename():
    rule = PrefixRule("EDIT_")

    result = rule.apply("Door_Large_Metal.wav")

    assert result == "EDIT_Door_Large_Metal.wav"


def test_prefix_rule_with_empty_prefix():
    rule = PrefixRule("")

    result = rule.apply("Door.wav")

    assert result == "Door.wav"


def test_suffix_rule():
    rule = SuffixRule("_EDIT")

    result = rule.apply("Door.wav")

    assert result == "Door_EDIT.wav"


def test_suffix_rule_with_multiple_periods():
    rule = SuffixRule("_FINAL")

    result = rule.apply("Door.Large.Metal.wav")

    assert result == "Door.Large.Metal_FINAL.wav"


def test_suffix_rule_without_extension():
    rule = SuffixRule("_EDIT")

    result = rule.apply("Door")

    assert result == "Door_EDIT"


def test_suffix_rule_with_empty_suffix():
    rule = SuffixRule("")

    result = rule.apply("Door.wav")

    assert result == "Door.wav"


def test_prefix_and_suffix_rules_share_the_same_interface():
    rules = [
        PrefixRule("SFX_"),
        SuffixRule("_EDIT"),
    ]

    filename = "Door.wav"

    for rule in rules:
        result = rule.apply(filename)

        assert isinstance(result, str)


def test_replace_rule():
    rule = ReplaceRule("FINAL", "")

    result = rule.apply("Door_FINAL.wav")

    assert result == "Door_.wav"


def test_replace_rule_multiple_occurrences():
    rule = ReplaceRule("-", "_")

    result = rule.apply("Door-Large-Metal.wav")

    assert result == "Door_Large_Metal.wav"


def test_replace_rule_can_modify_extensions():
    rule = ReplaceRule("wav", "aif")

    result = rule.apply("Door.wav")

    assert result == "Door.aif"


def test_replace_rule_with_no_match():
    rule = ReplaceRule("FINAL", "")

    result = rule.apply("Door.wav")

    assert result == "Door.wav"


def test_replace_rule_with_empty_replacement():
    rule = ReplaceRule("_TEMP", "")

    result = rule.apply("Door_TEMP.wav")

    assert result == "Door.wav"


def test_remove_rule():
    rule = RemoveRule("_FINAL")

    result = rule.apply("Door_FINAL.wav")

    assert result == "Door.wav"


def test_remove_rule_multiple_occurrences():
    rule = RemoveRule("_TEMP")

    result = rule.apply("Door_TEMP_Large_TEMP.wav")

    assert result == "Door_Large.wav"


def test_remove_rule_with_no_match():
    rule = RemoveRule("_FINAL")

    result = rule.apply("Door.wav")

    assert result == "Door.wav"


def test_remove_rule_can_remove_from_extension():
    rule = RemoveRule("wav")

    result = rule.apply("Door.wav")

    assert result == "Door."