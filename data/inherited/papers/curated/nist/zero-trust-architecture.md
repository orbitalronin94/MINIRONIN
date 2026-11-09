# Arquitectura Zero Trust: verificar el acceso al recurso

**Fuente primaria:** NIST SP 800-207, *Zero Trust Architecture* (2020). https://doi.org/10.6028/NIST.SP.800-207  
**Estado:** publicación final; consultar la página NIST para notas y documentos relacionados.  
**Derechos:** síntesis original; la publicación incluye autores de distintas afiliaciones, por lo que se debe respetar el aviso de derechos de cada material.

## Principio

Zero Trust elimina la confianza implícita basada únicamente en ubicación de red, propiedad del dispositivo o pertenencia a una red corporativa. Cada acceso a un recurso debe evaluarse con información contextual y políticas explícitas.

## Componentes conceptuales

La arquitectura separa la decisión de política de su aplicación. El motor de política evalúa identidad, estado del dispositivo, recurso solicitado, contexto y señales de riesgo; el punto de aplicación controla la sesión. La implementación concreta puede distribuir estas funciones entre servicios y componentes.

## Qué no significa

Zero Trust no equivale a instalar un producto, bloquear toda conexión externa o exigir autenticación repetida sin criterio. Tampoco garantiza seguridad por sí solo. Una organización debe inventariar recursos, definir identidades, registrar decisiones, proteger dispositivos y revisar continuamente las políticas.

## Diseño y operación

La transición suele ser gradual: identificar recursos críticos, mapear flujos, definir políticas, instrumentar telemetría y probar excepciones. Las decisiones deben equilibrar protección, disponibilidad y experiencia de usuario. Los accesos de emergencia necesitan controles y auditoría específicos.

**Conceptos:** mínimo privilegio, política de acceso, identidad, dispositivo, telemetría, segmentación.
