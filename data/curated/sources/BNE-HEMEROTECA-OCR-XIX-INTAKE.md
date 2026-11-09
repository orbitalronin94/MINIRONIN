# BNE Hemeroteca OCR — Spanish public-domain corpus

- Source: https://huggingface.co/datasets/ferjorosa/bne-hemeroteca-ocr-xix
- License: CC0 1.0; original content from Biblioteca Nacional de España.
- Dataset card: 834,641 pages, ~40,000 documents, ~800 million text tokens; 528 GB total including images.
- Text-only extraction uses Parquet column projection to avoid the image payload.
- First batch takes one Parquet shard each from science, history, literature, medicine, law, economics, education, politics, culture and industry.
- Only Spanish pages with valid rotation, at least 500 characters and publication date through 1900 are admitted. This avoids the early-20th-century tail noted by the curator.
- OCR is retained as-is; model ID, issue, page, date, BNE link and OCR diagnostics are preserved.
- Shards are published as release assets, not Git blobs, with Parquet and JSONL SHA-256 manifests.
