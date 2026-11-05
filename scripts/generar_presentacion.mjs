// Autoría local con el runtime de Artifact Tool. Todas las cifras se leen del manifiesto.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const root=process.cwd();
const modules=process.env.ARTIFACT_MODULES;
const skill=process.env.PRESENTATIONS_SKILL;
const python=process.env.ARTIFACT_PYTHON;
if(!modules||!skill||!python) throw Error('Defina ARTIFACT_MODULES, PRESENTATIONS_SKILL y ARTIFACT_PYTHON con las rutas del runtime.');
process.env.RUNTIME_NODE_MODULES=modules;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const m=JSON.parse(await fs.readFile(path.join(root,'resultados/metricas_validadas.json'),'utf8'));
const [p,q]=m.escenarios;
const build=path.join(root,'tmp','presentacion');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(root,'presentacion'),{recursive:true});
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const navy='#173B51',teal='#087F8C',orange='#D65A31',gray='#526277';
const f=n=>Number(n).toFixed(6);
function text(slide,s,x,y,w,h,size=28,color=navy,bold=false){
 const box=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 box.text=s; box.text.style={typeface:'Aptos',fontSize:size,color,bold};return box;
}
function slide(title,notes){
 const s=deck.slides.add();s.background.fill='#FFFFFF';
 text(s,title,60,42,1160,85,42,navy,true);
 text(s,'DATOS SIMULADOS / EJEMPLO DIDÁCTICO',60,672,1050,24,17,gray);
 text(s,String(deck.slides.items.length),1170,672,60,24,17,gray);
 s.speakerNotes.text=notes;return s;
}
function table(s,headers,rows,x,y,w,h){
 const t=s.tables.add({rows:rows.length+1,columns:headers.length,left:x,top:y,width:w,height:h,values:[headers,...rows]});
 t.borders.assign({fill:'#D9E2E8',width:1,style:'solid'});
 t.cells.block({row:0,column:0,rowCount:rows.length+1,columnCount:headers.length}).assign({textStyle:{typeface:'Aptos',fontSize:23,color:navy},margins:{left:12,right:12,top:10,bottom:10}});
 t.cells.block({row:0,column:0,rowCount:1,columnCount:headers.length}).assign({fill:navy,textStyle:{typeface:'Aptos',fontSize:22,bold:true,color:'#FFFFFF'}});
 return t;
}
function chart(s,series,ytitle,pos={left:520,top:165,width:700,height:440},options={}){
 // Las hojas editables de PowerPoint conservan nueve decimales en sus curvas.
 series=series.map(v=>({...v,xValues:v.xValues.map(n=>Number(n.toFixed(9))),values:v.values.map(n=>Number(n.toFixed(9)))}));
 const c=s.charts.add('scatter',{position:pos,series,scatterOptions:{style:'line'},hasLegend:series.length>1,legend:{position:'bottom',textStyle:{fontSize:19}},xAxis:{title:'Concurrencia (solicitudes)',min:20,max:100,majorUnit:20,textStyle:{fontSize:20}},yAxis:{title:ytitle,textStyle:{fontSize:20},majorGridlines:{fill:'#E5EAF0',width:1}},...options});
 applyPresentationChartFont(c,{fontFamily:'Arial'}); return c;
}
async function curva(nombre){
 const csv=await fs.readFile(path.join(root,`resultados/${nombre}/curvas.csv`),'utf8');
 return csv.replace(/^\uFEFF/,'').trim().split(/\r?\n/).slice(1).filter((_,i)=>i%10===0).map(l=>l.split(',').slice(0,3).map(Number));
}
const curvaP=await curva('principal'),curvaQ=await curva('monotono');
function serie(name,rows,col,color=teal){return {name,xValues:rows.map(r=>r[0]),values:rows.map(r=>r[col]),line:{fill:color,width:3},marker:{symbol:'none'}};}

let s=slide('Optimización del rendimiento de un servidor','Integrante A · 0:00–0:45. Presentar la pregunta: qué concurrencia maximiza el indicador de nuestro escenario. Aclarar desde el inicio que se trata de un simulador matemático, sin ensayos de carga reales.');
text(s,'¿Qué concurrencia\nconviene al modelo?',64,190,570,180,52,navy,true);
text(s,'Newton reconstruye la latencia\nBisección localiza el candidato\nLos extremos y enteros deciden',66,420,590,150,29,gray);
chart(s,[serie('Rendimiento',curvaP,2)],'Solicitudes/s',{left:670,top:175,width:550,height:425});

