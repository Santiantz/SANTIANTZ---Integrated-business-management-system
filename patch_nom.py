c = open('public/index.html', encoding='utf-8').read()

# ── 1. CSS: pago-row ────────────────────────────────────────────────────────
c = c.replace(
    '.inv-row input{flex:1;padding:6px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;}',
    '.inv-row input{flex:1;padding:6px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;}\n.pago-row{display:flex;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd);}',
    1
)

# ── 2. sec-nominas HTML (antes del cierre de .content) ──────────────────────
INP = 'width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;'
SEL = 'padding:5px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:11px;'

SEC_NOM = (
    '\n      <div class="sec" id="sec-nominas">\n'
    '        <div class="g4">\n'
    '          <div class="card"><div class="cl">Empleados activos</div><div class="cv b" id="nom-ne">0</div></div>\n'
    '          <div class="card"><div class="cl">Nómina semanal est.</div><div class="cv a" id="nom-sem">$0</div></div>\n'
    '          <div class="card"><div class="cl">Nómina mensual est.</div><div class="cv g" id="nom-mes">$0</div></div>\n'
    '          <div class="card"><div class="cl">Pagos este mes</div><div class="cv" id="nom-pme">0</div></div>\n'
    '        </div>\n'
    '        <div id="nom-filt" style="margin-bottom:10px;"></div>\n'
    '        <div class="g2" style="margin-bottom:12px;">\n'
    '          <div class="card">\n'
    '            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">\n'
    '              <div class="cl">Plantilla de empleados</div>\n'
    '              <button class="btn" style="font-size:11px;padding:4px 9px;" onclick="openNomModal(\'empleado\')">+ Empleado</button>\n'
    '            </div>\n'
    '            <div id="nom-empl"><div class="empty">Sin empleados registrados</div></div>\n'
    '          </div>\n'
    '          <div class="card">\n'
    '            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">\n'
    '              <div class="cl">Pagos recientes</div>\n'
    '              <button class="btn" style="font-size:11px;padding:4px 9px;" id="btn-nom-reg" onclick="openNomModal(\'nomina-pago\')">+ Registrar pago</button>\n'
    '            </div>\n'
    '            <div id="nom-pagos"><div class="empty">Sin pagos registrados</div></div>\n'
    '          </div>\n'
    '        </div>\n'
    '        <div class="card" style="margin-bottom:12px;">\n'
    '          <div class="cl" style="margin-bottom:8px;">Historial por empleado</div>\n'
    '          <div style="display:flex;gap:8px;margin-bottom:10px;align-items:center;">\n'
    '            <select id="nom-hemp" style="flex:1;' + SEL + '"><option value="">Selecciona empleado</option></select>\n'
    '            <select id="nom-hmes" style="' + SEL + '"><option value="">Todos los meses</option></select>\n'
    '            <button class="btn pri" onclick="renderNomHist()">Consultar</button>\n'
    '          </div>\n'
    '          <div id="nom-hist"><div class="empty">Selecciona un empleado para ver su historial</div></div>\n'
    '        </div>\n'
    '        <div class="card">\n'
    '          <div class="cl" style="margin-bottom:10px;">Propinas distribuidas</div>\n'
    '          <div class="g2">\n'
    '            <div>\n'
    '              <div class="fr"><label>Fecha</label><input type="date" id="prop-f" style="' + INP + '"></div>\n'
    '              <div class="fr" id="prop-ng-row"><label>Negocio</label><select id="prop-ng" style="' + INP + '"></select></div>\n'
    '              <div class="fr"><label>Total repartido ($)</label><input type="number" id="prop-m" step="0.01" placeholder="0.00" style="' + INP + '" oninput="calcPropinas()"></div>\n'
    '              <div class="fr"><label>Núm. empleados</label><input type="number" id="prop-ne" min="1" placeholder="0" style="' + INP + '" oninput="calcPropinas()"></div>\n'
    '              <div class="calc-box" style="margin-bottom:8px;">\n'
    '                <div class="calc-row"><span>Total repartido</span><span id="prop-tot">$0.00</span></div>\n'
    '                <div class="calc-row"><span>Núm. empleados</span><span id="prop-emp">0</span></div>\n'
    '                <div class="calc-row"><span style="color:var(--a5);">Por persona</span><span id="prop-ppe" style="color:var(--a5);font-weight:500;">$0.00</span></div>\n'
    '              </div>\n'
    '              <div class="fr"><label>Notas</label><input id="prop-n" placeholder="Opcional" style="' + INP + '"></div>\n'
    '              <button class="btn pri" id="btn-sprop" style="width:100%;margin-top:4px;">Registrar propinas</button>\n'
    '            </div>\n'
    '            <div>\n'
    '              <div style="display:flex;gap:6px;margin-bottom:10px;">\n'
    '                <select id="prop-fng" style="flex:1;' + SEL + '"><option value="">Todos los negocios</option></select>\n'
    '                <select id="prop-sem" style="' + SEL + '"><option value="">Todas las semanas</option></select>\n'
    '              </div>\n'
    '              <div id="prop-hist"><div class="empty">Sin propinas registradas</div></div>\n'
    '            </div>\n'
    '          </div>\n'
    '        </div>\n'
    '      </div>\n'
)

