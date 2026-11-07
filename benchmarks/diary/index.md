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