s=slide('Datos de partida','Integrante A · 0:45–2:30. Los tres nodos fueron diseñados a partir de L_sint=20+0.12x+0.004x². Los coeficientes son hipótesis didácticas, sin mediciones ni procedencia bibliográfica. El motor solo recibe esta tabla. Definir concurrencia como solicitudes promedio simultáneas. Dominio [20,100].');
table(s,['Concurrencia','Latencia (ms)'],p.datos_entrada.map(d=>[String(d.concurrencia),String(d.latencia_ms)]),60,180,440,270);
text(s,'Tres nodos sintéticos\nDominio observado [20,100]',65,500,440,95,28,gray);
chart(s,[{name:'Nodos sintéticos',xValues:p.datos_entrada.map(d=>d.concurrencia),values:p.datos_entrada.map(d=>d.latencia_ms),marker:{symbol:'circle',size:10,fill:teal},line:{fill:teal,width:0}}],'Latencia (ms)',undefined,{scatterOptions:{style:'marker'}});

s=slide('Interpolación de Newton','Integrante B · 2:30–3:35. Explicar el cociente de primer orden y luego la diferencia de pendientes. Mostrar los factores (x−20) y (x−50). La misma tabla reconstruye el polinomio, sin leer el generador. Fuentes: Chapra y Canale (2015), §18.1; Ascher y Greif (2011), §10.4; Kong et al. (2021), §17.5.');
table(s,['Orden 0','Orden 1','Orden 2'],p.diferencias_divididas.map(row=>row.map(v=>v===null?'':Number(v.toPrecision(6)).toString())),60,165,465,235);
text(s,'P₂(x) = 24 + 0.4(x−20)\n+ 0.004(x−20)(x−50)',65,445,520,110,28,navy,true);
text(s,p.formula,65,580,650,55,26,teal);
chart(s,[serie('Latencia',curvaP,1)],'Latencia (ms)',{left:590,top:160,width:625,height:395});

s=slide('Rendimiento y condición de máximo',"Integrante B · 3:35–4:35. Little relaciona el número promedio en el sistema con la tasa y el tiempo medio bajo hipótesis coherentes. Convertir ms a segundos da el factor 1000. Derivar el cociente para obtener g=L−xL′. En este ejemplo g=20−0.004x² y cambia de signo. Fuente: Whitt (2015), §1, https://www.columbia.edu/~ww2040/4615S15/LittlesLawNotes012715.pdf.");
text(s,'R(x) = 1000x / L(x)',65,185,600,80,40,navy,true);
text(s,'R′(x) = 1000 g(x) / L(x)²',65,280,640,65,31,navy);
text(s,'g(x) = L(x) − xL′(x)',65,370,640,65,31,teal,true);
text(s,'Régimen estable\nTiempo medio total en el sistema',65,500,560,100,28,gray);
const coef=p.coeficientes_potencias;
const gx=curvaP.map(row=>[row[0],coef.reduce((a,c,i)=>a+(1-i)*c*row[0]**i,0)]);
chart(s,[serie('g(x)',gx,1)],'g(x) (ms)',{left:720,top:190,width:500,height:400});

s=slide('Máximo continuo y decisión entera','Integrante B · 4:35–5:30. El punto continuo no es una configuración entera. Se comparan suelo, techo y todos los enteros, además de los extremos. Las latencias y rendimientos destacados corresponden a la recomendación entera. La tasa máxima continua es ligeramente mayor. Cifras: resultados/metricas_validadas.json.');
text(s,f(p.maximo_dominio.x),65,175,550,100,60,teal,true);
text(s,'Máximo de la variable continua',65,275,550,50,27,gray);
text(s,String(p.optimo_entero)+' solicitudes',65,365,550,90,52,navy,true);
text(s,`${f(p.latencia_en_recomendacion_ms)} ms\n${f(p.rendimiento_en_recomendacion_rps)} solicitudes/s`,65,465,600,110,28,navy);
chart(s,[serie('Modelo',curvaP,2),{name:'Máximo',xValues:[p.maximo_dominio.x],values:[p.maximo_dominio.rendimiento_rps],marker:{symbol:'circle',size:10,fill:orange},line:{fill:'none',width:0}}],'Rendimiento (solicitudes/s)',{left:660,top:170,width:560,height:435});

