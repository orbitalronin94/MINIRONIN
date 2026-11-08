from scripts.acquire_anarchist_library import clean_gutenberg


def test_clean_gutenberg_rejects_short_body():
    raw = (
        "Project Gutenberg header\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
        "Title\n\nA short body.\n"
        "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
        "Project Gutenberg footer"
    ).encode("utf-8")
    try:
        clean_gutenberg(raw)
    except ValueError as exc:
        assert "short book body" in str(exc)
    else:
        raise AssertionError("short fixture should be rejected")


def test_clean_gutenberg_rejects_missing_markers():
    try:
        clean_gutenberg(("x" * 12000).encode("utf-8"))
    except ValueError as exc:
        assert "markers" in str(exc)
    else:
        raise AssertionError("missing markers should be rejected")
