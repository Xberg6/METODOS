import math
import numpy as np
import pytest
from numpy.polynomial import Polynomial
from src.interpolacion import diferencias_divididas,evaluar_newton,validar_datos
from src.biseccion import biseccion,raices_en_intervalo
from src.modelo import Modelo
from src.analisis import analizar,complementar

X,Y=[20,50,100],[24,36,72]


def test_newton_y_modelo():
    x,t=diferencias_divididas(X,Y)
    assert t[0]==pytest.approx([24,.4,.004])
    assert evaluar_newton(x,t[0],X)==pytest.approx(Y,abs=1e-9)
    assert evaluar_newton(x,t[0],70)==pytest.approx(48)
    m=Modelo.construir(X,Y)
    assert m.coeficientes_potencias()==pytest.approx([20,.12,.004])
    assert m.g(50)==pytest.approx(10)
    assert m.g(100)==pytest.approx(-20)


@pytest.mark.parametrize('tol',[1e-2,1e-4,1e-6])
def test_biseccion_cotas(tol):
    m=Modelo.construir(X,Y)
    raiz,traza=biseccion(m.g,50,100,tol)
    assert abs(raiz-math.sqrt(5000))<=traza[-1]['error']<=tol
    for i,paso in enumerate(traza):
        assert m.g(paso['a'])*m.g(paso['b'])<=0
        assert paso['a']<=math.sqrt(5000)<=paso['b']
        if i:
            assert paso['ancho']==pytest.approx(traza[i-1]['ancho']/2)


@pytest.mark.parametrize('args',[(lambda x:x*x+1,-1,1),(lambda x:x,-1,1,-1),(lambda x:x,2,1),(lambda x:x-.1,-1,1,1e-10,1),(lambda x:float('nan'),0,1)])
def test_biseccion_rechaza(args):
    with pytest.raises(ValueError):
        biseccion(*args)


def test_raiz_extremo_y_par():
    assert biseccion(lambda x:x,0,1)==(0,[])
    p=Polynomial.fromroots([-.6,.2,.2,.8])
    assert raices_en_intervalo(p)==pytest.approx([-.6,.2,.8],abs=1e-8)


@pytest.mark.parametrize('x,y',[([1,1,3],[1,2,3]),([1,2],[1,2]),([1,2,3],[1,-2,3]),([1,2,3],[1,0,3]),([1,2.5,3],[1,2,3]),([-1,2,3],[1,2,3]),([1,2,3],[1,float('inf'),3]),([1,2,3],[1,float('nan'),3]),([1,2,3],[1,2]),(list(range(9)),[1]*9)])
def test_datos_invalidos(x,y):
    with pytest.raises(ValueError):
        validar_datos(x,y)


def test_orden_explicito():
    assert Modelo.construir([100,20,50],[72,24,36]).latencia(70)==pytest.approx(48)


def test_optimo_y_enteros():
    r=analizar(X,Y)
    assert r['maximo_dominio']['x']==pytest.approx(math.sqrt(5000),abs=1e-6)
    assert r['optimo_entero']==71
    assert r['rendimiento_en_recomendacion_rps']==pytest.approx(71000/(20+.12*71+.004*71**2))
    assert r['maximo_dominio']['rendimiento_rps']>=max(c['rendimiento_rps'] for c in r['candidatos_comparados'])
    assert r['rendimiento_en_recomendacion_rps']==max(e['rendimiento_rps'] for e in r['enteros'])
    assert r['optimo_continuo']['tipo']=='máximo local'
    m=Modelo.construir(X,Y)
    assert r['maximo_dominio']['rendimiento_rps']>=max(m.rendimiento(np.linspace(20,100,10001)))-1e-9
    assert abs(r['derivadas'][-1]['error'])<1e-7


def test_monotono_y_restauracion():
    a=analizar(X,Y)
    b=analizar(X,[24,30,40])
    assert b['optimo_continuo'] is None
    assert b['optimo_entero']==100
    assert b['rendimiento_en_recomendacion_rps']==pytest.approx(2500)
    assert not b['iteraciones']
    assert analizar(X,Y)==a


def test_constante():
    r=analizar([1,2,3],[2,4,6],x_consulta=2)
    assert r['optimo_entero']==1
    assert 'constante' in r['mensaje']


@pytest.mark.parametrize('dominio',[[0,100],[100,20],[20,float('nan')],[50.1,50.9]])
def test_dominios(dominio):
    with pytest.raises(ValueError):
        analizar(X,Y,dominio)


def test_latencia_negativa_entre_nodos():
    # Todos los nodos positivos, mínimo negativo cerca de x=0.5.
    with pytest.raises(ValueError,match='Latencia'):
        analizar([0,1,3],[.1,.1,6.1],x_consulta=1)


def test_varios_candidatos():
    # L=10 + (x-4)^2 (x-8)^2, positiva en todo el dominio.
    x=np.arange(1,10,2)
    y=10+(x-4)**2*(x-8)**2
    r=analizar(x,y,x_consulta=5)
    assert len(r['candidatos_comparados'])>=5
    m=Modelo.construir(x,y)
    assert r['maximo_dominio']['rendimiento_rps']>=max(m.rendimiento(np.linspace(1,9,20001)))-1e-5
    assert r['optimo_entero']==8


def test_sensibilidad_y_error():
    r=complementar(analizar(X,Y))
    assert len(r['sensibilidad'])==6
    assert all('optimo_entero' in s for s in r['sensibilidad'])
    assert r['comparacion_tolerancias'][-1]['error_referencia']<=1e-6
    assert r['comparacion_tolerancias'][0]['iteraciones']<r['comparacion_tolerancias'][-1]['iteraciones']


@pytest.mark.parametrize('kwargs',[{'max_iter':1},{'h':[0]},{'h':[float('nan')]},{'x_consulta':120},{'tolerancia':0}])
def test_parametros(kwargs):
    with pytest.raises(ValueError):
        analizar(X,Y,**kwargs)
