# PROTOCOLO DE TESTING 1310 — VERSIÓN 1.0 EXTENDIDA

**Manual operativo para un sistema de testing tipado, falsable, íntegro y auditable, con extensión para QA asistido por IA.**

**Pydantic v2 + matemática + ciberseguridad + estado del arte 2025-2026 + multi-agente + validación semántica.**


## PARTE 0 — PRINCIPIO Y GUÍA DE DECISIÓN

Un test no es una opinión. Es un **testimonio falsable** sobre el comportamiento del software. Cada test se convierte en un objeto tipado, con refutador obligatorio, severidad, estándar de ciberseguridad y sello 1310. El sistema, un **Auditor 1310**, verifica integridad, ejecuta y reporta.

**Sin refutador, no hay test. Hay ilusión de cobertura.**

**El sello 1310 no es decorativo.** Acredita que el test ha superado el protocolo de falsabilidad: tiene refutador explícito, condición de fallo, hash pre-registrado y auditoría de integridad. Un test sin sello 1310 es un script que se ejecuta. Un test con sello 1310 es un testimonio que se puede refutar.

**Este protocolo está diseñado para que un LLM pueda operarlo sin ambigüedad.** No es un protocolo para humanos que escriben tests a mano. Es un protocolo para humanos que escriben **el contrato** y agentes que generan, ejecutan y validan los tests que lo cumplen.

### Árbol de decisión: ¿qué nivel necesito?

**Pregunta 1: ¿Tu software, si falla, puede causar daño físico, financiero o legal?**
- **SÍ** → Nivel Full. Banca, salud, automoción, defensa, IoT médico.
- **NO** → Pregunta 2.

**Pregunta 2: ¿Tienes requisitos regulatorios que auditar (PCI DSS, GDPR, DORA, IEC 62304, ISO 26262)?**
- **SÍ** → Nivel Standard o Full según criticidad.
- **NO** → Pregunta 3.

**Pregunta 3: ¿Tu equipo tiene menos de 10 personas y necesita shipear cada semana?**
- **SÍ** → Nivel Lite.
- **NO** → Nivel Standard.

**Regla operativa:** si dudas entre dos niveles, empieza por el inferior. Siempre puedes subir.

### Tres niveles de operación

| Nivel | Público | Qué incluye | Qué NO incluye |
|---|---|---|---|
| **Lite** | Startups, equipos de 1-10 personas | Plugin de pytest. Refutador en docstring. Hash automático. Coste de generación. | Roles, SBOM, SLSA, ML, HIL, auditoría regulatoria. |
| **Standard** | Empresas medianas, SaaS B2B, equipos de 10-50 | Lite + roles + estándares + reporte de negocio + ML básico + multi-agente. | SLSA 3+, HIL, TLPT, MC/DC. |
| **Full** | Banca, salud, automoción, defensa, regulados | Standard + SBOM + SLSA 3+ + MC/DC + HIL + TLPT + segregación auditable + ML completo + validación semántica. | Nada. Es el protocolo completo. |


## PARTE 1 — CÓMO FUNCIONA EL PROTOCOLO

### 1.1 El ciclo de vida

El protocolo tiene 4 fases. Cada una tiene un propósito y un responsable.

**Fase 1 — PROPUESTO.** El Arquitecto (o el desarrollador, en Lite) escribe el test. Declara qué verifica, cómo se refuta, qué severidad tiene y a qué estándar contribuye.

**Fase 2 — PRE_REGISTRADO.** El sistema calcula un hash SHA-256 de la **identidad inmutable** del test (no de su estado) y lo guarda. A partir de aquí, el test no se puede modificar sin que el hash deje de coincidir.

**Fase 3 — EN_EJECUCION.** El Ejecutor (o el CI/CD) corre el test. Se registra el resultado: `PASSED`, `FAILED`, `BLOCKED` o `QUARANTINED`.

**Fase 4 — AUDITADO.** El Auditor 1310 verifica que el hash coincide, que el resultado es consistente y que el fallo (si lo hay) tiene causa raíz documentada.

**Regla de oro:** un test que no ha pasado por las 4 fases no es un test. Es un script.

### 1.2 El refutador, explicado

El refutador es la parte más importante del protocolo. Responde a la pregunta: **¿qué tendría que pasar para que este test deje de ser válido?**

Sin refutador, un test es una tautología. Verifica lo que verifica porque lo verifica. No aporta información.

**El problema de los tests generados por IA:** estudios empíricos muestran que los LLMs generan tests que compilan y alcanzan cobertura razonable pero **fallan en detectar bugs**, y frecuentemente exhiben "design smells" que socavan su efectividad. Cuando se usan ingenuamente, estos asistentes tienden a generar **tests tautológicos que reformulan la lógica de implementación en lugar de desafiarla**.

**Ejemplo malo (sin refutador):**
```python
def test_suma():
    assert 2 + 2 == 4
```

**Ejemplo bueno (con refutador):**
```python
def test_transferencia_no_permite_saldo_negativo():
    """
    REFUTADOR: Si al transferir 100€ desde una cuenta con 50€ sin overdraft activo,
    el saldo resultante es >= 0 y la transferencia se completa.
    CONDICION_FALLO: saldo_final >= 0 and transferencia.completada
    """
    cuenta = Cuenta(saldo=50, overdraft_activo=False)
    resultado = transferir(cuenta, destino, 100)
    assert resultado.fallida
    assert cuenta.saldo == 50
```

### 1.3 El Auditor, explicado

El Auditor 1310 no es un juez. Es un **verificador de integridad**.

Sus funciones:
1. **Verificar el hash.** Compara el hash actual del test con el pre-registrado.
2. **Validar el refutador semánticamente.** No basta con que exista. Tiene que ser falsable de verdad.
3. **Decidir si un fallo es significativo.** Usa el historial de ejecuciones.
4. **Reportar.** Genera un JSON con el estado de la suite, impacto de negocio y estándares cubiertos.

**El Auditor no puede validar un test que él mismo propuso.**


## PARTE 2 — MODELO DE DATOS (PYDANTIC V2)

### 2.1 Enumeraciones base

