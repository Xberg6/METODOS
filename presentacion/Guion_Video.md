# Guion oral para tres integrantes

Duración prevista de 9:45. Los tiempos incluyen los cambios de pantalla. Ensayen con la aplicación ya iniciada, el navegador en el caso principal y la presentación en modo exposición. Cada persona debe poder explicar sus cálculos con sus propias palabras.

| Tiempo | Persona | Diapositivas o pantalla |
| --- | --- | --- |
| 0:00–2:30 | A | 1–2. Pregunta, unidades y tres datos sintéticos |
| 2:30–5:30 | B | 3–5. Newton, rendimiento y elección de 71 |
| 5:30–6:55 | C | 6–7. Bisección, cota y sensibilidad |
| 6:55–8:30 | C | 8 y aplicación local en ejecución |
| 8:30–9:45 | A, B y C | 9. Interpretación de los dos escenarios |

## Integrante A

«Queremos saber qué concurrencia conviene en el intervalo que estudiamos. Concurrencia es el promedio de solicitudes simultáneas en el sistema. Latencia es el tiempo medio total de respuesta. Rendimiento es cuántas solicitudes por segundo estima el modelo.» Señalar los ejes de la primera gráfica. «Al subir la carga cambia tanto el número de solicitudes en curso como el tiempo que cada una permanece en el sistema.»

Mostrar la tabla de la segunda diapositiva. «Por ejemplo, la fila de 50 significa 50 solicitudes en curso con 36 ms de latencia. Elegimos tres cargas y generamos las latencias con 20+0.12x+0.004x². Sus coeficientes son hipótesis didácticas. El programa recibe los pares y reconstruye la curva. Esto nos permite comprobar sus resultados con una respuesta conocida.» Dar paso a B con la pregunta de cuánto tardaría una solicitud para x=70.

## Integrante B

«Entre los primeros nodos la pendiente es (36−24)/(50−20)=0.4. Entre los dos últimos es 0.72. Su diferencia, dividida por 100−20, da 0.004. Los tres coeficientes de Newton construyen P₂(x). Sustituir 70 da 24+20+4=48 ms.» Señalar los tres términos de la ecuación.

«48 ms son 0.048 segundos. Si en promedio hay 70 solicitudes en el sistema en régimen estable, la relación de Little da 70/0.048=1458.3333 solicitudes/s. Ahora queremos la mejor carga. Como la latencia también cambia, derivamos el cociente. El signo de la derivada depende de g=L−xL′. Para este caso g vale 20−0.004x². En 70 es positiva y en 71 es negativa.» Mostrar dónde deja de crecer la curva.

«El máximo continuo está alrededor de 70.71. Para elegir un entero comparamos las tasas. Con 71, la latencia es 48.684 ms y el rendimiento aproximadamente 1458.3847 solicitudes/s. Es ligeramente mayor que con 70, y comprobamos los 81 enteros del intervalo.»

## Integrante C

«Bisección mantiene una raíz dentro de dos límites. Desde [20,100] el primer punto medio es 60. Su signo positivo deja la raíz entre 60 y 100. Luego el punto medio 80 da signo negativo y seguimos con [60,80]. El semiancho limita el error en la posición de la raíz.» Mostrar la tabla de tolerancias. «Comparamos el valor obtenido con √5000. Si cambiamos un dato, cambia el modelo. En la sensibilidad modificamos solo una latencia por vez.»

**Demostración de 95 segundos.** Abra el navegador y pulse **Restablecer caso principal → Ejecutar análisis**. Señale 71 y abra la pestaña de métodos. Muestre la fila inicial de Newton y la primera iteración. En la tabla de entrada cambie 36 a 37.8 en la fila x=50 y confirme la celda con Enter. Pulse **Ejecutar análisis** y señale la nueva recomendación de 79. Cargue el caso monótono, ejecute y lea el mensaje del extremo superior. Restablezca el principal y ejecute de nuevo. Muestre dónde se descarga el ZIP. Si falta tiempo, recorte las pausas entre acciones para conservar la demostración.

## Cierre de los tres

A recuerda el alcance de los datos. B resume cómo el polinomio de Newton proporciona la función que necesita el método de optimización. C compara el óptimo interior del primer escenario con el máximo en el límite del segundo y propone medir latencias reales, repetir ensayos y validar con datos reservados como paso futuro.

**Apoyos visuales disponibles.** Las curvas de latencia, rendimiento, convergencia y sensibilidad están en `resultados/principal/`. Las capturas auténticas de los dos escenarios están en `validacion/capturas/`. La exposición debe incluir la aplicación funcionando y las voces reales de los tres estudiantes. Pendiente del equipo: grabar, revisar el audio, verificar duración y subir el archivo solicitado por la plataforma.
