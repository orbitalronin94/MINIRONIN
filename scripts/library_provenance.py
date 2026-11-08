"""Strict source-to-library attribution used after the 450k migration."""


SOURCE_PREFIXES = (
    ("HERETIC:", "heretic"),
    ("PRODATPHIL", "prodatphil"),
    ("MINIRONIN-ANARCHIST-LIBRARY", "anarchist"),
    ("MINIRONIN-CLASSICS-LIBRARY", "classics"),
    ("MINIRONIN-", "minironin_behavior"),
)


def infer_library_id(source: str) -> str:
    """Return the canonical library ID from the explicit ingestion source label.

    Unknown labels fail closed. Never infer provenance from domain alone:
    multiple libraries can contribute to the same domain.
    """
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Document source label is required for library attribution")
    for prefix, library_id in SOURCE_PREFIXES:
        if source.startswith(prefix):
            return library_id
    raise ValueError(f"Unregistered document source label: {source!r}")
