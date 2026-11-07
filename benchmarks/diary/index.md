# MINIRONIN — diario de inferencia

Todos los modelos se evalúan con los mismos IDs, prompts, generación greedy y holdout SHA-256.
«Respuestas cambiadas» mide diferencia literal frente a base, no calidad.
No hay puntuación automática de inteligencia: requiere revisión humana ciega.

| Modelo | Pasos | Preguntas | Respuestas distintas vs base | Tasa de cambio | SHA-256 checkpoint | SHA-256 holdout | Diario |
|---|---:|---:|---:|---:|---|---|---|
| base-seed-9519-before-long-training | 100 | 40 | — | — | `6648494c0f5f972b140e48e59e5c0bd1e686f7cb3b35b11e6983919e1b3f0c91` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [base.json](base.json) |
| long-train-step-10000 | 10000 | 40 | 40 | 100.0% | `e6ea2c493516492b55fa0340902d02263cf992c2c592e82fe8ace98afc36b813` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-10000.json](checkpoint-10000.json) |
| long-train-step-20000 | 20000 | 40 | 40 | 100.0% | `b4a534a911ef50940b1aa1445c6eecb245eb2a79e31421ea5d18d9f0eaf1cfec` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-20000.json](checkpoint-20000.json) |
| long-train-step-30000 | 30000 | 40 | 40 | 100.0% | `ca487a467f78e267bb35def05e9af6a8dff94ddc26a41db053bdc9c5be803dfb` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-30000.json](checkpoint-30000.json) |
| long-train-step-40000 | 40000 | 40 | 40 | 100.0% | `7a35c99b60f3c4c0489ba2d0e043de4bdded1555da4f0b2ffcd765a1d71e4a2b` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-40000.json](checkpoint-40000.json) |
| long-train-step-50000 | 50000 | 40 | 40 | 100.0% | `7f6333c2087d2aebaa11027f6d17d2e89664fa2aa45d99b02e8b793ab0b9e1bd` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-50000.json](checkpoint-50000.json) |
| long-train-step-60000 | 60000 | 40 | 40 | 100.0% | `626e58cdd1b42d23c87f2d70fcf13d9a774d91fc1fab7cbb511e4f662e353a52` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-60000.json](checkpoint-60000.json) |
| long-train-step-70000 | 70000 | 40 | 40 | 100.0% | `069eccaad60e723af8931a8fa3e20ce1fa51cf79e65c06829797affa8fb64571` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-70000.json](checkpoint-70000.json) |
| long-train-step-80000 | 80000 | 40 | 40 | 100.0% | `7c8ac544960ea66e71a68d203eea79784f6869d55b177604d3fff4efa5b45272` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-80000.json](checkpoint-80000.json) |
| long-train-step-90000 | 90000 | 40 | 40 | 100.0% | `d64ce51e3bb2c248e82e11f6ad7571b5b4db3d7b038b21fab7ed89d496b0ee97` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-90000.json](checkpoint-90000.json) |
| long-train-step-100000 | 100000 | 40 | 40 | 100.0% | `6f0e45f4e574f60c782bcebe8ed58caaefa06fe0383305fc53c699e1415d2960` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-100000.json](checkpoint-100000.json) |
| long-train-step-110000 | 110000 | 40 | 40 | 100.0% | `c778d54142de2595179152f73e7fbfbfd7c1b48deaabde2205d6b116b20ae4ba` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-110000.json](checkpoint-110000.json) |
| long-train-step-120000 | 120000 | 40 | 40 | 100.0% | `e2b10147d4be936a9e25e5dce9986b2e75669f0b83bda29bfaba97e95e44dff7` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-120000.json](checkpoint-120000.json) |
| long-train-step-130000 | 130000 | 40 | 40 | 100.0% | `4eea4efe7e1c65da0ee7985ae3c09a7f69eab3cce90e2cabaa8694b6857cc986` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-130000.json](checkpoint-130000.json) |
| long-train-step-140000 | 140000 | 40 | 40 | 100.0% | `cb4fad3e5c94d6505d180879af52ee2e4ed59cd4a537725b52566c84215fe5a5` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-140000.json](checkpoint-140000.json) |
| long-train-step-150000 | 150000 | 40 | 40 | 100.0% | `5e18921ec512957b4e97fb2f794dad5f44fa3e5b41843769e231d2da7538d87e` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-150000.json](checkpoint-150000.json) |
| long-train-step-160000 | 160000 | 40 | 40 | 100.0% | `539e5d34d0bdf5400e823c2be92ed1447ea0454e658b11d9521bd4980f52b441` | `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d` | [checkpoint-160000.json](checkpoint-160000.json) |
