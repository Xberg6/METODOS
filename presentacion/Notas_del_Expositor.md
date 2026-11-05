## Diapositiva 1

Integrante A · 0:00–0:45. Presentar la pregunta: qué concurrencia maximiza el indicador de nuestro escenario. Aclarar desde el inicio que se trata de un simulador matemático, sin ensayos de carga reales.

## Diapositiva 2

Integrante A · 0:45–2:30. Los tres nodos fueron diseñados a partir de L_sint=20+0.12x+0.004x². Los coeficientes son hipótesis didácticas, sin mediciones ni procedencia bibliográfica. El motor solo recibe esta tabla. Definir concurrencia como solicitudes promedio simultáneas. Dominio [20,100].

## Diapositiva 3

Integrante B · 2:30–3:35. Explicar el cociente de primer orden y luego la diferencia de pendientes. Mostrar los factores (x−20) y (x−50). La misma tabla reconstruye el polinomio, sin leer el generador. Fuentes: Chapra y Canale (2015), §18.1; Ascher y Greif (2011), §10.4; Kong et al. (2021), §17.5.

## Diapositiva 4

Integrante B · 3:35–4:35. Little relaciona el número promedio en el sistema con la tasa y el tiempo medio bajo hipótesis coherentes. Convertir ms a segundos da el factor 1000. Derivar el cociente para obtener g=L−xL′. En este ejemplo g=20−0.004x² y cambia de signo. Fuente: Whitt (2015), §1, https://www.columbia.edu/~ww2040/4615S15/LittlesLawNotes012715.pdf.

## Diapositiva 5

Integrante B · 4:35–5:30. El punto continuo no es una configuración entera. Se comparan suelo, techo y todos los enteros, además de los extremos. Las latencias y rendimientos destacados corresponden a la recomendación entera. La tasa máxima continua es ligeramente mayor. Cifras: resultados/metricas_validadas.json.

## Diapositiva 6

Integrante C · 5:30–6:20. La cota del error es el semiancho del intervalo antes de actualizar. Cada paso conserva el cambio de signo. La traza automática parte de [20,100], mientras la prueba matemática también usa [50,100]. Se comprueba la solución con sqrt(5000). Referencia: Ascher y Greif (2011), pp. 43–44.

## Diapositiva 7

Integrante C · 6:20–6:55. Cada barra corresponde a modificar una sola latencia en ±5 %. No son mediciones repetidas ni intervalos de confianza. Al modificar un dato se reconstruye el polinomio y se vuelve a verificar positividad, candidatos y enteros.

## Diapositiva 8

Integrante C · 6:55–8:30. Cambiar a la aplicación real. Cargar principal, ejecutar, explicar la tabla de Newton y las iteraciones. Modificar una latencia y recalcular. Cargar monótono: debe recomendar 100, con mensaje de ausencia de punto crítico interior. Restaurar principal y mostrar 71. Descargar el ZIP. Esta diapositiva usa una captura real y no reemplaza la demostración en ejecución.

## Diapositiva 9

Los tres · 8:30–9:45. A: recordar que son datos sintéticos y que el modelo ilustra una decisión de planificación. B: explicar que Newton produce L y bisección solo busca un candidato con hipótesis verificadas. C: contrastar principal con monótono y recordar que siempre se comparan fronteras y enteros. Para extrapolar al mundo real harían falta mediciones repetidas, incertidumbre y datos independientes.