```python
from enum import Enum
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import hashlib

class TipoTest(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    SECURITY = "security"
    INTEGRITY = "integrity"
    PERFORMANCE = "performance"
    PROPERTY = "property"
    CONTRACT = "contract"
    MUTATION = "mutation"
    CHAOS = "chaos"
    ML_DRIFT = "ml_drift"
    ML_FAIRNESS = "ml_fairness"
    ML_EXPLAINABILITY = "ml_explainability"
    ML_ROBUSTNESS = "ml_robustness"
    LLM_HALLUCINATION = "llm_hallucination"
    LLM_BIAS = "llm_bias"
    LLM_SAFETY = "llm_safety"

class CategoriaTest(str, Enum):
    A = "critico"
    B = "importante"
    C = "edge"
    D = "exploratorio"

class EstadoTest(str, Enum):
    PROPUESTO = "propuesto"
    PRE_REGISTRADO = "pre_registrado"
    EN_EJECUCION = "en_ejecucion"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    QUARANTINED = "quarantined"
    OBSOLETO = "obsoleto"
    TAUTOLOGICO = "tautologico"
    REFUTADOR_INVALIDO = "refutador_invalido"

class EstandarCiberseguridad(str, Enum):
    NIST_800_218 = "nist_sp_800_218"
    NIST_800_218A = "nist_sp_800_218a"
    ISO_27001 = "iso_27001"
    OWASP_ASVS = "owasp_asvs"
    OWASP_TOP_10 = "owasp_top_10_2025"
    SLSA = "slsa"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"
    NIST_800_53 = "nist_sp_800_53"
    ISO_26262 = "iso_26262"
    IEC_62304 = "iec_62304"
    ISO_21434 = "iso_21434"
    DORA = "dora"

class Severidad(str, Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFO = "info"

class Dominio(str, Enum):
    GENERAL = "general"
    CIBERSEGURIDAD = "ciberseguridad"
    BANCA = "banca"
    IOT = "iot"
    SALUD = "salud"
    AUTOMOCION = "automocion"
    VIDEOJUEGOS = "videojuegos"
    DEVOPS = "devops"
    CLOUD = "cloud"
    DEFENSA = "defensa"
    ML = "ml"

class Rol(str, Enum):
    PROPOSITOR = "propositor"
    EJECUTOR = "ejecutor"
    AUDITOR = "auditor_1310"
    CRONISTA = "cronista"
    GENERADOR_LLM = "generador_llm"
    VALIDADOR_SEMANTICO = "validador_semantico"

class NivelProtocolo(str, Enum):
    LITE = "lite"
    STANDARD = "standard"
    FULL = "full"

class ModeloLLM(str, Enum):
    GPT_4 = "gpt-4"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_SONNET = "claude-sonnet-4.6"
    CLAUDE_OPUS = "claude-opus-4.7"
    GEMINI_PRO = "gemini-2.5-pro"
    GEMINI_FLASH = "gemini-3-flash"
    QWEN_CODER = "qwen3-coder"
    DEVSTRAL_SMALL = "devstral-small-2"
    SEED = "seed-1.6"
    DEEPSEEK = "deepseek-v3.1"
```

### 2.2 Firma del test

```python
Probability = Annotated[float, Field(ge=0.0, le=1.0, strict=True)]

class FirmaTest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    cobertura_lineas: Probability
    cobertura_ramas: Probability
    cobertura_mcdc: Probability = 0.0
    mutacion_killed: Probability
    determinismo: Probability
    tiempo_ejecucion_ms: Annotated[int, Field(ge=0)]
    dependencias_externas: Annotated[int, Field(ge=0)]
    aislamiento: Probability
    flakiness: Probability
    integridad_tautologica: Probability  # 0.0 = tautológico, 1.0 = falsable

    def vector_10d(self) -> tuple[float, ...]:
        return (
            self.cobertura_lineas, self.cobertura_ramas,
            self.mutacion_killed, self.determinismo,
            float(self.tiempo_ejecucion_ms), float(self.dependencias_externas),
            self.aislamiento, self.flakiness,
            self.integridad_tautologica, self.cobertura_mcdc,
        )
```

### 2.3 Test inmutable con versionado

```python
SHA256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]

class TestInmutable(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=r"^TST-\d{4}$")]
    version: Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")] = "1.0.0"
    test_padre: Optional[str] = None
    motivo_version: Optional[str] = None

    tipo: TipoTest
    categoria: CategoriaTest
    dominio: Dominio
    nivel_protocolo: NivelProtocolo

    enunciado: Annotated[str, Field(min_length=10, max_length=500)]
    precondiciones: list[str] = Field(default_factory=list)
    pasos: list[str] = Field(default_factory=list)
    resultado_esperado: str

    refutador: Annotated[str, Field(min_length=10)]
    condicion_de_fallo: Annotated[str, Field(min_length=5)]
    refutador_es_falsable: bool = False  # validado por ValidadorSemantico

    severidad: Severidad
    estandares: list[EstandarCiberseguridad] = Field(default_factory=list)

    firma_esperada: Optional[FirmaTest] = None
    requisito_ref: Optional[str] = None
    riesgo_ref: Optional[str] = None
    fmea_ref: Optional[str] = None

    hash_sha256: SHA256
    fecha: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    sello: Literal[1310] = 1310

    # Generación por IA
    generado_por_llm: bool = False
    modelo_llm: Optional[ModeloLLM] = None
    prompt_version: Optional[str] = None
    coste_generacion: Optional[float] = None
    tokens_entrada: Optional[int] = None
    tokens_salida: Optional[int] = None

    @field_validator("refutador")
    @classmethod
    def refutador_no_generico(cls, v: str) -> str:
        prohibidos = ["depende", "quizás", "a veces", "puede ser", "siempre", "nunca"]
        if any(p in v.lower() for p in prohibidos):
            raise ValueError("refutador genérico: no es falsable")
        return v

    @field_validator("motivo_version")
    @classmethod
    def version_cambia_requiere_motivo(cls, v, info):
        if info.data.get("test_padre") and not v:
            raise ValueError("test versionado sin motivo de versión")
        return v


class TestEstado(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    test_id: str
    version: str
    estado: EstadoTest
    timestamp: str
    firma_observada: Optional[FirmaTest] = None
    hash_inmutable: SHA256
    propuesto_por: Rol
    ejecutado_por: Rol
    validado_por: Optional[Rol] = None
```

**Regla de versionado:** un test con `test_padre` no reemplaza al padre. Lo versiona. El padre se marca como `OBSOLETO` y se mantiene en el corpus para trazabilidad.

### 2.4 Coste de generación por LLM

**El problema:** generar 100 tests con GPT-4 cuesta dinero. El coste por test varía enormemente según el modelo y la estrategia. Sakura con Qwen3-Coder cuesta **$0.07 por test**, aproximadamente la mitad de Gemini CLI con Gemini 2.5 Pro, mientras que Devstral Small 2 iguala el precio de la gama Flash a **$0.02 por test**. TestForge genera tests para un archivo completo a **$0.63 por archivo**. DiffTestGen incurre en **$0.041 por instancia** comparado con $0.045 de Testora++. Claude-Sonnet-4.5 con single prompting reduce el coste de **$0.95 a $0.20 por instancia**.

```python
class CosteGeneracion(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    test_id: str
    modelo: ModeloLLM
    tokens_entrada: Annotated[int, Field(ge=0)]
    tokens_salida: Annotated[int, Field(ge=0)]

    # Precios por millón de tokens (USD)
    precio_entrada: float
    precio_salida: float

    # Estrategia de generación
    estrategia: Literal["single_prompt", "multi_prompt", "agentic", "hibrida"]
    num_intentos: Annotated[int, Field(ge=1)] = 1

    @property
    def coste_total(self) -> float:
        return (
            (self.tokens_entrada / 1_000_000) * self.precio_entrada
            + (self.tokens_salida / 1_000_000) * self.precio_salida
        )

    @property
    def coste_por_intento(self) -> float:
        return self.coste_total / self.num_intentos

    @classmethod
    def desde_modelo(cls, test_id: str, modelo: ModeloLLM,
                     tokens_in: int, tokens_out: int,
                     estrategia: str = "single_prompt") -> "CosteGeneracion":
        PRECIOS = {
            ModeloLLM.GPT_4: (30.0, 60.0),
            ModeloLLM.GPT_4O_MINI: (0.15, 0.60),
            ModeloLLM.CLAUDE_SONNET: (3.0, 15.0),
            ModeloLLM.CLAUDE_OPUS: (10.0, 50.0),
            ModeloLLM.GEMINI_PRO: (1.25, 10.0),
            ModeloLLM.GEMINI_FLASH: (0.10, 0.40),
            ModeloLLM.QWEN_CODER: (0.07, 0.07),
            ModeloLLM.DEVSTRAL_SMALL: (0.02, 0.02),
            ModeloLLM.SEED: (0.19, 0.19),
            ModeloLLM.DEEPSEEK: (0.27, 1.10),
        }
        p_in, p_out = PRECIOS.get(modelo, (1.0, 3.0))
        return cls(
            test_id=test_id, modelo=modelo,
            tokens_entrada=tokens_in, tokens_salida=tokens_out,
            precio_entrada=p_in, precio_salida=p_out,
            estrategia=estrategia
        )


class PresupuestoGeneracion(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    limite_total: float = 100.0
    limite_por_test: float = 1.0
    gasto_acumulado: float = 0.0
    tests_generados: int = 0

    @property
    def coste_medio(self) -> float:
        return self.gasto_acumulado / self.tests_generados if self.tests_generados else 0.0

    def puede_generar(self, coste_estimado: float) -> bool:
        return (self.gasto_acumulado + coste_estimado <= self.limite_total
                and coste_estimado <= self.limite_por_test)
```

