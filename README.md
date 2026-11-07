# MINIRONIN

**MINIRONIN** is an independent research project to build a compact language model targeting **~10 million parameters**.

It may inherit and curate reusable *data libraries* from [RONIN-IA](https://github.com/orbitalronin94/RONIN-IA) and [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). It will **not** inherit their training procedures, model checkpoints, GitHub Actions workflows, automation, or promotion logic.

## Project boundaries

- **Data inheritance only:** source corpora, documents, and dataset metadata may be imported after provenance, license, integrity, and deduplication checks.
- **Independent model:** MINIRONIN defines its own architecture, tokenizer contract, initialization, training objective, evaluation, and release criteria.
- **No workflow inheritance:** no workflow files or training scripts are copied from RONIN-IA or HERETIC-RONIN.
- **Open-source foundations:** PyTorch is the initial implementation foundation. Tokenizer and evaluation dependencies require separate review and pinning.
- **Honest sizing:** the 10M target is a parameter budget, not a performance claim.

## First model baseline

<badge color="success">Implemented baseline</badge>

The initial decoder-only Transformer implementation is configured at **9,970,176 trainable parameters**:
- 6 Transformer blocks, width 256
- 8 attention heads (32 dimensions per head)
- MLP width 768
- 23,000 token vocabulary
- 512 learned position embeddings
- tied token/output embeddings
- pre-LayerNorm, causal self-attention, GELU MLP

Implementation: `src/minironin/`; configuration: `configs/model-10m.json`; tests: `tests/test_model.py`. The parameter count is calculated analytically and asserted in a test; the tests have not yet been run in GitHub Actions.

## Repository map

- `docs/SPEC.md` — technical design and constraints.
- `docs/ROADMAP.md` — staged milestones and acceptance gates.
- `data/INHERITANCE.md` — source-by-source data admission register.
- `docs/OPEN_SOURCE_REGISTER.md` — exact upstream dependencies and license review.
- `src/minironin/` — independent model implementation.
- `tests/` — architecture and reproducibility tests.

## Data inheritance status

Sibling inventories have been inspected and recorded, but **no corpus payload has yet been copied into MINIRONIN**. RONIN-IA reports 286,468 train-scoped documents / 684,738,932 bytes; HERETIC-RONIN reports 260,971 documents / 703,593,871 bytes, including a 256,237-document RONIN-derived base plus 4,734 Cosmopedia records. These inventories overlap and must never be summed. See [the inheritance register](data/INHERITANCE.md) for license and admission caveats.

## Non-goals

- Reproducing the 95M/100M RONIN-IA model or the 500M HERETIC-RONIN student.
- Reusing sibling training recipes or workflow YAML.
- Claiming that corpus volume alone produces model capability.
- Promoting checkpoints without independent evaluation.
