# Data inheritance register

Only data libraries may be inherited from RONIN-IA and HERETIC-RONIN. This register is the admission authority for MINIRONIN.

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

## Source inventory

| Source ID | Origin | Location | License evidence | Files | Bytes | SHA-256 manifest | Status |
|---|---|---|---|---:|---:|---|---|
| RONIN-IA-PENDING | RONIN-IA | Pending inventory | Pending | — | — | — | Not admitted |
| HERETIC-PENDING | HERETIC-RONIN | Pending inventory | Pending | — | — | — | Not admitted |

No corpus files have yet been admitted to MINIRONIN by this register.
