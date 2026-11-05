"""Audita sin sobrescribir los archivos que comprueba."""
import csv
import hashlib
import io
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.analisis import analizar,complementar
from src.exportacion import leer_csv
from src.modelo import Modelo


def comparar(actual,esperado,ruta='raíz',tol=1e-6):
    if isinstance(esperado,dict):
        if not isinstance(actual,dict) or actual.keys()!=esperado.keys():
            raise AssertionError(f'{ruta}: campos diferentes')
        for k,v in esperado.items():
            comparar(actual[k],v,f'{ruta}.{k}',tol)
    elif isinstance(esperado,list):
        if len(actual)!=len(esperado):
            raise AssertionError(f'{ruta}: longitud distinta')
        for i,v in enumerate(esperado):
            comparar(actual[i],v,f'{ruta}[{i}]',tol)
    elif isinstance(esperado,(int,float)) and not isinstance(esperado,bool):
        if not isinstance(actual,(int,float)) or not math.isfinite(actual) or abs(actual-esperado)>tol:
            raise AssertionError(f'{ruta}: {actual} != {esperado} (tolerancia {tol})')
    elif actual!=esperado:
        raise AssertionError(f'{ruta}: valor diferente')


def auditar_resultados(base):
    base=Path(base)
    manifiesto=json.loads((base/'metricas_validadas.json').read_text(encoding='utf-8'))
    if [r['escenario'] for r in manifiesto['escenarios']]!=['principal','monotono']:
        raise AssertionError('Faltan escenarios o están duplicados')
    lineas=[]
    for r in manifiesto['escenarios']:
        nombre=r['escenario']
        archivo='ejemplo_simulado.csv' if nombre=='principal' else 'ejemplo_monotono_simulado.csv'
        x,y=leer_csv(ROOT/'data'/archivo)
        fresco=complementar(analizar(x,y,r['dominio'],r['tolerancia'],r['parametros']['max_iter'],nombre,r['parametros']['h'],r['parametros']['x_consulta']))
        comparar(r,fresco,nombre)
        # Comprobación independiente con las expresiones generadoras conocidas.
        if nombre=='principal':
            latencia_ref=lambda z: 20+.12*z+.004*z*z
            raiz_ref=math.sqrt(5000)
            comparar(r['maximo_dominio']['x'],raiz_ref,'raíz analítica',r['tolerancia'])
            comparar(r['coeficientes'],[24,.4,.004],'diferencias divididas')
            for dato in r['iteraciones']:
                if not dato['a']<=raiz_ref<=dato['b']:
                    raise AssertionError('Una fila de bisección perdió la raíz de referencia')
                comparar(dato['g_m'],20-.004*dato['m']**2,'g(m)')
                comparar(dato['error'],(dato['b']-dato['a'])/2,'cota del punto medio')
        else:
            latencia_ref=lambda z: 20+.2*z
            comparar(r['iteraciones'],[],'bisección monótona')
            comparar(r['optimo_continuo'],None,'interior monótono')
        for z,ms in zip(x,y):
            comparar(latencia_ref(z),ms,'dato sintético de referencia')
        enteros=range(math.ceil(r['dominio'][0]),math.floor(r['dominio'][1])+1)
        elegido=max(enteros,key=lambda z:1000*z/latencia_ref(z))
        comparar(r['optimo_entero'],elegido,'máximo entero independiente')
        comparar(r['latencia_en_recomendacion_ms'],latencia_ref(elegido),'latencia del entero')
        comparar(r['rendimiento_en_recomendacion_rps'],1000*elegido/latencia_ref(elegido),'tasa del entero')
        carpeta=base/nombre
        comparar(json.loads((carpeta/'resumen.json').read_text(encoding='utf-8')),r,f'{nombre}.resumen')
        for clave in ['datos_entrada','candidatos_comparados','enteros','derivadas','sensibilidad','comparacion_tolerancias','iteraciones']:
            filas=list(csv.DictReader((carpeta/f'{clave}.csv').read_text(encoding='utf-8-sig').splitlines()))
            if len(filas)!=len(r[clave]):
                raise AssertionError(f'{nombre}/{clave}: número de filas')
            for fila,esperada in zip(filas,r[clave]):
                if fila['procedencia']!=r['etiqueta']:
                    raise AssertionError('Etiqueta de simulación ausente')
                for k,v in esperada.items():
                    actual=float(fila[k]) if isinstance(v,(int,float)) else None if v is None and fila[k]=='' else fila[k]
                    comparar(actual,v,f'{nombre}/{clave}/{k}')
        m=Modelo.construir(x,y)
        curvas=list(csv.DictReader((carpeta/'curvas.csv').read_text(encoding='utf-8-sig').splitlines()))
        if len(curvas)!=601:
            raise AssertionError('Curva incompleta')
        for fila in curvas:
            z=float(fila['x'])
            comparar(float(fila['latencia_ms']),float(m.latencia(z)),'curva.latencia')
            comparar(float(fila['rendimiento_rps']),float(m.rendimiento(z)),'curva.rendimiento')
            if fila['procedencia']!=r['etiqueta']:
                raise AssertionError('Procedencia de curva incorrecta')
        trazas=json.loads((carpeta/'trazabilidad_graficas.json').read_text(encoding='utf-8'))
        for archivo,huella in trazas['sha256'].items():
            if hashlib.sha256((carpeta/archivo).read_bytes()).hexdigest()!=huella:
                raise AssertionError(f'{nombre}/{archivo}: huella diferente de la generación')
        lineas.append(f'PASS: {nombre}: JSON completo, tablas CSV, 601 puntos de curvas y huellas de PNG.')
    return manifiesto,lineas


