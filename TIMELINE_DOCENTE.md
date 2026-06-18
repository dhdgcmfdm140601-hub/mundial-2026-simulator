# Storytelling docente - Live Coding Clase 5
## QA y Testing Potenciado por GenIA

Este archivo es tu guia de segundo monitor. El flujo correcto del live coding es:

```text
Cargar contexto -> ejecutar PROMPT_RTC_QA.md en modo plan -> ida y vuelta -> revisar plan -> pedir que aplique el plan -> ejecutar/ver evidencia
```

---

## Resumen ejecutivo

El live coding muestra como usar IA para hacer QA con control humano. No se trata de pedirle a la IA que "genere tests" directamente. Se trata de darle contexto, pedirle que trabaje en modo plan, dejar que haga preguntas, validar su propuesta y recien despues pedirle que aplique el plan.

La app ya funciona. El objetivo de la demo es construir evidencia de calidad sobre esa app:

- casos de prueba,
- tests automatizados,
- smoke test visual,
- QA Report,
- decision GO / NO-GO / GO con observaciones.

Frase guia:

> Hoy no vamos a usar IA para programar a ciegas. Vamos a usar IA como copiloto QA: primero contexto, despues plan, despues ejecucion.

Cadena de valor:

```text
QA.md + PROMPT_RTC_QA.md -> modo plan -> preguntas -> plan -> aprobacion docente -> aplicar plan -> evidencia
```

Lo que se va a probar en la demo:

- `POST /simulator/run`: que la simulacion devuelva una estructura valida.
- Campeon: que coincida con el ganador de la final.
- Grupos: que se distribuyan correctamente.
- Dashboard: que las metricas post-simulacion sean consistentes.
- Frontend: smoke test con Playwright sobre boton simular, campeon, dashboard y responsive.

---

## Setup antes de empezar

Terminal 1:

```powershell
cd "C:\Users\Leandro\Documents\Alkemy\Clase 5\live-coding"
python -m uvicorn main:app --reload --port 8000
```

Abrir:

```text
http://localhost:8000
http://localhost:8000/docs
```

Terminal 2, validacion previa:

```powershell
cd "C:\Users\Leandro\Documents\Alkemy\Clase 5\live-coding"
python -m pytest tests/ -v
```

Tabs recomendadas:

- UI del simulador.
- Swagger.
- Editor con `QA.md`.
- Editor con `PROMPT_RTC_QA.md`.
- Editor con `tests/`.
- Agente IA.

---

## Paso a paso del live coding

### 1. Apertura: que vamos a demostrar (2 min)

Mostrar la UI o Swagger.

Decir:

> En clases anteriores construimos y debuggeamos el simulador. Hoy cambiamos de rol: somos QA. La pregunta ya no es "como lo construyo", sino "como demuestro que esta listo para produccion".

> El punto clave: no le vamos a pedir a la IA que genere tests de una. Primero le vamos a dar contexto, despues la vamos a poner en modo plan, y recien cuando el plan nos cierre le vamos a pedir que lo aplique.

---

### 2. Cargar contexto en el agente (4 min)

Mostrar `QA.md`.

Decir:

> Este archivo es el contrato de calidad del proyecto. Le dice al agente cuales son los endpoints, las reglas de negocio, los quality gates, las herramientas permitidas y los IDs del DOM para pruebas frontend.

Accion:

1. Cargar `QA.md` en el agente.
2. Confirmar verbalmente:

> Ahora el agente entiende el sistema y entiende que no debe generar de inmediato.

---

### 3. Ejecutar PROMPT_RTC_QA.md en modo plan (6-8 min)

Mostrar `PROMPT_RTC_QA.md`.

Decir:

> Ahora no voy a improvisar un prompt. Voy a usar el prompt RTC de QA. Este prompt ordena el trabajo: rol, tarea y criterio. Lo importante es que lo voy a ejecutar en modo plan.

Accion:

Pegar completo el bloque `Prompt RTC principal` de `PROMPT_RTC_QA.md`.

Ese bloque ya trae la estructura RTC:

```text
[ROL]
Sos un QA Engineer Senior...

[TAREA]
Trabaja en modo plan...
Quiero testear POST /simulator/run...
No apliques el plan hasta que yo diga exactamente: "aplica el plan".

[CRITERIO]
El plan debe incluir...
```

Decir:

> Fijense que el prompt no pide codigo todavia. Es un RTC para planificar QA: define rol, tarea y criterio, pero bloquea la ejecucion hasta que yo apruebe el plan.

---

### 4. Ida y vuelta con el agente (5-7 min)