**Regla 1310:** si el coste de generación de un test supera el coste estimado del bug que previene, el test no se genera con ese modelo. Se usa un modelo más barato o se escribe a mano. El protocolo distingue entre **tests de generación barata** (Qwen3-Coder, Devstral) y **tests de generación premium** (Claude Opus, GPT-4).

**Un test suite con 100 casos usando GPT-4 puede costar entre $5 y $50 por ejecución**. El coste debe presupuestarse, no descubrirse.

### 2.5 Versionado de prompts de generación

**El problema:** si el prompt del Propositor cambia, los tests generados cambian. Eso es un cambio de versión del protocolo, no del test. El protocolo debe distinguirlo.

**Estado del arte 2026:** Los prompts son código — necesitan control de versiones, testing y despliegues graduales como el software. Las mejores prácticas incluyen versionar los prompts de generación junto con el código. Cuando los patrones de test cambian, los prompts se actualizan en consecuencia.

```python
class PromptGeneracion(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=r"^PRM-\d{3}$")]
    version: Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")]
    contenido: str
    modelo_objetivo: ModeloLLM
    hash_sha256: SHA256

    # Métricas de calidad del prompt
    tests_generados: int = 0
    tests_validos: int = 0
    tests_tautologicos: int = 0
    coste_medio_por_test: float = 0.0

    @property
    def tasa_validez(self) -> float:
        return self.tests_validos / self.tests_generados if self.tests_generados else 0.0

    @property
    def tasa_tautologia(self) -> float:
        return self.tests_tautologicos / self.tests_generados if self.tests_generados else 0.0


class HistorialPrompts(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    prompts: list[PromptGeneracion] = Field(default_factory=list)

    def mejor_prompt(self, modelo: ModeloLLM) -> Optional[PromptGeneracion]:
        candidatos = [p for p in self.prompts if p.modelo_objetivo == modelo]
        if not candidatos:
            return None
        return max(candidatos, key=lambda p: p.tasa_validez)

    def detectar_regresion(self, prompt_nuevo: PromptGeneracion,
                           prompt_anterior: PromptGeneracion,
                           umbral: float = 0.05) -> bool:
        """Detecta si un nuevo prompt degrada la calidad."""
        return (prompt_anterior.tasa_validez - prompt_nuevo.tasa_validez) > umbral
```

**Regla 1310:** un cambio de prompt que reduce la tasa de validez en más de un 5% se considera regresión. El prompt anterior se mantiene como fallback. No se actualiza el prompt en producción sin A/B testing previo.

### 2.6 Validación semántica de refutadores

**El problema:** un LLM puede escribir "REFUTADOR: si el resultado es incorrecto, el test falla". Eso no es un refutador. Es una tautología. El validador actual solo detecta palabras prohibidas (`depende`, `quizás`). No detecta tautologías semánticas.

**Estado del arte 2026:** **VALTEST** utiliza **entropía semántica** para validar automáticamente casos de test generados por LLMs. Mide la incertidumbre en las partes semánticas de un caso de test y usa esas señales para identificar tests inválidos antes de que se usen en tareas downstream. Estudios empíricos muestran que los LLMs generan oráculos con puntuación de mutación promedio del **43%**, similar al **45%** de los oráculos diseñados por humanos.

```python
class ValidadorSemantico(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    modelo_validador: ModeloLLM = ModeloLLM.GPT_4O_MINI
    umbral_entropia: float = 0.7
    umbral_confianza: float = 0.85

    def validar_refutador(self, refutador: str,
                          condicion_fallo: str,
                          contexto_codigo: str) -> "ResultadoValidacion":
        """
        Valida si un refutador es semánticamente falsable.
        Usa entropía semántica para detectar tautologías.
        """
        ...

    def detectar_tautologia_estructural(self, refutador: str,
                                         codigo: str) -> bool:
        """
        Detecta si el refutador reformula la implementación
        en lugar de desafiarla (tautología estructural).
        """
        ...

    def detectar_tautologia_semantica(self, refutador: str) -> bool:
        """
        Detecta si el refutador es vacuamente cierto
        (ej: 'si el resultado es incorrecto, falla').
        """
        ...


class ResultadoValidacion(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    es_falsable: bool
    entropia_semantica: Probability
    confianza: Probability
    razon: str
    tipo_tautologia: Optional[Literal[
        "vacuamente_cierto", "reformulacion", "mock_passthrough",
        "assert_interno", "snapshot_inutil"
    ]] = None
```

**Tipos de test tautológico que el ValidadorSemantico debe detectar:**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Vacuamente cierto** | El refutador no puede ser falso en ninguna circunstancia | "Si el resultado es incorrecto, el test falla" |
| **Reformulación** | El refutador usa la misma lógica que la implementación | `assert construir_query(x) == construir_query(x)` |
| **Mock passthrough** | El test verifica que el mock devuelve lo que se le configuró | `mock.return_value = 5; assert obj.metodo() == 5` |
| **Assert interno** | El test verifica estado interno, no comportamiento | `assert obj._cache == {}` |
| **Snapshot inútil** | El snapshot no verifica nada útil | `expect(foo()).toMatchSnapshot()` sin revisión |

**Regla 1310:** si el ValidadorSemantico detecta una tautología, el test pasa a estado `TAUTOLOGICO`. No se ejecuta. No cuenta para cobertura. No bloquea release. Pero se registra en el corpus negativo como fallo del Propositor.

### 2.7 Multi-agente: roles como agentes

**El problema:** un LLM puede generar un test, pero no puede validarlo sin sesgo. La segregación de funciones que en un equipo humano es un problema organizativo, en un sistema multi-agente es una arquitectura natural.

**Estado del arte 2026:** TestAgent propone un enfoque de generación de tests basado en LLM que aborda las limitaciones de los enfoques actuales emulando prácticas humanas de testing mediante un mecanismo de **colaboración multi-agente**. Diseña tres agentes especializados. Investigaciones recientes argumentan que los frameworks multi-agente generan mejores tests unitarios que un único prompt bien elaborado, refinando iterativamente la cobertura y verificando oráculos de forma cruzada.

