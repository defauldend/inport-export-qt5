# inport-export-qt5

Herramienta PyQt5 para importar, exportar y visualizar datos (CSV/Excel/SQLite/API).

Última actualización: 2025-10-17

## Novedades principales

- Importar y exportar CSV y Excel desde la UI.
- Operaciones con bases de datos SQLite a través de un diálogo (importar/ exportar tablas).
- Carga de datos desde APIs JSON (ej.: JSONPlaceholder) y normalización a DataFrame.
- Vista en tabla (QTableView) vinculada a pandas.DataFrame.
- Mensajería de éxito/error y validaciones básicas para operaciones de I/O.

## Estructura resumida

- `main.py` — Entrada principal y ventana (`MainWindow`) con botones y diálogo de BD.
- `pyqt_data_app/` — Subproyectos y versiones históricas.

## Requisitos

- Python 3.8+
- PyQt5
- pandas
- sqlalchemy
- requests

Instala dependencias (recomendado usar un virtualenv):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r pyqt_data_app/requirements.txt || pip install pyqt5 pandas sqlalchemy requests
```

Si `pyqt_data_app/requirements.txt` no existe o está incompleto instala manualmente:

```bash
pip install PyQt5 pandas sqlalchemy requests
```

## Ejecutar

```bash
python3 main.py
```

O ejecutar la versión incluida en `pyqt_data_app`:

```bash
python3 pyqt_data_app/main.py
```

## Uso rápido

- Botones para importar/exportar CSV y Excel.
- "Database Operations" abre un diálogo para especificar nombre de BD y tabla (SQLite por defecto).
- "Fetch from API" obtiene datos de un endpoint JSON de ejemplo y los muestra en la tabla.
- Menú Help → Novedades muestra el resumen de nuevas funcionalidades.

## Contribuir

1. Haz un fork y crea una rama con tu feature/bugfix.
2. Asegura que las dependencias están en un entorno virtual.
3. Añade tests cuando sea posible.

## Licencia

Añade la licencia que prefieras (por ejemplo MIT) en un archivo `LICENSE`.

---

Si quieres, puedo generar un `CHANGELOG.md` con entradas por versión o crear un archivo `requirements.txt` raíz.  # inport-export-qt5
