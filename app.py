"""Interfaz local. Toda la matemática está en src, independiente de Streamlit."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.analisis import analizar, complementar, ETIQUETA
from src.exportacion import leer_csv, paquete_zip, csv_bytes
from src.graficas import figuras, png

st.set_page_config(page_title='Laboratorio de rendimiento',page_icon='📈',layout='wide')
RAIZ=Path(__file__).resolve().parent


def cargar(nombre='Principal'):
    archivo='ejemplo_simulado.csv' if nombre=='Principal' else 'ejemplo_monotono_simulado.csv'
    x,y=leer_csv(RAIZ/'data'/archivo)
    st.session_state.tabla=pd.DataFrame({'concurrencia':x,'latencia_ms':y})
    st.session_state.revision=st.session_state.get('revision',0)+1
    st.session_state.pop('resultado',None)
    st.session_state.pop('paquete',None)
    st.session_state.pop('firma',None)
    st.session_state.xmin=20.0
    st.session_state.xmax=100.0
    st.session_state.consulta=70.0
    st.session_state.origen=nombre
    st.session_state.selector_escenario=nombre


if 'tabla' not in st.session_state:
    cargar()

st.caption('MÉTODOS NUMÉRICOS · PROYECTO FINAL')
st.title('Laboratorio de rendimiento')
st.write('Estima qué concurrencia maximiza el rendimiento de un modelo de latencia y examina cómo se obtiene la recomendación.')
st.info(ETIQUETA+' · Los ejemplos no son mediciones de un servidor real.')

with st.sidebar:
    st.header('Configuración')
    escenario=st.selectbox('Escenario de demostración',['Principal','Monótono'],key='selector_escenario')
    st.button('Cargar escenario',on_click=cargar,args=(escenario,),width='stretch')
    st.button('Restablecer caso principal',on_click=cargar,width='stretch')
    st.divider()
    a=st.number_input('Concurrencia mínima',key='xmin',step=1.0)
    b=st.number_input('Concurrencia máxima',key='xmax',step=1.0)
    tol=st.selectbox('Tolerancia absoluta en x',[1e-2,1e-4,1e-6,1e-8],index=2,format_func=lambda z:f'{z:g}')
    limite=st.number_input('Máximo de iteraciones',min_value=1,max_value=1000,value=100,step=1)
    consulta=st.number_input('Punto de consulta x',key='consulta',step=1.0)
    pasos=st.text_input('Pasos h (separados por comas)','1,0.1,0.01,0.001')
    st.caption('El dominio debe quedar dentro de los nodos. Se admite un máximo de 8 nodos y 100001 enteros.')

with st.expander('Datos de entrada y CSV',expanded=True):
    st.caption(f"Origen cargado: {st.session_state.origen}. Ediciones y CSV se tratan como escenarios didácticos no validados.")
    tabla=st.data_editor(st.session_state.tabla,num_rows='dynamic',hide_index=True,key=f"editor_{st.session_state.revision}",width='stretch',column_config={'concurrencia':st.column_config.NumberColumn('Concurrencia (solicitudes)',format='%d'),'latencia_ms':st.column_config.NumberColumn('Latencia media (ms)',format='%.4f')})
    firma=hashlib.sha256((tabla.to_json()+repr((a,b,tol,limite,consulta,pasos))).encode()).hexdigest()
    archivo=st.file_uploader('Importar CSV con columnas concurrencia,latencia_ms',type='csv')
    if st.button('Usar CSV',disabled=archivo is None):
        st.session_state.pop('resultado',None)
        st.session_state.pop('paquete',None)
        try:
            archivo.seek(0)
            x,y=leer_csv(archivo)
            st.session_state.tabla=pd.DataFrame({'concurrencia':x,'latencia_ms':y})
            st.session_state.revision+=1
            st.session_state.origen='CSV importado'
            st.session_state.pop('firma',None)
            st.rerun()
        except ValueError as e:
            st.session_state.firma=firma
            st.session_state.estado='entrada inválida'
            st.session_state.error=str(e)
    st.caption('Entre 3 y 8 filas. Los nodos se ordenan antes del cálculo. Latencias estrictamente positivas.')

if st.session_state.get('firma') != firma:
    st.session_state.pop('resultado',None)
    st.session_state.pop('paquete',None)
    st.session_state.estado='sin ejecutar'

if st.button('Ejecutar análisis',type='primary',width='stretch'):
    st.session_state.pop('resultado',None)
    st.session_state.firma=firma
    try:
        h=[float(v.strip()) for v in pasos.split(',')]
        r=complementar(analizar(tabla['concurrencia'].tolist(),tabla['latencia_ms'].tolist(),[a,b],tol,int(limite),'interfaz',h,consulta))
        st.session_state.resultado=r
        st.session_state.estado='calculado' if r['optimo_continuo'] else 'no hay máximo interior'
        st.session_state.paquete=paquete_zip(r)
    except (ValueError,TypeError,OverflowError) as e:
        st.session_state.estado='entrada inválida'
        st.session_state.error=str(e)

estado=st.session_state.get('estado','sin ejecutar')
st.caption(f'Estado del cálculo: {estado.upper()}')
if estado=='entrada inválida':
    st.error(st.session_state.error)
if 'resultado' not in st.session_state:
    st.write('Revisa la tabla y pulsa **Ejecutar análisis** para obtener resultados con estos parámetros.')
    st.stop()

r=st.session_state.resultado
st.success(r['mensaje'])
cols=st.columns(2)
cols[0].metric('Concurrencia entera (solicitudes)',str(r['optimo_entero']))
cols[1].metric('Tasa (solicitudes/s)',f"{r['rendimiento_en_recomendacion_rps']:.4f}")
cols=st.columns(2)
cols[0].metric('Latencia en la recomendación (ms)',f"{r['latencia_en_recomendacion_ms']:.4f}")
cols[1].metric('Máximo continuo (concurrencia)',f"{r['maximo_dominio']['x']:.6f}")
st.caption('Las tarjetas de rendimiento y latencia corresponden a la recomendación entera. El máximo continuo se compara por separado.')

modelo,metodos,graficos,validacion=st.tabs(['Datos y modelo','Métodos numéricos','Resultados y gráficas','Validación y sensibilidad'])
with modelo:
    st.subheader('Modelo reconstruido desde la tabla')
    st.code(r['formula'],language=None)
    st.latex(r'R(x)=\frac{1000x}{L(x)},\qquad g(x)=L(x)-xL\prime(x)')
    st.write('x representa solicitudes promedio simultáneamente en el sistema. La relación requiere régimen estable y una latencia media que incluya toda la permanencia en el sistema.')
    st.dataframe(pd.DataFrame(r['datos_entrada']),hide_index=True,width='stretch')
    st.write(f"Consulta x={consulta:g}: L={r['consulta']['latencia_ms']:.6f} ms; R={r['consulta']['rendimiento_rps']:.6f} solicitudes/s.")
with metodos:
    st.subheader('Diferencias divididas de Newton')
    st.dataframe(pd.DataFrame(r['diferencias_divididas'],columns=[f'Orden {i}' for i in range(len(r['coeficientes']))]),hide_index=True,width='stretch')
    st.caption('Cada fila inicia en su nodo ordenado. La primera fila contiene los coeficientes de Newton.')
    st.subheader('Bisección paso a paso')
    if r['iteraciones']:
        st.dataframe(pd.DataFrame(r['iteraciones']),hide_index=True,width='stretch')
        st.caption('error = (b-a)/2 antes de actualizar el intervalo; se detiene al cumplir la tolerancia en x o hallar un cero exacto.')
    else:
        st.info(r['estado_biseccion'])
with graficos:
    st.dataframe(pd.DataFrame(r['candidatos_comparados']),hide_index=True,width='stretch')
    fs=figuras(r)
    for nombre in ['latencia','rendimiento','convergencia']:
        st.pyplot(fs[nombre],width='stretch')
        st.download_button(f'Descargar {nombre} PNG',png(fs[nombre]),file_name=f'{nombre}.png',mime='image/png')
with validacion:
    st.subheader('Sensibilidad de la recomendación')
    st.pyplot(fs['sensibilidad'],width='stretch')
    st.dataframe(pd.DataFrame(r['sensibilidad']),hide_index=True,width='stretch')
    st.subheader('Tolerancia y convergencia')
    st.dataframe(pd.DataFrame(r['comparacion_tolerancias']),hide_index=True,width='stretch')
    st.subheader('Comprobación por diferencias centrales')
    st.dataframe(pd.DataFrame(r['derivadas']),hide_index=True,width='stretch')
    st.write(f"Latencia mínima comprobada: {r['minimo_latencia_ms']:.6f} ms. Se evaluaron {len(r['enteros'])} enteros.")
    for advertencia in r['advertencias'][1:]:
        st.caption(advertencia)
    evidencia=RAIZ/'validacion'/'REPORTE_PRUEBAS.md'
    if evidencia.exists():
        with st.expander('Evidencia de pruebas de esta versión'):
            st.markdown(evidencia.read_text(encoding='utf-8'))
    else:
        st.caption('Reporte de pruebas aún no generado. Ejecute python -m pytest -q.')
for fig in fs.values():
    plt.close(fig)
st.divider()
c1,c2,c3=st.columns(3)
c1.download_button('Descargar resumen JSON',json.dumps(r,ensure_ascii=False,indent=2),file_name='resumen.json',mime='application/json')
c2.download_button('Descargar candidatos CSV',csv_bytes(r['candidatos_comparados']),file_name='candidatos.csv',mime='text/csv')
c3.download_button('Descargar análisis completo ZIP',st.session_state.paquete,file_name='analisis_simulado.zip',mime='application/zip')
