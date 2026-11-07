# MINIRONIN

**MINIRONIN** is an independent research project to build a compact language model targeting **~10 million parameters**.

It may inherit and curate reusable *data libraries* from [RONIN-IA](https://github.com/orbitalronin94/RONIN-IA) and [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). It will **not** inherit their training procedures, model checkpoints, GitHub Actions workflows, automation, or promotion logic.

## Project boundaries

- **Data inheritance only:** source corpora, documents, and dataset metadata may be imported after provenance, license, integrity, and deduplication checks.
- **Independent model:** MINIRONIN defines its own architecture, tokenizer contract, initialization, training objective, evaluation, and release criteria.
- **No workflow inheritance:** no workflow files or training scripts are copied from RONIN-IA or HERETIC-RONIN.
- **Open-source foundations:** use well-documented, permissively licensed research and software as references; record exact upstream projects, versions, and licenses before adopting code or assets.
- **Honest sizing:** the 10M target is a parameter budget, not a performance claim.

## Initial model direction

A compact decoder-only Transformer is the baseline candidate: approximately six blocks, width 256, eight attention heads, a 768-wide feed-forward layer, tied token embeddings, and a vocabulary sized to land near the 10M budget. The final configuration must be counted by executable parameter accounting before training.

## Repository map

- `docs/SPEC.md` — technical design and constraints.
- `docs/ROADMAP.md` — staged milestones and acceptance gates.
- `data/INHERITANCE.md` — source-by-source data admission register.
- `docs/OPEN_SOURCE_REGISTER.md` — exact upstream dependencies and license review.
- `src/minironin/` — model implementation.
- `tests/` — architecture, data, and reproducibility tests.

## Current status

**Design bootstrap.** The repository is being initialized. No inherited corpus is considered admitted until a source is inventoried and its license, provenance, hashes, and transformation history are recorded in the inheritance register. No training run or model checkpoint is being claimed at this stage.

## Non-goals

- Reproducing the 95M/100M RONIN-IA model or the 500M HERETIC-RONIN student.
- Reusing sibling training recipes or workflow YAML.
- Claiming that corpus volume alone produces model capability.
- Promoting checkpoints without independent evaluation.