```python
class AgenteTesting(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=r"^AGT-\d{3}$")]
    rol: Rol
    modelo: ModeloLLM
    prompt_ref: Optional[str] = None

    # Permisos
    puede_proponer: bool = False
    puede_ejecutar: bool = False
    puede_validar: bool = False
    puede_generar: bool = False
    puede_validar_semanticamente: bool = False


class SistemaMultiAgente(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    agentes: list[AgenteTesting] = Field(default_factory=list)
    max_iteraciones: Annotated[int, Field(ge=1, le=10)] = 3

    def orquestar_generacion(self, requisito: str,
                              codigo: str) -> list[TestInmutable]:
        """
        Orquesta el ciclo:
        1. GeneradorLLM propone tests.
        2. ValidadorSemantico valida refutadores.
        3. Auditor verifica integridad.
        4. Ejecutor corre.
        5. Si falla, vuelve a 1 con feedback.
        """
        ...

    def _agente_por_rol(self, rol: Rol) -> Optional[AgenteTesting]:
        for a in self.agentes:
            if a.rol == rol:
                return a
        return None
```

**Roles mapeados a agentes:**

| Rol humano | Agente LLM | Función |
|---|---|---|
| Propositor | GeneradorLLM | Genera tests desde requisitos y código |
| Validador | ValidadorSemantico | Valida que los refutadores sean falsables |
| Ejecutor | Ejecutor | Corre los tests en CI/CD |
| Auditor | Auditor1310 | Verifica integridad, hash, roles |
| Cronista | Cronista | Documenta resultados, mantiene corpus negativo |

**Regla 1310:** un test generado por `GeneradorLLM` no puede ser validado semánticamente por el mismo modelo. Si el Generador usa GPT-4, el Validador usa Claude o Gemini. La diversidad de modelos es la garantía de independencia.

### 2.8 Historial de ejecuciones y flakiness

```python
class HistorialEjecuciones(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    test_id: str
    ventana: int = 20
    resultados: list[bool] = Field(default_factory=list)

    @property
    def tasa_exito(self) -> float:
        return sum(self.resultados) / len(self.resultados) if self.resultados else 1.0

    @property
    def es_flaky(self) -> bool:
        return 0.05 < self.tasa_exito < 0.95

    @property
    def fallo_es_significativo(self) -> bool:
        if not self.es_flaky:
            return True
        ultimos_3 = self.resultados[-3:]
        return len(ultimos_3) == 3 and all(not r for r in ultimos_3)
```

**Implementación escalable:** el historial vive en SQLite (`.testing1310/historial.db`). La ventana de 20 se calcula con `ORDER BY timestamp DESC LIMIT 20`.


## PARTE 3 — LA MATEMÁTICA DEL TESTING

### 3.1 Ecuación maestra del fitness

```python
Alpha = Annotated[float, Field(ge=0.5, le=2.5, strict=True)]

class EcuacionMaestraTesting(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    phi: Probability
    psi: Probability
    omega: Probability
    alpha: Alpha
    epsilon: Annotated[float, Field(gt=0.0, strict=True)]
    k: Optional[Probability] = None

    def fitness(self) -> float:
        return self.phi * self.psi * (self.omega ** self.alpha) * self.epsilon
```

### 3.2 Las seis condiciones de reducción (SCR)

```python
class SCRTesting(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    estatico: bool = True
    epsilon_uno: bool = True
    psi_uno: bool = True
    alpha_uno: bool = True
    phi_uno: bool = True
    r_infinito: bool = True

    def amputaciones(self) -> int:
        return sum([self.estatico, self.epsilon_uno, self.psi_uno,
                    self.alpha_uno, self.phi_uno, self.r_infinito])
```

### 3.3 Property-Based Testing con refinamiento adversarial

**Estado del arte 2026:** PROBE introduce Refinamiento Adversarial: un agente Validador genera contra-implementaciones (código semánticamente incorrecto que satisface la propiedad generada) para exponer lagunas en la especificación. PROBE incrementa las puntuaciones de mutación en un 9.79% e identificó 45 bugs previamente desconocidos en bibliotecas de primer nivel.

```python
class PropiedadPBT(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    invariante: str
    generador: str
    num_ejemplos: Annotated[int, Field(ge=100, le=10000)] = 1000
    shrinkage: bool = True
    refinamiento_adversarial: bool = True
    contraejemplo: Optional[str] = None
```

### 3.4 Mutation Testing con LLM

**Estado del arte 2025-2026:** Firefly demuestra que incluso diseños con 95% de cobertura pueden tener hasta un 28% de bugs no detectados. SMART demuestra que los LLMs pueden generar mutantes de alta calidad, incluso modelos de 7B igualando a GPT-4o.

```python
class MutacionLLM(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    tipo_mutacion: str
    contexto: str
    mutante_generado: str
    killed: bool
    equivalente: bool = False
    test_aware: bool = True
```

### 3.5 Property-Based Testing para LLM

```python
class PropiedadLLM(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    invariante: str
    prompt_generador: str
    num_ejemplos: Annotated[int, Field(ge=10, le=1000)] = 50
    metrica: Literal["hallucination", "faithfulness", "toxicity",
                     "bias", "answer_relevancy"]
    umbral: Probability
    direccion: Literal["mayor_que", "menor_que"]
```

### 3.6 Semantic Entropy para validación de tests

**Estado del arte 2026:** VALTEST introduce un marco que aprovecha la entropía semántica para validar automáticamente casos de test generados por LLMs. Los resultados sugieren que la entropía semántica es una señal fiable para identificar tests inválidos. La entropía semántica se calcula generando múltiples respuestas para la misma pregunta y midiendo la incertidumbre entre clusters semánticos.

```python
class EntropiaSemantica(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    test_id: str
    num_muestras: Annotated[int, Field(ge=5, le=50)] = 10
    entropia: Annotated[float, Field(ge=0.0, le=1.0)]
    clusters_semanticos: Annotated[int, Field(ge=1)]
    confianza: Probability

    @property
    def test_valido(self) -> bool:
        """Entropía baja = test consistente = válido."""
        return self.entropia < 0.7 and self.confianza > 0.85
```


## PARTE 4 — INTEGRIDAD Y CIBERSEGURIDAD

### 4.1 Cadena de integridad

```python
class IntegridadTest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    hash_sha256: SHA256
    firma_gpg: Optional[str] = None
    sbom_ref: Optional[str] = None
    slsa_nivel: Annotated[int, Field(ge=0, le=4)] = 0
    provenance_ref: Optional[str] = None
    vulnerabilidades_conocidas: list[str] = Field(default_factory=list)
```

**Estado del arte 2026:** Los ataques a la cadena de suministro más que se duplicaron globalmente en 2025. SLSA provenance crea una cadena criptográfica que vincula un artefacto a su commit de origen.

### 4.2 OWASP Top 10:2025 — mapeo operativo con honestidad