c = c.replace(
    '      <div class="sec" id="sec-usuarios">',
    SEC_NOM + '      <div class="sec" id="sec-usuarios">',
    1
)

# ── 3. Modales empleado + nomina-pago (antes del cierre de #mbg) ────────────
MODALS = (
    '\n  <div class="modal" id="m-empleado" style="display:none;">\n'
    '    <h3>Agregar empleado</h3>\n'
    '    <div class="fg2"><div class="fr"><label>Nombre completo</label><input id="empl-n" placeholder="Nombre"></div>'
    '<div class="fr"><label>Puesto</label><input id="empl-p" placeholder="Ej: Cocinero"></div></div>\n'
    '    <div class="fg2"><div class="fr"><label>Salario base ($)</label><input type="number" id="empl-s" step="0.01" placeholder="0.00"></div>'
    '<div class="fr"><label>Tipo de pago</label><select id="empl-t" style="' + INP + '">'
    '<option value="semanal">Semanal</option><option value="quincenal">Quincenal</option><option value="mensual">Mensual</option>'
    '</select></div></div>\n'
    '    <div class="fr" id="empl-ng-row"><label>Negocio</label><select id="empl-ng" style="' + INP + '"></select></div>\n'
    '    <div class="ma"><button class="btn" onclick="closeModal()">Cancelar</button>'
    '<button class="btn pri" id="btn-sempl">Guardar empleado</button></div>\n'
    '  </div>\n'
    '\n  <div class="modal" id="m-nomina-pago" style="display:none;">\n'
    '    <h3>Registrar pago de nómina</h3>\n'
    '    <div class="fr"><label>Empleado</label><select id="npg-emp" style="' + INP + '"><option value="">Selecciona empleado</option></select></div>\n'
    '    <div class="fg2"><div class="fr"><label>Periodo desde</label><input type="date" id="npg-d1" style="' + INP + '"></div>'
    '<div class="fr"><label>Hasta</label><input type="date" id="npg-d2" style="' + INP + '"></div></div>\n'
    '    <div class="fg2"><div class="fr"><label>Fecha de pago</label><input type="date" id="npg-f" style="' + INP + '"></div>'
    '<div class="fr"><label>Monto bruto ($)</label><input type="number" id="npg-m" step="0.01" placeholder="0.00" oninput="calcNomPago()" style="' + INP + '"></div></div>\n'
    '    <div class="fr"><label>Deducciones ($)</label><input type="number" id="npg-x" step="0.01" placeholder="0.00" oninput="calcNomPago()" style="' + INP + '"></div>\n'
    '    <div class="calc-box" style="margin-bottom:8px;">\n'
    '      <div class="calc-row"><span>Bruto</span><span id="npg-br">$0.00</span></div>\n'
    '      <div class="calc-row"><span>Deducciones</span><span id="npg-de" style="color:var(--a3);">-$0.00</span></div>\n'
    '      <div class="calc-row"><span style="font-weight:500;">Neto a pagar</span><span id="npg-ne" style="color:var(--a2);font-weight:600;">$0.00</span></div>\n'
    '    </div>\n'
    '    <div class="fr"><label>Notas</label><input id="npg-n" placeholder="Opcional" style="' + INP + '"></div>\n'
    '    <div class="fr"><label>Comprobante (PDF/foto)</label>\n'
    '      <div class="upload-zone" onclick="document.getElementById(\'npg-w\').click()">'
    '<input type="file" id="npg-w" accept=".pdf,.jpg,.jpeg,.png" style="display:none" onchange="handleNomFile(this)">'
    '<div style="font-size:14px;color:var(--t3);">&#128247;</div>'
    '<div style="font-size:11px;color:var(--t2);">Comprobante de pago</div></div>\n'
    '      <div id="npg-fn" style="font-size:10px;color:var(--t3);margin-top:4px;">Sin comprobante</div>\n'
    '    </div>\n'
    '    <div class="ma"><button class="btn" onclick="closeModal()">Cancelar</button>'
    '<button class="btn pri" id="btn-snpago">Registrar pago</button></div>\n'
    '  </div>\n'
)

