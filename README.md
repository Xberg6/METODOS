# Laboratorio de rendimiento de un servidor

Simulador de Métodos Numéricos para estudiar qué carga concurrente maximiza la tasa estimada de solicitudes completadas. Abra `informe/Informe_Final.pdf` para leer el desarrollo. En **Modelo matemático**, «Cálculo guiado de la latencia» y «Cálculo guiado del rendimiento y del máximo» se sigue un ejemplo con números y unidades. «Cómo leer una iteración de bisección» explica la tabla que muestra el programa.

## Instalación y ejecución

El simulador se ejecuta en su computadora y se usa desde el navegador. **No necesita Docker, Codex, una cuenta de GitHub ni claves de acceso.** Se recomienda **Python 3.12** (versión usada para las pruebas en Windows); el mínimo es Python 3.11. Se necesita Internet para descargar el proyecto e instalar sus dependencias. Después, el simulador funciona localmente.

### Descargar el proyecto

1. En la página del repositorio de GitHub, pulse **Code → Download ZIP**.
2. Extraiga el ZIP completo en una carpeta. No abra el programa desde dentro del ZIP.
3. Instale Python desde [python.org](https://www.python.org/downloads/). En Windows, marque **Add Python to PATH** y vuelva a abrir la terminal después de instalarlo.

También puede descargarlo con Git (opcional si usa el ZIP).

```bash
git clone https://github.com/Xberg6/METODOS.git
cd METODOS
```

### Windows, con doble clic

1. Ejecute **Instalar_dependencias.cmd**. Espere el mensaje «Instalacion completada». Este paso crea `.entorno` e instala lo indicado en `requirements.txt`.
2. Ejecute **Abrir_simulador.cmd**. Mantenga abierta la ventana mientras usa el programa.
3. En el navegador, abra **http://127.0.0.1:8501** y pulse **Ejecutar análisis**.

En usos posteriores basta con abrir `Abrir_simulador.cmd`. Vuelva a ejecutar el instalador si actualiza el proyecto y cambian sus dependencias.

### Windows, desde PowerShell

Abra una terminal dentro de la carpeta que contiene `app.py`. Estos comandos no requieren activar el entorno ni cambiar la política de ejecución de PowerShell. Si su instalación reconoce `py` en lugar de `python`, use `py -3.12` en el primer comando.

```powershell
python -m venv .entorno
.\.entorno\Scripts\python.exe -m pip install -r requirements.txt
.\.entorno\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

### macOS o Linux

Desde la carpeta que contiene `app.py`, use Python 3.11 o posterior. Estas plataformas tienen comandos de instalación propios y todavía no se han probado en este proyecto.

```bash
python3 -m venv .entorno
.entorno/bin/python -m pip install -r requirements.txt
.entorno/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

En Ubuntu/Debian, si falla la creación del entorno porque falta `venv`, instale el paquete `python3-venv` correspondiente a su Python y repita el primer comando.

Abra **http://127.0.0.1:8501**. Pulse **Ejecutar análisis**. Para detener el servicio, vuelva a la terminal y pulse **Ctrl+C**. Cada compañero ejecuta su propia instancia en su computadora.

### Comprobar que funciona

En el caso principal, el resultado debe recomendar **71 solicitudes**, con **48.684 ms** y aproximadamente **1458.384685 solicitudes/s**. Al cargar y ejecutar el escenario **Monótono**, debe recomendar **100 solicitudes**, con **40 ms** y **2500 solicitudes/s**.

Para ejecutar pruebas o usar la consola, sustituya `python` en los siguientes comandos por `.\.entorno\Scripts\python.exe` en Windows o `.entorno/bin/python` en macOS/Linux. No es necesario volver a instalar dependencias en cada ejecución.

```text
python -m src.main --demo
python -m src.main --csv data/ejemplo_monotono_simulado.csv --dominio 20 100 --consulta 70 --tolerancia 0.000001 --max-iter 100 --h 1 0.1 0.01 --salida resultados_personales
python -m pytest -q --junitxml=validacion/pytest.xml
python validacion/verificar_entregables.py
```

`--demo` regenera los resultados de referencia en `resultados/`. La ejecución con `--salida resultados_personales` guarda un análisis en una carpeta separada. La auditoría revisa los documentos y resultados incluidos; no es necesaria para abrir el simulador.

### Problemas frecuentes

- **«python no se reconoce» o se abre Microsoft Store.** Instale Python desde el enlace anterior y abra una terminal nueva. En Windows también puede usar `py -3.12`.
- **«No module named streamlit» u otra dependencia.** Ejecute el instalador o el comando de instalación de `requirements.txt` y use siempre el Python de `.entorno` para iniciar la aplicación.
- **El navegador no abre la página.** Compruebe que la terminal sigue abierta y no muestra un error. Escriba `http://127.0.0.1:8501` en el navegador.
- **El puerto 8501 está ocupado.** Detenga una instancia anterior con Ctrl+C o añada `--server.port 8502` al comando de Streamlit y abra `http://127.0.0.1:8502`.
- **La instalación falla por conexión.** Revise el acceso a Internet y vuelva a ejecutar el instalador. Conserve el mensaje de error para identificar el paquete que falló.

## Qué se comparte en GitHub

Se incluyen el código, los datos de ejemplo, las pruebas, el informe, la presentación y los resultados verificados. `.gitignore` excluye entornos de Python, dependencias descargadas, archivos temporales, secretos locales, el ZIP de la entrega y los libros de referencia. Cada persona instala sus dependencias en su propio entorno. Los libros no son necesarios para ejecutar la aplicación; sus referencias bibliográficas están en el informe.

## Datos y modelo

**DATOS SIMULADOS / EJEMPLO DIDÁCTICO.** Para el escenario principal se eligieron las cargas 20, 50 y 100 y se generaron sus latencias con `20+0.12x+0.004x²`. Los 20 ms representan una base hipotética. Los términos lineal y cuadrático ilustran cómo podría aumentar la espera con la carga. Para el segundo caso se eligió `20+0.2x`. Las entradas fueron diseñadas para estudiar un máximo interior y un máximo en la frontera. La aplicación reconstruye cada curva exclusivamente desde la tabla de entrada.

`x` representa solicitudes promedio en el sistema. La latencia media `L` incluye todo el tiempo en él. Bajo régimen estable, la ley de Little da `R = x/(L/1000)` en solicitudes/s. Newton interpola `L`. La derivada de `R` tiene el mismo signo que `g=L−xL′` cuando `L>0`. Se buscan los puntos críticos en el dominio y se comparan con sus extremos. Se evalúan también todos los enteros admisibles. Para comprobar una capacidad real harían falta mediciones independientes y repetidas.

| Escenario sintético | Máximo de x en [20,100] | Entero elegido | Latencia del entero (ms) | Rendimiento del entero (solicitudes/s) |
| --- | ---: | ---: | ---: | ---: |
| Principal | 70.710679 | 71 | 48.684000 | 1458.384685 |
| Monótono | 100.000000 | 100 | 40.000000 | 2500.000000 |

La raíz analítica del principal es √5000 ≈ 70.710678119. Bisección calcula 70.710678697 con tolerancia 1e−6. Por eso sus valores pueden diferir en la última cifra mostrada. La fuente de los resultados es `resultados/metricas_validadas.json`.

## Probar la interfaz

1. Ejecute el caso principal. Revise `Datos y modelo`, `Métodos numéricos` y las gráficas.
2. Cambie la latencia 36 a 37.8 en la fila de concurrencia 50. Pulse Enter para confirmar la celda y vuelva a ejecutar. El entero debe cambiar de 71 a 79.
3. Seleccione **Monótono** y pulse **Cargar escenario**, o importe `data/ejemplo_monotono_simulado.csv` con **Usar CSV**. Ejecute y compruebe que el resultado es 100 sin iteraciones de bisección.
4. Pulse **Restablecer caso principal** y ejecute de nuevo. El resultado vuelve a 71. Pruebe el resumen JSON o el ZIP de tablas y figuras.

La tabla admite 3 a 8 nodos con concurrencias enteras distintas entre 0 y 1000000 y latencias positivas finitas. El CSV de entrada usa coma como separador, punto decimal y cabecera `concurrencia,latencia_ms`. El dominio y el punto de consulta se ajustan en la barra lateral. El dominio debe contener al menos un entero, quedar entre los nodos y abarcar como máximo 100001 enteros. La tolerancia controla el error absoluto en concurrencia. El programa limita la bisección a `max_iter` pasos. Los distintos `h` comprueban la derivada mediante diferencias centrales. Los resultados se invalidan al cambiar entradas. La verificación de positividad y puntos críticos usa aritmética de punto flotante, con limitaciones para datos mal condicionados.

## Archivos de la entrega

- `src/`, `app.py`, `data/`, `tests/`: fuentes, dos ejemplos y pruebas. La CLI funciona sin abrir la interfaz.
- `resultados/`: manifiesto numérico, CSV, resúmenes JSON y cuatro PNG por escenario. La carpeta de cada escenario incluye las huellas de los archivos generados.
- `informe/`: informe en Word, PDF y Markdown más trazabilidad bibliográfica. Para sustituir los nombres del equipo en el archivo editable, recuerden volver a exportarlo a PDF.
- `presentacion/`: PowerPoint editable, notas y guion para tres voces.
- `validacion/`: informes de pruebas y consistencia y capturas reales en `capturas/`.

## Regeneración de materiales académicos

Tras regenerar el manifiesto y ejecutar pytest con `--junitxml`, `python scripts/generar_informe.py` crea el DOCX y el Markdown. Para exportar el PDF en un equipo con LibreOffice, use `soffice --headless --convert-to pdf --outdir informe informe/Informe_Final.docx` o la exportación a PDF en Word. El generador de PowerPoint `scripts/generar_presentacion.mjs` usa Node y el runtime de Artifact Tool de autoría. Requiere las variables `ARTIFACT_MODULES`, `PRESENTATIONS_SKILL` y `ARTIFACT_PYTHON` descritas al comienzo del script. Su finalizador requiere una ruta final libre. La aplicación, las pruebas y el uso de los documentos ya exportados son independientes de ese runtime.

La auditoría vuelve a calcular ambos escenarios, comprueba CSV y JSON y extrae las principales cifras del informe y del PPTX. Una modificación manual de las cifras exige repetir el cotejo. `validacion/REPORTE_CONSISTENCIA.md` registra el alcance. El equipo completa sus nombres, revisa el contenido y graba el video con sus tres intervenciones antes de entregar.