| Categoría OWASP | Automatizable | Herramienta | Test 1310 |
|---|---|---|---|
| A01: Broken Access Control | Parcial | ZAP, Burp | Integration + Security |
| A02: Security Misconfiguration | **Sí** | Checkov, Trivy | Integrity + IaC scan |
| A03: Supply Chain Failures | **Sí** | Syft, Snyk | Integrity + SBOM |
| A04: Cryptographic Failures | **Sí** | SAST | Unit + Security |
| A05: Injection (incl. Prompt Injection) | **Sí** | SQLMap, SAST | Unit + Property |
| A06: Insecure Design | **NO** (requiere humano) | Manual + LLM | Threat model + E2E |
| A07: Authentication Failures | Parcial | ZAP, custom | E2E + Security |
| A08: Data Integrity Failures | **Sí** | Sigstore | Integrity + Contract |
| A09: Logging Failures | **Sí** | Custom | Integration |
| A10: Mishandling Exceptional Conditions | **NO** (requiere humano) | Custom | Integration + Chaos |

**Regla de honestidad:** A06 y A10 no son automatizables. El protocolo lo dice explícitamente.

### 4.3 NIST SP 800-218A — AI SSDF Profile

```python
class PracticaSSDF(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    grupo: Literal["PO", "PS", "PW", "RV"]
    practica_id: str
    es_ai_profile: bool = False
    evidencia: str
```

### 4.4 Chaos Engineering para agentes AI

**Estado del arte 2026:** AgentChaos propone inyección programática de fallos en runtime sobre APIs de LLM. El 14.4% de los agentes llegan a producción con aprobación completa de seguridad e IT.

```python
class TestChaosAI(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    tipo_fallo: Literal["latencia", "timeout", "respuesta_malformada",
                        "alucinacion", "tool_failure", "context_overflow"]
    sistema_ref: str
    num_configuraciones: Annotated[int, Field(ge=1, le=100)] = 10
    tasa_degradacion_aceptable: Probability
```

### 4.5 Red teaming adversarial continuo

```python
class RedTeamingContinuo(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    id: str
    objetivo: str
    tipo_ejercicio: Literal["TLPT", "Vibe Red Teaming", "Fuzzing adversarial"]
    frecuencia: Literal["diario", "semanal", "mensual", "trimestral", "anual"]
    framework: Optional[str] = None
    hallazgos: list[str] = Field(default_factory=list)
    test_regresion_asociado: Optional[str] = None

    def generar_test_desde_hallazgo(self, hallazgo: str) -> TestInmutable:
        """Todo hallazgo de red team se convierte en test de regresión."""
        ...
```

### 4.6 Ciclos regulatorios

```python
class CicloRegulatorio(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    estandar: EstandarCiberseguridad
    frecuencia: Literal["diario", "semanal", "mensual", "trimestral", "anual", "trienal"]
    tipo_test: TipoTest
    obligatorio: bool

CICLOS_REGULATORIOS = {
    EstandarCiberseguridad.PCI_DSS: CicloRegulatorio(
        estandar=EstandarCiberseguridad.PCI_DSS,
        frecuencia="trimestral", tipo_test=TipoTest.SECURITY, obligatorio=True),
    EstandarCiberseguridad.DORA: CicloRegulatorio(
        estandar=EstandarCiberseguridad.DORA,
        frecuencia="trienal", tipo_test=TipoTest.SECURITY, obligatorio=True),
    EstandarCiberseguridad.IEC_62304: CicloRegulatorio(
        estandar=EstandarCiberseguridad.IEC_62304,
        frecuencia="anual", tipo_test=TipoTest.INTEGRATION, obligatorio=True),
}
```

**Regla:** un test que declara `PCI_DSS` como estándar debe ejecutarse al menos trimestralmente. Si no se ejecuta en 90 días, el Auditor lo marca como `CADUCADO`.


## PARTE 5 — EL LORE COMO TIPO

### 5.1 Sello 1310

```python
class Sello(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    valor: Literal[1310] = 1310
    fecha_referencia: Literal["1307-10-13"] = "1307-10-13"
    significado: Literal["caida_y_refundacion"] = "caida_y_refundacion"
    acredita: Literal["protocolo_falsable"] = "protocolo_falsable"
    visible_en_indice: bool = True
```

**Regla dura:** Pydantic valida `sello: Literal[1310] = 1310`. Si un test no tiene sello, no se instancia. Si se intenta modificar el sello, el hash cambia y el test queda `BLOCKED`.

### 5.2 Heterónimos del testing

```python
class HeteronimoTesting(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    nombre: Literal["arquitecto", "ejecutor", "auditor_1310", "cronista",
                    "generador_llm", "validador_semantico"]
    funcion: str
    puede_proponer: bool
    puede_ejecutar: bool
    puede_validar: bool
```

### 5.3 Capas de visibilidad

```python
class CapaTesting(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    nivel: Annotated[int, Field(ge=0, le=6)]
    nombre: str
    visible_en_ci: bool
    visible_en_github: bool
    incluye_1310: bool
```


## PARTE 6 — CICLO DE VIDA

```
PROPUESTO
  │  (asignar id, versión, categoría, refutador, estándares)
  ▼
GENERADO_POR_LLM  ← si generado_por_llm=True
  │  (validar refutador con ValidadorSemantico)
  ▼
PRE_REGISTRADO  ← hash SHA-256 calculado sobre TestInmutable
  │  (congelado, no editable)
  ▼
EN_EJECUCION
  │  (CI/CD ejecuta el test)
  ▼
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
▼              ▼              ▼              ▼              ▼
PASSED         FAILED         BLOCKED        QUARANTINED    TAUTOLOGICO
```

```python
TRANSICIONES: dict[EstadoTest, set[EstadoTest]] = {
    EstadoTest.PROPUESTO: {EstadoTest.PRE_REGISTRADO, EstadoTest.GENERADO_POR_LLM},
    EstadoTest.GENERADO_POR_LLM: {EstadoTest.PRE_REGISTRADO,
                                   EstadoTest.TAUTOLOGICO,
                                   EstadoTest.REFUTADOR_INVALIDO},
    EstadoTest.PRE_REGISTRADO: {EstadoTest.EN_EJECUCION},
    EstadoTest.EN_EJECUCION: {EstadoTest.PASSED, EstadoTest.FAILED,
                               EstadoTest.BLOCKED, EstadoTest.QUARANTINED},
    EstadoTest.PASSED: set(),
    EstadoTest.FAILED: {EstadoTest.EN_EJECUCION, EstadoTest.QUARANTINED},
    EstadoTest.BLOCKED: {EstadoTest.EN_EJECUCION},
    EstadoTest.QUARANTINED: {EstadoTest.EN_EJECUCION},
    EstadoTest.TAUTOLOGICO: {EstadoTest.PROPUESTO},  # requiere reescritura
    EstadoTest.REFUTADOR_INVALIDO: {EstadoTest.PROPUESTO},
    EstadoTest.SKIPPED: {EstadoTest.EN_EJECUCION},
    EstadoTest.OBSOLETO: set(),
}
```

Un test **TAUTOLOGICO** no se elimina. Se marca. Y se documenta en el corpus negativo como fallo del Propositor. Un test **FAILED** no se elimina. Se marca. Y se documenta el fallo.


## PARTE 7 — EL AUDITOR 1310

### 7.1 Auditor con versionado, riesgo y validación semántica

