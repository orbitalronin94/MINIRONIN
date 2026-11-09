# PleIAs Spanish Public Domain Books

- Source: https://huggingface.co/datasets/PleIAs/Spanish-PD-Books
- Pinned revision: `001eaf13681f483069361dd82195ce279e12ed63`
- Dataset card reports 247,491 texts and 2,697,414,811 words; 129 Parquet shards, about 52.1 GB total.
- Curator states the collection is public domain in all regions and describes the EU post-mortem 70-year criterion; texts may be used for model training and republication.
- First admission batch: shards 1–8 (up to 16,000 books; actual accepted count measured after filtering).
- Each shard becomes compressed JSONL release assets with source Parquet SHA-256, output SHA-256, source revision and per-record attribution metadata.
- Only full text rows of at least 1,000 characters are admitted; original title/author/date/URL metadata is preserved where present. OCR imperfections require sampling.
- Later batches can add shards 9–129 without placing tens of gigabytes in Git history.
