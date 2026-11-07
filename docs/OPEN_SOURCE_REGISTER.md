# Open-source foundation register

Candidate references only; nothing is approved for code reuse until exact versions/commits and licenses are reviewed.

| Component | Candidate | Intended role | License family | Pinned version/commit | Review status |
|---|---|---|---|---|---|
| Tensor runtime | PyTorch | Model implementation and training | BSD-style | TBD | Candidate |
| Tokenizer | Hugging Face Tokenizers | Fast BPE/WordPiece tokenization | Apache-2.0 | TBD | Candidate |
| Tokenizer | SentencePiece | Unigram/BPE tokenizer option | Apache-2.0 | TBD | Candidate |
| Compact GPT reference | nanoGPT | Architecture/implementation reference | MIT | TBD | Candidate; inspect exact revision |
| Evaluation reference | EleutherAI evaluation ecosystem | Benchmark methodology | Per-component | TBD | Candidate; inspect exact component |

## Approval checklist

- [ ] Exact upstream repository and commit/tag recorded.
- [ ] License file inspected at that revision.
- [ ] Transitive dependencies reviewed where relevant.
- [ ] Required notices and attribution retained.
- [ ] Scope of code copied/adapted documented.
- [ ] Dependency pinned and reproducibility impact assessed.
