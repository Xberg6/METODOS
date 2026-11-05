"""Interpolación de Newton propia, sin ajuste de biblioteca."""
import numpy as np
from numpy.polynomial import Polynomial


def validar_datos(x, y):
    """Ordena explícitamente y valida los nodos de entrada."""
    try:
        x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    except (ValueError, TypeError) as exc:
        raise ValueError("La concurrencia y la latencia deben ser números.") from exc
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
        raise ValueError("Se requieren dos columnas de igual longitud.")
    if not 3 <= len(x) <= 8:
        raise ValueError("Use entre 3 y 8 observaciones; más nodos aumentan la oscilación.")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("Todos los datos deben ser finitos, sin celdas vacías.")
    if np.any(x < 0) or np.any(x != np.floor(x)) or np.any(x > 1e6):
        raise ValueError("La concurrencia debe ser entera, entre 0 y 1000000.")
    if np.any(y <= 0):
        raise ValueError("Todas las latencias deben ser positivas.")
    order = np.argsort(x)
    x, y = x[order], y[order]
    if np.any(np.diff(x) == 0):
        raise ValueError("La concurrencia no puede contener nodos duplicados.")
    return x, y


def diferencias_divididas(x, y):
    """Tabla triangular: fila i, columna j = f[x_i,...,x_(i+j)]."""
    x, y = validar_datos(x, y)
    n = len(x)
    tabla = np.full((n, n), np.nan)
    tabla[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            tabla[i, j] = (tabla[i + 1, j - 1] - tabla[i, j - 1]) / (x[i + j] - x[i])
    return x, tabla


def evaluar_newton(x, coeficientes, valor):
    """Horner anidado para la base de Newton, acepta vectores."""
    valor = np.asarray(valor, dtype=float)
    resultado = np.zeros_like(valor) + coeficientes[-1]
    for j in range(len(coeficientes) - 2, -1, -1):
        resultado = coeficientes[j] + (valor - x[j]) * resultado
    return resultado


def polinomio_newton(x, coeficientes):
    """Convierte la base de Newton a potencias sin ajustar los datos."""
    p = Polynomial([coeficientes[-1]])
    for j in range(len(coeficientes) - 2, -1, -1):
        p = p * Polynomial([-x[j], 1]) + coeficientes[j]
    return p
