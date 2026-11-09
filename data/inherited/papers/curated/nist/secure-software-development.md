# Desarrollo seguro de software: prácticas a lo largo del ciclo de vida

**Fuente primaria:** NIST SP 800-218, *Secure Software Development Framework (SSDF) Version 1.1* (2022). https://doi.org/10.6028/NIST.SP.800-218  
**Estado:** versión 1.1 final.  
**Derechos:** síntesis original de publicación oficial con coautoría mixta; comprobar avisos específicos antes de redistribuir extractos.

## Enfoque

El SSDF propone integrar prácticas de seguridad en el ciclo de vida del software en vez de tratarlas como una inspección final. Organiza recomendaciones en preparar la organización, proteger el software, producir software bien protegido y responder a vulnerabilidades.

## Prácticas recurrentes

La organización necesita roles, formación y criterios comunes. El código, herramientas, entornos y paquetes deben protegerse frente a manipulación. El proceso de desarrollo debe incluir revisión, pruebas, análisis de dependencias y generación de artefactos reproducibles cuando sea posible. Las vulnerabilidades encontradas requieren priorización, corrección y comunicación.

## Evidencia

Una afirmación como «desarrollamos de forma segura» debe apoyarse en artefactos verificables: políticas, revisiones, resultados de pruebas, inventarios de componentes, registros de compilación y seguimiento de defectos. Ninguna herramienta aislada demuestra la seguridad de todo el producto.

## Integración práctica

El SSDF es deliberadamente compatible con distintos modelos de ciclo de vida. Puede mapearse a repositorios, pipelines CI/CD, gestión de dependencias y procesos de publicación. Las prácticas deben adaptarse a la escala y amenaza real del proyecto.

**Conceptos:** SDLC, secure-by-design, dependencias, revisión de código, vulnerabilidades, trazabilidad.