El agente deberia preguntar cosas como:

- si la DB arranca limpia,
- si debe revisar tests existentes,
- que nivel de cobertura se busca,
- si debe incluir smoke test frontend,
- si debe generar QA Report.

Respuestas sugeridas:

```text
La DB de test debe arrancar limpia.
Revisa los tests existentes para no duplicar cobertura.
Priorizo reglas de negocio y consistencia de metricas.
Inclui una propuesta de smoke test frontend, pero no la ejecutes todavia.
Quiero que el resultado termine en una seccion de QA Report.
```

Decir:

> Este ida y vuelta es parte del trabajo QA. El agente no esta ejecutando: esta reduciendo ambiguedad.

---

### 5. Revisar el plan antes de aplicarlo (4 min)

Cuando el agente muestre el plan, pausar.

Decir:

> Este es el momento mas importante del live coding. El agente ya propuso que va a hacer, pero todavia no hizo nada. Aca el humano decide si el plan sirve.

Checklist para revisar en voz alta:

- El plan cubre `POST /simulator/run`.
- Incluye campeon = ganador de final.
- Incluye grupos balanceados.
- Incluye dashboard consistente.
- No duplica tests existentes.
- Indica archivos a tocar o crear.
- Indica comando de ejecucion.
- Termina con QA Report.

Si hay que ajustar:

```text
Ajusta el plan: evita duplicar tests existentes y deja separado API tests de smoke test frontend.
No apliques todavia.
```

Si el plan esta bien:

```text
El plan esta aprobado. Ahora aplica el plan.
```

Decir:

> Recien ahora le doy permiso para aplicar. Ese es el control humano del proceso.

---

### 6. Ejecutar y mostrar evidencia (5 min)

Cuando el agente genere o proponga tests, ejecutar:

```powershell
python -m pytest tests/ -v
```

Decir:

> La evidencia no es la respuesta del agente. La evidencia es el resultado ejecutable: tests en verde, salida de consola y QA Report.

Cuando pase:

> Esto nos permite tomar una decision: GO, NO-GO o GO con observaciones.

---

### 7. Smoke test visual con Playwright (4 min)

Con `uvicorn` corriendo:

```powershell
python demo_playwright.py
```

Decir:

> pytest valida la API. Playwright valida el flujo visible: carga la app, encuentra el boton de simular, ejecuta la simulacion, valida campeon, dashboard y responsive.

Remate:

> Esto no reemplaza todos los tests, pero sirve como prueba de humo antes de una entrega.

---

### 8. Cierre y puente al ejercicio (2 min)

Decir:

> El patron que quiero que repitan es: cargo contexto, ejecuto el prompt RTC en modo plan, respondo preguntas, reviso el plan y recien despues digo "aplica el plan".

> No deleguen criterio. Usen la IA para acelerar el trabajo, pero mantengan control sobre el alcance, el plan y la decision final.

---

## Plan B si algo falla

### Puerto ocupado

```powershell
Get-NetTCPConnection -LocalPort 8000
Stop-Process -Id <PID> -Force
python -m uvicorn main:app --reload --port 8000
```

### El agente quiere aplicar sin plan

Responder:

```text
No apliques cambios todavia. Volve a modo plan:
1. haceme preguntas,
2. proponeme el plan,
3. espera mi aprobacion explicita.
```

### El plan no convence

Responder:

```text
No-GO por ahora. Ajusta el plan para cubrir estos criterios:
- no duplicar tests existentes,
- separar API tests de smoke test frontend,
- incluir QA Report,
- indicar comandos de ejecucion.
```

### Playwright falla

Mostrar manualmente:

- `http://localhost:8000`
- click en "Simular Mundial"
- campeon visible,
- dashboard visible.

Decir:

> Cuando falla un E2E, primero distinguimos si fallo el producto, el entorno o el test.

---

## Checklist rapido

Antes:

- [ ] `uvicorn` corriendo.
- [ ] UI abre.
- [ ] Swagger abre.
- [ ] `python -m pytest tests/ -v` pasa.
- [ ] `QA.md` listo para cargar.
- [ ] `PROMPT_RTC_QA.md` listo para ejecutar.

Durante:

- [ ] Explicar cambio de rol.
- [ ] Cargar `QA.md`.
- [ ] Ejecutar `PROMPT_RTC_QA.md` en modo plan.
- [ ] Responder preguntas del agente.
- [ ] Revisar plan.
- [ ] Decir "aplica el plan".
- [ ] Ejecutar tests.
- [ ] Mostrar QA Report / evidencia.
