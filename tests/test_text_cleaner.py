
import pytest

from src.text_cleaner import clean_text


def test_removes_extra_spaces():
    assert clean_text("  Hello   World  ") == "Hello World"




def test_preserves_meaningful_line_breaks():
    assert clean_text("INVOICE\n\nTOTAL: 5000") == (
        "INVOICE\n\nTOTAL: 5000"
    )



def test_removes_null_characters():
    assert clean_text("Hello\x00World") == "HelloWorld"


def test_empty_text():
    assert clean_text("   ") == ""


def test_rejects_non_string():
    with pytest.raises(TypeError):
        clean_text(123)
