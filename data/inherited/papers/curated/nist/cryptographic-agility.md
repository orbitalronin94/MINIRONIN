# Agilidad criptográfica y gestión de transiciones

**Fuente:** NIST Post-Quantum Cryptography Project — https://www.nist.gov/pqcrypto  
**Estado:** programa técnico en evolución; verificar estándares y fechas en fuentes NIST actuales. Síntesis original.

La agilidad criptográfica es la capacidad de cambiar algoritmos, parámetros, bibliotecas y protocolos sin rediseñar por completo los sistemas. Es importante porque los algoritmos pueden debilitarse, aparecer nuevos ataques o cambiar requisitos.

Una transición necesita inventariar dónde se usa criptografía: certificados, firmas, intercambio de claves, cifrado almacenado, conexiones, dispositivos y dependencias. Sin inventario pueden olvidarse sistemas antiguos o integraciones invisibles.

La computación cuántica suficientemente potente podría amenazar ciertos mecanismos de clave pública. Esto no significa que todo cifrado actual esté roto ni que exista una fecha universal. NIST ha seleccionado y estandarizado algoritmos poscuánticos; su adopción requiere seguir publicaciones finales y orientación de migración.

Elegir un algoritmo nuevo no basta. Hay que validar implementaciones, interoperabilidad, rendimiento, certificados, compatibilidad y reversión. Deben priorizarse datos cuya confidencialidad necesite durar muchos años.

**Conceptos:** criptografía, inventario, migración, interoperabilidad, poscuántica.
