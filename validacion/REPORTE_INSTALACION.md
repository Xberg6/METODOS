# Verificación de instalación para compartir el proyecto

Fecha de revisión: 4 de noviembre de 2026 (America/La_Paz).

Se creó un entorno virtual `.entorno` nuevo con Python 3.12.14 en Windows y se instalaron los paquetes exclusivamente desde `requirements.txt`. La instalación terminó correctamente. `pip check` no detectó dependencias incompatibles.

La suite completa se ejecutó con ese entorno y obtuvo **46 pruebas aprobadas en 37.93 segundos**, sin fallos. El XML de esta ejecución se conserva localmente en `tmp/pytest_instalacion_limpia.xml`; el XML de la validación original de la entrega sigue en `validacion/pytest.xml`.

También se exportaron los archivos preparados en el índice de Git a una carpeta independiente. Desde esa copia, la auditoría de entregables aprobó los escenarios, tablas, huellas de gráficos y cifras de los documentos. Los CSV conservan sus bytes originales mediante `.gitattributes`, para que Git no altere las huellas al descargar en otro sistema.

Dependencias principales instaladas durante esta comprobación:

```text
numpy==2.5.4
pandas==3.1.1
matplotlib==3.11.2
streamlit==1.66.1
pytest==9.2.0
python-docx==1.2.0
pypdf==6.21.4
reportlab==4.5.1
```

El README incluye descarga por ZIP o Git, instalación con doble clic en Windows, comandos de terminal, ejecución local, resultados esperados y problemas frecuentes. El instalador crea el entorno y comprueba la versión mínima de Python. El lanzador usa el entorno del proyecto sin depender de Codex ni de rutas personales.

Alcance: se verificó la instalación y ejecución de pruebas en Windows. Los comandos de macOS/Linux están documentados, pero esas plataformas no se probaron. Una instalación futura puede resolver otras versiones dentro de los rangos permitidos por `requirements.txt`.
