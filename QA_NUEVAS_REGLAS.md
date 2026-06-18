# QA_NUEVAS_REGLAS.md — Protección contra duplicados
## Extension del QA.md original — Reglas de duplicados

---

## Reglas de negocio nuevas

| Regla | Descripción | Capa de protección |
|-------|-------------|-------------------|
| Código de equipo único | El código (3 chars) debe ser único — **409 si se repite** | BD (unique) + Service (validación pre-insert) |
| Nombre de equipo único | El nombre de equipo debe ser único — **409 si se repite** | BD (unique) + Service (validación pre-insert) |
| Nombre de equipo único en update | Actualizar a un nombre ya existente (de otro equipo) — **409** | Service (validación pre-update) |
| Código de equipo único en update | Actualizar a un código ya existente (de otro equipo) — **409** | Service (validación pre-update) |
| Jugador único por equipo | No puede haber dos jugadores con el mismo `name` + `team_id` — **409** | BD (unique compuesto) + Service (validación pre-insert) |
| Jugador único en update | Cambiar `name` o `team_id` a una combinación ya existente — **409** | Service (validación pre-update) |
| Mismo nombre, distinto equipo | Válido — permite "Luis Martínez" en Argentina y "Luis Martínez" en México | No hay restricción |
| IntegrityError global | Cualquier violación de constraint no capturada por validación previa devuelve **409** en vez de **500** | Exception handler global en FastAPI |

---

## Endpoints actualizados (contratos con duplicados)

### `POST /teams/`
- **Body:** `{ "name": string, "code": string (3 chars, único) }`
- **201:** equipo creado con `id`, `name`, `code`, `group_name: null`
- **409:** código duplicado **o** nombre duplicado
- **422:** datos inválidos

### `GET /teams/`
- **200:** lista de equipos. `group_name` es `null` hasta que se simula.

### `GET /teams/{id}`
- **200:** equipo con su lista de `players`
- **404:** equipo no existe

### `PUT /teams/{id}`
- **200:** equipo actualizado
- **404:** no existe
- **409:** código duplicado **o** nombre duplicado (en otro equipo)

### `DELETE /teams/{id}`
- **204:** eliminado
- **404:** no existe

### `POST /players/`
- **Body:** `{ "name": string, "position": "GK"|"DF"|"MF"|"FW", "team_id": int }`
- **201:** jugador creado
- **404:** equipo no existe
- **400:** posición inválida
- **409:** jugador con ese `name` + `team_id` ya existe

### `PUT /players/{id}`
- **200:** jugador actualizado
- **404:** jugador no existe
- **400:** posición inválida o equipo no existe
- **409:** la combinación `name` + `team_id` ya existe en otro jugador

---

## Capas de protección (defense in depth)

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI                           │
│  ┌───────────────────────────────────────────────┐   │
│  │ Exception handler global (IntegrityError)      │   │
│  │ → Captura cualquier violación de constraint    │   │
│  │ → Devuelve 409 (fallback ante race conditions) │   │
│  └───────────────────────────────────────────────┘   │
│                          │                             │
│  ┌───────────────────────────────────────────────┐   │
│  │ Services (validación pre-insert / pre-update)  │   │
│  │ → TeamService: get_by_code + get_by_name       │   │
│  │ → PlayerService: get_by_name_and_team          │   │
│  │ → HTTPException 409 si ya existe               │   │
│  └───────────────────────────────────────────────┘   │
│                          │                             │
│  ┌───────────────────────────────────────────────┐   │
│  │ SQLAlchemy Models (constraints a nivel BD)     │   │
│  │ → teams.name: unique=True                      │   │
│  │ → teams.code: unique=True                      │   │
│  │ → players(name + team_id): UniqueConstraint    │   │
│  └───────────────────────────────────────────────┘   │
│                          │                             │
│                    SQLite (worldcup.db)                │
└─────────────────────────────────────────────────────┘
```

---

## Tests nuevos (8 tests agregados)

### `tests/test_teams.py`

| Test | Lo que verifica |
|------|----------------|
| `test_create_team_duplicate_name` | Crear equipo con nombre existente → 409 |
| `test_update_team_duplicate_name` | Actualizar a un nombre ya ocupado por otro equipo → 409 |
| `test_update_team_duplicate_code_different_team` | Actualizar a un código ya ocupado por otro equipo → 409 |

### `tests/test_players.py`

| Test | Lo que verifica |
|------|----------------|
| `test_create_player_duplicate_in_same_team` | Mismo nombre + mismo equipo → 409 |
| `test_create_player_same_name_different_team` | Mismo nombre, distinto equipo → 201 ✅ (válido) |
| `test_update_player_duplicate_name_in_team` | Actualizar a un nombre ya ocupado en ese equipo → 409 |
| `test_update_player_move_to_team_with_duplicate` | Mover a otro equipo donde ya existe ese nombre → 409 |

---

## Estado actual de la cobertura de tests

```
tests/
├── conftest.py              ← fixture client con DB en memoria
├── test_teams.py            ← CRUD + duplicados (code + name) + update duplicados
├── test_players.py          ← CRUD + posiciones inválidas + equipo inexistente + duplicados (name + team_id)
├── test_simulator.py        ← simulación completa (happy path + reglas + edge cases)
├── test_dashboard.py        ← métricas post-simulación
├── test_frontend_smoke.py   ← smoke test con Playwright (requiere playwright instalado)
└── test_dashboard.py
```

---

## Comandos para correr los tests nuevos

```bash
# Todos los tests
python -m pytest tests/ -v

# Solo tests de equipos
python -m pytest tests/test_teams.py -v

# Solo tests de jugadores
python -m pytest tests/test_players.py -v

# Tests específicos
python -m pytest tests/test_teams.py::test_create_team_duplicate_name -v
python -m pytest tests/test_teams.py::test_update_team_duplicate_code_different_team -v
python -m pytest tests/test_players.py::test_create_player_duplicate_in_same_team -v
python -m pytest tests/test_players.py::test_create_player_same_name_different_team -v
python -m pytest tests/test_players.py::test_update_player_duplicate_name_in_team -v
python -m pytest tests/test_players.py::test_update_player_move_to_team_with_duplicate -v
```

---

## Datos sintéticos — nuevos escenarios de edge case

Agregar a los existentes:

- Equipo con nombre duplicado (ej: crear "Argentina" + "ARG", luego "Argentina" + "BRA")
- Jugador con mismo nombre en el mismo equipo (ej: "Lionel Messi" + team_id=1 dos veces)
- Jugador con mismo nombre en equipo diferente (válido — ej: "Luis Martínez" en ARG y "Luis Martínez" en MEX)
- Actualizar equipo a nombre ya existente
- Actualizar equipo a código ya existente
- Mover jugador a equipo donde ya existe otro con su mismo nombre

---

*Archivo complementario — Nuevas reglas de protección contra duplicados | Generado junto con QA.md original*