```python
class Auditor1310(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    suite: list[TestInmutable]
    pre_registro: dict[str, SHA256] = Field(default_factory=dict)
    resultados: list[dict] = Field(default_factory=list)
    historiales: dict[str, HistorialEjecuciones] = Field(default_factory=dict)
    fmeas: dict[str, FMEA] = Field(default_factory=dict)
    validador: ValidadorSemantico = Field(default_factory=ValidadorSemantico)
    presupuesto: PresupuestoGeneracion = Field(default_factory=PresupuestoGeneracion)

    def pre_registrar(self, t: TestInmutable) -> SHA256:
        h = hashlib.sha256(t.model_dump_json().encode()).hexdigest()
        self.pre_registro[t.id] = h
        return h

    def verificar_integridad(self, t: TestInmutable, e: TestEstado) -> bool:
        h_actual = hashlib.sha256(t.model_dump_json().encode()).hexdigest()
        return (h_actual == self.pre_registro[t.id]
                and e.hash_inmutable == self.pre_registro[t.id])

    def validar_refutador(self, t: TestInmutable) -> bool:
        resultado = self.validador.validar_refutador(
            t.refutador, t.condicion_de_fallo, t.enunciado
        )
        if not resultado.es_falsable:
            t.estado = EstadoTest.TAUTOLOGICO
            return False
        return True

    def decidir_bloqueo(self, test_id: str, estado: TestEstado) -> bool:
        historial = self.historiales.get(test_id)
        test = self._test_de(test_id)
        if not historial or not historial.fallo_es_significativo:
            return False
        if test.severidad == Severidad.CRITICA:
            return True
        return estado == EstadoTest.FAILED and test.categoria == CategoriaTest.A

    def generar_con_presupuesto(self, requisito: str, codigo: str,
                                 modelo: ModeloLLM) -> Optional[TestInmutable]:
        """Genera un test solo si hay presupuesto."""
        coste_estimado = self._estimar_coste(modelo, requisito, codigo)
        if not self.presupuesto.puede_generar(coste_estimado):
            return None
        return self._generar(requisito, codigo, modelo)
```

### 7.2 Roles y segregación de funciones

```python
class Permisos(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    rol: Rol
    puede_proponer: bool
    puede_ejecutar: bool
    puede_validar: bool
    puede_generar: bool
    puede_validar_semanticamente: bool

PERMISOS = {
    Rol.PROPOSITOR: Permisos(rol=Rol.PROPOSITOR,
                             puede_proponer=True, puede_ejecutar=False,
                             puede_validar=False, puede_generar=False,
                             puede_validar_semanticamente=False),
    Rol.GENERADOR_LLM: Permisos(rol=Rol.GENERADOR_LLM,
                                puede_proponer=True, puede_ejecutar=False,
                                puede_validar=False, puede_generar=True,
                                puede_validar_semanticamente=False),
    Rol.VALIDADOR_SEMANTICO: Permisos(rol=Rol.VALIDADOR_SEMANTICO,
                                      puede_proponer=False, puede_ejecutar=False,
                                      puede_validar=True, puede_generar=False,
                                      puede_validar_semanticamente=True),
    Rol.EJECUTOR: Permisos(rol=Rol.EJECUTOR,
                           puede_proponer=False, puede_ejecutar=True,
                           puede_validar=False, puede_generar=False,
                           puede_validar_semanticamente=False),
    Rol.AUDITOR: Permisos(rol=Rol.AUDITOR,
                          puede_proponer=False, puede_ejecutar=False,
                          puede_validar=True, puede_generar=False,
                          puede_validar_semanticamente=False),
    Rol.CRONISTA: Permisos(rol=Rol.CRONISTA,
                           puede_proponer=False, puede_ejecutar=False,
                           puede_validar=False, puede_generar=False,
                           puede_validar_semanticamente=False),
}
```

**Regla para equipos pequeños:** si un usuario tiene múltiples roles, el sistema lo marca como `RIESGO_SEGREGACION` en el reporte.

**Regla para multi-agente:** el `GeneradorLLM` no puede ser el mismo modelo que el `ValidadorSemantico`. Si el Generador usa GPT-4, el Validador usa Claude o Gemini.

### 7.3 Gestión de costes de ejecución

```python
class CosteEjecucion(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    test_id: str
    coste_unitario: float
    num_ejecuciones: int
    coste_total: float
```

**Regla 1310:** si el coste de un test supera el coste estimado del bug que previene, el test no se ejecuta en cada commit. Se ejecuta en nightly o pre-release.

### 7.4 Métricas de escape de emulación

```python
class MetricaEscape(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    nivel_origen: Literal["emulacion", "sil", "pil", "hil"]
    bugs_encontrados: int
    bugs_escapados_a_hil: int
    tasa_escape: float

    @property
    def justifica_hil(self) -> bool:
        return self.tasa_escape > 0.3
```


## PARTE 8 — IMPLEMENTACIÓN LITE

### 8.1 Quickstart de 5 minutos

```
Paso 1: Instalar el plugin
  pip install testing1310

Paso 2: Activar en conftest.py
  from testing1310 import plugin
  def pytest_configure(config):
      plugin.activar(modo="lite")

Paso 3: Escribir un test con refutador
  def test_transferencia_no_permite_saldo_negativo():
      """
      REFUTADOR: Si al transferir 100€ desde una cuenta con 50€ sin overdraft,
      el saldo resultante es >= 0 y la transferencia se completa.
      CONDICION_FALLO: saldo_final >= 0 and transferencia.completada
      SEVERIDAD: alta
      SELLO: 1310
      """
      cuenta = Cuenta(saldo=50, overdraft_activo=False)
      resultado = transferir(cuenta, destino, 100)
      assert resultado.fallida
      assert cuenta.saldo == 50

Paso 4: Ejecutar
  pytest --testing1310

Paso 5: Ver el reporte
  cat .testing1310/reporte.json
```

**Eso es todo.** Cinco minutos. Sin Pydantic. Sin modelos. Sin SHA-256 manual.

### 8.2 Guía de onboarding para LLM

```
Eres un agente de testing 1310. Cada test que generas tiene:
1. Un refutador explícito (qué tendría que pasar para que el test falle)
2. Una condición de fallo (el assert concreto)
3. Una severidad (critica, alta, media, baja, info)
4. Al menos un estándar de ciberseguridad si tipo == SECURITY
5. Un sello 1310

No generas tests sin refutador. No generas refutadores genéricos
("depende", "quizás", "a veces"). No generas tests tautológicos.
Un test tautológico es aquel que verifica la implementación
en lugar de desafiarla. Si no puedes formular un refutador que
pueda ser falso, el test no es un test. Es un script.

Si generas un test con un refutador tautológico, el ValidadorSemantico
lo detectará y el test pasará a estado TAUTOLOGICO. No contará para
cobertura. No bloqueará release. Pero quedará registrado como fallo
del Propositor.
```


## PARTE 9 — IMPLEMENTACIÓN FULL

### 9.1 Arquitectura completa

El nivel Full usa todos los modelos definidos en PARTE 2. El Auditor 1310 orquesta:

1. **Pre-registro** de cada `TestInmutable`.
2. **Validación semántica** del refutador.
3. **Verificación de integridad** (hash SHA-256).
4. **Ejecución** con registro de `TestEstado`.
5. **Decisión de bloqueo** basada en historial, severidad y categoría.
6. **Reporte** con impacto de negocio, costes y estándares cubiertos.

### 9.2 Gestión de anomalías para dominios regulados

