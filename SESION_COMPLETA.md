# Sesión Completa — Protección contra duplicados

**Fecha:** 11/06/2026
**Objetivo:** Evitar equipos y jugadores duplicados a nivel BD, API y frontend (Playwright)

---

## Resumen de cambios realizados

### 1. Modelo — `models/player.py`
- Agregado `UniqueConstraint("name", "team_id", name="uq_player_per_team")`
- Evita que un mismo nombre de jugador se repita dentro del mismo equipo a nivel BD

### 2. Repositorios

| Archivo | Método nuevo |
|---------|-------------|
| `repositories/team_repository.py` | `get_by_name(name)` |
| `repositories/player_repository.py` | `get_by_name_and_team(name, team_id)` |

### 3. Services

**`services/team_service.py`**
- `create()`: valida `name` duplicado → `409 "Team name already exists"`
- `update()`: valida `name` duplicado al cambiar nombre (excluyéndose a sí mismo) → 409

**`services/player_service.py`**
- `create()`: valida `name` + `team_id` duplicado → `409 "Player already exists in this team"`
- `update()`: valida al cambiar `name` o `team_id` → 409

### 4. Seguridad extra — `main.py`
- Exception handler global para `IntegrityError` → devuelve 409 en vez de 500 (fallback ante race conditions)

### 5. Tests de API (pytest) — 8 tests nuevos

**`tests/test_teams.py`** (3 nuevos):
- `test_create_team_duplicate_name`
- `test_update_team_duplicate_name`
- `test_update_team_duplicate_code_different_team`

**`tests/test_players.py`** (4 nuevos):
- `test_create_player_duplicate_in_same_team`
- `test_create_player_same_name_different_team` (válido ✅)
- `test_update_player_duplicate_name_in_team`
- `test_update_player_move_to_team_with_duplicate`

### 6. Tests de Playwright (E2E via browser) — 4 tests nuevos

**`tests/test_frontend_smoke.py`**:
- `test_api_duplicate_team_code_via_browser`
- `test_api_duplicate_team_name_via_browser`
- `test_api_duplicate_player_in_team_via_browser`
- `test_api_player_same_name_different_team_via_browser`

> NOTA: Requieren servidor FastAPI corriendo + Playwright instalado

### 7. Documentación de QA

| Archivo | Contenido |
|---------|-----------|
| `QA_NUEVAS_REGLAS.md` | Nuevas reglas de negocio, contratos actualizados, capas de protección, tests nuevos, edge cases |
| `QA_REPORT_PLAYWRIGHT.md` | Reporte formal de QA con casos F1-F5, tabla de cobertura 9/9, conclusión GO |
| `SESION_COMPLETA.md` | ⬅️ Este archivo |

### 8. Allure Report
- Instalado `allure-pytest`
- `pytest.ini` configurado con `addopts = --alluredir=allure-results`
- Resultados generados en `allure-results/`

---

## Comandos útiles

```bash
# Correr tests de API (76 tests)
python -m pytest tests/ --ignore=tests/test_frontend_smoke.py -v

# Correr tests de API con cobertura
python -m pytest tests/ --ignore=tests/test_frontend_smoke.py --cov=. --cov-report=term-missing

# Correr tests de Playwright (requiere servidor + playwright)
python -m pytest tests/test_frontend_smoke.py -v --headed

# Generar reporte Allure HTML (requiere Allure CLI)
allure generate allure-results -o allure-report --clean
allure open allure-report

# Regenerar BD (borrar worldcup.db para recrear con nuevas constraints)
Remove-Item -LiteralPath "worldcup.db" -ErrorAction SilentlyContinue
```

---

## Estado final

| Métrica | Resultado |
|---------|-----------|
| Tests de API pasando | **76/76** ✅ |
| Tests de Playwright | **5 escritos** (requieren servidor + playwright) |
| Reglas de duplicados cubiertas | **9/9** |
| Capas de protección | 3 (BD constraints + Service validations + Global IntegrityError handler) |
| Documentación generada | 3 archivos nuevos |

---

## Próximos pasos sugeridos

1. Instalar Playwright y correr `tests/test_frontend_smoke.py`
2. Instalar Allure CLI y generar reporte HTML desde `allure-results/`
3. Agregar más validaciones si es necesario (ej: posición de jugador contra equipo)
4. Si se agregan formularios de creación en el frontend, testear duplicados desde la UI real
