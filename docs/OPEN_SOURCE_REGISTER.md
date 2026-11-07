# Registro de fundamentos de código abierto

Son referencias candidatas. No se aprueba reutilizar código hasta revisar versiones/commits exactos y licencias.

| Componente | Candidato | Función prevista | Familia de licencia | Versión/commit fijado | Estado de revisión |
|---|---|---|---|---|---|
| Motor de tensores | PyTorch | Implementación y entrenamiento del modelo | Familia BSD | Pendiente | Candidato |
| Tokenizador | Hugging Face Tokenizers | Tokenización rápida BPE/WordPiece | Apache-2.0 | Pendiente | Candidato |
| Tokenizador | SentencePiece | Opción de tokenizador Unigram/BPE | Apache-2.0 | Pendiente | Candidato |
| Referencia GPT compacto | nanoGPT | Referencia de arquitectura/implementación | MIT | Pendiente | Candidato; revisar revisión exacta |
| Referencia de evaluación | Ecosistema de evaluación de EleutherAI | Metodología de benchmarks | Según componente | Pendiente | Candidato; revisar componente concreto |

## Lista de aprobación

- [ ] Registrar repositorio upstream exacto y commit/tag.
- [ ] Inspeccionar el archivo de licencia en esa revisión.
- [ ] Revisar dependencias transitivas cuando corresponda.
- [ ] Conservar avisos y atribuciones obligatorios.
- [ ] Documentar el alcance del código copiado/adaptado.
- [ ] Fijar la dependencia y evaluar el impacto en la reproducibilidad.
