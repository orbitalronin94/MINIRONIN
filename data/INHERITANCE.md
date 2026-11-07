# Data inheritance register

Only data libraries may be inherited from RONIN-IA and HERETIC-RONIN. This register is the admission authority for MINIRONIN.

**Snapshot date:** 2026-11-07. Counts below are inherited from the sibling repositories' published dataset registers. They are inventory evidence, not a claim that MINIRONIN has already copied or consumed those bytes.

## Admission rules

A source remains **pending** until its original upstream license and provenance are verified. Presence in a sibling repository or a successful download is not sufficient evidence.

For each source record:
- stable source ID and source project;
- exact path/artifact and upstream URL/revision;
- original license and evidence URL;
- retrieval date, file count, byte size, and SHA-256;
- languages/domains and format;
- transformations performed;
- deduplication and quality results;
- admission status and reason.

## Explicit exclusions

- GitHub Actions workflows and all workflow configuration.
- Training/evaluation procedures and scripts.
- Model checkpoints and optimizer state.
- Unattributed or license-unknown content.
- Evaluation/holdout material that could contaminate training.

## Verified sibling inventory

| Source ID | Origin | Snapshot evidence | Published train-scoped inventory | MINIRONIN status |
|---|---|---|---:|---|
| RONIN-IA-TRAIN-2026-11-07 | RONIN-IA | `data/datasets/README.md`, cut 2026-11-07 | 286,468 docs / 684,738,932 UTF-8 bytes | Candidate for selective import; global G-0 and near-duplicate gates remain unresolved |
| HERETIC-CORPUS-2026-11-07 | HERETIC-RONIN | `data/datasets/README.md`, updated 2026-11-07; audit run [42362365447](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42362365447) | 260,971 docs / 703,593,871 bytes | Candidate snapshot; must reconcile source-level overlap before import |
| HERETIC-COSMOPEDIA-V0.1 | HERETIC-RONIN | `HuggingFaceTB/cosmopedia`, revision `0ae6ec63f91742bd2d1eaef4f02232c55d719385` | 4,734 docs / 22,927,899 bytes | Separate synthetic-text slice; quality limitations recorded upstream |
| RONIN-PAPERS-INTERNAL | RONIN-IA | `orbitalronin94/Papers`, revision `d7bf3ae446f666ce3be73b11aab7090e1605a889` | 9 Markdown files / 750,857 bytes | Internal-use authorization only; no external redistribution permission |

### Important overlap rule

The HERETIC audit explicitly describes its 260,971-document corpus as the 256,237-document RONIN-IA-derived base (680,665,972 bytes) plus 4,734 Cosmopedia documents (22,927,899 bytes), after its own deduplication. These totals overlap the RONIN-IA inventory. **Do not add the RONIN-IA and HERETIC totals together.** MINIRONIN must reconcile document hashes across both origins and preserve the original source-level provenance.

The RONIN-IA README reports 286,468 train-scoped documents / 684,738,932 bytes across literature, Mathlib4, NASA file-reviewed, Papers, ScienceVerse, and CoVoST 2. This is a scoped count, not proof of global Level A eligibility: its 64-library strict Level A gate is reported as 0/64, and global G-0 remains failed. The HERETIC register likewise distinguishes admitted corpus bytes from candidates and describes its audit as a heuristic rather than a public benchmark or semantic deduplication proof.

### Known source-level cautions

- **RONIN-IA Papers:** 9 owner-authored Markdown files, internal training/research permission only; do not redistribute externally.
- **CoVoST 2:** translation-only CC0-1.0 export; retain only the approved translation text and exclude audio, source Common Voice text, speaker/client IDs, paths, and Tatoeba material.
- **Mathlib4:** Apache-2.0 at the pinned upstream revision; preserve license and file headers.
- **ScienceVerse:** CC BY/CC0 per DOI; preserve article attribution and license metadata.
- **NASA NTRS:** only the individually file-reviewed public-use subset is train-scoped; do not treat the full catalog as automatically admitted.
- **Cosmopedia:** Apache-2.0 declared by dataset publisher, but synthetic and seeded from external material; use only as experimental next-token text, not as verified answer supervision.
- Other candidates in either sibling repository remain excluded until their own admission evidence is inspected.

## Import status

**One source payload is now imported:** the nine owner-authored Markdown papers from `orbitalronin94/Papers`, pinned at revision `d7bf3ae446f666ce3be73b11aab7090e1605a889`. They are stored under `data/inherited/papers/` and authorized for internal MINIRONIN research/training only; redistribution is not authorized. The other sibling corpus inventories remain unimported. The dedicated `data-audit.yml` workflow checks the exact file count, UTF-8 integrity, empties, exact duplicates, and computes SHA-256 values into an artifact manifest. Import does not yet mean tokenization, split assignment, or training consumption.

## Source links

- [RONIN-IA dataset register](https://github.com/orbitalronin94/RONIN-IA/blob/main/data/datasets/README.md)
- [HERETIC-RONIN dataset register](https://github.com/orbitalronin94/HERETIC-RONIN/blob/main/data/datasets/README.md)
- [HERETIC-RONIN combined corpus audit](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42362365447)
