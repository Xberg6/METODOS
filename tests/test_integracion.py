import io
import json
import shutil
import zipfile
import pytest
from pathlib import Path
from src.main import ejecutar_demo
from src.exportacion import leer_csv,paquete_zip
from validacion.verificar_entregables import auditar_resultados,comparar,cotejar_texto


@pytest.fixture(scope='module')
def resultados(tmp_path_factory):
    base=tmp_path_factory.mktemp('resultados')
    ejecutar_demo(base)
    return base


def test_exportaciones_y_manifiesto(resultados):
    manifiesto,lineas=auditar_resultados(resultados)
    assert len(lineas)==2
    paquete=paquete_zip(manifiesto['escenarios'][0])
    with zipfile.ZipFile(io.BytesIO(paquete)) as z:
        assert z.testzip() is None
        assert z.read('latencia.png').startswith(b'\x89PNG')
        assert json.loads(z.read('resumen.json'))['optimo_entero']==71


def test_auditoria_detecta_cifra_alterada_y_restaura(resultados,tmp_path):
    copia=tmp_path/'copia'
    shutil.copytree(resultados,copia)
    p=copia/'principal'/'resumen.json'
    original=p.read_text(encoding='utf-8')
    modificado=json.loads(original)
    modificado['rendimiento_en_recomendacion_rps']+=1
    p.write_text(json.dumps(modificado),encoding='utf-8')
    with pytest.raises(AssertionError,match='rendimiento_en_recomendacion'):
        auditar_resultados(copia)
    p.write_text(original,encoding='utf-8')
    auditar_resultados(copia)


def test_auditoria_detecta_curva_alterada(resultados,tmp_path):
    copia=tmp_path/'copia'
    shutil.copytree(resultados,copia)
    p=copia/'principal'/'curvas.csv'
    texto=p.read_text(encoding='utf-8-sig').replace('24.0,','25.0,',1)
    p.write_text(texto,encoding='utf-8-sig')
    with pytest.raises(AssertionError):
        auditar_resultados(copia)


@pytest.mark.parametrize('texto',['x,y\n20,24','concurrencia,latencia_ms\ntexto,1','concurrencia,latencia_ms\n1,','concurrencia,latencia_ms\n1,2,3'])
def test_csv_invalido(texto):
    with pytest.raises(ValueError):
        leer_csv(io.StringIO(texto))


def test_csv_ausente():
    with pytest.raises(ValueError):
        leer_csv('archivo_que_no_existe.csv')


def test_redondeo_documental():
    cotejar_texto('SIMULADOS 70.710678 solicitudes/s ms',[70.710678118],'prueba')
    with pytest.raises(AssertionError):
        cotejar_texto('SIMULADOS 70.710600 solicitudes/s ms',[70.710678118],'prueba')