```python
def cerrar_fallo(self, test_id: str, anomalia: Anomalia) -> bool:
    """Un fallo en dominio regulado solo se cierra con causa raíz."""
    test = self._test_de(test_id)
    if test.dominio in [Dominio.SALUD, Dominio.AUTOMOCION, Dominio.BANCA]:
        if not anomalia.causa_raiz or not anomalia.accion_correctiva:
            return False
    return True
```

### 9.3 Reporte de negocio

```python
class ReporteNegocio(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    total: int
    passed: int
    failed: int
    blocked: int
    tautologicos: int
    refutadores_invalidos: int

    bugs_prevenidos_estimados: int
    coste_bug_produccion_evitado: float
    tiempo_medio_reparacion_reducido: float
    cobertura_owasp: float
    cobertura_requisitos: float
    roi_estimado: float

    # Costes de generación
    coste_generacion_total: float
    coste_generacion_medio_por_test: float
    tests_generados_por_llm: int

    # Transparencia del cálculo
    formula_roi: str = "(beneficio - coste) / coste"
    formula_bugs: str = "failed * tasa_escape_historica"
    tasa_escape_historica: float
    coste_medio_bug_produccion: float
    coste_testing: float
```

**Estado del arte 2026:** Los equipos que adoptan TDD reportan reducciones de defectos entre 40% y 90%. Las organizaciones que implementan automatización de pruebas pueden reducir entre 40% y 85% los costos operativos de QA.


## PARTE 10 — CONSEJOS POR DOMINIO

### 10.1 Ciberseguridad

**Nivel:** Standard o Full.

**Frameworks:** Semgrep, CodeQL, SonarQube (SAST). ZAP, Burp Suite (DAST). Atheris, AFL++ (fuzzing). Snyk, Dependabot, Trivy (SCA). Syft, CycloneDX (SBOM). slsa-github-generator, in-toto (SLSA provenance).

**Prácticas:** Threat modeling antes del primer test. SAST/DAST en cada commit. Red teaming adversarial continuo. SBOM + SLSA 3+.

### 10.2 Banca y Servicios Financieros

**Nivel:** Full.

**Frameworks:** Pact, PactFlow (contract). Hypothesis (PBT financiero). Parasoft, Tricentis Tosca (compliance). JMeter, k6, Gatling (performance). TIBER-EU (TLPT).

**Prácticas:** Contract testing obligatorio entre servicios. PBT financiero. TLPT trienal. Trazabilidad DORA. Ciclos regulatorios diferenciados.

### 10.3 IoT y Sistemas Embebidos

**Nivel:** Standard o Full según criticidad.

**Frameworks:** Unity Test (C). Google Test (C++). Ceedling (C embedded). PlatformIO, ArduinoUnit (board automation). Renode, QEMU (simulación). LabVIEW, dSPACE (HIL). Otii, Joulescope (power profiling).

**Prácticas:** Fallback HIL → PIL → SIL → emulación. Métricas de escape. Power profiling como test no funcional. Fuzzing de red.

### 10.4 Salud y Dispositivos Médicos

**Nivel:** Full.

**Frameworks:** Jira + Xray / TestRail (trazabilidad). Greenlight Guru, MasterControl (QMS). pytest, JUnit (unit). Hypothesis (PBT clínico). ELK, Splunk (auditoría de accesos).

**Prácticas:** Trazabilidad requisito-test. Gestión de anomalías con causa raíz. IEC 62304 en revisión 2026. Human-in-the-loop.

### 10.5 Automoción

**Nivel:** Full.

**Frameworks:** Parasoft C/C++test (MC/DC). Floyd (Rust, open-source). Reactis, Testwell CTC++ (coverage). CodeSonar (static). dSPACE, Vector (MIL/SIL/PIL/HIL). CANoe, Vehicle Spy (bus).

**Prácticas:** MC/DC obligatorio para ASIL C/D. ISO 21434 TARA. MIL/SIL/PIL/HIL. Alternativa open-source: Floyd para Rust, LLVM-Cov extendido para DO-178C.

### 10.6 Videojuegos

**Nivel:** Standard.

**Frameworks:** TITAN (agentes LLM en MMORPG). MIMIC (personalidades de agente). GameEval (browser games). Applitools (regresión visual). RenderDoc, Unity Profiler (performance).

**Prácticas:** Agentes LLM como testers exploratorios. Presupuesto de ejecución acotado. Balance testing con Monte Carlo.

### 10.7 DevOps y Cloud

**Nivel:** Lite o Standard.

**Frameworks:** SonarQube (quality gate). Checkov, OPA, Terratest (IaC). Trivy, Grype (contenedores). Syft, CycloneDX (SBOM). Prometheus, Grafana, OpenTelemetry (observabilidad). Flagger, Argo Rollouts (canary).

**Prácticas:** Quality gates automáticos. Ephemeral environments. Shift-right con canary. Observabilidad como test.

### 10.8 ML y LLM

**Nivel:** Standard o Full.

**Frameworks:** DeepEval, Promptfoo, Giskard (LLM testing). Evidently, NannyML (drift). Fairlearn, AIF360 (fairness). SHAP, LIME (explicabilidad). Great Expectations, Pandera (data validation).

**Prácticas:** Drift testing continuo. Fairness testing. LLM hallucination, bias, safety. Red teaming de modelos generativos. Coste de ejecución monitorizado.


## PARTE 11 — DECISIONES DE DISEÑO

1. **Frozen vs mutable:** inmutable para identidad. Mutable para estado. Separados.
2. **Quién propone tests:** cualquiera. Solo Auditor valida. Roles explícitos.
3. **Firma:** SHA-256 + GPG/Sigstore. SLSA provenance para artefactos.
4. **Tests exploratorios:** refutador opcional. Estado `SKIPPED`.
5. **Sello 1310:** **OBLIGATORIO.** Acredita protocolo falsable.
6. **Tests fallidos:** `CorpusNegativo`. Activo más valioso.
7. **Flakiness:** historial + umbral. Cuarentena con deadline.
8. **ML:** extensión `TestML`.
9. **HIL:** fallback con métrica de escape.
10. **ROI:** `ReporteNegocio` con fórmulas transparentes.
11. **Versionado:** semántico. `test_padre` + `motivo_version`.
12. **Riesgo:** FMEA/FTA obligatorio para severidad >= 9.
13. **Red teaming:** continuo. Cada hallazgo genera test de regresión.
14. **Coste:** monitorizado. Tests de commit vs tests de release.
15. **Ciclos regulatorios:** diferenciados por estándar.
16. **Onboarding:** quickstart 5 min + guía para LLM.
17. **Escalabilidad:** SQLite para historial. Buffer circular.
18. **Priorización:** tests críticos primero. Frameworks por capa, no por moda.
19. **Adopción:** roadmap por fases.
20. **Coste de generación:** `CosteGeneracion` + `PresupuestoGeneracion`.
21. **Versionado de prompts:** `PromptGeneracion` + `HistorialPrompts`.
22. **Validación semántica:** `ValidadorSemantico` + `EntropiaSemantica`.
23. **Multi-agente:** `SistemaMultiAgente` con roles como agentes.
24. **Detección de tautologías:** estado `TAUTOLOGICO` + tipos de tautología.
25. **Diversidad de modelos:** Generador y Validador usan modelos distintos.

### Roadmap de adopción

