"""Extrae únicamente páginas pertinentes de los libros locales para revisión."""
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'tmp'/'fuentes'
DEST.mkdir(parents=True,exist_ok=True)
for ruta in (ROOT/'Libros').glob('*.pdf'):
    if 'Chapra' in ruta.name:
        etiqueta,paginas='chapra',[4,5,6,118,119,403,404]
    elif 'Ascher' in ruta.name:
        etiqueta,paginas='ascher',[3,4,5,60,61,321,322]
    else:
        etiqueta,paginas='kong',[3,4,5,316,317,336,337]
    reader=PdfReader(ruta)
    contenido='\n\n'.join(f'PÁGINA DEL PDF {n}\n'+reader.pages[n-1].extract_text() for n in paginas)
    (DEST/f'{etiqueta}.txt').write_text(contenido,encoding='utf-8')
    print(etiqueta, len(reader.pages),'páginas; extractos guardados')
