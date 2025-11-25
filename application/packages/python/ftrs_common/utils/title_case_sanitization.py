# Acronyms that should always remain in uppercase
PRESERVE_ACRONYMS = frozenset(["NHS", "GP", "ICB", "PCN"])


def to_title_case_preserving_acronyms(text: str) -> str:
    """
    Convert text to title case while preserving specific acronyms.

    Args:
        text: The text to convert.

    Returns:
        Title-cased text with preserved acronyms

    """

    if not text or not text.strip():
        return text

    title_cased = text.title()

    # Restore acronyms to uppercase
    words = title_cased.split()
    sanitized_words = []

    for word in words:
        # Check if the word (ignoring case) is in our acronym list
        if word.upper() in PRESERVE_ACRONYMS:
            sanitized_words.append(word.upper())
        else:
            sanitized_words.append(word)

    return " ".join(sanitized_words)


def sanitize_string_field(value: str) -> str:
    if isinstance(value, str):
        return to_title_case_preserving_acronyms(value)
    return value
