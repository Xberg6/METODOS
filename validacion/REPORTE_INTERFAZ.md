# Verificación de la interfaz local

El 3 de noviembre de 2026 se abrió Streamlit en un navegador de Windows en `127.0.0.1:8501`. Se recorrieron las pantallas con controles reales del navegador. Las capturas son imágenes de esta sesión y de la revisión inicial de las gráficas. Esta fue una verificación asistida. El ensayo de exposición por los estudiantes queda pendiente.

| Flujo | Observación |
| --- | --- |
| Ejecutar principal | Entero 71, tasa 1458.3847 solicitudes/s, latencia 48.6840 ms y máximo continuo 70.710679 |
| Abrir pestañas de métodos y gráficos | Tabla triangular, traza real, gráfica de latencia y curva de rendimiento visibles |
| Cargar el escenario monótono | Estado sin ejecutar después de la carga. Al calcular, extremo superior 100, 40 ms y 2500 solicitudes/s |
| Restaurar principal | Se recuperaron las cifras del primer caso. El selector actualizado refleja también el escenario restaurado |
| Descargar ZIP | El navegador confirmó la descarga del paquete de análisis. La prueba de integración abre el paquete generado y verifica su contenido |
| Entrada inválida | AppTest modifica el dominio a uno inválido, verifica el mensaje y la ausencia de tarjetas anteriores |
| CSV | AppTest carga los bytes del caso monótono con el componente de subida, usa el botón de importación, comprueba el entero 100 y después verifica el rechazo de un archivo con cabecera incorrecta. El ensayo del equipo puede incluir el selector de archivos de su propio navegador |

Se corrigió el recorte de cifras de la primera disposición con cuatro tarjetas, repartiendo las cifras en dos columnas y acortando el rótulo de la tasa. La evidencia se encuentra en `capturas/principal_resumen.png`, `capturas/monotono.png` y `capturas/principal.png`.
