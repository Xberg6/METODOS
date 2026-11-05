"""Modelo calculado exclusivamente a partir de la tabla de entrada."""
from dataclasses import dataclass
import numpy as np
from numpy.polynomial import Polynomial
from .interpolacion import validar_datos, diferencias_divididas, polinomio_newton, evaluar_newton
from .biseccion import raices_en_intervalo


@dataclass
class Modelo:
    x: np.ndarray
    y: np.ndarray
    tabla: np.ndarray
    p: Polynomial
    centro: float
    escala: float

    @classmethod
    def construir(cls, x, y):
        x, y = validar_datos(x, y)
        _, tabla = diferencias_divididas(x, y)
        centro, escala = float((x[0] + x[-1]) / 2), float((x[-1] - x[0]) / 2)
        # Construcción en la variable t=(x-centro)/escala para reducir cancelación.
        t = (x - centro) / escala
        c = y.copy()
        for j in range(1, len(x)):
            c[j:] = (c[j:] - c[j-1:-1]) / (t[j:] - t[:-j])
        p = polinomio_newton(t, c)
        if not np.all(np.isfinite(p.coef)):
            raise ValueError("El modelo excede la precisión numérica; revise las escalas.")
        if not np.allclose(p(t), y, rtol=1e-9, atol=1e-9):
            raise ValueError("Interpolación mal condicionada: reduzca nodos o revise los datos.")
        return cls(x, y, tabla, p, centro, escala)

    def latencia(self, x):
        return self.p((np.asarray(x) - self.centro) / self.escala)

    def derivada(self, x):
        return self.p.deriv()((np.asarray(x) - self.centro) / self.escala) / self.escala

    def g(self, x):
        return self.latencia(x) - np.asarray(x) * self.derivada(x)

    def rendimiento(self, x):
        latencia = self.latencia(x)
        if np.any(latencia <= 0):
            raise ValueError("El modelo tiene latencia no positiva.")
        r = 1000 * np.asarray(x) / latencia
        if not np.all(np.isfinite(r)):
            raise ValueError("El rendimiento excede la precisión numérica.")
        return r

    def polinomio_g(self):
        return self.p - Polynomial([self.centro / self.escala, 1]) * self.p.deriv()

    def verificar_dominio(self, dominio):
        a, b = map(float, dominio)
        if not np.isfinite([a, b]).all() or not self.x[0] <= a < b <= self.x[-1]:
            raise ValueError("Dominio inválido: debe estar dentro de los nodos, sin extrapolación.")
        if np.ceil(a) > np.floor(b):
            raise ValueError("El dominio no contiene ninguna concurrencia entera.")
        if np.floor(b) - np.ceil(a) > 100000:
            raise ValueError("Use un dominio de hasta 100001 enteros para comprobarlos todos.")
        ta, tb = (a-self.centro)/self.escala, (b-self.centro)/self.escala
        puntos = [ta, tb] + raices_en_intervalo(self.p.deriv(), ta, tb)
        minimo = float(min(self.p(t) for t in puntos))
        margen = 1e-10 * max(abs(self.y).max(), 1)
        if not np.isfinite(minimo) or minimo <= margen:
            raise ValueError("Latencia no positiva o demasiado próxima a cero dentro del dominio.")
        return minimo

    def coeficientes_potencias(self):
        return self.p(Polynomial([-self.centro / self.escala, 1 / self.escala])).coef.tolist()

    def formula(self):
        partes = [f"{v:+.10g}" + ("" if i == 0 else " x" if i == 1 else f" x^{i}")
                  for i, v in enumerate(self.coeficientes_potencias()) if abs(v) > 1e-12]
        return "L(x) = " + " ".join(partes).lstrip("+")
