"""Optimización, comparación discreta, error y sensibilidad."""
import math
import numpy as np
from .modelo import Modelo
from .biseccion import biseccion, raices_en_intervalo

ETIQUETA = "DATOS SIMULADOS / EJEMPLO DIDÁCTICO"


def analizar(x, y, dominio=None, tolerancia=1e-6, max_iter=100, escenario="personalizado", h=(1, .1, .01, .001), x_consulta=70):
    modelo = Modelo.construir(x, y)
    if dominio is None:
        dominio = [float(modelo.x[0]), float(modelo.x[-1])]
    if not math.isfinite(tolerancia) or not 1e-10 <= tolerancia <= .1:
        raise ValueError("La tolerancia debe estar entre 1e-10 y 0.1.")
    if not isinstance(max_iter, (int, np.integer)) or isinstance(max_iter, bool) or max_iter < 1:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")
    if not len(h) or len(h) > 20 or not np.isfinite(h).all() or np.any(np.asarray(h) <= 0):
        raise ValueError("Introduzca entre 1 y 20 pasos h positivos y finitos.")
    minimo = modelo.verificar_dominio(dominio)
    a, b = map(float, dominio)
    if not math.isfinite(x_consulta) or not a <= x_consulta <= b:
        raise ValueError("El punto de consulta debe pertenecer al dominio.")
    ta, tb = (a-modelo.centro)/modelo.escala, (b-modelo.centro)/modelo.escala
    pg = modelo.polinomio_g()
    crit_g = raices_en_intervalo(pg.deriv(), ta, tb)
    cortes = [a] + [modelo.centro + modelo.escala*z for z in crit_g if ta < z < tb] + [b]
    raices, traza = [], []
    umbral = 2e-12 * max(float(np.sum(abs(pg.coef))), 1)
    constante = np.max(np.abs(pg.coef)) < 1e-12 * max(np.max(abs(modelo.p.coef)), 1)
    if not constante:
        for z in cortes:
            if abs(modelo.g(z)) <= umbral and a < z < b:
                raices.append(float(z))
        for izq, der in zip(cortes, cortes[1:]):
            if abs(modelo.g(izq)) > umbral and abs(modelo.g(der)) > umbral and np.signbit(modelo.g(izq)) != np.signbit(modelo.g(der)):
                raiz, pasos = biseccion(modelo.g, izq, der, tolerancia, max_iter)
                raices.append(raiz)
                traza += [dict(raiz=len(raices), **paso) for paso in pasos]
    raices.sort()
    candidatos = []
    for z in [a, *raices, b]:
        delta = min(max(tolerancia*4, (b-a)*1e-5), (z-a)/2, (b-z)/2)
        signo = "frontera"
        if delta > 0:
            izquierda, derecha = float(modelo.g(z-delta)), float(modelo.g(z+delta))
            signo = "máximo local" if izquierda > 0 > derecha else "mínimo local" if izquierda < 0 < derecha else "estacionario sin cambio de signo"
        candidatos.append(dict(x=float(z), latencia_ms=float(modelo.latencia(z)), rendimiento_rps=float(modelo.rendimiento(z)), tipo=signo))
    mejor = max(candidatos, key=lambda c: c["rendimiento_rps"])
    enteros = np.arange(math.ceil(a), math.floor(b)+1, dtype=int)
    rendimientos = modelo.rendimiento(enteros)
    entero = int(enteros[np.argmax(rendimientos)])
    interior = a < mejor["x"] < b and not constante
    advertencias = [ETIQUETA, "La tasa es una estimación del modelo bajo régimen estable, no capacidad medida de un servidor.",
                   "Dominio restringido a los nodos. Las comprobaciones polinómicas usan punto flotante, no aritmética certificada."]
    if len(x) > 3:
        advertencias.append("Más de tres nodos: riesgo de oscilación y sensibilidad del polinomio interpolador.")
    if constante:
        mensaje = "Rendimiento constante: todos los puntos son óptimos; se elige el menor entero admisible."
    elif not raices:
        lugar = "superior" if mejor["x"] == b else "inferior"
        mensaje = f"Sin punto crítico interior; el máximo del modelo está en el extremo {lugar} del dominio"
    elif not interior:
        mensaje = "Hay puntos críticos interiores, pero el máximo global está en un extremo del dominio."
    else:
        mensaje = "Máximo interior verificado frente a los extremos y candidatos; enteros evaluados exhaustivamente."
    derivadas = []
    for paso in h:
        if a <= x_consulta-paso and x_consulta+paso <= b:
            numerica = float((modelo.rendimiento(x_consulta+paso)-modelo.rendimiento(x_consulta-paso))/(2*paso))
            exacta = float(1000*modelo.g(x_consulta)/modelo.latencia(x_consulta)**2)
            derivadas.append(dict(h=float(paso), x=x_consulta, analitica=exacta, central=numerica, error=abs(numerica-exacta)))
        else:
            advertencias.append(f"h={paso:g} omitido: diferencia central saldría del dominio.")
    vecino = sorted(set([math.floor(mejor['x']), math.ceil(mejor['x'])]) & set(enteros.tolist()))
    return dict(escenario=escenario, simulado=True, etiqueta=ETIQUETA,
                datos_entrada=[dict(concurrencia=int(z), latencia_ms=float(v)) for z,v in zip(modelo.x, modelo.y)],
                dominio=[a,b], unidades=dict(concurrencia="solicitudes concurrentes",latencia="ms",rendimiento="solicitudes/s"),
                metodo_interpolacion="Newton con diferencias divididas",coeficientes=modelo.tabla[0].tolist(),
                coeficientes_potencias=modelo.coeficientes_potencias(), formula=modelo.formula(),
                diferencias_divididas=[[None if np.isnan(v) else float(v) for v in fila] for fila in modelo.tabla],
                estado_biseccion="convergió" if traza else "No aplica (sin cambio de signo)", iteraciones=traza,
                optimo_continuo=mejor if interior else None, maximo_dominio=mejor, optimo_entero=entero,
                latencia_en_recomendacion_ms=float(modelo.latencia(entero)),rendimiento_en_recomendacion_rps=float(modelo.rendimiento(entero)),
                candidatos_comparados=candidatos, vecinos=[dict(x=int(z), rendimiento_rps=float(modelo.rendimiento(z))) for z in vecino],
                enteros=[dict(x=int(z), rendimiento_rps=float(r)) for z,r in zip(enteros,rendimientos)],
                minimo_latencia_ms=minimo,parametros=dict(max_iter=max_iter,h=list(h),x_consulta=x_consulta),
                consulta=dict(x=x_consulta,latencia_ms=float(modelo.latencia(x_consulta)),rendimiento_rps=float(modelo.rendimiento(x_consulta))),
                tolerancia=tolerancia, advertencias=advertencias,mensaje=mensaje,derivadas=derivadas)


