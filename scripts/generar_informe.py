"""Construye Markdown y DOCX desde una misma estructura y métricas ejecutadas."""
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]


def contenido():
    m=json.loads((ROOT/'resultados/metricas_validadas.json').read_text(encoding='utf-8'))
    p,q=m['escenarios']
    suite=ET.parse(ROOT/'validacion/pytest.xml').getroot().find('testsuite')
    numero=suite.attrib['tests']
    bloques=[]
    def h(t): bloques.append(('h',t))
    def sub(t): bloques.append(('sub',t))
    def t(s): bloques.append(('p',s))
    def tabla(cab,filas): bloques.append(('tabla',(cab,filas)))
    def fig(ruta,leyenda): bloques.append(('fig',(ruta,leyenda)))
    def salto(): bloques.append(('salto',''))
    bloques.append(('titulo','Optimización del rendimiento de un servidor'))
    t('Interpolación de Newton y búsqueda del máximo mediante bisección')
    t('Proyecto final de Métodos Numéricos · Ingeniería de Sistemas · 3 de noviembre de 2026')
    t('Integrantes: __________________________________________________________')
    t('DATOS SIMULADOS / EJEMPLO DIDÁCTICO')
    h('Resumen')
    t(f"Se desarrolló un simulador local en Python para estudiar qué concurrencia maximiza una tasa estimada de solicitudes completadas. La interpolación de Newton reconstruye la latencia a partir de tres nodos sintéticos y la bisección resuelve la condición de derivada nula. En el escenario principal, el máximo continuo se aproxima en x={p['maximo_dominio']['x']:.6f}; la recomendación discreta es {p['optimo_entero']} solicitudes concurrentes, con latencia {p['latencia_en_recomendacion_ms']:.6f} ms y rendimiento {p['rendimiento_en_recomendacion_rps']:.6f} solicitudes/s. Un segundo escenario lineal alcanza su máximo en el límite superior, con {q['optimo_entero']} solicitudes concurrentes. La implementación compara extremos, candidatos interiores y todos los enteros admisibles. Los resultados ilustran un procedimiento numérico y no certifican la capacidad de un servidor real.")
    h('Introducción')
    t('La concurrencia expresa cuántas solicitudes permanecen simultáneamente en un sistema. Aumentarla puede aprovechar recursos disponibles, pero también elevar la latencia por esperas y contención. Por ello, una decisión de planificación debe considerar conjuntamente la cantidad de solicitudes en curso y su tiempo de respuesta. La pregunta de este proyecto es qué concurrencia maximiza el rendimiento estimado dentro de un dominio observado.')
    t('Se estudia un modelo matemático reproducible, sin generar tráfico HTTP, instalar un servidor de producción ni medir hardware. La aplicación permite editar datos, inspeccionar los procedimientos y exportar las evidencias del cálculo.')
    h('Justificación')
    t('Newton permite obtener una función continua a partir de datos discretos considerados exactos. Su representación mediante diferencias divididas facilita la construcción progresiva del polinomio y su evaluación (Chapra y Canale, 2015, §18.1; Ascher y Greif, 2011, §10.4; Kong et al., 2021, §17.5). La bisección se elige por su reducción controlada del intervalo cuando una función continua cambia de signo (Chapra y Canale, 2015, pp. 99–100). Ambos métodos se conectan: la interpolación define el modelo cuya condición de optimalidad se resuelve después.')
    salto()
    h('Modelo matemático')
    sub('Variables e hipótesis')
    t('x es el número promedio de solicitudes en el sistema; L(x) es su tiempo medio total de permanencia, en milisegundos; R(x) es una tasa estimada en solicitudes/s. Bajo régimen estable, la relación de Little conecta el número promedio en el sistema con la tasa y el tiempo medio (Whitt, 2015, §1). Al convertir milisegundos a segundos se obtiene x = R(x)L(x)/1000 y, por tanto, R(x)=1000x/L(x). Se supone una definición consistente de las solicitudes y de su permanencia total.')
    sub('Procedencia de los datos')
    t('Los nodos del caso principal fueron diseñados como ejemplo didáctico usando L_sint(x)=20+0.12x+0.004x². Los 20 ms son una base hipotética; el término lineal y el cuadrático representan incrementos ilustrativos de latencia. Ningún coeficiente procede de mediciones, registros ni bibliografía. El motor recibe solamente la tabla y reconstruye el polinomio: recuperar el generador verifica el algoritmo, pero no demuestra capacidad predictiva sobre datos reales.')
    tabla(['Concurrencia','Latencia principal (ms)','Latencia monótona (ms)'],[[str(a['concurrencia']),f"{a['latencia_ms']:g}",f"{b['latencia_ms']:g}"] for a,b in zip(p['datos_entrada'],q['datos_entrada'])])
    t('Tabla 1. DATOS SIMULADOS / EJEMPLO DIDÁCTICO. El dominio de ambos escenarios es [20,100]. El segundo conjunto procede del generador sintético L_sint(x)=20+0.2x.')
    sub('Interpolación y condición de optimalidad')
    t('Para nodos distintos, f[x_i]=y_i y f[x_i,…,x_j]=(f[x_(i+1),…,x_j]−f[x_i,…,x_(j−1)])/(x_j−x_i). El polinomio suma cada diferencia dividida multiplicada por los factores de Newton correspondientes (Kong et al., 2021, pp. 305–306).')
    t(f"Los coeficientes calculados son {p['coeficientes'][0]:g}, {p['coeficientes'][1]:g} y {p['coeficientes'][2]:g}. Por tanto, P₂(x)=24+0.4(x−20)+0.004(x−20)(x−50), equivalente a {p['formula']}. En el punto de consulta x=70 se obtiene L={p['consulta']['latencia_ms']:.6f} ms y R={p['consulta']['rendimiento_rps']:.6f} solicitudes/s.")
    t('Por la regla del cociente, R′(x)=1000[L(x)−xL′(x)]/L(x)². Si L(x)>0, el signo de la derivada coincide con g(x)=L(x)−xL′(x). Para el caso principal, g(x)=20−0.004x². Su raíz positiva de referencia es √5000, y el signo cambia de positivo a negativo. Para el caso monótono g(x)=20, de modo que no existe punto crítico interior.')
    salto()
    sub('Cálculo guiado de la latencia')
    t('Queremos estimar cuánto tarda una solicitud cuando hay 70 en curso. La tabla da datos para 20, 50 y 100. Como 70 está entre esos valores, podemos interpolar. Leer (50,36) significa que en ese escenario había un promedio de 50 solicitudes en curso y que cada una permanecía en el sistema una media de 36 ms.')
    tabla(['Símbolo','Qué representa','Valor en este ejemplo'],[['xᵢ','Concurrencia del nodo de índice i','x₀ = 20, x₁ = 50, x₂ = 100'],['yᵢ = L(xᵢ)','Latencia del nodo i, en ms','y₀ = 24, y₁ = 36, y₂ = 72'],['x','Concurrencia que se quiere evaluar','70 solicitudes en curso'],['P₂(x)','Latencia que estima el polinomio de grado ≤ 2','P₂(70) = 48 ms']])
    t('El subíndice i enumera las filas desde cero. El número 2 de P₂ indica el grado máximo del polinomio que se puede construir con tres nodos distintos. Para comprobar de dónde venía la primera fila sintética, se sustituye x=20 en el generador: 20 + 0.12 × 20 + 0.004 × 20² = 20 + 2.4 + 1.6 = 24 ms. Ese cálculo crea la entrada. Los pasos siguientes reconstruyen la curva usando los tres pares de la tabla.')
    sub('Paso 1. Calcular las pendientes entre nodos')
    t('Entre las dos primeras filas, la latencia aumenta 36−24 = 12 ms cuando la concurrencia aumenta 50−20 = 30. Su pendiente media es f[20,50] = 12/30 = 0.4 ms por solicitud adicional en curso. Entre las dos últimas filas, f[50,100] = (72−36)/(100−50) = 36/50 = 0.72. El segundo tramo es más empinado, así que una sola recta no reproduce las tres latencias.')
    sub('Paso 2. Incorporar el cambio de pendiente')
    t('La diferencia dividida de segundo orden usa los extremos de los tres nodos: f[20,50,100] = (0.72−0.4)/(100−20) = 0.32/80 = 0.004. Sus unidades son ms por unidad de concurrencia al cuadrado. El primer coeficiente de Newton es la latencia inicial, 24 ms. El segundo es la primera pendiente, 0.4. El tercero es 0.004, que corrige la curvatura.')
    sub('Paso 3. Estimar la latencia para 70 solicitudes')
    t('Newton da P₂(x) = 24 + 0.4(x−20) + 0.004(x−20)(x−50). El primer término arranca en 24 ms. El segundo suma la tendencia lineal. El tercero se anula en los dos primeros nodos y permite ajustar el tercero. Con x=70, P₂(70) = 24 + 0.4 × 50 + 0.004 × 50 × 20 = 24 + 20 + 4 = 48 ms. Se puede comprobar en el último nodo: P₂(100) = 24 + 32 + 16 = 72 ms.')
    salto()
    sub('Cálculo guiado del rendimiento y del máximo')
    t('1. Convertir tiempo en tasa. Con x=70 y L(70)=48 ms, el tiempo medio en segundos es W=48/1000=0.048 s. En régimen estable, x=R×W. Al despejar se obtiene R=70/0.048=1458.333333 solicitudes/s. La división usa el número medio en curso y el tiempo medio que ocupa cada solicitud. El 1000 viene de las unidades: un segundo contiene 1000 ms.')
    t('2. Preguntar si conviene aumentar la concurrencia. El rendimiento depende de x tanto en el numerador como en la latencia del denominador. Expandir el polinomio da L(x)=20+0.12x+0.004x². Su derivada, L′(x)=0.12+0.008x, estima cuánto aumenta la latencia por una unidad adicional de concurrencia. En x=70 vale 0.12+0.008×70=0.68 ms por unidad. La prima significa derivada respecto a x.')
    t('3. Determinar el sentido del cambio. La regla del cociente da R′(x)=1000g(x)/L(x)². En este caso g(x)=(20+0.12x+0.004x²)−x(0.12+0.008x)=20−0.004x², en ms. En 70, g(70)=48−70×0.68=0.4 ms. Por eso R′(70)=1000×0.4/48²=0.173611 solicitudes/s por unidad de concurrencia. La pendiente positiva indica que la curva aún sube ligeramente. En 71, g(71)=20−0.004×5041=−0.164 ms, así que ya baja.')
    t('4. Ubicar el máximo continuo. El cambio de positivo a negativo encierra un máximo entre 70 y 71. En este ejemplo podemos comprobar el método con álgebra: 20−0.004x²=0 implica x²=20/0.004=5000. La raíz del dominio es √5000≈70.710678. El símbolo x* designa esa ubicación del máximo. La bisección calcula su aproximación usando solo el modelo reconstruido y los signos. El apartado «Cómo leer una iteración de bisección» explica las columnas de la aplicación.')
    t(f"5. Convertir la solución en una decisión entera. Probar 70 da {p['vecinos'][0]['rendimiento_rps']:.6f} solicitudes/s. Para 71, L(71)=20+0.12×71+0.004×71²=20+8.52+20.164={p['latencia_en_recomendacion_ms']:.3f} ms. Por tanto R(71)=71000/{p['latencia_en_recomendacion_ms']:.3f}={p['rendimiento_en_recomendacion_rps']:.6f} solicitudes/s. La ganancia frente a 70 es {p['vecinos'][1]['rendimiento_rps']-p['vecinos'][0]['rendimiento_rps']:.6f} solicitudes/s. La aplicación compara los 81 enteros de 20 a 100, incluidos los extremos, y confirma que 71 es el mejor. La pequeña diferencia importa al interpretar la precisión práctica de la recomendación.")
    t(f"6. Repetir el razonamiento con el escenario lineal. Las pendientes son (30−24)/30=0.2 y (40−30)/50=0.2. Su diferencia es cero. Newton produce L(x)=24+0.2(x−20)=20+0.2x. Como L′(x)=0.2, g(x)=20+0.2x−0.2x=20 ms para todo x. La tasa crece en todo el intervalo. El mejor extremo es 100, con L(100)=20+0.2×100={q['latencia_en_recomendacion_ms']:.0f} ms y R(100)=1000×100/40={q['rendimiento_en_recomendacion_rps']:.0f} solicitudes/s. El número de iteraciones de bisección es cero.")
    salto()
    h('Implementación numérica')
    t('El código separa el núcleo numérico de Streamlit. interpolacion.py construye la tabla; modelo.py calcula L, L′, R y g; biseccion.py implementa la búsqueda; analisis.py compara candidatos y enteros; exportacion.py produce CSV, JSON, PNG y ZIP. app.py presenta entradas, resultados y mensajes. src.main proporciona una ejecución sin interacción.')
    sub('Procedimiento reproducible')
    t('1. Leer y ordenar los nodos. Rechazar duplicados, latencias no positivas, datos no finitos o concurrencias no enteras. 2. Construir Newton mediante diferencias divididas. 3. Derivar el polinomio calculado y comprobar la positividad de L en extremos y puntos estacionarios. 4. Aislar candidatos de g usando puntos críticos de g para subdividir el dominio. 5. Aplicar bisección solamente en intervalos con cambio de signo. 6. Comparar candidatos y fronteras. 7. Evaluar todos los enteros y exportar la recomendación junto con los parámetros.')
    t('La variable interna t=(x−centro)/escala normaliza los nodos para reducir cancelación. La forma en potencias de x se conserva para mostrarla. Se admiten entre 3 y 8 observaciones y hasta 100001 enteros en el dominio. Se bloquea la extrapolación. Con grados superiores se aíslan recursivamente raíces de derivadas, incluyendo posibles raíces tangentes; se emplean tolerancias relativas de punto flotante. Esta comprobación excede una malla finita, pero no constituye una certificación por aritmética de intervalos; casos muy mal condicionados o raíces casi coincidentes requieren otro análisis.')
    sub('Bisección y criterio de parada')
    t('Se verifica continuidad por la naturaleza polinómica y signos opuestos en los extremos. En cada paso se calcula m=a+(b−a)/2, se conserva el subintervalo que encierra la raíz y se registra la cota (b−a)/2 antes de actualizar. Se detiene cuando esa cota no supera la tolerancia absoluta en x, o cuando g(m)=0 exactamente. El agotamiento del máximo de iteraciones produce un error. Este control evita confundir un residuo pequeño con un error pequeño en la variable (Ascher y Greif, 2011, pp. 43–44; Kong et al., 2021, p. 327).')
    t(f"La ejecución principal usa tolerancia {p['tolerancia']:g} y límite {p['parametros']['max_iter']}. La búsqueda automática inicia en [20,100], donde g cambia de signo; por ello su traza difiere de la demostración manual que inicia en [50,100]. Los tests comprueban también ese segundo intervalo. Ambos conducen al mismo máximo dentro de la tolerancia.")
    sub('Validación auxiliar de la derivada')
    t('La expansión de Taylor de R(x+h) y R(x−h), al restarse y dividirse por 2h, produce D_hR(x)=[R(x+h)−R(x−h)]/(2h)=R′(x)+O(h²) si existen derivadas suficientes. Se contrasta esta aproximación con la derivada analítica del modelo. Reducir h disminuye inicialmente la truncación, pero puede amplificar el redondeo. Esta validación no es el método principal de optimización.')
    salto()
    sub('Cómo leer una iteración de bisección')
    t('a y b son los límites izquierdo y derecho del tramo que todavía puede contener la raíz. m=(a+b)/2 es su punto medio. En el dominio inicial, g(20)=18.4 ms y g(100)=−20 ms. Como los signos son opuestos y g es continua, el tramo encierra una raíz. Cada fila de la tabla usa el mismo cálculo, con límites nuevos.')
    tabla(['Paso','a','b','m','g(m) en ms','Cota en x'],[[str(v['iteracion']),f"{v['a']:g}",f"{v['b']:g}",f"{v['m']:g}",f"{v['g_m']:g}",f"{v['error']:g}"] for v in p['iteraciones'][:3]])
    t('Primera fila: m=(20+100)/2=60 y g(60)=20−0.004×60²=5.6. Como g(60)>0 y g(100)<0, se conserva [60,100]. En la segunda fila, m=80 y g(80)=−5.6, así que se conserva [60,80]. En la tercera, m=70 y g(70)=0.4, por lo que se pasa a [70,80]. La cota anterior a la actualización es (b−a)/2. En la primera fila esto vale (100−20)/2=40 unidades de concurrencia. Este es el mayor error posible al tomar el punto medio como estimación de la raíz en ese paso.')
    ult=p['iteraciones'][-1]
    t(f"En la fila {ult['iteracion']}, a={ult['a']:.9f}, b={ult['b']:.9f} y m={ult['m']:.9f}. La cota es {ult['error']:.3e}, inferior a la tolerancia 1e−6 (una millonésima de unidad de concurrencia). La distancia efectiva respecto a √5000 es {abs(ult['m']-math.sqrt(5000)):.3e}. La cota siempre disminuye al reducir el intervalo. El error efectivo de un punto medio aislado puede ser menor por casualidad aun usando una tolerancia más gruesa, como se ve en la tabla de convergencia.")
    sub('Cómo comprobar la derivada y leer el error')
    v=p['derivadas'][0]; por_x={u['x']:u['rendimiento_rps'] for u in p['enteros']}
    t(f"El paso h es la distancia que miramos a cada lado del punto de consulta. Para x=70 y h=1 se toman 69 y 71. Las tasas calculadas son R(69)={por_x[69]:.8f} y R(71)={por_x[71]:.8f} solicitudes/s. Su pendiente media es [R(71)−R(69)]/(2×1)={v['central']:.8f}. Frente a R′(70)={v['analitica']:.8f}, el error absoluto es |{v['central']:.8f}−{v['analitica']:.8f}|≈{v['error']:.8f}. Las barras verticales indican distancia sin signo. Estos resultados tienen unidades de solicitudes/s por unidad de concurrencia. La notación O(h²) indica que, al dividir h entre diez, se espera que la parte del error debida a la aproximación disminuya unas cien veces, mientras el redondeo sea pequeño.")
    t('La coordenada interna t=(x−centro)/escala sirve para evaluar el mismo polinomio con números más próximos a cero. Aquí centro=(20+100)/2=60, escala=(100−20)/2=40 y para x=70 resulta t=(70−60)/40=0.25. Al presentar los resultados, la aplicación vuelve a la unidad original de concurrencia.')
    salto()
    h('Resultados y discusión')
    sub('Máximo continuo y recomendación entera')
    tabla(['Escenario','Máximo x','Entero','L(entero) ms','R(entero) solicitudes/s'],[[r['escenario'],f"{r['maximo_dominio']['x']:.6f}",str(r['optimo_entero']),f"{r['latencia_en_recomendacion_ms']:.6f}",f"{r['rendimiento_en_recomendacion_rps']:.6f}"] for r in (p,q)])
    t('Tabla 2. DATOS SIMULADOS / EJEMPLO DIDÁCTICO. Valores calculados y redondeados a seis decimales. Máximo x incluye fronteras; en el escenario monótono el campo optimo_continuo del JSON es nulo porque no hay máximo interior.')
    t(f"En el principal, R(x*)={p['maximo_dominio']['rendimiento_rps']:.6f} solicitudes/s y L(x*)={p['maximo_dominio']['latencia_ms']:.6f} ms. Los extremos producen {p['candidatos_comparados'][0]['rendimiento_rps']:.6f} y {p['candidatos_comparados'][-1]['rendimiento_rps']:.6f} solicitudes/s. Se compararon {len(p['enteros'])} enteros; entre los vecinos, R(70)={p['vecinos'][0]['rendimiento_rps']:.6f} y R(71)={p['vecinos'][1]['rendimiento_rps']:.6f} solicitudes/s. Se recomienda 71 por su mayor tasa dentro del modelo, aunque la diferencia local es pequeña.")
    fig('resultados/principal/latencia.png','Figura 1. Latencia reconstruida y nodos sintéticos del escenario principal.')
    salto()
    sub('Forma de la función objetivo')
    fig('resultados/principal/rendimiento.png','Figura 2. El candidato interior supera los extremos; la recomendación entera se compara separadamente.')
    t('La tasa crece inicialmente porque aumenta la concurrencia más rápido que la latencia relativa. Después del máximo, la penalización de latencia domina. Esta interpretación corresponde a las funciones construidas, no a una medición de saturación real.')
    tabla(['Tolerancia','Iteraciones','Máximo x','Error contra √5000'],[[f"{t['tolerancia']:g}",str(t['iteraciones']),f"{t['x']:.6f}",f"{t['error_referencia']:.3e}"] for t in p['comparacion_tolerancias']])
    t(f"Tabla 3. Convergencia del caso principal con intervalo automático [20,100]. En la ejecución a {p['tolerancia']:g}, la cota final es {p['iteraciones'][-1]['error']:.3e} y el error frente a la raíz analítica es {abs(p['maximo_dominio']['x']-math.sqrt(5000)):.3e}. El control en x aporta una interpretación directa de la precisión.")
    salto()
    sub('Convergencia y diferencias centrales')
    fig('resultados/principal/convergencia.png','Figura 3. Reducción del semiancho en cada paso de bisección.')
    tabla(['h','Derivada analítica','Diferencia central','Error absoluto'],[[f"{d['h']:g}",f"{d['analitica']:.8f}",f"{d['central']:.8f}",f"{d['error']:.3e}"] for d in p['derivadas']])
    t('Tabla 4. Derivadas de R en x=70; unidades (solicitudes/s) por unidad de concurrencia. La reducción inicial del error concuerda con la fórmula central. La exactitud de interpolación en los nodos comprueba la implementación, no el error respecto de una población real desconocida.')
    salto()
    sub('Sensibilidad a las latencias de entrada')
    fig('resultados/principal/sensibilidad.png','Figura 4. Cada latencia se perturba por separado en ±5 % y se reconstruye el modelo.')
    tabla(['Nodo alterado','Cambio','Óptimo x','Entero','R(entero) solicitudes/s'],[[str(s['nodo']),f"{s['cambio_porcentaje']:+g}%",f"{s['optimo_x']:.4f}",str(s['optimo_entero']),f"{s['rendimiento_rps']:.4f}"] for s in p['sensibilidad']])
    t('Tabla 5. Escenarios sintéticos de sensibilidad independientes. Una variación pequeña de una entrada puede desplazar el entero recomendado. No se trata de un intervalo de confianza ni de una simulación aleatoria de ruido experimental; cada perturbación es determinista y mantiene el resto de los datos.')
    s=next(v for v in p['sensibilidad'] if v['nodo']==50 and v['cambio_porcentaje']==5)
    t(f"Ejemplo de lectura. En el nodo x=50, una variación de +5 % transforma su latencia de 36 a 36×(1+5/100)=37.8 ms. Se conservan (20,24) y (100,72). Al repetir Newton y la búsqueda con el nuevo nodo (50,37.8), el máximo continuo pasa a {s['optimo_x']:.4f} y el mejor entero a {s['optimo_entero']}, con {s['rendimiento_rps']:.4f} solicitudes/s. La gráfica muestra cómo cambia la decisión cuando cambia un dato de entrada.")
    salto()
    sub('Escenario independiente y evidencia de interfaz')
    t(f"Con el conjunto lineal se reconstruye {q['formula']}. La función g permanece positiva y no hay intervalo válido para bisección. La interfaz muestra: «{q['mensaje']}». El máximo se obtiene en x={q['maximo_dominio']['x']:.6f}, con L={q['latencia_en_recomendacion_ms']:.6f} ms y R={q['rendimiento_en_recomendacion_rps']:.6f} solicitudes/s. Volver al caso principal restaura sus resultados, lo que comprueba que el programa depende de los datos introducidos.")
    for nombre,leyenda in [('principal_resumen','Figura 5. Captura real de la aplicación local, escenario principal.'),('monotono','Figura 6. Captura real del escenario sin máximo interior.')]:
        ruta=f'validacion/capturas/{nombre}.png'
        if (ROOT/ruta).exists():
            fig(ruta,leyenda)
    salto()
    sub('Pruebas y limitaciones')
    t(f"La última ejecución registrada contiene {numero} pruebas automatizadas, {suite.attrib['failures']} fallos y {suite.attrib['errors']} errores. Se comprueban nodos, derivadas, cotas, extremos, todos los enteros, sensibilidad, entradas inválidas, varios candidatos y ausencia de raíz. AppTest verifica el cambio principal–monótono–principal y la eliminación de resultados obsoletos. La auditoría altera una cifra en una copia temporal, exige detectar la discrepancia y vuelve a comprobar los datos restaurados. El detalle de comandos y estados consta en validacion/REPORTE_PRUEBAS.md y REPORTE_CONSISTENCIA.md.")
    t('Las cifras internas se comparan con tolerancia absoluta de 1e-6. La presentación a seis decimales admite media millonésima por redondeo. Los PNG se generan con el mismo resultado que alimenta los CSV y se registran sus huellas SHA-256. El texto de DOCX, PDF y PPTX se extrae para cotejar cifras clave; las comprobaciones visuales se registran por separado porque extraer texto no prueba la legibilidad.')
    t('Las principales limitaciones son la naturaleza sintética de los datos, el escaso número de nodos, la falta de variabilidad experimental y la validez restringida al dominio. Interpolar datos experimentales ruidosos no garantiza una buena predicción; harían falta ensayos repetidos, incertidumbre y validación con datos independientes. El uso de punto flotante introduce límites adicionales, especialmente con polinomios de grado alto. No se estima un límite universal de concurrencia ni se recomienda configurar un servidor real a partir de este ejemplo.')
    h('Conclusiones')
    t(f"La integración de Newton y bisección permite transformar una tabla de latencias en una recomendación explicable. En el caso principal, el máximo interior calculado conduce a {p['optimo_entero']} solicitudes concurrentes; en el caso lineal, el mejor valor admisible es {q['optimo_entero']}. La comparación de extremos y la búsqueda discreta resultan indispensables para no confundir una raíz con un máximo global o una solución continua con una configuración entera.")
    t('La sensibilidad muestra que la recomendación depende de los datos y supuestos. La aplicación, sus pruebas y la trazabilidad documental permiten reproducir el procedimiento. La utilidad profesional del enfoque es orientar preguntas de planificación y pruebas de carga futuras; comprobar una capacidad real exige evidencia experimental que este proyecto no produce.')
    h('Bibliografía')
    for cita in ['Chapra, S. C., y Canale, R. P. (2015). Métodos numéricos para ingenieros (7.ª ed.). McGraw-Hill Interamericana.', 'Ascher, U. M., y Greif, C. (2011). A First Course in Numerical Methods. Society for Industrial and Applied Mathematics.', 'Kong, Q., Siauw, T., y Bayen, A. M. (2021). Python Programming and Numerical Methods: A Guide for Engineers and Scientists. Academic Press.', "Whitt, W. (2015, 27 de enero). Notes on Little’s Law: L = λW. IEOR 4615: Service Engineering. Columbia University. https://www.columbia.edu/~ww2040/4615S15/LittlesLawNotes012715.pdf"]:
        t(cita)
    salto()
    h('Anexos')
    sub('Listado organizado de fuentes')
    tabla(['Archivo','Responsabilidad'],[['src/interpolacion.py','Validación, diferencias divididas y evaluación de Newton'],['src/biseccion.py','Bisección y aislamiento recursivo de raíces'],['src/modelo.py','Latencia, derivadas y dominio'],['src/analisis.py','Máximo continuo, enteros, error y sensibilidad'],['src/graficas.py','Figuras con unidades y procedencia'],['src/exportacion.py','Lectura CSV y exportaciones JSON, CSV, PNG, ZIP'],['src/main.py','Interfaz de línea de comandos'],['app.py','Interfaz Streamlit'],['tests/','Pruebas matemáticas, integración e interfaz'],['validacion/verificar_entregables.py','Auditoría de resultados y documentos'],['scripts/generar_informe.py','Generador de este informe']])
    t('Las fuentes .py completas se entregan por separado en esas rutas. README.md contiene instalación y ejecución. Los libros originales son material de consulta y no se incluyen en el paquete de entrega.')
    sub('Reproducción y exposición')
    for cmd in ['python -m pip install -r requirements.txt','python -m pytest -q --junitxml=validacion/pytest.xml','python -m src.main --demo','python -m streamlit run app.py','python scripts/generar_informe.py','python validacion/verificar_entregables.py']:
        bloques.append(('codigo',cmd))
    t('Los tres integrantes deben revisar las cifras, completar los datos personales, ensayar la demostración y grabar sus intervenciones. El guion propone una exposición de 9 minutos y 45 segundos. La grabación y aprobación humanas permanecen pendientes hasta que el equipo las realice.')
    return bloques,m


