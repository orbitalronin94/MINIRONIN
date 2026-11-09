# Autenticación y gestión de autenticadores

**Fuente primaria:** NIST SP 800-63B-4, *Authentication and Authenticator Management* (2025). https://doi.org/10.6028/NIST.SP.800-63B-4  
**Estado:** revisión 4 final, julio de 2025.  
**Derechos:** síntesis original; consultar los avisos del documento oficial antes de reproducir material fuente.

## Autenticación

La autenticación comprueba que el solicitante controla uno o más autenticadores vinculados a una cuenta. Un autenticador puede basarse en conocimiento, posesión o características inherentes, pero las combinaciones y requisitos dependen del nivel de garantía y del riesgo del servicio.

## Gestión del ciclo de vida

La seguridad no termina al registrar un autenticador. Deben contemplarse emisión, activación, uso, revocación, sustitución, pérdida y recuperación. Un proceso de recuperación débil puede anular la protección del mecanismo principal.

## Contraseñas y factores

La política debe evitar reglas arbitrarias que empeoren la seguridad, como cambios periódicos sin indicios de compromiso o composiciones excesivamente rígidas. La longitud, el bloqueo de contraseñas comprometidas, la limitación de intentos y el almacenamiento mediante funciones resistentes a ataques son aspectos relevantes. La autenticación multifactor reduce ciertos riesgos, pero no hace invulnerable una cuenta frente a phishing o ingeniería social.

## Contexto

Los requisitos deben ajustarse al riesgo, accesibilidad y sensibilidad de los datos. La autenticación es una parte de un sistema mayor que incluye autorización, sesiones, auditoría y respuesta ante incidentes.

**Conceptos:** autenticador, autenticación, MFA, recuperación, phishing, nivel de garantía.
