"""Bisección propia y aislamiento de raíces mediante la derivada."""
import math
import numpy as np


def biseccion(f, a: float, b: float, tolerancia=1e-6, max_iter=100):
    """Devuelve raíz y traza. La cota es el semiancho ANTES de actualizar."""
    if not all(math.isfinite(v) for v in (a, b, tolerancia)) or a >= b or tolerancia <= 0:
        raise ValueError("Intervalo o tolerancia de bisección inválidos.")
    if not isinstance(max_iter, (int, np.integer)) or isinstance(max_iter, bool) or max_iter < 1:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")
    fa, fb = float(f(a)), float(f(b))
    if not math.isfinite(fa) or not math.isfinite(fb):
        raise ValueError("La función no es finita en los extremos.")
    if fa == 0:
        return a, []
    if fb == 0:
        return b, []
    if np.signbit(fa) == np.signbit(fb):
        raise ValueError("Bisección requiere un cambio de signo o una raíz en un extremo.")
    traza = []
    for k in range(1, max_iter + 1):
        m = a + (b - a) / 2
        fm = float(f(m))
        if not math.isfinite(fm):
            raise ValueError("La función no es finita dentro del intervalo.")
        error = (b - a) / 2
        traza.append(dict(iteracion=k, a=a, b=b, m=m, g_m=fm, ancho=b-a, error=error))
        if fm == 0 or error <= tolerancia:
            return m, traza
        if m == a or m == b:
            raise ValueError("La tolerancia solicitada supera la precisión de punto flotante.")
        if np.signbit(fa) != np.signbit(fm):
            b, fb = m, fm
        else:
            a, fa = m, fm
    raise ValueError(f"No convergió en {max_iter} iteraciones; aumente el límite.")


def raices_en_intervalo(p, a=-1.0, b=1.0, tolerancia=1e-11):
    """Aísla raíces de un polinomio entre raíces de su derivada.

    Cada tramo es monótono. También comprueba raíces de multiplicidad par.
    Se usa sobre una coordenada normalizada; es un control numérico, no
    una certificación por aritmética de intervalos.
    """
    p = p.trim(tol=0)
    escala = max(float(np.sum(np.abs(p.coef))), 1e-300)
    p = p / escala
    p = p.trim(tol=2e-14)
    if p.degree() < 1:
        return []
    cortes = [a] + raices_en_intervalo(p.deriv(), a, b, tolerancia) + [b]
    raices = []
    for z in cortes:
        if abs(p(z)) <= 2e-12:
            raices.append(float(z))
    for izq, der in zip(cortes, cortes[1:]):
        if abs(p(izq)) > 2e-12 and abs(p(der)) > 2e-12 and np.signbit(p(izq)) != np.signbit(p(der)):
            r, _ = biseccion(p, izq, der, tolerancia, 100)
            raices.append(r)
    unicas = []
    for z in sorted(raices):
        if not unicas or z - unicas[-1] > 5 * tolerancia:
            unicas.append(z)
    return unicas