def generar():
    bloques,m=contenido()
    salida=ROOT/'informe'
    salida.mkdir(exist_ok=True)
    doc=Document()
    sec=doc.sections[0]
    sec.page_height=Inches(11.69)
    sec.page_width=Inches(8.27)
    sec.top_margin=sec.bottom_margin=Inches(.65)
    sec.left_margin=sec.right_margin=Inches(.75)
    for nombre in ['Normal','Title','Heading 1','Heading 2','Caption']:
        estilo=doc.styles[nombre]
        estilo.font.name='Calibri'
        estilo.font.color.rgb=RGBColor(0,0,0)
    doc.styles['Normal'].font.size=Pt(11.5)
    doc.styles['Normal'].paragraph_format.space_after=Pt(7)
    doc.styles['Normal'].paragraph_format.line_spacing=1.08
    doc.styles['Title'].font.size=Pt(24)
    for borde in doc.styles['Title']._element.xpath('./w:pPr/w:pBdr'):
        borde.getparent().remove(borde)
    doc.styles['Heading 1'].font.size=Pt(16)
    doc.styles['Heading 2'].font.size=Pt(12)
    pie=sec.footer.paragraphs[0]
    pie.alignment=2
    pie.add_run('Métodos Numéricos · ')
    campo=OxmlElement('w:fldSimple'); campo.set(qn('w:instr'),'PAGE'); pie._p.append(campo)
    md=[]
    for tipo,valor in bloques:
        if tipo in ('titulo','h','sub'):
            if tipo=='titulo': doc.add_paragraph(valor,'Title'); md.append('# '+valor)
            else:
                doc.add_heading(valor,1 if tipo=='h' else 2)
                md.append(('## ' if tipo=='h' else '### ')+valor)
        elif tipo=='p':
            doc.add_paragraph(valor); md.append(valor)
        elif tipo=='codigo':
            p=doc.add_paragraph(); run=p.add_run(valor); run.font.name='Consolas'; run.font.size=Pt(9)
            md.append('`'+valor+'`')
        elif tipo=='salto':
            doc.add_page_break()
        elif tipo=='tabla':
            cab,filas=valor
            tabla=doc.add_table(rows=1,cols=len(cab)); tabla.style='Table Grid'
            for i,v in enumerate(cab): tabla.rows[0].cells[i].text=v
            for fila in filas:
                for c,v in zip(tabla.add_row().cells,fila): c.text=str(v)
            for ir,fila in enumerate(tabla.rows):
                for c in fila.cells:
                    tcpr=c._tc.get_or_add_tcPr()
                    shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'173B51' if ir==0 else 'F2F6F8' if ir%2==0 else 'FFFFFF'); tcpr.append(shd)
                    borders=OxmlElement('w:tcBorders')
                    for lado in ['top','left','bottom','right']:
                        borde=OxmlElement('w:'+lado); borde.set(qn('w:val'),'single'); borde.set(qn('w:sz'),'4'); borde.set(qn('w:color'),'D9D9D9'); borders.append(borde)
                    tcpr.append(borders)
                    for p in c.paragraphs:
                        p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(4)
                        for run in p.runs:
                            run.font.size=Pt(9.5)
                            if ir==0: run.bold=True; run.font.color.rgb=RGBColor(255,255,255)
            trpr=tabla.rows[0]._tr.get_or_add_trPr(); repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
            md.append('| '+' | '.join(cab)+' |\n| '+' | '.join(['---']*len(cab))+' |\n'+'\n'.join('| '+' | '.join(map(str,f))+' |' for f in filas))
        elif tipo=='fig':
            ruta,leyenda=valor
            ancho=5.1 if 'capturas' in ruta else 6.45
            if 'capturas' in ruta and 'monotono' in ruta: doc.add_page_break()
            doc.add_picture(str(ROOT/ruta),width=Inches(ancho))
            doc.add_paragraph(leyenda,'Caption')
            md.append(f'![{leyenda}](../{ruta})\n\n{leyenda}')
    doc.save(salida/'Informe_Final.docx')
    (salida/'Informe_Final.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
    print('Generados Informe_Final.md e Informe_Final.docx a partir del manifiesto.')


if __name__=='__main__':
    generar()
