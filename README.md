# PyRuta

App Android para estudiar la certificación **PCAP** (Python), de VGTechAI.

Este repositorio contiene, por ahora, el **banco de preguntas compartido**: una sola fuente de preguntas que
usan tanto PyRuta como el videojuego **Python Code Quest** (modo *Simulacro PCAP*). Corregir o agregar una
pregunta aquí la actualiza en ambos.

## Banco de preguntas

- `banco-preguntas/pcap.json` — 57 preguntas de práctica en español, en las 5 secciones del temario PCAP-31-03.
- `banco-preguntas/schema.json` — formato (JSON Schema).
- `tools/validar_banco.py` — validador. Revisa la estructura y **ejecuta el código** de cada pregunta con
  `"verify": "output"` para comprobar que la alternativa correcta es exactamente lo que muestra Python.
  Corre automáticamente en GitHub Actions en cada cambio.

Las preguntas son de elaboración propia para practicar; **no** son preguntas oficiales del examen.

| Sección | Peso aprox. en el examen | Preguntas |
| --- | --- | --- |
| Módulos y paquetes | 12 % | 11 |
| Excepciones | 14 % | 10 |
| Cadenas de texto | 18 % | 11 |
| Programación orientada a objetos | 34 % | 13 |
| Comprensiones, lambdas, clausuras, generadores y archivos | 22 % | 12 |

### Formato de una pregunta

```json
{
  "id": "PCAP-EXC-001",
  "exam": "PCAP",
  "section": "excepciones",
  "difficulty": 1,
  "type": "single",
  "prompt": "¿Qué muestra este código?",
  "code": "try:\n    print(1 / 0)\nexcept ZeroDivisionError:\n    print(\"A\")\nfinally:\n    print(\"C\")",
  "options": ["A C", "A B C", "B C", "A"],
  "answer": [0],
  "explanation": "Se ejecuta el except (A) y siempre el finally (C).",
  "verify": "output"
}
```

- `type`: `single` (una correcta) o `multiple` (varias correctas; `answer` lista todos los índices).
- `difficulty`: 1 básico, 2 intermedio, 3 avanzado.
- `answer`: índices (desde 0) de las opciones correctas. Las apps deberían **mezclar** el orden al mostrarlas.

### Usarlo en la app Android (Kotlin)

Copia `banco-preguntas/pcap.json` a `app/src/main/assets/` y léelo con la biblioteca estándar:

```kotlin
val texto = context.assets.open("pcap.json").bufferedReader().use { it.readText() }
val preguntas = org.json.JSONObject(texto).getJSONArray("questions")
for (i in 0 until preguntas.length()) {
    val q = preguntas.getJSONObject(i)
    val enunciado = q.getString("prompt")
    val codigo = q.optString("code", "")
    // q.getJSONArray("options"), q.getJSONArray("answer"), q.getString("explanation")
}
```

### Agregar preguntas

1. Agrega la pregunta a `pcap.json` con un `id` nuevo (`PCAP-<SEC>-<NNN>`).
2. Si es de «¿qué muestra este código?», añade `"verify": "output"`.
3. Ejecuta `python tools/validar_banco.py`: debe terminar con `0 errores`.
