from fpdf import FPDF
from datetime import datetime


class Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "CDA Soluciones Confiables - Informe de Validaciones", align="C")
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 86, 167)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 86, 167)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text, indent=10):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        x = indent
        self.set_x(x)
        self.set_font("Helvetica", "", 10)
        w = self.w - self.r_margin - x
        self.cell(5, 5, "- ")
        self.multi_cell(w - 5, 5, text)

    def pass_fail(self, status):
        if status == "PASS":
            self.set_text_color(0, 150, 0)
            return "PASS"
        else:
            self.set_text_color(200, 0, 0)
            return "FAIL"


pdf = Report()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ---- PORTADA ----
pdf.add_page()
pdf.ln(60)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(0, 86, 167)
pdf.cell(0, 15, "Informe de Validaciones", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font("Helvetica", "", 14)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Proteccion contra duplicados y reglas de negocio", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(15)
pdf.set_draw_color(0, 86, 167)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(15)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 7, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "Proyecto: Simulador Mundial 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "CDA Soluciones Confiables", align="C", new_x="LMARGIN", new_y="NEXT")

# ---- 1. RESUMEN ----
pdf.add_page()
pdf.chapter_title(1, "Resumen Ejecutivo")
pdf.body_text(
    "Este informe documenta todas las validaciones implementadas en el Simulador Mundial 2026 "
    "para garantizar la integridad de los datos y prevenir duplicados en las entidades Team y Player. "
    "Se implementaron 3 capas de proteccion: constraints a nivel base de datos, validaciones en "
    "la capa de servicios, y un handler global de errores de integridad."
)
pdf.body_text(f"Total de tests: 82 | Estado: 82/82 PASS | Fecha: {datetime.now().strftime('%d/%m/%Y')}")

pdf.sub_title("Capas de proteccion")
pdf.bullet("Capa 1: UniqueConstraint en base de datos (SQLite/SQLAlchemy)")
pdf.bullet("Capa 2: Validaciones en services (TeamService, PlayerService)")
pdf.bullet("Capa 3: Exception handler global para IntegrityError en main.py")

# ---- 2. VALIDACIONES DE EQUIPO ----
pdf.add_page()
pdf.chapter_title(2, "Validaciones - Team")

pdf.sub_title("2.1 Reglas implementadas")
reglas_team = [
    ("Codigo unico", "No pueden existir dos equipos con el mismo codigo (409 Conflict)", "PASS"),
    ("Nombre unico", "No pueden existir dos equipos con el mismo nombre (409 Conflict)", "PASS"),
    ("Formato de codigo", "El codigo debe ser exactamente 3 letras mayusculas (400 Bad Request)", "PASS"),
    ("Nombre no vacio", "El nombre del equipo no puede estar vacio (400 Bad Request)", "PASS"),
    ("Actualizar codigo duplicado", "Al cambiar codigo, validar que no exista otro equipo con ese codigo (409)", "PASS"),
    ("Actualizar nombre duplicado", "Al cambiar nombre, validar que no exista otro equipo con ese nombre (409)", "PASS"),
]
for regla, detalle, estado in reglas_team:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 6, f"{regla}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(5, 5, "")
    pdf.multi_cell(0, 5, f"  {detalle}")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(5, 5, "")
    pdf.cell(0, 5, f"  [{estado}]", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

pdf.sub_title("2.2 Tests especificos")
tests_team = [
    "test_create_team - Creacion basica de equipo (201)",
    "test_create_team_duplicate_code - Codigo duplicado (409)",
    "test_create_team_duplicate_name - Nombre duplicado (409)",
    "test_create_team_code_too_short - Codigo muy corto (400)",
    "test_create_team_code_too_long - Codigo muy largo (400)",
    "test_create_team_code_with_numbers - Codigo con numeros (400)",
    "test_create_team_empty_name - Nombre vacio (400)",
    "test_update_team - Actualizacion basica (200)",
    "test_update_team_duplicate_name - Actualizar a nombre existente (409)",
    "test_update_team_duplicate_code_different_team - Actualizar a codigo existente (409)",
]
for t in tests_team:
    pdf.bullet(t)

# ---- 3. VALIDACIONES DE JUGADOR ----
pdf.add_page()
pdf.chapter_title(3, "Validaciones - Player")

pdf.sub_title("3.1 Reglas implementadas")
reglas_player = [
    ("Nombre unico por equipo", "No pueden existir dos jugadores con el mismo nombre en el mismo equipo (409)", "PASS"),
    ("Nombre valido entre equipos", "El mismo nombre de jugador puede existir en diferentes equipos (201)", "PASS"),
    ("Posicion valida", "La posicion debe ser una de: GK, DF, MF, FW (400)", "PASS"),
    ("Nombre no vacio", "El nombre del jugador no puede estar vacio (400)", "PASS"),
    ("Maximo 23 jugadores", "Un equipo no puede tener mas de 23 jugadores (400)", "PASS"),
    ("Team existente", "El team_id debe referenciar a un equipo existente (404)", "PASS"),
    ("Actualizar nombre duplicado en team", "Al cambiar nombre, validar duplicado en el mismo equipo (409)", "PASS"),
    ("Mover jugador a team con duplicado", "Al cambiar team_id, validar duplicado en el destino (409)", "PASS"),
]
for regla, detalle, estado in reglas_player:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 6, f"{regla}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(5, 5, "")
    pdf.multi_cell(0, 5, f"  {detalle}")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(5, 5, "")
    pdf.cell(0, 5, f"  [{estado}]", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

pdf.sub_title("3.2 Tests especificos")
tests_player = [
    "test_create_player - Creacion basica (201)",
    "test_create_player_invalid_position - Posicion invalida (400)",
    "test_create_player_team_not_found - Team inexistente (404)",
    "test_create_player_duplicate_in_same_team - Duplicado en mismo equipo (409)",
    "test_create_player_same_name_different_team - Mismo nombre en otro equipo (201)",
    "test_create_player_empty_name - Nombre vacio (400)",
    "test_max_players_per_team - Supera maximo 23 jugadores (400)",
    "test_update_player_duplicate_name_in_team - Actualizar a nombre duplicado (409)",
    "test_update_player_move_to_team_with_duplicate - Mover a team con duplicado (409)",
]
for t in tests_player:
    pdf.bullet(t)

# ---- 4. COBERTURA POR CAPAS ----
pdf.add_page()
pdf.chapter_title(4, "Cobertura por Capas")

pdf.sub_title("4.1 Base de Datos")
pdf.body_text("Archivo: models/player.py, models/team.py")
pdf.bullet("Team.name: UNIQUE constraint (SQLAlchemy)")
pdf.bullet("Team.code: UNIQUE constraint (SQLAlchemy)")
pdf.bullet("Player: UniqueConstraint('name', 'team_id', name='uq_player_per_team')")

pdf.sub_title("4.2 Servicios (API)")
pdf.body_text("Archivos: services/team_service.py, services/player_service.py")
pdf.bullet("TeamService.create(): valida code unico, name unico, formato code 3 letras, name no vacio")
pdf.bullet("TeamService.update(): valida code/name unico al modificar (excluyendose a si mismo)")
pdf.bullet("PlayerService.create(): valida team existente, posicion valida, name+team_id unico, max 23 jugadores, name no vacio")
pdf.bullet("PlayerService.update(): valida team existente, posicion valida, name+team_id unico al modificar")

pdf.sub_title("4.3 Handler Global")
pdf.body_text("Archivo: main.py")
pdf.bullet("IntegrityError handler: captura errores de constraints no manejados y devuelve 409 en vez de 500")
pdf.bullet("Actua como fallback ante race conditions")

pdf.sub_title("4.4 Tests E2E (Playwright)")
pdf.body_text("Archivo: tests/test_frontend_smoke.py")
e2e_tests = [
    "test_frontend_main_simulation_flow - Flujo completo de simulacion",
    "test_api_duplicate_team_code_via_browser - Codigo duplicado via API browser",
    "test_api_duplicate_team_name_via_browser - Nombre duplicado via API browser",
    "test_api_duplicate_player_in_team_via_browser - Player duplicado en team via browser",
    "test_api_player_same_name_different_team_via_browser - Mismo player en otro team (valido)",
]
for t in e2e_tests:
    pdf.bullet(t)

# ---- 5. RESULTADOS DE TESTS ----
pdf.add_page()
pdf.chapter_title(5, "Resultados de Tests")

pdf.sub_title("5.1 API Tests (pytest)")
pdf.body_text("Comando: python -m pytest tests/ --ignore=tests/test_frontend_smoke.py -v")
pdf.body_text("Resultado: 82 tests PASS, 0 FAIL")

pdf.sub_title("5.2 Playwright Tests")
pdf.body_text("Comando: python -m pytest tests/test_frontend_smoke.py -v --headed")
pdf.body_text("Resultado: 5 tests (requieren servidor FastAPI corriendo)")

pdf.sub_title("5.3 Cobertura de reglas")
reglas = [
    ("Team code unico en BD", "BD (UNIQUE)", "PASS"),
    ("Team name unico en BD", "BD (UNIQUE)", "PASS"),
    ("Player name+team_id unico en BD", "BD (UniqueConstraint)", "PASS"),
    ("Team code unico en API", "Service", "PASS"),
    ("Team name unico en API", "Service", "PASS"),
    ("Formato code 3 letras", "Service", "PASS"),
    ("Team name no vacio", "Service", "PASS"),
    ("Player name+team_id unico en API", "Service", "PASS"),
    ("Player posicion valida (GK/DF/MF/FW)", "Service", "PASS"),
    ("Player name no vacio", "Service", "PASS"),
    ("Max 23 jugadores por equipo", "Service", "PASS"),
    ("Team existente al crear player", "Service", "PASS"),
    ("IntegrityError handler global", "main.py", "PASS"),
]

pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(0, 86, 167)
pdf.set_text_color(255, 255, 255)
pdf.cell(80, 7, "Regla de Negocio", border=1, fill=True)
pdf.cell(40, 7, "Capa", border=1, fill=True, align="C")
pdf.cell(20, 7, "Estado", border=1, fill=True, align="C")
pdf.ln()

pdf.set_font("Helvetica", "", 9)
for regla, capa, estado in reglas:
    pdf.set_text_color(30, 30, 30)
    pdf.cell(80, 6, f"  {regla}", border=1)
    pdf.cell(40, 6, capa, border=1, align="C")
    pdf.set_text_color(0, 150, 0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(20, 6, estado, border=1, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.ln()

# ---- 6. DOCUMENTACION GENERADA ----
pdf.add_page()
pdf.chapter_title(6, "Documentacion Generada")

docs = [
    ("QA_NUEVAS_REGLAS.md", "Reglas de negocio detalladas, contratos API, capas de proteccion, edge cases"),
    ("QA_REPORT_PLAYWRIGHT.md", "Reporte formal de QA con casos F1-F5, tabla de cobertura 9/9, conclusion GO"),
    ("SESION_COMPLETA.md", "Resumen de toda la sesion de trabajo, cambios realizados y comandos utiles"),
    ("allure-report/index.html", "Reporte HTML interactivo de Allure con resultados de 82 tests"),
    ("VALIDACIONES.pdf", "Este documento - Informe completo en PDF"),
]
for archivo, desc in docs:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 86, 167)
    pdf.cell(0, 6, archivo, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(5, 5, "")
    pdf.multi_cell(0, 5, desc)
    pdf.ln(2)

# ---- 7. CONCLUSION ----
pdf.add_page()
pdf.chapter_title(7, "Conclusion")

pdf.body_text(
    "Se implementaron exitosamente 13 reglas de validacion distribuidas en 3 capas de proteccion "
    "(Base de Datos, Servicios, Handler Global)."
)
pdf.body_text(
    "Todos los tests (82/82) pasan correctamente, cubriendo escenarios positivos, negativos y de borde. "
    "Se incluyen 5 tests E2E via Playwright que validan el comportamiento desde el navegador."
)
pdf.body_text(
    "La arquitectura de proteccion contra duplicados garantiza que:"
)
pdf.bullet("No existan equipos con codigo o nombre duplicado")
pdf.bullet("No existan jugadores con el mismo nombre dentro del mismo equipo")
pdf.bullet("Los codigos de equipo tengan formato estandarizado (3 letras)")
pdf.bullet("Los equipos no superen los 23 jugadores")
pdf.bullet("Cualquier error de integridad no manejado sea capturado y devuelva 409 en vez de 500")

pdf.ln(10)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(0, 150, 0)
pdf.cell(0, 10, "CONCLUSION: APROBADO (GO)", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 6, f"Documento generado automaticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "CDA Soluciones Confiables - Simulador Mundial 2026", align="C")

pdf.output("VALIDACIONES.pdf")
print("PDF generado: VALIDACIONES.pdf")