c = c.replace(
    '</div>\n\n<script',
    MODALS + '\n</div>\n\n<script',
    1
)

# ── 4. NAV: agregar nominas a propietario y admin_negocio ───────────────────
c = c.replace(
    "propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}]",
    "propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}]",
    1
)
c = c.replace(
    "admin_negocio:[{s:'mi-negocio',i:'◈',l:'Mi negocio',g:'Operación'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'}]",
    "admin_negocio:[{s:'mi-negocio',i:'◈',l:'Mi negocio',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'}]",
    1
)

# ── 5. SMETA: agregar nominas ───────────────────────────────────────────────
c = c.replace(
    "'cierre-caja':{t:'Cierre de caja',s:'POS El Cheff y conciliación'}};",
    "'cierre-caja':{t:'Cierre de caja',s:'POS El Cheff y conciliación'},nominas:{t:'Nóminas',s:'Empleados y pagos de nómina por negocio'}};",
    1
)

# ── 6. showSec R map: agregar nominas ───────────────────────────────────────
c = c.replace(
    "const R={dashboard:renderDash,requisiciones:renderRequisiciones,negocios:renderNegocios,facturas:renderFacturas,ventas:renderVentas,usuarios:renderUsuarios,'mi-negocio':renderMiNegocio,'inv-cocina':renderInvCocina,'inv-barras':renderInvBarras,'cierre-caja':renderCierre};",
    "const R={dashboard:renderDash,requisiciones:renderRequisiciones,negocios:renderNegocios,facturas:renderFacturas,ventas:renderVentas,usuarios:renderUsuarios,'mi-negocio':renderMiNegocio,'inv-cocina':renderInvCocina,'inv-barras':renderInvBarras,'cierre-caja':renderCierre,nominas:renderNominas};",
    1
)

# ── 7. openModalDirect: extender para empleado y nomina-pago ────────────────
c = c.replace(
    "if(type==='usuario'){document.getElementById('u-neg').innerHTML=negocios.map(n=>\"<option value=\\\"\"+(n.id)+\"\\\">\"+(n.nombre)+\"</option>\").join('');toggleNegSel();}",
    "if(type==='usuario'){document.getElementById('u-neg').innerHTML=negocios.map(n=>\"<option value=\\\"\"+(n.id)+\"\\\">\"+(n.nombre)+\"</option>\").join('');toggleNegSel();}"
    "\n  if(type==='empleado'){const esBoss=userData.rol==='propietario';document.getElementById('empl-ng-row').style.display=esBoss?'':'none';if(esBoss)document.getElementById('empl-ng').innerHTML=negocios.map(n=>\"<option value=\\\"\"+(n.id)+\"\\\">\"+(n.nombre)+\"</option>\").join('');}"
    "\n  if(type==='nomina-pago'){const emps=window._nomEmps||[];document.getElementById('npg-emp').innerHTML='<option value=\"\">Selecciona empleado</option>'+emps.map(e=>\"<option value=\\\"\"+(e.id)+\"\\\" data-nid=\\\"\"+(e.negocioId)+\"\\\" data-sal=\\\"\"+(e.salarioBase||0)+\"\\\">\"+(e.nombre)+\"</option>\").join('');['npg-m','npg-x','npg-n'].forEach(function(id){const el=document.getElementById(id);if(el)el.value='';});calcNomPago();}",
    1
)