def valores_clave(manifiesto):
    valores=[]
    for r in manifiesto['escenarios']:
        valores += [r['maximo_dominio']['x'], r['optimo_entero'],r['latencia_en_recomendacion_ms'],r['rendimiento_en_recomendacion_rps']]
    return valores


def cotejar_texto(texto,valores,nombre):
    numeros=[float(s) for s in re.findall(r'(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?',texto)]
    for valor in valores:
        if not any(abs(v-valor)<=.5e-6+1e-10 for v in numeros):
            raise AssertionError(f'{nombre}: falta la cifra {valor:.6f} (redondeo 6 decimales)')
    if 'SIMULADOS' not in texto or 'solicitudes/s' not in texto or 'ms' not in texto:
        raise AssertionError(f'{nombre}: faltan unidades o etiqueta de procedencia')


def auditar_documentos(root,manifiesto):
    root=Path(root)
    salidas=[]
    valores=valores_clave(manifiesto)
    principal=manifiesto['escenarios'][0]
    # Valores de la sustitución guiada y de la diferencia central en x=70, h=1.
    tasas={fila['x']:fila['rendimiento_rps'] for fila in principal['enteros']}
    manual=(tasas[71]-tasas[69])/2
    analitica=1000*(20-.004*70**2)/(20+.12*70+.004*70**2)**2
    valores_informe=valores+[tasas[70],tasas[69],tasas[71],manual,analitica,abs(manual-analitica)]
    md=(root/'informe'/'Informe_Final.md').read_text(encoding='utf-8')
    cotejar_texto(md,valores_informe,'Markdown')
    # Tabla contractual: valida la correspondencia entre escenario y cada cifra.
    for r in manifiesto['escenarios']:
        fila=next((l for l in md.splitlines() if l.startswith('| '+r['escenario']+' |')),None)
        if fila is None:
            raise AssertionError('Falta tabla de resultados por escenario')
        campos=[c.strip() for c in fila.split('|')[2:-1]]
        esperado=[r['maximo_dominio']['x'],r['optimo_entero'],r['latencia_en_recomendacion_ms'],r['rendimiento_en_recomendacion_rps']]
        comparar([float(c) for c in campos],esperado,'tabla Markdown',.5e-6+1e-10)
    salidas.append('PASS: Markdown, tabla por escenario y cifras con redondeo a 6 decimales.')
    docx=root/'informe'/'Informe_Final.docx'
    if docx.exists():
        with zipfile.ZipFile(docx) as z:
            xml=ET.fromstring(z.read('word/document.xml'))
            texto=' '.join(e.text or '' for e in xml.iter() if e.tag.endswith('}t'))
        cotejar_texto(texto,valores_informe,'DOCX')
        salidas.append('PASS: cifras clave, unidades y etiqueta en texto extraído de DOCX.')
    else:
        salidas.append('NO VERIFICADO: DOCX ausente.')
    pdf=root/'informe'/'Informe_Final.pdf'
    if pdf.exists():
        from pypdf import PdfReader
        texto=' '.join(p.extract_text() for p in PdfReader(pdf).pages)
        cotejar_texto(texto,valores_informe,'PDF')
        salidas.append('PASS: cifras clave, unidades y etiqueta en texto extraído de PDF.')
    else:
        salidas.append('NO VERIFICADO: PDF ausente.')
    pptx=root/'presentacion'/'Presentacion_Visual.pptx'
    if pptx.exists():
        with zipfile.ZipFile(pptx) as z:
            textos=[]
            for nombre in z.namelist():
                if re.match(r'ppt/slides/slide\d+\.xml$',nombre):
                    xml=ET.fromstring(z.read(nombre))
                    textos += [e.text or '' for e in xml.iter() if e.tag.endswith('}t')]
            texto=' '.join(textos)
            cotejar_texto(texto,valores,'PPTX')
        salidas.append('PASS: cifras clave visibles, unidades y procedencia en PPTX (XML de diapositivas).')
    else:
        salidas.append('NO VERIFICADO: PPTX ausente.')
    return salidas