def complementar(resultado):
    """Perturba cada latencia por separado. No cambia los datos originales."""
    x = [d['concurrencia'] for d in resultado['datos_entrada']]
    y = [d['latencia_ms'] for d in resultado['datos_entrada']]
    sensibilidad = []
    for i in range(len(x)):
        for cambio in (-.05,.05):
            yp = y.copy()
            yp[i] *= 1+cambio
            try:
                r = analizar(x,yp,resultado['dominio'],resultado['tolerancia'],resultado['parametros']['max_iter'],x_consulta=resultado['parametros']['x_consulta'])
                sensibilidad.append(dict(nodo=x[i], cambio_porcentaje=100*cambio, optimo_x=r['maximo_dominio']['x'], optimo_entero=r['optimo_entero'], rendimiento_rps=r['rendimiento_en_recomendacion_rps'], estado=r['mensaje']))
            except ValueError as e:
                sensibilidad.append(dict(nodo=x[i],cambio_porcentaje=100*cambio, estado=f"Inválido: {e}"))
    resultado['sensibilidad'] = sensibilidad
    # Referencia analítica independiente solo para el caso sintético conocido.
    es_principal = x == [20,50,100] and y == [24,36,72]
    comparaciones = []
    for tol in (1e-2,1e-4,1e-6):
        try:
            r = analizar(x,y,resultado['dominio'],tol,resultado['parametros']['max_iter'],x_consulta=resultado['parametros']['x_consulta'])
            comparaciones.append(dict(tolerancia=tol, iteraciones=len(r['iteraciones']), x=r['maximo_dominio']['x'], error_referencia=abs(r['maximo_dominio']['x']-math.sqrt(5000)) if es_principal and resultado['dominio'][0]<math.sqrt(5000)<resultado['dominio'][1] else None))
        except ValueError as e:
            comparaciones.append(dict(tolerancia=tol, estado=str(e)))
    resultado['comparacion_tolerancias'] = comparaciones
    return resultado
