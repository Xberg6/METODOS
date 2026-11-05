from streamlit.testing.v1 import AppTest
from pathlib import Path


def boton(at,texto):
    return next(b for b in at.button if b.label==texto)


def test_interfaz_cambio_estado_y_escenarios():
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=45).run()
    assert not at.exception
    boton(at,'Ejecutar análisis').click().run()
    assert not at.exception
    assert at.session_state['resultado']['optimo_entero']==71
    at.selectbox[0].select('Monótono').run()
    boton(at,'Cargar escenario').click().run()
    assert not at.metric
    boton(at,'Ejecutar análisis').click().run()
    assert not at.exception
    assert at.session_state['resultado']['optimo_entero']==100
    boton(at,'Restablecer caso principal').click().run()
    boton(at,'Ejecutar análisis').click().run()
    assert at.session_state['resultado']['optimo_entero']==71
    at.number_input(key='xmin').set_value(110).run()
    assert not at.metric
    boton(at,'Ejecutar análisis').click().run()
    assert at.error
    assert not at.metric
    assert not at.exception
    boton(at,'Restablecer caso principal').click().run()
    carpeta=Path(__file__).resolve().parents[1]/'data'
    at.file_uploader[0].set_value(('caso.csv',(carpeta/'ejemplo_monotono_simulado.csv').read_bytes(),'text/csv')).run()
    boton(at,'Usar CSV').click().run()
    boton(at,'Ejecutar análisis').click().run()
    assert not at.exception
    assert at.session_state['resultado']['optimo_entero']==100
    at.file_uploader[0].set_value(('error.csv',b'x,y\n1,2','text/csv')).run()
    boton(at,'Usar CSV').click().run()
    assert at.session_state['estado']=='entrada inválida'
    assert at.error and not at.metric and not at.exception
