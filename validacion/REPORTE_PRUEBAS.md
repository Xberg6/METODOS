# Pruebas del proyecto

Windows, Python 3.12, 3 de noviembre de 2026. La ejecución final de `python -m pytest -q --junitxml=validacion/pytest.xml` registró **46 aprobadas, 0 fallidas y 0 omitidas**. El XML contiene los nombres y tiempos de cada prueba. Se ejecutó el intérprete con las dependencias locales del proyecto.

La suite comprueba reconstrucción de Newton, condiciones de bisección, reducción del intervalo para tres tolerancias, derivadas, extremos, máximo interior, máximo de frontera, rango discreto, latencias inválidas entre nodos, varios puntos críticos, entradas malformadas, sensibilidad y restauración de estado. Las pruebas de integración generan los dos escenarios, reabren los archivos y comprueban el ZIP. Una prueba altera una cifra del resumen en una copia temporal, obtiene el fallo esperado y verifica que la restauración pasa. Otra prueba altera una curva. AppTest ejercita los controles de la aplicación sin depender de la pantalla.

Se ejecutó `python -m src.main --demo` y se generaron `resultados/principal/`, `resultados/monotono/` y el manifiesto JSON. Las pruebas de integración vuelven a ejecutar los dos ejemplos en un directorio temporal. El cotejo de archivos de entrega se registra aparte al ejecutar `python validacion/verificar_entregables.py`.

Incidencias corregidas: AppTest exigía resolver la ruta de `app.py` desde el directorio de pruebas. Se usó una ruta derivada del archivo de test. Se configuró el modo de producción de Streamlit para el runtime local. El navegador reveló recorte de las tarjetas en ventanas estrechas. Se corrigió la distribución y se volvió a abrir la aplicación. La versión actual también rechaza filas CSV con campos sobrantes. Las limitaciones de conexión local del entorno aislado exigieron ejecutar la prueba integral en Windows con acceso a localhost.

La revisión académica y la grabación del video corresponden al equipo. La inspección de la interfaz y su alcance figuran en `REPORTE_INTERFAZ.md`.

La suite final se ejecutó dos veces (46/46 en ambas) con una regeneración intermedia mediante `python -m src.main --demo --salida tmp/repeticion`. Se compararon los dos objetos de escenario y los 16 CSV de ambas ejecuciones. Los objetos coincidieron y cada CSV fue idéntico byte por byte. La prueba de interfaz también carga un CSV válido mediante el componente de subida, calcula 100 y después comprueba que importar un archivo con columnas equivocadas muestra «entrada inválida» y retira los resultados antiguos.
