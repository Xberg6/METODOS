"""Empaqueta el proyecto académico sin libros, dependencias ni temporales."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def empaquetar():
    raiz = Path(__file__).resolve().parents[1]
    archivos = [raiz / nombre for nombre in (
        'README.md', 'requirements.txt', 'app.py', 'pytest.ini', 'Abrir_simulador.cmd',
        'Instalar_dependencias.cmd', '.gitignore', '.gitattributes', '.streamlit/config.toml',
    )]
    for nombre in ('src', 'data', 'tests', 'scripts', 'informe', 'presentacion', 'resultados', 'validacion'):
        archivos.extend(p for p in (raiz / nombre).rglob('*')
                        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    destino = raiz / 'Proyecto_Servidor_para_revision.zip'
    with ZipFile(destino, 'w', ZIP_DEFLATED) as paquete:
        for archivo in sorted(archivos):
            paquete.write(archivo, archivo.relative_to(raiz).as_posix())
    with ZipFile(destino) as paquete:
        problema = paquete.testzip()
        if problema:
            raise RuntimeError(f'Archivo ilegible en el paquete: {problema}')
        print(f'{destino.name}: {len(paquete.namelist())} archivos verificados.')


if __name__ == '__main__':
    empaquetar()