def main():
    lineas=['# Reporte de consistencia','', 'Tolerancia interna absoluta: 1e-6. Presentación: ±0.5 × 10^-6 para cifras a seis decimales.','']
    fallo=False
    try:
        manifiesto,resultado=auditar_resultados(ROOT/'resultados')
        lineas+=resultado
        lineas+=auditar_documentos(ROOT,manifiesto)
        if any(l.startswith('NO VERIFICADO:') for l in lineas):
            raise AssertionError('Falta al menos un entregable documental obligatorio')
        suite=ET.parse(ROOT/'validacion'/'pytest.xml').getroot().find('testsuite')
        if int(suite.attrib['failures']) or int(suite.attrib['errors']) or int(suite.attrib['tests'])==0:
            raise AssertionError('La última ejecución pytest contiene fallos o no tiene pruebas')
        lineas.append(f"PASS: pytest, {suite.attrib['tests']} pruebas, 0 fallos; ejecución {suite.attrib['timestamp']}.")
        lineas.append('La suite incluye alteración deliberada de una cifra exportada y exige que la auditoría la detecte, en copia temporal.')
    except (AssertionError,ValueError,OSError,KeyError) as e:
        lineas.append(f'FAIL: {e}')
        fallo=True
    lineas += ['', 'Revisión visual: consultar REPORTE_INTERFAZ.md y REPORTE_VISUAL.md. La extracción de texto no prueba la calidad de la maquetación.',
               'NO VERIFICADO: grabación del video, intervenciones de los tres integrantes y revisión académica humana.',
               '', 'Estado: '+('REQUIERE CORRECCIÓN' if fallo else 'APTO PARA REVISIÓN HUMANA'),
               'El estado anterior se refiere a controles automáticos ejecutados. No sustituye la aprobación del equipo.']
    (ROOT/'validacion'/'REPORTE_CONSISTENCIA.md').write_text('\n\n'.join(lineas)+'\n',encoding='utf-8')
    print('\n'.join(lineas))
    return int(fallo)


if __name__=='__main__':
    raise SystemExit(main())