| Fase | Duración | Qué se implementa | Métrica de éxito |
|---|---|---|---|
| **Piloto** | 1-2 meses | Nivel Lite en 1 equipo. Refutadores en docstring. | 20 tests con refutador. |
| **Expansión** | 3-6 meses | Nivel Standard en 2-3 equipos. Roles, historial, reporte negocio, validación semántica. | ROI > 1.0. Flakiness < 5%. Tautológicos < 10%. |
| **Escala** | 6-12 meses | Nivel Full en toda la organización. SBOM, SLSA, ML, ciclos regulatorios, multi-agente. | Auditoría regulatoria pasada. |
| **Optimización** | 12+ meses | Red teaming continuo. Experience paper publicado. | Casos de éxito documentados. |



**La extensión para QA con IA:** el protocolo está diseñado para que un LLM pueda operarlo sin ambigüedad. El humano define el contrato (refutador, severidad, estándar). El LLM genera el test. El ValidadorSemantico verifica que el refutador sea falsable. El Auditor verifica integridad. El Ejecutor corre. El Cronista documenta. Y todo tiene coste, versión y trazabilidad.

**1310.**

*El que diseña el test también escribe el pipeline. Y el que lo ejecuta, también. Pero el que elige el nivel, decide qué protocolo necesita. Y el que valida el refutador, decide si el test es un test o es una ilusión.*


# ANEXO A — ALTERNATIVAS DESCARTADAS DURANTE EL DISEÑO

### A.1 Sello 1310 opcional en nivel Lite

**Considerado:** permitir que el nivel Lite no incluya el sello 1310.

**Descartado:** el sello no es un adorno. Es la acreditación de que el test ha pasado por el protocolo de falsabilidad. Sin sello, no hay test.

### A.2 Hash sobre el modelo completo

**Considerado:** calcular SHA-256 sobre el objeto completo incluyendo estado.

**Descartado:** el hash cambiaría en cada ejecución. Alternativa: separar `TestInmutable` de `TestEstado`.

### A.3 Historial de flakiness estático

**Considerado:** declarar flakiness como campo del test.

**Descartado:** el flakiness es dinámico. Alternativa: `HistorialEjecuciones` con ventana de 20.

### A.4 Tests de ML fuera del protocolo

**Considerado:** sistema aparte para ML.

**Descartado:** en banca, el 40% del riesgo es modelo. Alternativa: `TipoTest.ML_*`.

### A.5 HIL obligatorio en IoT

**Considerado:** exigir HIL para todos los tests de firmware.

**Descartado:** el hardware es caro. Alternativa: fallback + `MetricaEscape`.

### A.6 Automatización total de OWASP Top 10

**Considerado:** prometer cobertura automatizada de las 10 categorías.

**Descartado:** A06 y A10 no son automatizables. Alternativa: tabla honesta con "Automatizable: Sí/Parcial/NO".

### A.7 Threat modeling opcional

**Considerado:** recomendación, no obligación.

**Descartado:** sin modelo de amenazas, un test de seguridad es un checklist.

### A.8 ROI sin fórmula explícita

**Considerado:** ROI como número calculado internamente.

**Descartado:** no es auditable. Alternativa: `formula_roi` explícita en el reporte.

### A.9 Versionado por sobrescritura

**Considerado:** sobrescribir el test anterior cuando cambia.

**Descartado:** se pierde trazabilidad. Alternativa: versionado semántico con `test_padre`.

### A.10 Un único nivel

**Considerado:** un solo protocolo sin niveles.

**Descartado:** un banco necesita Full. Una startup necesita Lite. Alternativa: tres niveles.

### A.11 Sello 1310 como metáfora sin función

**Considerado:** elemento narrativo decorativo.

**Descartado:** si no acredita nada, no hay razón para mantenerlo. Alternativa: `Literal[1310]` validado por Pydantic.

### A.12 Ejecución de todos los tests en cada commit

**Considerado:** suite completa en cada commit.

**Descartado:** los tests de LLM cuestan dinero. Alternativa: tests de commit vs tests de release.

### A.13 Red teaming anual

**Considerado:** una vez al año.

**Descartado:** el atacante no espera. Alternativa: `RedTeamingContinuo`.

### A.14 Ciclos regulatorios unificados

**Considerado:** mismo ciclo para todos los estándares.

**Descartado:** PCI DSS es trimestral, DORA trienal, IEC 62304 anual. Alternativa: `CicloRegulatorio` diferenciado.

### A.15 Historial en memoria

**Considerado:** JSON en memoria durante la suite.

**Descartado:** 300.000 registros en memoria es inmanejable. Alternativa: SQLite.

### A.16 Framework único por capa

**Considerado:** recomendar un solo framework por capa.

**Descartado:** depende del lenguaje y del equipo. Alternativa: tabla con alternativas.

### A.17 Refutador opcional

**Considerado:** permitir tests sin refutador.

**Descartado:** sin refutador, un test es una tautología. Alternativa: obligatorio en todos los niveles.

### A.18 Sello calculado dinámicamente

**Considerado:** sello como función del hash.

**Descartado:** el sello no es un hash. Es una acreditación constante.

### A.19 Auditor único sin roles

**Considerado:** un solo rol de "tester".

**Descartado:** la segregación es requisito en PCI DSS, SOX y DORA. Alternativa: cuatro roles.

### A.20 Documentación extensa como onboarding

**Considerado:** el manual completo como onboarding.

**Descartado:** un dev nuevo no lee 40 páginas. Alternativa: quickstart de 5 minutos.

### A.21 Generación de tests sin coste monitorizado

**Considerado:** generar tests sin `CosteGeneracion`.

**Descartado:** un test suite con GPT-4 cuesta entre $5 y $50 por ejecución. El coste debe presupuestarse. Alternativa: `CosteGeneracion` + `PresupuestoGeneracion`.

### A.22 Versionado de prompts ignorado

**Considerado:** no versionar los prompts de generación.

**Descartado:** si el prompt cambia, los tests cambian. Es un cambio de versión del protocolo. Alternativa: `PromptGeneracion` + `HistorialPrompts`.

### A.23 Validación semántica solo con palabras prohibidas

**Considerado:** el validador actual solo detecta palabras prohibidas.

**Descartado:** un LLM puede escribir "si el resultado es incorrecto, falla". Eso es tautológico pero no contiene palabras prohibidas. Alternativa: `ValidadorSemantico` con entropía semántica.

### A.24 Un solo agente LLM para todo

**Considerado:** un agente que genera, valida y ejecuta.

**Descartado:** un agente no puede validar sin sesgo. Alternativa: `SistemaMultiAgente` con roles separados y modelos diversos.

### A.25 Tests tautológicos tratados como passed

**Considerado:** un test tautológico pasa porque el assert es verdadero.

**Descartado:** un test tautológico no verifica nada. Alternativa: estado `TAUTOLOGICO` que no cuenta para cobertura.

---

## CIERRE

El Protocolo de Testing 1310 formaliza cada prueba como un objeto tipado, con refutador obligatorio, severidad, estándar de ciberseguridad, firma de integridad, roles segregados, validación semántica y sello 1310. El Auditor verifica. El sistema reporta. Y la suite crece por refutación, no por acumulación.

**El sello 1310 es obligatorio.** Acredita que el test ha superado el protocolo de falsabilidad. Sin sello, no hay test. Hay script.


**1310.**

*El que diseña el protocolo también decide qué descartar. Y el que lee el anexo, sabe por qué.*