# ── 8. Nuevas funciones JS ──────────────────────────────────────────────────
NEW_JS = r"""
window.openNomModal=function(type){
  if(!window._nomEmps)window._nomEmps=[];
  openModalDirect(type);
};

window.handleNomFile=function(input){
  const f=input.files[0];if(!f)return;
  window._nomFileData=f;
  const fn=document.getElementById('npg-fn');
  if(fn){fn.textContent='OK: '+f.name;fn.style.color='var(--a2)';}
};

window.calcNomPago=function(){
  const m=parseFloat(document.getElementById('npg-m')?.value)||0;
  const x=parseFloat(document.getElementById('npg-x')?.value)||0;
  if(document.getElementById('npg-br'))document.getElementById('npg-br').textContent='$'+m.toFixed(2);
  if(document.getElementById('npg-de'))document.getElementById('npg-de').textContent='-$'+x.toFixed(2);
  if(document.getElementById('npg-ne'))document.getElementById('npg-ne').textContent='$'+(m-x).toFixed(2);
};

window.calcPropinas=function(){
  const m=parseFloat(document.getElementById('prop-m')?.value)||0;
  const ne=parseInt(document.getElementById('prop-ne')?.value)||0;
  if(document.getElementById('prop-tot'))document.getElementById('prop-tot').textContent='$'+m.toFixed(2);
  if(document.getElementById('prop-emp'))document.getElementById('prop-emp').textContent=ne;
  if(document.getElementById('prop-ppe'))document.getElementById('prop-ppe').textContent='$'+(ne>0?(m/ne).toFixed(2):'0.00');
};

async function renderNominas(){
  const esBoss=['propietario','director'].includes(userData.rol);
  const nid=userData.negocioId;
  const empQ=esBoss?query(collection(db,'empleados'),where('activo','==',true)):query(collection(db,'empleados'),where('negocioId','==',nid),where('activo','==',true));
  const pagQ=esBoss?query(collection(db,'nominas_pagos'),orderBy('creadoEn','desc')):query(collection(db,'nominas_pagos'),where('negocioId','==',nid),orderBy('creadoEn','desc'));
  const [empSnap,pagSnap]=await Promise.all([getDocs(empQ),getDocs(pagQ)]);
  const emps=empSnap.docs.map(function(d){return Object.assign({id:d.id},d.data());});
  const pags=pagSnap.docs.map(function(d){return Object.assign({id:d.id},d.data());});
  const semEmp=emps.filter(function(e){return e.tipo==='semanal';}).reduce(function(a,e){return a+(e.salarioBase||0);},0);
  const quinEmp=emps.filter(function(e){return e.tipo==='quincenal';}).reduce(function(a,e){return a+(e.salarioBase||0);},0);
  const mensEmp=emps.filter(function(e){return e.tipo==='mensual';}).reduce(function(a,e){return a+(e.salarioBase||0);},0);
  document.getElementById('nom-ne').textContent=emps.length;
  document.getElementById('nom-sem').textContent='$'+(semEmp+quinEmp/2.17+mensEmp/4.33).toFixed(2);
  document.getElementById('nom-mes').textContent='$'+(semEmp*4.33+quinEmp*2+mensEmp).toFixed(2);
  const mesAct=new Date().toISOString().substring(0,7);
  document.getElementById('nom-pme').textContent=pags.filter(function(p){return (p.fechaPago||'').startsWith(mesAct);}).length;
  if(esBoss){
    document.getElementById('nom-filt').innerHTML="<div style=\"display:flex;gap:8px;align-items:center;\"><span style=\"font-size:10px;color:var(--t3);\">Filtrar por negocio:</span><select id=\"nom-fng\" style=\"padding:5px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:11px;\"><option value=\"\">Todos</option>"+negocios.map(function(n){return "<option value=\""+n.id+"\">"+n.nombre+"</option>";}).join('')+"</select></div>";
    const fng=document.getElementById('nom-fng');
    if(fng)fng.addEventListener('change',function(){renderNomEmps(emps,pags,this.value);renderNomPagos(pags,this.value);});
  }
  window._nomEmps=emps;window._nomPags=pags;
  renderNomEmps(emps,pags,'');
  renderNomPagos(pags,'');
  const hEl=document.getElementById('nom-hemp');
  if(hEl)hEl.innerHTML='<option value="">Selecciona empleado</option>'+emps.map(function(e){return "<option value=\""+e.id+"\">"+(e.nombre)+(esBoss?' ('+getNegNom(e.negocioId)+')':'')+"</option>";}).join('');
  const meses=[...new Set(pags.map(function(p){return (p.fechaPago||'').substring(0,7);}).filter(Boolean))].sort().reverse();
  const hmEl=document.getElementById('nom-hmes');
  if(hmEl)hmEl.innerHTML='<option value="">Todos los meses</option>'+meses.map(function(m){return "<option value=\""+m+"\">"+m+"</option>";}).join('');
  const td=new Date().toISOString().split('T')[0];
  const pfEl=document.getElementById('prop-f');if(pfEl&&!pfEl.value)pfEl.value=td;
  const ngEl=document.getElementById('prop-ng');
  if(ngEl)ngEl.innerHTML=negocios.map(function(n){return "<option value=\""+n.id+"\">"+n.nombre+"</option>";}).join('');
  const fngEl=document.getElementById('prop-fng');
  if(fngEl)fngEl.innerHTML='<option value="">Todos los negocios</option>'+negocios.map(function(n){return "<option value=\""+n.id+"\">"+n.nombre+"</option>";}).join('');
  const ngRow=document.getElementById('prop-ng-row');
  if(ngRow)ngRow.style.display=esBoss?'':'none';
  renderPropinasHist('','');
}

function renderNomEmps(emps,pags,filtNid){
  const list=filtNid?emps.filter(function(e){return e.negocioId===filtNid;}):emps;
  const el=document.getElementById('nom-empl');
  if(!list.length){el.innerHTML="<div class=\"empty\">Sin empleados"+(filtNid?' en este negocio':'')+"</div>";return;}
  el.innerHTML=list.map(function(e){
    const ultPag=pags.filter(function(p){return p.empleadoId===e.id;}).sort(function(a,b){return (b.fechaPago||'').localeCompare(a.fechaPago||'');})[0];
    return "<div style=\"display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--bd);\">"
      +"<div><div style=\"font-size:12px;font-weight:500;color:var(--t);\">"+e.nombre+"</div>"
      +"<div style=\"font-size:10px;color:var(--t3);margin-top:2px;\">"+e.puesto+" — "+getNegNom(e.negocioId)+" — <span class=\"badge "+(e.tipo==='semanal'?'b':e.tipo==='quincenal'?'a':'g')+"\" style=\"font-size:8px;\">"+e.tipo+"</span></div>"
      +"<div style=\"font-size:9px;color:var(--t3);margin-top:2px;\">Ult. pago: "+(ultPag?ultPag.fechaPago:'Sin registro')+"</div></div>"
      +"<div style=\"text-align:right;flex-shrink:0;\"><div style=\"color:var(--a);font-size:13px;font-weight:500;\">$"+(e.salarioBase||0).toFixed(2)+"</div>"
      +"<button class=\"btn red\" style=\"font-size:9px;padding:1px 5px;margin-top:4px;\" id=\"nbaja-"+e.id+"\">Dar baja</button></div></div>";
  }).join('');
  list.forEach(function(e){
    const b=document.getElementById('nbaja-'+e.id);
    if(b)b.addEventListener('click',async function(){
      if(!confirm('Dar de baja a '+e.nombre+'?'))return;
      await updateDoc(doc(db,'empleados',e.id),{activo:false});
      renderNominas();
    });
  });
}

function renderNomPagos(pags,filtNid){
  const list=(filtNid?pags.filter(function(p){return p.negocioId===filtNid;}):pags).slice(0,20);
  const el=document.getElementById('nom-pagos');
  if(!list.length){el.innerHTML="<div class=\"empty\">Sin pagos registrados</div>";return;}
  el.innerHTML=list.map(function(p){
    return "<div class=\"pago-row\">"
      +"<div style=\"width:8px;height:8px;border-radius:50%;background:"+(p.comprobanteUrl?'var(--a2)':'var(--a3)')+";flex-shrink:0;\"></div>"
      +"<div style=\"flex:1;min-width:0;\">"
      +"<div style=\"font-size:11px;color:var(--t);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;\">"+p.empleadoNombre+" <span style=\"font-size:9px;color:var(--t3);\">"+p.puesto+"</span></div>"
      +"<div style=\"font-size:9px;color:var(--t3);\">"+p.fechaPago+" — "+(p.periodo||'')+" — "+getNegNom(p.negocioId)+"</div></div>"
      +"<div style=\"text-align:right;flex-shrink:0;\">"
      +"<span style=\"font-size:11px;color:var(--a2);font-weight:500;\">$"+(p.neto||p.monto||0).toFixed(2)+"</span>"
      +(p.comprobanteUrl?"<br><a href=\""+p.comprobanteUrl+"\" target=\"_blank\" style=\"font-size:9px;color:var(--a4);\">Comp.</a>":"<br><span style=\"font-size:9px;color:var(--a3);\">Sin comp.</span>")
      +"</div></div>";
  }).join('');
}

window.renderNomHist=async function(){
  const empId=document.getElementById('nom-hemp').value;
  const mes=document.getElementById('nom-hmes').value;
  const el=document.getElementById('nom-hist');
  if(!empId){el.innerHTML="<div class=\"empty\">Selecciona un empleado</div>";return;}
  const snap=await getDocs(query(collection(db,'nominas_pagos'),where('empleadoId','==',empId),orderBy('creadoEn','desc')));
  let pags=snap.docs.map(function(d){return Object.assign({id:d.id},d.data());});
  if(mes)pags=pags.filter(function(p){return (p.fechaPago||'').startsWith(mes);});
  const tot=pags.reduce(function(a,p){return a+(p.neto||p.monto||0);},0);
  const ded=pags.reduce(function(a,p){return a+(p.deducciones||0);},0);
  el.innerHTML=pags.length
    ?"<div class=\"g3\" style=\"margin-bottom:10px;\"><div class=\"card\"><div class=\"cl\">Pagos</div><div class=\"cv b\">"+pags.length+"</div></div><div class=\"card\"><div class=\"cl\">Total neto</div><div class=\"cv g\">$"+tot.toFixed(2)+"</div></div><div class=\"card\"><div class=\"cl\">Deducciones</div><div class=\"cv r\">$"+ded.toFixed(2)+"</div></div></div>"
      +"<table><thead><tr><th>Fecha pago</th><th>Periodo</th><th>Bruto</th><th>Deduc.</th><th>Neto</th><th>Comp.</th><th>Por</th></tr></thead><tbody>"
      +pags.map(function(p){return "<tr><td>"+p.fechaPago+"</td><td style=\"font-size:10px;\">"+(p.periodo||'—')+"</td><td>$"+(p.monto||0).toFixed(2)+"</td><td style=\"color:var(--a3);\">-$"+(p.deducciones||0).toFixed(2)+"</td><td style=\"color:var(--a2);font-weight:500;\">$"+(p.neto||p.monto||0).toFixed(2)+"</td><td>"+(p.comprobanteUrl?"<a href=\""+p.comprobanteUrl+"\" target=\"_blank\" style=\"font-size:10px;color:var(--a4);\">Ver</a>":"<span style=\"font-size:10px;color:var(--t3);\">—</span>")+"</td><td style=\"font-size:10px;color:var(--t3);\">"+(p.registradoPor||'')+"</td></tr>";}).join('')
      +"</tbody></table>"
    :"<div class=\"empty\">Sin pagos"+(mes?" en "+mes:'')+"</div>";
};

async function renderPropinasHist(filtNid,filtSem){
  const esBoss=['propietario','director'].includes(userData.rol);
  const nid=userData.negocioId;
  let q=esBoss?query(collection(db,'ef_pagos'),where('categoria','==','Propinas')):query(collection(db,'ef_pagos'),where('negocioId','==',nid),where('categoria','==','Propinas'));
  const snap=await getDocs(q);
  let props=snap.docs.map(function(d){return Object.assign({id:d.id},d.data());}).sort(function(a,b){return (b.fecha||'').localeCompare(a.fecha||'');});
  if(filtNid)props=props.filter(function(p){return p.negocioId===filtNid;});
  if(filtSem){
    const ws=new Date(filtSem+'T00:00:00');
    const we=new Date(filtSem+'T00:00:00');we.setDate(we.getDate()+6);
    props=props.filter(function(p){if(!p.fecha)return false;const d=new Date(p.fecha+'T00:00:00');return d>=ws&&d<=we;});
  }
  const sems=[...new Set(props.map(function(p){if(!p.fecha)return null;const d=new Date(p.fecha+'T00:00:00');const day=d.getDay();const mon=new Date(d);mon.setDate(d.getDate()-day+(day===0?-6:1));return mon.toISOString().split('T')[0];}).filter(Boolean))].sort().reverse();
  const semSel=document.getElementById('prop-sem');
  if(semSel){const cur=semSel.value;semSel.innerHTML='<option value="">Todas las semanas</option>'+sems.map(function(s){return "<option value=\""+s+"\">"+(s)+"</option>";}).join('');}
  const el=document.getElementById('prop-hist');
  if(!props.length){el.innerHTML="<div class=\"empty\">Sin propinas registradas</div>";return;}
  const tot=props.reduce(function(a,p){return a+(p.monto||0);},0);
  el.innerHTML="<div class=\"g3\" style=\"margin-bottom:8px;\"><div class=\"card\"><div class=\"cl\">Registros</div><div class=\"cv b\">"+props.length+"</div></div><div class=\"card\"><div class=\"cl\">Total repartido</div><div class=\"cv\" style=\"color:var(--a5);\">$"+tot.toFixed(2)+"</div></div><div class=\"card\"><div class=\"cl\">Promedio</div><div class=\"cv\" style=\"color:var(--a5);\">$"+(props.length?tot/props.length:0).toFixed(2)+"</div></div></div>"
    +"<table><thead><tr><th>Fecha</th><th>Negocio</th><th>Total</th><th>Empl.</th><th>Por persona</th><th>Por</th></tr></thead><tbody>"
    +props.map(function(p){return "<tr><td>"+(p.fecha||'')+"</td><td style=\"font-size:10px;\">"+getNegNom(p.negocioId)+"</td><td style=\"color:var(--a5);font-weight:500;\">$"+(p.monto||0).toFixed(2)+"</td><td style=\"text-align:center;\">"+(p.numEmpleados||'—')+"</td><td style=\"color:var(--a5);\">$"+(p.montoPorPersona||0).toFixed(2)+"</td><td style=\"font-size:10px;color:var(--t3);\">"+(p.registradoPor||'')+"</td></tr>";}).join('')
    +"</tbody></table>";
}

document.getElementById('btn-sempl').addEventListener('click',async function(){
  const n=document.getElementById('empl-n').value.trim();
  const p=document.getElementById('empl-p').value.trim();
  const s=parseFloat(document.getElementById('empl-s').value)||0;
  if(!n||!p||!s)return alert('Completa nombre, puesto y salario');
  const nid=userData.rol==='propietario'?document.getElementById('empl-ng').value:userData.negocioId;
  if(!nid)return alert('Selecciona el negocio');
  await addDoc(collection(db,'empleados'),{nombre:n,puesto:p,salarioBase:s,tipo:document.getElementById('empl-t').value,negocioId:nid,activo:true,creadoPor:userData.nombre,creadoEn:serverTimestamp()});
  ['empl-n','empl-p','empl-s'].forEach(function(id){document.getElementById(id).value='';});
  closeModal();renderNominas();alert('Empleado registrado');
});

document.getElementById('btn-snpago').addEventListener('click',async function(){
  const empSel=document.getElementById('npg-emp');
  const empId=empSel.value;
  const opt=empSel.options[empSel.selectedIndex];
  const nid=opt?.dataset?.nid||userData.negocioId;
  const m=parseFloat(document.getElementById('npg-m').value)||0;
  const x=parseFloat(document.getElementById('npg-x').value)||0;
  const f=document.getElementById('npg-f').value;
  if(!empId||!m||!f)return alert('Completa empleado, monto y fecha');
  const btn=this;btn.textContent='Guardando…';btn.disabled=true;
  try{
    let url=null,nom=null;
    if(window._nomFileData){
      const r2=ref(storage,'nominas/'+(nid||'g')+'/'+f+'_'+window._nomFileData.name);
      await uploadBytes(r2,window._nomFileData);url=await getDownloadURL(r2);nom=window._nomFileData.name;
    }
    const emp=(window._nomEmps||[]).find(function(e){return e.id===empId;});
    const d1=document.getElementById('npg-d1').value;
    const d2=document.getElementById('npg-d2').value;
    const periodo=d1&&d2?d1+' al '+d2:d1||'';
    await addDoc(collection(db,'nominas_pagos'),{empleadoId:empId,negocioId:nid||emp?.negocioId,empleadoNombre:emp?.nombre||'',puesto:emp?.puesto||'',periodo,fechaPago:f,monto:m,deducciones:x,neto:m-x,comprobanteUrl:url,comprobante:nom,notas:document.getElementById('npg-n').value,registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    window._nomFileData=null;
    document.getElementById('npg-fn').textContent='Sin comprobante';
    document.getElementById('npg-fn').style.color='var(--t3)';
    ['npg-m','npg-x','npg-n','npg-d1','npg-d2'].forEach(function(id){document.getElementById(id).value='';});
    calcNomPago();closeModal();renderNominas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Registrar pago';btn.disabled=false;
});

document.getElementById('btn-sprop').addEventListener('click',async function(){
  const f=document.getElementById('prop-f').value;
  const m=parseFloat(document.getElementById('prop-m').value)||0;
  const ne=parseInt(document.getElementById('prop-ne').value)||0;
  const esBoss=['propietario','director'].includes(userData.rol);
  const nid=esBoss?document.getElementById('prop-ng').value:userData.negocioId;
  if(!f||!m||!nid)return alert('Completa fecha, negocio y monto');
  const btn=this;btn.textContent='Guardando…';btn.disabled=true;
  try{
    const ppe=ne>0?parseFloat((m/ne).toFixed(2)):0;
    await addDoc(collection(db,'ef_pagos'),{categoria:'Propinas',concepto:'Propinas distribuidas',negocioId:nid,fecha:f,monto:m,numEmpleados:ne,montoPorPersona:ppe,notas:document.getElementById('prop-n').value,registradoPor:userData.nombre,comprobante:null,creadoEn:serverTimestamp()});
    ['prop-m','prop-ne','prop-n'].forEach(function(id){document.getElementById(id).value='';});
    calcPropinas();
    alert('Propinas registradas');
    renderPropinasHist(esBoss?document.getElementById('prop-fng').value:'',document.getElementById('prop-sem').value);
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Registrar propinas';btn.disabled=false;
});

document.getElementById('prop-fng').addEventListener('change',function(){
  renderPropinasHist(this.value,document.getElementById('prop-sem').value);
});
document.getElementById('prop-sem').addEventListener('change',function(){
  renderPropinasHist(document.getElementById('prop-fng').value,this.value);
});
document.getElementById('npg-emp').addEventListener('change',function(){
  const opt=this.options[this.selectedIndex];
  const sal=parseFloat(opt?.dataset?.sal)||0;
  if(sal>0){document.getElementById('npg-m').value=sal.toFixed(2);calcNomPago();}
});
"""

assert '</script>' in c
c = c.replace('</script>', NEW_JS + '\n</script>', 1)

# ── Verificar ────────────────────────────────────────────────────────────────
bt = c.count('`')
assert bt == 0, f'Quedaron {bt} backticks!'

open('public/index.html', 'w', encoding='utf-8').write(c)

checks = ['sec-nominas','nom-ne','nom-empl','nom-pagos','nom-hist','prop-hist',
          'm-empleado','m-nomina-pago','renderNominas','renderNomEmps','renderNomPagos',
          'renderNomHist','renderPropinasHist','calcPropinas','calcNomPago',
          'btn-sempl','btn-snpago','btn-sprop','nominas.*Operaci',
          'nominas.*renderNominas']
import re
for ch in checks:
    found = bool(re.search(ch, c))
    print(('OK' if found else 'FAIL'), ch)

print('Lines:', c.count('\n'))
print('Backticks:', bt)
