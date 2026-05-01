#!/usr/bin/env python3
import sys

with open('public/index.html','r',encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════
# 1. FIX openAdd — requisiciones should scroll to mi-negocio form
#    For propietario/director/admin_negocio viewing requisiciones,
#    open a modal to add a requisicion. We add a modal m-requisicion
#    and map requisiciones→'requisicion' in openAdd.
# ═══════════════════════════════════════════════════════════════════
OLD_OPENADD = "  const map={dashboard:'negocio',requisiciones:null,negocios:'negocio',facturas:'factura',ventas:'venta',usuarios:'usuario','mi-negocio':null,'inv-cocina':null,'inv-barras':null,'cierre-caja':null};"
NEW_OPENADD = "  const map={dashboard:'negocio',requisiciones:'requisicion',negocios:'negocio',facturas:'factura',ventas:'venta',usuarios:'usuario','mi-negocio':null,'inv-cocina':null,'inv-barras':null,'cierre-caja':null,tesoreria:'tesoreria-dep'};"
assert OLD_OPENADD in html, "FAIL: openAdd map not found"
html = html.replace(OLD_OPENADD, NEW_OPENADD, 1)
print("OK openAdd map fixed")

# ═══════════════════════════════════════════════════════════════════
# 2. Update openModalDirect to handle 'requisicion' and 'tesoreria-dep'
# ═══════════════════════════════════════════════════════════════════
OLD_OMD = "  if(type==='nomina-pago'){const emps=window._nomEmps||[];document.getElementById('npg-emp').innerHTML='<option value=\"\">Selecciona empleado</option>'+emps.map(e=>\"<option value=\\\"\"+(e.id)+\"\\\" data-nid=\\\"\"+(e.negocioId)+\"\\\" data-sal=\\\"\"+(e.salarioBase||0)+\"\\\">\"+(e.nombre)+\"</option>\").join('');['npg-m','npg-x','npg-n'].forEach(function(id){const el=document.getElementById(id);if(el)el.value='';});calcNomPago();}\n};"
NEW_OMD = """  if(type==='nomina-pago'){const emps=window._nomEmps||[];document.getElementById('npg-emp').innerHTML='<option value="">Selecciona empleado</option>'+emps.map(e=>"<option value=\\""+e.id+"\\" data-nid=\\""+e.negocioId+"\\" data-sal=\\""+(e.salarioBase||0)+"\\">"+e.nombre+"</option>").join('');['npg-m','npg-x','npg-n'].forEach(function(id){const el=document.getElementById(id);if(el)el.value='';});calcNomPago();}
  if(type==='requisicion'){const el=document.getElementById('req-neg-row');if(el)el.style.display=['propietario','director'].includes(userData.rol)?'':'none';const ns=document.getElementById('req-neg');if(ns)ns.innerHTML=negocios.map(n=>"<option value=\\""+n.id+"\\">"+n.nombre+"</option>").join('');const ws=getWeekStart(new Date().toISOString().split('T')[0]);const ws2=document.getElementById('req-sem');if(ws2&&!ws2.value)ws2.value=ws;}
  if(type==='tesoreria-dep'){const ns=document.getElementById('td-neg');if(ns)ns.innerHTML=negocios.map(n=>"<option value=\\""+n.id+"\\">"+n.nombre+"</option>").join('');const f=document.getElementById('td-fecha');if(f&&!f.value)f.value=new Date().toISOString().split('T')[0];}
};"""

# Check what's actually in the file around nomina-pago
idx = html.find("if(type==='nomina-pago')")
if idx < 0:
    print("FAIL: nomina-pago handler not found")
    sys.exit(1)
# Find the closing }; of openModalDirect
end_idx = html.find('\n};', idx)
assert end_idx > 0, "FAIL: end of openModalDirect not found"
old_block = html[idx:end_idx+3]
new_block = """if(type==='nomina-pago'){const emps=window._nomEmps||[];document.getElementById('npg-emp').innerHTML='<option value="">Selecciona empleado</option>'+emps.map(e=>"<option value=\\""+e.id+"\\" data-nid=\\""+e.negocioId+"\\" data-sal=\\""+(e.salarioBase||0)+"\\">"+e.nombre+"</option>").join('');['npg-m','npg-x','npg-n'].forEach(function(id){const el=document.getElementById(id);if(el)el.value='';});calcNomPago();}
  if(type==='requisicion'){const el=document.getElementById('req-neg-row');if(el)el.style.display=['propietario','director'].includes(userData.rol)?'':'none';const ns=document.getElementById('req-neg');if(ns)ns.innerHTML=negocios.map(n=>"<option value=\\""+n.id+"\\">"+n.nombre+"</option>").join('');const ws=getWeekStart(new Date().toISOString().split('T')[0]);const ws2=document.getElementById('req-sem');if(ws2&&!ws2.value)ws2.value=ws;}
  if(type==='tesoreria-dep'){const ns=document.getElementById('td-neg');if(ns)ns.innerHTML=negocios.map(n=>"<option value=\\""+n.id+"\\">"+n.nombre+"</option>").join('');const f=document.getElementById('td-fecha');if(f&&!f.value)f.value=new Date().toISOString().split('T')[0];}
};"""
html = html[:idx] + new_block + html[end_idx+3:]
print("OK openModalDirect extended")

# ═══════════════════════════════════════════════════════════════════
# 3. NAV — add tesoreria to propietario and director
# ═══════════════════════════════════════════════════════════════════
OLD_NAV_PROP = "  propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'mi-negocio',i:'◈',l:'Mi negocio',g:'Operación'},{s:'inv-cocina',i:'🍽',l:'Cocina',g:'Operación'},{s:'inv-barras',i:'🍹',l:'Barras',g:'Operación'},{s:'cierre-caja',i:'💰',l:'Caja',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}],"
NEW_NAV_PROP = "  propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'tesoreria',i:'◆',l:'Tesorería',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'mi-negocio',i:'◈',l:'Mi negocio',g:'Operación'},{s:'inv-cocina',i:'🍽',l:'Cocina',g:'Operación'},{s:'inv-barras',i:'🍹',l:'Barras',g:'Operación'},{s:'cierre-caja',i:'💰',l:'Caja',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}],"
assert OLD_NAV_PROP in html, "FAIL: propietario NAV not found"
html = html.replace(OLD_NAV_PROP, NEW_NAV_PROP, 1)

OLD_NAV_DIR = "  director:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'}],"
NEW_NAV_DIR = "  director:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'tesoreria',i:'◆',l:'Tesorería',g:'Operación'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'}],"
assert OLD_NAV_DIR in html, "FAIL: director NAV not found"
html = html.replace(OLD_NAV_DIR, NEW_NAV_DIR, 1)
print("OK NAV updated with tesoreria")

# ═══════════════════════════════════════════════════════════════════
# 4. SMETA — add tesoreria entry + fix showSec R map
# ═══════════════════════════════════════════════════════════════════
OLD_SMETA = "const SMETA={dashboard:{t:'Dashboard',s:'Visión consolidada'},requisiciones:{t:'Requisiciones',s:'Solicitudes de fondos'},negocios:{t:'Mis negocios',s:'Cuentas y administradores'},facturas:{t:'Facturas de compra',s:'Registro de compras'},ventas:{t:'Ventas',s:'Desplazamiento de productos'},usuarios:{t:'Usuarios',s:'Accesos al sistema'},'mi-negocio':{t:'Mi negocio',s:'Requisiciones y reportes'},'inv-cocina':{t:'Inventario cocina',s:'Cierre diario y cuadre vs ventas'},'inv-barras':{t:'Inventario barras',s:'Bebidas, guarnición y cuadre'},'cierre-caja':{t:'Cierre de caja',s:'POS El Cheff y conciliación'},nominas:{t:'Nóminas',s:'Empleados y pagos de nómina por negocio'}};"
NEW_SMETA = "const SMETA={dashboard:{t:'Dashboard',s:'Visión consolidada'},requisiciones:{t:'Requisiciones',s:'Solicitudes de fondos'},tesoreria:{t:'Tesorería',s:'Cuenta maestra y distribución por negocio'},negocios:{t:'Mis negocios',s:'Cuentas y administradores'},facturas:{t:'Facturas de compra',s:'Registro de compras'},ventas:{t:'Ventas',s:'Desplazamiento de productos'},usuarios:{t:'Usuarios',s:'Accesos al sistema'},'mi-negocio':{t:'Mi negocio',s:'Requisiciones y reportes'},'inv-cocina':{t:'Inventario cocina',s:'Cierre diario y cuadre vs ventas'},'inv-barras':{t:'Inventario barras',s:'Bebidas, guarnición y cuadre'},'cierre-caja':{t:'Cierre de caja',s:'POS El Cheff y conciliación'},nominas:{t:'Nóminas',s:'Empleados y pagos de nómina por negocio'}};"
assert OLD_SMETA in html, "FAIL: SMETA not found"
html = html.replace(OLD_SMETA, NEW_SMETA, 1)
print("OK SMETA updated")

# ═══════════════════════════════════════════════════════════════════
# 5. showSec R map — add tesoreria:renderTesoreria
# ═══════════════════════════════════════════════════════════════════
OLD_RMAP = "  const R={dashboard:renderDash,requisiciones:renderRequisiciones,negocios:renderNegocios,facturas:renderFacturas,ventas:renderVentas,usuarios:renderUsuarios,'mi-negocio':renderMiNegocio,'inv-cocina':renderInvCocina,'inv-barras':renderInvBarras,'cierre-caja':renderCierre,nominas:renderNominas};"
NEW_RMAP = "  const R={dashboard:renderDash,requisiciones:renderRequisiciones,tesoreria:renderTesoreria,negocios:renderNegocios,facturas:renderFacturas,ventas:renderVentas,usuarios:renderUsuarios,'mi-negocio':renderMiNegocio,'inv-cocina':renderInvCocina,'inv-barras':renderInvBarras,'cierre-caja':renderCierre,nominas:renderNominas};"
assert OLD_RMAP in html, "FAIL: showSec R map not found"
html = html.replace(OLD_RMAP, NEW_RMAP, 1)
print("OK showSec R map updated")

# ═══════════════════════════════════════════════════════════════════
# 6. HTML — add sec-tesoreria before sec-usuarios
#           and upgrade sec-mi-negocio with Excel upload
# ═══════════════════════════════════════════════════════════════════
OLD_SECUSR = '      <div class="sec" id="sec-usuarios">'
NEW_SECUSR = '''      <div class="sec" id="sec-tesoreria">
        <div class="g4" style="margin-bottom:12px;">
          <div class="card"><div class="cl">Saldo cuenta maestra</div><div class="cv a" id="ts-master">$0</div></div>
          <div class="card"><div class="cl">Distribuido</div><div class="cv r" id="ts-dist">$0</div></div>
          <div class="card"><div class="cl">Dep&oacute;sitos mes</div><div class="cv g" id="ts-dep-mes">$0</div></div>
          <div class="card"><div class="cl">Movimientos hoy</div><div class="cv b" id="ts-hoy">0</div></div>
        </div>
        <div class="g2" style="margin-bottom:12px;">
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Depositar a cuenta maestra</div>
            <div class="fr"><label>Fecha</label><input type="date" id="ts-dep-fecha" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="fr"><label>Monto ($)</label><input type="number" id="ts-dep-monto" step="0.01" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="fr"><label>Concepto</label><input id="ts-dep-concepto" placeholder="Descripci&oacute;n del dep&oacute;sito" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <button class="btn pri" style="width:100%;" onclick="tesoDepositar()">+ Depositar</button>
          </div>
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Distribuir a negocio</div>
            <div class="fr"><label>Negocio</label><select id="ts-dist-neg" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></select></div>
            <div class="fr"><label>Fecha</label><input type="date" id="ts-dist-fecha" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="fr"><label>Monto ($)</label><input type="number" id="ts-dist-monto" step="0.01" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="fr"><label>Concepto / Semana</label><input id="ts-dist-concepto" placeholder="Ej: Semana 15 &mdash; Operaci&oacute;n" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="fr"><label>Umbral de alerta ($)</label><input type="number" id="ts-dist-umbral" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <button class="btn grn" style="width:100%;" onclick="tesoDistribuir()">&#10140; Distribuir</button>
          </div>
        </div>
        <div class="card" style="margin-bottom:12px;">
          <div class="cl" style="margin-bottom:8px;">Saldos por negocio</div>
          <div id="ts-saldos-neg"><div class="empty">Sin datos</div></div>
        </div>
        <div class="card" style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div class="cl">Historial de movimientos</div>
            <select id="ts-filt-neg" style="padding:5px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:11px;" onchange="renderTesoHist()"><option value="">Todos los negocios</option></select>
          </div>
          <div id="ts-historial"><div class="empty">Sin movimientos</div></div>
        </div>
        <div class="card">
          <div class="cl" style="margin-bottom:8px;">Conciliaci&oacute;n semanal</div>
          <div style="display:flex;gap:8px;margin-bottom:8px;align-items:center;">
            <input type="date" id="ts-conc-sem" style="padding:5px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:11px;">
            <select id="ts-conc-neg" style="flex:1;padding:5px 8px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:11px;"><option value="">Todos</option></select>
            <button class="btn pri" onclick="renderConciliacion()">Consultar</button>
          </div>
          <div id="ts-conc-result"><div class="empty">Selecciona semana para conciliar</div></div>
        </div>
      </div>

      <div class="sec" id="sec-usuarios">'''

assert OLD_SECUSR in html, "FAIL: sec-usuarios not found"
html = html.replace(OLD_SECUSR, NEW_SECUSR, 1)
print("OK sec-tesoreria inserted")

# ═══════════════════════════════════════════════════════════════════
# 7. UPGRADE sec-mi-negocio — add Excel upload to requisicion form
# ═══════════════════════════════════════════════════════════════════
OLD_REQ_CARD = '''          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Nueva requisición</div>
            <div class="fr"><label>Subir PDF de gastos (opcional — IA extrae monto y notas)</label>
              <div class="upload-zone" onclick="document.getElementById('mn-req-pdf').click()" id="mn-req-pdf-zone"><input type="file" id="mn-req-pdf" accept=".pdf" onchange="analizarReqPDF(this)" style="display:none"><div style="font-size:18px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);">PDF de facturas / gastos de la semana</div></div>
              <div id="mn-req-pdf-status" style="font-size:10px;color:var(--t3);margin-top:4px;"></div>
            </div>
            <div class="fr"><label>Monto ($)</label><input id="mn-monto" type="number" step="0.01" placeholder="0.00"></div>
            <div class="fr"><label>Semana del</label><input id="mn-semana" type="date"></div>
            <div class="fr"><label>Motivo</label><textarea id="mn-motivo" placeholder="¿Para qué se usarán los fondos?"></textarea></div>
            <button class="btn pri" style="width:100%;" onclick="crearRequisicion()">Enviar al propietario</button>
          </div>'''

NEW_REQ_CARD = '''          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Nueva requisición</div>
            <div style="display:flex;gap:6px;margin-bottom:10px;">
              <button class="btn pri" id="req-tab-form" onclick="reqTab('form')" style="font-size:11px;">&#9998; Formulario</button>
              <button class="btn" id="req-tab-xlsx" onclick="reqTab('xlsx')" style="font-size:11px;">&#128202; Excel</button>
              <button class="btn" id="req-tab-pdf" onclick="reqTab('pdf')" style="font-size:11px;">&#129302; PDF + IA</button>
            </div>
            <div id="req-form-panel">
              <div class="fr"><label>Monto ($)</label><input id="mn-monto" type="number" step="0.01" placeholder="0.00"></div>
              <div class="fr"><label>Semana del</label><input id="mn-semana" type="date"></div>
              <div class="fr"><label>Motivo</label><textarea id="mn-motivo" placeholder="Para qu&eacute; se usar&aacute;n los fondos?"></textarea></div>
              <button class="btn pri" style="width:100%;" onclick="crearRequisicion()">Enviar al propietario</button>
            </div>
            <div id="req-xlsx-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('req-xlsx-file').click()"><input type="file" id="req-xlsx-file" accept=".xlsx,.xls" onchange="importReqXLSX(this)" style="display:none"><div style="font-size:20px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);">Excel de gastos de la semana</div><div style="font-size:10px;color:var(--t3);margin-top:2px;">Columnas: FECHA &middot; PROVEEDOR &middot; FOLIO &middot; DESCRIPCION &middot; OBSERVACIONES &middot; MONTO &middot; CLABE</div></div>
              <div id="req-xlsx-preview"></div>
            </div>
            <div id="req-pdf-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('mn-req-pdf').click()" id="mn-req-pdf-zone"><input type="file" id="mn-req-pdf" accept=".pdf" onchange="analizarReqPDF(this)" style="display:none"><div style="font-size:20px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);">PDF de facturas &mdash; Claude extrae proveedores y montos</div></div>
              <div id="mn-req-pdf-status" style="font-size:10px;color:var(--t3);margin-top:4px;"></div>
              <div class="fr" style="margin-top:8px;"><label>Monto total ($)</label><input id="mn-monto-pdf" type="number" step="0.01" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
              <div class="fr"><label>Semana del</label><input id="mn-semana-pdf" type="date" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
              <div class="fr"><label>Motivo / Resumen</label><textarea id="mn-motivo-pdf" placeholder="Extracto de Claude..."></textarea></div>
              <button class="btn pri" style="width:100%;" onclick="crearRequisicionPDF()">Enviar al propietario</button>
            </div>
          </div>'''

assert OLD_REQ_CARD in html, "FAIL: req card in mi-negocio not found"
html = html.replace(OLD_REQ_CARD, NEW_REQ_CARD, 1)
print("OK mi-negocio req card upgraded")

# ═══════════════════════════════════════════════════════════════════
# 8. MODALS — add m-requisicion before <!-- MODALS -->
# ═══════════════════════════════════════════════════════════════════
OLD_MBG = "\n<!-- MODALS -->\n<div class=\"modal-bg\" id=\"mbg\""
NEW_MBG = """
<!-- MODALS -->
<div class="modal-bg" id="mbg\""""

OLD_MODAL_NEG = '  <div class="modal" id="m-negocio" style="display:none;">'
NEW_MODAL_NEG = '''  <div class="modal" id="m-requisicion" style="display:none;">
    <h3>Nueva requisici&oacute;n</h3>
    <div class="fr" id="req-neg-row"><label>Negocio</label><select id="req-neg" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></select></div>
    <div class="fg2"><div class="fr"><label>Semana del</label><input type="date" id="req-sem" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div><div class="fr"><label>Monto ($)</label><input type="number" id="req-monto" step="0.01" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div></div>
    <div class="fr"><label>Motivo</label><textarea id="req-motivo" placeholder="Para qu&eacute; se usar&aacute;n los fondos?" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;height:60px;resize:vertical;"></textarea></div>
    <div class="ma"><button class="btn" onclick="closeModal()">Cancelar</button><button class="btn pri" onclick="saveRequisicionModal()">Enviar</button></div>
  </div>

  <div class="modal" id="m-tesoreria-dep" style="display:none;">
    <h3>Depositar a cuenta maestra</h3>
    <div class="fr"><label>Fecha</label><input type="date" id="td-fecha" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
    <div class="fr"><label>Monto ($)</label><input type="number" id="td-monto" step="0.01" placeholder="0.00" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
    <div class="fr"><label>Concepto</label><input id="td-concepto" placeholder="Descripci&oacute;n del dep&oacute;sito" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
    <div class="fr"><label>Negocio origen (opcional)</label><select id="td-neg" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"><option value="">Cuenta maestra general</option></select></div>
    <div class="ma"><button class="btn" onclick="closeModal()">Cancelar</button><button class="btn pri" onclick="saveTesoDeposito()">Depositar</button></div>
  </div>

  <div class="modal" id="m-negocio" style="display:none;">'''

assert OLD_MODAL_NEG in html, "FAIL: m-negocio modal not found"
html = html.replace(OLD_MODAL_NEG, NEW_MODAL_NEG, 1)
print("OK modals m-requisicion and m-tesoreria-dep added")

# ═══════════════════════════════════════════════════════════════════
# 9. JS — all new functions
# ═══════════════════════════════════════════════════════════════════
NEW_JS = r"""
/* ── TESORERIA ───────────────────────────────────────────────────── */

async function renderTesoreria(){
  const negId=userData.negocioId||negocios[0]?.id;
  const today=new Date().toISOString().split('T')[0];
  const mesAct=today.substring(0,7);
  const [movSnap]=await Promise.all([
    getDocs(query(collection(db,'tesoreria_movimientos'),orderBy('creadoEn','desc')))
  ]);
  const movs=movSnap.docs.map(function(d){return Object.assign({id:d.id},d.data());});
  const deps=movs.filter(function(m){return m.tipo==='deposito';});
  const dists=movs.filter(function(m){return m.tipo==='distribucion';});
  const totalDep=deps.reduce(function(a,m){return a+(m.monto||0);},0);
  const totalDist=dists.reduce(function(a,m){return a+(m.monto||0);},0);
  const saldoMaestro=totalDep-totalDist;
  document.getElementById('ts-master').textContent='$'+saldoMaestro.toFixed(2);
  document.getElementById('ts-dist').textContent='$'+totalDist.toFixed(2);
  const depMes=deps.filter(function(m){return (m.fecha||'').startsWith(mesAct);}).reduce(function(a,m){return a+(m.monto||0);},0);
  document.getElementById('ts-dep-mes').textContent='$'+depMes.toFixed(2);
  document.getElementById('ts-hoy').textContent=movs.filter(function(m){return m.fecha===today;}).length;
  const f=document.getElementById('ts-dep-fecha');if(f&&!f.value)f.value=today;
  const df=document.getElementById('ts-dist-fecha');if(df&&!df.value)df.value=today;
  const dn=document.getElementById('ts-dist-neg');
  if(dn)dn.innerHTML=negocios.map(function(n){return "<option value='"+n.id+"'>"+n.nombre+"</option>";}).join('');
  const fn=document.getElementById('ts-filt-neg');
  if(fn)fn.innerHTML='<option value="">Todos los negocios</option>'+negocios.map(function(n){return "<option value='"+n.id+"'>"+n.nombre+"</option>";}).join('');
  const cn=document.getElementById('ts-conc-neg');
  if(cn)cn.innerHTML='<option value="">Todos</option>'+negocios.map(function(n){return "<option value='"+n.id+"'>"+n.nombre+"</option>";}).join('');
  const cw=document.getElementById('ts-conc-sem');
  if(cw&&!cw.value)cw.value=getWeekStart(today);
  window._tesoMovs=movs;
  renderSaldosNeg(movs);
  renderTesoHist();
}

function renderSaldosNeg(movs){
  const el=document.getElementById('ts-saldos-neg');
  if(!negocios.length){el.innerHTML="<div class='empty'>Sin negocios</div>";return;}
  const saldos=negocios.map(function(n){
    const recibido=movs.filter(function(m){return m.tipo==='distribucion'&&m.negocioId===n.id;}).reduce(function(a,m){return a+(m.monto||0);},0);
    const gastado=movs.filter(function(m){return m.tipo==='gasto'&&m.negocioId===n.id;}).reduce(function(a,m){return a+(m.monto||0);},0);
    const saldo=recibido-gastado;
    const umbral=n.umbral||0;
    return{n,recibido,gastado,saldo,alerta:umbral>0&&saldo<umbral};
  });
  el.innerHTML="<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;'>"+saldos.map(function(s){
    return "<div class='card' style='border-left:3px solid "+(s.alerta?'var(--a3)':s.n.color||'var(--a)')+";'>"
      +"<div style='display:flex;align-items:center;gap:6px;margin-bottom:4px;'><div style='width:8px;height:8px;border-radius:50%;background:"+(s.n.color||'#e8c87a')+"'></div><div style='font-size:11px;font-weight:500;color:var(--t);'>"+s.n.nombre+"</div></div>"
      +"<div style='font-size:18px;font-weight:600;color:"+(s.alerta?'var(--a3)':s.saldo>=0?'var(--a2)':'var(--a3)')+"'>$"+s.saldo.toFixed(2)+"</div>"
      +(s.alerta?"<div style='font-size:9px;color:var(--a3);margin-top:2px;'>&#9888; Bajo umbral</div>":'')
      +"<div style='font-size:9px;color:var(--t3);margin-top:3px;'>Rec: $"+s.recibido.toFixed(2)+" &middot; Gas: $"+s.gastado.toFixed(2)+"</div>"
      +"</div>";
  }).join('')+"</div>";
}

window.renderTesoHist=function(){
  const movs=window._tesoMovs||[];
  const filtNeg=document.getElementById('ts-filt-neg')?.value||'';
  const list=(filtNeg?movs.filter(function(m){return m.negocioId===filtNeg||(!m.negocioId&&!filtNeg);}):movs).slice(0,50);
  const el=document.getElementById('ts-historial');
  if(!list.length){el.innerHTML="<div class='empty'>Sin movimientos</div>";return;}
  el.innerHTML="<table><thead><tr><th>Fecha</th><th>Tipo</th><th>Negocio</th><th>Concepto</th><th>Monto</th><th>Por</th></tr></thead><tbody>"
    +list.map(function(m){
      const tipoBadge=m.tipo==='deposito'?"<span class='badge g'>Dep&oacute;sito</span>":m.tipo==='distribucion'?"<span class='badge b'>Distribuc&oacute;n</span>":"<span class='badge r'>Gasto</span>";
      return "<tr><td>"+(m.fecha||'—')+"</td><td>"+tipoBadge+"</td><td style='font-size:10px;'>"+getNegNom(m.negocioId)+"</td><td style='font-size:11px;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>"+(m.concepto||'—')+"</td><td style='font-family:monospace;color:"+(m.tipo==='deposito'?'var(--a2)':'var(--a3)')+"'>"+(m.tipo==='deposito'?'+':'-')+"$"+(m.monto||0).toFixed(2)+"</td><td style='font-size:10px;color:var(--t3);'>"+(m.registradoPor||'—')+"</td></tr>";
    }).join('')+"</tbody></table>";
};

window.renderConciliacion=async function(){
  const sem=document.getElementById('ts-conc-sem')?.value||'';
  const filtNeg=document.getElementById('ts-conc-neg')?.value||'';
  const el=document.getElementById('ts-conc-result');
  if(!sem){el.innerHTML="<div class='empty'>Selecciona semana</div>";return;}
  el.innerHTML="<div class='abox info'><span class='spin'></span> Calculando...</div>";
  const semEnd=new Date(sem+'T00:00:00');semEnd.setDate(semEnd.getDate()+6);
  const semEndStr=semEnd.toISOString().split('T')[0];
  const inRange=function(f){return f>=sem&&f<=semEndStr;};
  const movs=window._tesoMovs||[];
  const deps=movs.filter(function(m){return m.tipo==='deposito'&&inRange(m.fecha||'');});
  const dists=movs.filter(function(m){return m.tipo==='distribucion'&&inRange(m.fecha||'')&&(!filtNeg||m.negocioId===filtNeg);});
  const reqSnap=await getDocs(query(collection(db,'requisiciones'),where('estado','==','aprobada')));
  const reqSem=reqSnap.docs.map(function(d){return d.data();}).filter(function(r){return r.semana>=sem&&r.semana<=semEndStr&&(!filtNeg||r.negocioId===filtNeg);});
  const totalDep=deps.reduce(function(a,m){return a+(m.monto||0);},0);
  const totalDist=dists.reduce(function(a,m){return a+(m.monto||0);},0);
  const totalReq=reqSem.reduce(function(a,r){return a+(r.monto||0);},0);
  const diff=totalDist-totalReq;
  el.innerHTML="<div class='g3' style='margin-bottom:10px;'>"
    +"<div class='card'><div class='cl'>Dep&oacute;sitos semana</div><div class='cv g'>$"+totalDep.toFixed(2)+"</div></div>"
    +"<div class='card'><div class='cl'>Distribuido</div><div class='cv b'>$"+totalDist.toFixed(2)+"</div></div>"
    +"<div class='card'><div class='cl'>Req. aprobadas</div><div class='cv a'>$"+totalReq.toFixed(2)+"</div></div>"
    +"</div>"
    +"<div class='"+(Math.abs(diff)<100?'cuadre-ok':'cuadre-err')+"'>"
    +"<div style='font-size:11px;'>Diferencia distribuido vs requisiciones: <span style='font-weight:600;color:"+(Math.abs(diff)<100?'var(--a2)':'var(--a3)')+"'>"+(diff>=0?'+':'')+"$"+diff.toFixed(2)+"</span></div>"
    +(Math.abs(diff)>=100?"<div style='font-size:10px;margin-top:3px;color:var(--a3);'>Revisar: hay diferencia entre lo distribuido y las requisiciones aprobadas</div>":'<div style="font-size:10px;margin-top:3px;color:var(--a2);">Cuadre OK</div>')
    +"</div>";
};

window.tesoDepositar=async function(){
  const fecha=document.getElementById('ts-dep-fecha')?.value||'';
  const monto=parseFloat(document.getElementById('ts-dep-monto')?.value)||0;
  const concepto=document.getElementById('ts-dep-concepto')?.value||'';
  if(!fecha||!monto||!concepto)return alert('Completa fecha, monto y concepto');
  const btn=event.target;btn.textContent='Guardando...';btn.disabled=true;
  try{
    await addDoc(collection(db,'tesoreria_movimientos'),{tipo:'deposito',fecha,monto,concepto,negocioId:null,registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    document.getElementById('ts-dep-monto').value='';document.getElementById('ts-dep-concepto').value='';
    renderTesoreria();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='+ Depositar';btn.disabled=false;
};

window.tesoDistribuir=async function(){
  const negId=document.getElementById('ts-dist-neg')?.value||'';
  const fecha=document.getElementById('ts-dist-fecha')?.value||'';
  const monto=parseFloat(document.getElementById('ts-dist-monto')?.value)||0;
  const concepto=document.getElementById('ts-dist-concepto')?.value||'';
  const umbral=parseFloat(document.getElementById('ts-dist-umbral')?.value)||0;
  if(!negId||!fecha||!monto)return alert('Completa negocio, fecha y monto');
  const btn=event.target;btn.textContent='Distribuyendo...';btn.disabled=true;
  try{
    await addDoc(collection(db,'tesoreria_movimientos'),{tipo:'distribucion',fecha,monto,concepto,negocioId:negId,registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    if(umbral>0){
      const negRef=doc(db,'negocios',negId);
      await updateDoc(negRef,{umbral});
      const ni=negocios.findIndex(function(n){return n.id===negId;});
      if(ni>=0)negocios[ni].umbral=umbral;
    }
    document.getElementById('ts-dist-monto').value='';document.getElementById('ts-dist-concepto').value='';
    renderTesoreria();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='→ Distribuir';btn.disabled=false;
};

window.saveTesoDeposito=async function(){
  const fecha=document.getElementById('td-fecha')?.value||'';
  const monto=parseFloat(document.getElementById('td-monto')?.value)||0;
  const concepto=document.getElementById('td-concepto')?.value||'';
  const negId=document.getElementById('td-neg')?.value||null;
  if(!fecha||!monto||!concepto)return alert('Completa fecha, monto y concepto');
  const btn=event.target;btn.textContent='Guardando...';btn.disabled=true;
  try{
    await addDoc(collection(db,'tesoreria_movimientos'),{tipo:'deposito',fecha,monto,concepto,negocioId:negId||null,registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    closeModal();renderTesoreria();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Depositar';btn.disabled=false;
};

/* ── REQUISICION MODAL ───────────────────────────────────────────── */

window.saveRequisicionModal=async function(){
  const semana=document.getElementById('req-sem')?.value||'';
  const monto=parseFloat(document.getElementById('req-monto')?.value)||0;
  const motivo=document.getElementById('req-motivo')?.value.trim()||'';
  const esBoss=['propietario','director'].includes(userData.rol);
  const negId=esBoss?document.getElementById('req-neg')?.value:userData.negocioId;
  if(!semana||!monto||!motivo||!negId)return alert('Completa todos los campos');
  const btn=event.target;btn.textContent='Enviando...';btn.disabled=true;
  try{
    await addDoc(collection(db,'requisiciones'),{negocioId:negId,semana,monto,motivo,adminNombre:userData.nombre,adminEmail:currentUser.email,estado:'pendiente',creadoEn:serverTimestamp()});
    closeModal();renderRequisiciones();renderDash();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Enviar';btn.disabled=false;
};

/* ── REQUISICION TAB + EXCEL + PDF mejorado ─────────────────────── */

window.reqTab=function(tab){
  ['form','xlsx','pdf'].forEach(function(t){
    var p=document.getElementById('req-'+t+'-panel');
    if(p)p.style.display=t===tab?'':'none';
    var b=document.getElementById('req-tab-'+t);
    if(b)b.className=t===tab?'btn pri':'btn';
  });
  if(tab==='pdf'){
    var k=localStorage.getItem('ant_key');
    var inp=document.getElementById('fac-api-key');
    if(k&&inp&&!inp.value)inp.value=k;
  }
};

window.importReqXLSX=function(input){
  var file=input.files[0];if(!file)return;
  if(typeof XLSX==='undefined'){alert('SheetJS no cargo.');return;}
  var prev=document.getElementById('req-xlsx-preview');
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'>Procesando Excel...</div>";
  var reader=new FileReader();
  reader.onload=function(e){
    try{
      var wb=XLSX.read(e.target.result,{type:'array',cellDates:true,raw:false,defval:''});
      var ws=wb.Sheets[wb.SheetNames[0]];
      var rows=XLSX.utils.sheet_to_json(ws,{header:1,raw:false,defval:''});
      if(rows.length<2){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Archivo vacio</div>";return;}
      var hdrs=rows[0].map(function(h){return String(h||'').toUpperCase().trim();});
      var fi=function(kws){for(var k=0;k<kws.length;k++){var idx=hdrs.findIndex(function(h){return h.includes(kws[k]);});if(idx>-1)return idx;}return -1;};
      var cols={fecha:fi(['FECHA']),prov:fi(['PROVEEDOR','VENDOR','EMISOR']),folio:fi(['FOLIO','FACTURA','NUM']),desc:fi(['DESCRIPCION','CONCEPTO','DESCRIPCI']),obs:fi(['OBSERVACION','NOTAS','OBS']),monto:fi(['MONTO','TOTAL','IMPORTE','AMOUNT']),clabe:fi(['CLABE','CUENTA','BANK'])};
      var fmtDate=function(v){if(!v)return '';var d=new Date(v);if(!isNaN(d.getTime()))return d.toISOString().split('T')[0];return String(v).substring(0,10);};
      var fmtNum=function(v){return parseFloat(String(v||0).replace(/[$,\s]/g,''))||0;};
      var data=rows.slice(1).filter(function(r){return r.some(function(c){return String(c||'').trim();});}).map(function(r){
        return{fecha:fmtDate(cols.fecha>=0?r[cols.fecha]:''),prov:cols.prov>=0?String(r[cols.prov]||''):'',folio:cols.folio>=0?String(r[cols.folio]||''):'',desc:cols.desc>=0?String(r[cols.desc]||''):'',obs:cols.obs>=0?String(r[cols.obs]||''):'',monto:fmtNum(cols.monto>=0?r[cols.monto]:0),clabe:cols.clabe>=0?String(r[cols.clabe]||''):''};
      }).filter(function(r){return r.prov&&r.monto>0;});
      if(!data.length){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>No se detectaron registros con proveedor y monto</div>";return;}
      var totMonto=data.reduce(function(a,r){return a+(r.monto||0);},0);
      var IS='padding:3px 5px;background:var(--s2);border:1px solid var(--bd);border-radius:4px;color:var(--t);font-size:10px;width:100%;';
      var h="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>"+data.length+" proveedor"+(data.length!==1?'es':'')+" &mdash; Total: $"+totMonto.toFixed(2)+"</div>";
      h+="<div style='overflow-x:auto;'><table><thead><tr><th>Fecha</th><th>Proveedor</th><th>Folio</th><th>Descripci&oacute;n</th><th>Monto</th></tr></thead><tbody>";
      data.forEach(function(r,i){
        h+="<tr>"
          +"<td><input id='rq-f-"+i+"' value='"+r.fecha+"' style='width:90px;"+IS+"'></td>"
          +"<td><input id='rq-p-"+i+"' value=\""+r.prov.replace(/"/g,'')+"\" style='width:120px;"+IS+"'></td>"
          +"<td><input id='rq-fo-"+i+"' value=\""+r.folio.replace(/"/g,'')+"\" style='width:80px;"+IS+"'></td>"
          +"<td><input id='rq-d-"+i+"' value=\""+r.desc.replace(/"/g,'')+"\" style='width:150px;"+IS+"'></td>"
          +"<td style='color:var(--a);font-weight:500;'>$"+r.monto.toFixed(2)+"</td></tr>";
      });
      h+="</tbody></table></div>";
      h+="<div class='fr' style='margin-top:10px;'><label>Semana del</label><input type='date' id='rq-xl-sem' style='width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;' value='"+(getWeekStart(new Date().toISOString().split('T')[0])||'')+"'></div>";
      h+="<div class='fr'><label>Notas adicionales (opcional)</label><textarea id='rq-xl-notas' style='width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;height:50px;resize:vertical;' placeholder='Observaciones...'></textarea></div>";
      h+="<button class='btn pri' style='width:100%;margin-top:6px;' onclick='guardarReqXLSX("+data.length+","+totMonto.toFixed(2)+")'>Enviar requisici&oacute;n $"+totMonto.toFixed(2)+"</button></div>";
      prev.innerHTML=h;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarReqXLSX=async function(count,totMonto){
  var semana=document.getElementById('rq-xl-sem')?.value||'';
  var notas=document.getElementById('rq-xl-notas')?.value||'';
  if(!semana)return alert('Selecciona la semana');
  var partidas=[];
  for(var i=0;i<count;i++){
    var prov=document.getElementById('rq-p-'+i)?.value||'';if(!prov)continue;
    partidas.push({proveedor:prov,folio:document.getElementById('rq-fo-'+i)?.value||'',descripcion:document.getElementById('rq-d-'+i)?.value||'',fecha:document.getElementById('rq-f-'+i)?.value||''});
  }
  var motivo='Gastos semana '+semana+': '+partidas.map(function(p){return p.proveedor;}).join(', ')+(notas?'. '+notas:'');
  var btn=event.target;btn.textContent='Enviando...';btn.disabled=true;
  try{
    await addDoc(collection(db,'requisiciones'),{negocioId:userData.negocioId,semana,monto:totMonto,motivo,partidas,adminNombre:userData.nombre,adminEmail:currentUser.email,estado:'pendiente',fuente:'excel',creadoEn:serverTimestamp()});
    document.getElementById('req-xlsx-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>Requisicion enviada por $"+totMonto.toFixed(2)+"</div>";
    document.getElementById('req-xlsx-file').value='';
    renderMiNegocio();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Enviar requisicion';btn.disabled=false;
};

window.crearRequisicionPDF=async function(){
  var monto=parseFloat(document.getElementById('mn-monto-pdf')?.value)||0;
  var semana=document.getElementById('mn-semana-pdf')?.value||'';
  var motivo=document.getElementById('mn-motivo-pdf')?.value.trim()||'';
  if(!monto||!semana||!motivo)return alert('Completa monto, semana y motivo');
  var btn=event.target;btn.textContent='Enviando...';btn.disabled=true;
  try{
    await addDoc(collection(db,'requisiciones'),{negocioId:userData.negocioId,semana,monto,motivo,adminNombre:userData.nombre,adminEmail:currentUser.email,estado:'pendiente',fuente:'pdf-ia',creadoEn:serverTimestamp()});
    ['mn-monto-pdf','mn-semana-pdf','mn-motivo-pdf'].forEach(function(id){var el=document.getElementById(id);if(el)el.value='';});
    alert('Requisicion enviada');renderMiNegocio();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Enviar al propietario';btn.disabled=false;
};

window.analizarReqPDF=async function(input){
  var file=input.files[0];if(!file)return;
  var apiKey=localStorage.getItem('ant_key')||'';
  var status=document.getElementById('mn-req-pdf-status');
  var zone=document.getElementById('mn-req-pdf-zone');
  if(!apiKey){status.textContent='Sin API Key. Usala primero en Facturas > PDF+IA.';status.style.color='var(--a3)';return;}
  zone.style.borderColor='var(--a4)';status.style.color='var(--a4)';status.textContent='Analizando con Claude...';
  var reader=new FileReader();
  reader.onload=async function(e){
    try{
      var bytes=new Uint8Array(e.target.result);
      var b64='';var CHUNK=8192;
      for(var i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
      var resp=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:1000,messages:[{role:'user',content:[{type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},{type:'text',text:'Analiza este documento de gastos/facturas. Responde SOLO con JSON: {"total":0.00,"resumen":"descripcion breve para motivo de requisicion","proveedores":[{"nombre":"proveedor","concepto":"descripcion","monto":0.00}]}'}]}]})});
      if(!resp.ok){var err2=await resp.json().catch(function(){return{};});throw new Error(err2.error?.message||'HTTP '+resp.status);}
      var data=await resp.json();
      var text=data.content?.[0]?.text||'';
      var match=text.match(/\{[\s\S]*\}/);
      if(!match)throw new Error('Claude no devolvio JSON valido');
      var extracted=JSON.parse(match[0]);
      if(extracted.total>0){var mp=document.getElementById('mn-monto-pdf');if(mp)mp.value=extracted.total.toFixed(2);}
      if(extracted.resumen){var mv=document.getElementById('mn-motivo-pdf');if(mv)mv.value=extracted.resumen;}
      zone.style.borderColor='var(--a2)';status.style.color='var(--a2)';
      var provs=extracted.proveedores||[];
      var provHtml='OK: '+file.name+' — $'+((extracted.total||0).toFixed(2))+' total';
      if(provs.length){
        provHtml+='<div style="margin-top:6px;background:var(--s2);border-radius:5px;padding:6px 8px;">';
        provHtml+=provs.map(function(p){return '<div style="display:flex;justify-content:space-between;font-size:10px;padding:2px 0;border-bottom:1px solid var(--bd);"><span>'+p.nombre+'</span><span style="color:var(--a);">$'+((p.monto||0).toFixed(2))+'</span></div>';}).join('');
        provHtml+='</div>';
      }
      status.innerHTML=provHtml;
    }catch(err3){
      zone.style.borderColor='var(--a3)';status.style.color='var(--a3)';status.textContent='Error: '+err3.message;
    }
  };
  reader.readAsArrayBuffer(file);
};
"""

# Remove the old analizarReqPDF (already in file from previous patches, now replaced above)
# Find position of last </script> and insert before it
last_idx = html.rindex('</script>')
# Remove the old analizarReqPDF function that's in the module script
import re
html = re.sub(
    r'\n\nwindow\.analizarReqPDF=async function\(input\)\{[\s\S]*?\};\n',
    '\n',
    html, count=1
)
print("OK old analizarReqPDF removed")

# Now insert new JS before last </script>
last_idx = html.rindex('</script>')
html = html[:last_idx] + NEW_JS + '\n</script>' + html[last_idx+len('</script>'):]
print("OK new JS inserted")

# ═══════════════════════════════════════════════════════════════════
# 10. VERIFY
# ═══════════════════════════════════════════════════════════════════
bt = html.count('`')
print("Backticks:", bt)
if bt > 0:
    for i,line in enumerate(html.split('\n'),1):
        if '`' in line:
            print("  L"+str(i)+":", line[:120])

checks = [
    ('openAdd requisicion', "requisiciones:'requisicion'" in html),
    ('openModalDirect requisicion handler', "type==='requisicion'" in html),
    ('nav tesoreria propietario', "s:'tesoreria'" in html),
    ('SMETA tesoreria', "tesoreria:{t:'Tesor" in html),
    ('showSec tesoreria', "tesoreria:renderTesoreria" in html),
    ('sec-tesoreria HTML', 'id="sec-tesoreria"' in html),
    ('m-requisicion modal', 'id="m-requisicion"' in html),
    ('m-tesoreria-dep modal', 'id="m-tesoreria-dep"' in html),
    ('renderTesoreria', 'async function renderTesoreria' in html),
    ('tesoDepositar', 'window.tesoDepositar' in html),
    ('tesoDistribuir', 'window.tesoDistribuir' in html),
    ('renderConciliacion', 'window.renderConciliacion' in html),
    ('saveRequisicionModal', 'window.saveRequisicionModal' in html),
    ('reqTab', 'window.reqTab' in html),
    ('importReqXLSX', 'window.importReqXLSX' in html),
    ('req-xlsx-panel', 'id="req-xlsx-panel"' in html),
    ('req-pdf-panel', 'id="req-pdf-panel"' in html),
    ('crearRequisicionPDF', 'window.crearRequisicionPDF' in html),
    ('analizarReqPDF updated', 'mn-monto-pdf' in html),
    ('ts-saldos-neg', 'id="ts-saldos-neg"' in html),
    ('saldos por negocio', 'renderSaldosNeg' in html),
]
all_ok=True
for name,ok in checks:
    print(("OK " if ok else "FAIL ")+name)
    if not ok: all_ok=False

lines=html.count('\n')+1
print("Lines:", lines)

if not all_ok or bt>0:
    print("ERRORS — not saving")
    sys.exit(1)

with open('public/index.html','w',encoding='utf-8') as f:
    f.write(html)
print("SAVED")