s=slide('Control del error','Integrante C · 5:30–6:20. La cota del error es el semiancho del intervalo antes de actualizar. Cada paso conserva el cambio de signo. La traza automática parte de [20,100], mientras la prueba matemática también usa [50,100]. Se comprueba la solución con sqrt(5000). Referencia: Ascher y Greif (2011), pp. 43–44.');
table(s,['Tolerancia','Pasos','Error real'],p.comparacion_tolerancias.map(v=>[v.tolerancia.toExponential(0),String(v.iteraciones),v.error_referencia.toExponential(2)]),60,170,530,260);
text(s,'Cota = (b − a) / 2\nError en concurrencia',65,480,550,110,33,teal,true);
const c=s.charts.add('line',{position:{left:650,top:170,width:570,height:435},categories:p.iteraciones.map(v=>String(v.iteracion)),series:[{name:'log10 de la cota',values:p.iteraciones.map(v=>Number(Math.log10(v.error).toFixed(9))),line:{fill:teal,width:3}}],hasLegend:false,xAxis:{title:'Iteración',textStyle:{fontSize:20}},yAxis:{title:'log10(cota de error)',textStyle:{fontSize:20}}});applyPresentationChartFont(c,{fontFamily:'Arial'});

s=slide('Sensibilidad de la recomendación','Integrante C · 6:20–6:55. Cada barra corresponde a modificar una sola latencia en ±5 %. No son mediciones repetidas ni intervalos de confianza. Al modificar un dato se reconstruye el polinomio y se vuelve a verificar positividad, candidatos y enteros.');
const sens=p.sensibilidad;
const c2=s.charts.add('bar',{position:{left:60,top:165,width:820,height:440},categories:sens.map(v=>`x=${v.nodo} ${v.cambio_porcentaje>0?'+':''}${v.cambio_porcentaje}%`),series:[{name:'Entero recomendado',values:sens.map(v=>v.optimo_entero),fill:teal}],barOptions:{direction:'column'},hasLegend:false,dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:22}},xAxis:{title:'Latencia perturbada por separado',textStyle:{fontSize:20}},yAxis:{title:'Concurrencia recomendada',textStyle:{fontSize:20}}});applyPresentationChartFont(c2,{fontFamily:'Arial'});
text(s,'±5 %',930,215,285,110,66,orange,true);
text(s,'Datos distintos\nDecisión distinta',930,365,280,120,30,navy);

s=slide('Demostración de la aplicación local','Integrante C · 6:55–8:30. Cambiar a la aplicación real. Cargar principal, ejecutar, explicar la tabla de Newton y las iteraciones. Modificar una latencia y recalcular. Cargar monótono: debe recomendar 100, con mensaje de ausencia de punto crítico interior. Restaurar principal y mostrar 71. Descargar el ZIP. Esta diapositiva usa una captura real y no reemplaza la demostración en ejecución.');
const captura=path.join(root,'validacion/capturas/principal_resumen.png');
try{await fs.access(captura);s.images.add({blob:new Uint8Array(await fs.readFile(captura)),contentType:'image/png',alt:'Captura real de Streamlit, caso principal',fit:'contain',position:{left:60,top:145,width:770,height:495}});}catch{}
text(s,'Cargar y ejecutar\nEditar una latencia\nCambiar escenario\nExportar resultados',875,230,345,255,30,navy);

s=slide('Conclusiones y límite del modelo','Los tres · 8:30–9:45. A: recordar que son datos sintéticos y que el modelo ilustra una decisión de planificación. B: explicar que Newton produce L y bisección solo busca un candidato con hipótesis verificadas. C: contrastar principal con monótono y recordar que siempre se comparan fronteras y enteros. Para extrapolar al mundo real harían falta mediciones repetidas, incertidumbre y datos independientes.');
table(s,['Escenario','Entero','Latencia (ms)','R (solicitudes/s)'],[p,q].map(r=>[r.escenario,String(r.optimo_entero),f(r.latencia_en_recomendacion_ms),f(r.rendimiento_en_recomendacion_rps)]),60,155,1160,190);
text(s,`Caso monótono: máximo x = ${f(q.maximo_dominio.x)}\nSin raíz interior de g(x)`,65,385,650,100,31,teal,true);
text(s,'La recomendación depende del modelo\nSu validez se restringe a [20,100]\nLa capacidad real requiere mediciones',65,520,1140,125,30,navy);

await fs.writeFile(path.join(build,'metricas_fuente.json'),JSON.stringify(m,null,2));
const candidate=path.join(build,'candidato.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidate);
for(let i=0;i<deck.slides.items.length;i++){
 const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const final=path.join(root,'presentacion','Presentacion_Visual.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[2,3,6,9].flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:9,requiredNativeTableOwnerSlides:[2,3,6,9],requiredNativeChartOwnerSlides:[1,2,3,4,5,6,7],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Aptos','Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validacion.json')});
console.log(JSON.stringify(result));
await fs.writeFile(path.join(root,'presentacion','Notas_del_Expositor.md'),deck.slides.items.map((s,i)=>`## Diapositiva ${i+1}\n\n${s.speakerNotes.text}`).join('\n\n'));
