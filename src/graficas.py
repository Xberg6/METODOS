"""Figuras reproducibles a partir del mismo resultado que usa la interfaz."""
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from .modelo import Modelo
from .analisis import ETIQUETA


def figuras(r):
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False, 'figure.dpi':120})
    m = Modelo.construir([d['concurrencia'] for d in r['datos_entrada']],[d['latencia_ms'] for d in r['datos_entrada']])
    x = np.linspace(*r['dominio'], 601)
    salida = {}
    for nombre, titulo, unidad, valores in [('latencia','Modelo de latencia','Latencia media (ms)',m.latencia(x)),('rendimiento','Rendimiento estimado','Rendimiento (solicitudes/s)',m.rendimiento(x))]:
        fig, ax = plt.subplots(figsize=(8,4.4), layout='constrained')
        ax.plot(x,valores,color='#087F8C',lw=2.5,label='Modelo interpolado')
        if nombre == 'latencia':
            ax.scatter(m.x,m.y,color='#172B4D',s=40,label='Nodos sintéticos',zorder=3)
        else:
            z=r['maximo_dominio']['x']
            ax.scatter([z],[m.rendimiento(z)],color='#D65A31',s=65,label=f'Máximo continuo {z:.4f}',zorder=4)
            ax.scatter([r['optimo_entero']],[r['rendimiento_en_recomendacion_rps']],marker='x',s=75,color='#172B4D',label=f"Entero {r['optimo_entero']}",zorder=5)
        ax.set(xlabel='Concurrencia (solicitudes en curso)',ylabel=unidad,title=titulo)
        ax.legend(fontsize=8)
        ax.grid(alpha=.18)
        fig.suptitle(f"{r['escenario']} · {ETIQUETA}",fontsize=8,color='#526277')
        salida[nombre]=fig
    fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
    if r['iteraciones']:
        for raiz in sorted(set(t['raiz'] for t in r['iteraciones'])):
            filas=[t for t in r['iteraciones'] if t['raiz']==raiz]
            ax.semilogy([t['iteracion'] for t in filas],[t['error'] for t in filas],color='#087F8C',marker='.',label=f'Raíz {raiz}')
        ax.axhline(r['tolerancia'],color='#D65A31',ls='--',label='Tolerancia')
        ax.legend()
    else:
        ax.text(.5,.5,'No aplica: sin bisección',ha='center',transform=ax.transAxes)
    ax.set(xlabel='Iteración',ylabel='Cota del error en concurrencia',title='Convergencia de bisección')
    ax.grid(alpha=.18)
    fig.suptitle(f"{r['escenario']} · {ETIQUETA}",fontsize=8)
    salida['convergencia']=fig
    fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
    filas=[s for s in r.get('sensibilidad',[]) if 'optimo_entero' in s]
    if filas:
        ax.barh([f"x={s['nodo']}  {s['cambio_porcentaje']:+.0f}%" for s in filas],[s['optimo_entero'] for s in filas],color='#087F8C')
        ax.axvline(r['optimo_entero'],ls='--',color='#D65A31',label='Caso base')
        ax.legend()
    ax.set(xlabel='Concurrencia entera recomendada',ylabel='Latencia perturbada por separado',title='Sensibilidad a cambios de ±5 %')
    fig.suptitle(f"{r['escenario']} · {ETIQUETA}",fontsize=8)
    salida['sensibilidad']=fig
    return salida


def png(fig):
    buffer=BytesIO()
    fig.savefig(buffer,format='png',dpi=160)
    return buffer.getvalue()
