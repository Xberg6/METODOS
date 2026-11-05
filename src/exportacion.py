"""Lectura CSV, exportaciones y paquete descargable."""
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .modelo import Modelo
from .graficas import figuras,png


def leer_csv(origen):
    try:
        if hasattr(origen,'read'):
            contenido=origen.read()
            contenido=contenido.decode('utf-8-sig') if isinstance(contenido,bytes) else contenido
        else:
            contenido=Path(origen).read_text(encoding='utf-8-sig')
        lector=csv.DictReader(io.StringIO(contenido),strict=True)
        if lector.fieldnames != ['concurrencia','latencia_ms']:
            raise ValueError("El CSV debe tener las columnas concurrencia,latencia_ms, en ese orden.")
        filas=list(lector)
        if any(None in fila for fila in filas):
            raise ValueError('Cada fila del CSV debe contener exactamente dos valores.')
        return [float(f['concurrencia']) for f in filas],[float(f['latencia_ms']) for f in filas]
    except (OSError,UnicodeError,TypeError,KeyError,csv.Error,ValueError) as e:
        raise ValueError(f"No se pudo leer el CSV: {e}") from e


def csv_bytes(filas,campos=None):
    buf=io.StringIO(newline='')
    campos=campos or list(dict.fromkeys(k for f in filas for k in f))
    writer=csv.DictWriter(buf,fieldnames=campos)
    writer.writeheader()
    writer.writerows(filas)
    return buf.getvalue().encode('utf-8-sig')


def archivos_resultado(r):
    salida={'resumen.json':json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')}
    for clave in ['datos_entrada','candidatos_comparados','enteros','derivadas','sensibilidad','comparacion_tolerancias']:
        filas=[dict(**f,procedencia=r['etiqueta'],escenario=r['escenario']) for f in r.get(clave,[])]
        salida[f'{clave}.csv']=csv_bytes(filas)
    salida['iteraciones.csv']=csv_bytes([dict(**t,procedencia=r['etiqueta']) for t in r['iteraciones']],['raiz','iteracion','a','b','m','g_m','ancho','error','procedencia'])
    m=Modelo.construir([d['concurrencia'] for d in r['datos_entrada']],[d['latencia_ms'] for d in r['datos_entrada']])
    salida['curvas.csv']=csv_bytes([dict(x=float(x),latencia_ms=float(m.latencia(x)),rendimiento_rps=float(m.rendimiento(x)),procedencia=r['etiqueta']) for x in np.linspace(*r['dominio'],601)])
    for nombre,fig in figuras(r).items():
        salida[nombre+'.png']=png(fig)
        plt.close(fig)
    salida['trazabilidad_graficas.json']=json.dumps({'escenario':r['escenario'],'unidades':r['unidades'],'etiqueta':r['etiqueta'],'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in salida.items() if k.endswith(('.png','.csv'))}},indent=2).encode()
    return salida


def exportar(r,carpeta):
    carpeta=Path(carpeta)
    carpeta.mkdir(parents=True,exist_ok=True)
    for nombre,contenido in archivos_resultado(r).items():
        (carpeta/nombre).write_bytes(contenido)


def paquete_zip(r):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for nombre,contenido in archivos_resultado(r).items():
            z.writestr(nombre,contenido)
    return buf.getvalue()
