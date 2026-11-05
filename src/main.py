"""CLI: python -m src.main --demo (ambos escenarios)."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from . import __version__
from .analisis import analizar,complementar
from .exportacion import leer_csv,exportar

RAIZ=Path(__file__).resolve().parents[1]


def ejecutar_demo(salida='resultados',tolerancia=1e-6,max_iter=100):
    resultados=[]
    for nombre,archivo in [('principal','ejemplo_simulado.csv'),('monotono','ejemplo_monotono_simulado.csv')]:
        x,y=leer_csv(RAIZ/'data'/archivo)
        r=complementar(analizar(x,y,tolerancia=tolerancia,max_iter=max_iter,escenario=nombre))
        exportar(r,Path(salida)/nombre)
        resultados.append(r)
    manifiesto=dict(version=__version__,fecha_utc=datetime.now(timezone.utc).isoformat(),escenarios=resultados)
    Path(salida,'metricas_validadas.json').write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    return manifiesto


def main():
    parser=argparse.ArgumentParser(description='Simulador de concurrencia y latencia con Newton y bisección.')
    grupo=parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--demo',action='store_true',help='Generar ambos escenarios sintéticos')
    grupo.add_argument('--csv',type=Path)
    parser.add_argument('--salida',type=Path,default=Path('resultados'))
    parser.add_argument('--dominio',nargs=2,type=float)
    parser.add_argument('--tolerancia',type=float,default=1e-6)
    parser.add_argument('--max-iter',type=int,default=100)
    parser.add_argument('--h',nargs='+',type=float,default=[1,.1,.01,.001])
    parser.add_argument('--consulta',type=float,default=70)
    args=parser.parse_args()
    try:
        if args.demo:
            if args.dominio or args.h != [1,.1,.01,.001] or args.consulta !=70:
                parser.error('--demo usa los parámetros de referencia; utilice --csv para personalizar dominio, h o consulta.')
            resultados=ejecutar_demo(args.salida,args.tolerancia,args.max_iter)['escenarios']
        else:
            x,y=leer_csv(args.csv)
            r=complementar(analizar(x,y,args.dominio,args.tolerancia,args.max_iter,args.csv.stem,args.h,args.consulta))
            exportar(r,args.salida)
            resultados=[r]
        for r in resultados:
            print(f"{r['escenario']}: entero={r['optimo_entero']}, R={r['rendimiento_en_recomendacion_rps']:.6f} solicitudes/s; {r['mensaje']}")
    except ValueError as e:
        parser.exit(2,f'Entrada inválida: {e}\n')


if __name__=='__main__':
    main()
