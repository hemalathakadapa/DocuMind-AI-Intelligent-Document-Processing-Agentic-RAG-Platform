

import re


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.replace("\x00", "")

    # Keep line breaks, but normalize spaces and tabs within each line.
    lines = text.splitlines()
    cleaned_lines = [
        re.sub(r"[^\S\n]+", " ", line).strip()
        for line in lines
    ]

    # Remove empty lines at the beginning and end,
    # while preserving meaningful line breaks inside the document.
    return "\n".join(cleaned_lines).strip()
