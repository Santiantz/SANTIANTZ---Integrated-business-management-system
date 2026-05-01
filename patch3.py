#!/usr/bin/env python3
import re, sys

with open('public/index.html','r',encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════
# 1. SEC-INV-COCINA — replace with dual-source + diff comparison
# ═══════════════════════════════════════════════════════════════════
OLD_COCINA = '''      <div class="sec" id="sec-inv-cocina">
        <div class="abox info">🍽️ Registra el inventario final de cocina. El sistema cuadrará contra ventas.</div>
        <div class="g2">
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Inventario cocina del día</div>
            <div class="fr"><label>Fecha</label><input type="date" id="ic-fecha"></div>
            <div class="fr"><label>Turno</label><select id="ic-turno" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"><option>Cierre del día</option><option>Turno mañana</option><option>Turno tarde</option><option>Turno noche</option></select></div>
            <div id="ic-items"></div>
            <button class="btn" style="font-size:11px;width:100%;margin-bottom:8px;" onclick="addInvItem('ic-items')">+ Agregar ingrediente</button>
            <div class="fr"><label>Notas</label><textarea id="ic-notas" placeholder="Observaciones del turno..."></textarea></div>
            <button class="btn pri" style="width:100%;" onclick="guardarInventario('cocina')">Guardar inventario cocina</button>
          </div>
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Últimos registros</div>
            <div id="ic-historial"><div class="empty">Sin registros</div></div>
            <div style="margin-top:10px;"><div class="cl" style="margin-bottom:6px;">Cuadre vs ventas</div><div id="ic-cuadre"></div></div>
          </div>
        </div>
      </div>'''

NEW_COCINA = '''      <div class="sec" id="sec-inv-cocina">
        <div class="g2" style="margin-bottom:10px;">
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Datos del registro</div>
            <div class="fr"><label>Fecha</label><input type="date" id="ic-fecha"></div>
            <div class="fr"><label>Turno</label><select id="ic-turno" style="width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"><option>Cierre del d&iacute;a</option><option>Turno ma&ntilde;ana</option><option>Turno tarde</option><option>Turno noche</option></select></div>
            <div class="fr"><label>Notas</label><textarea id="ic-notas" placeholder="Observaciones..."></textarea></div>
          </div>
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Comparar y guardar</div>
            <button class="btn pri" style="width:100%;margin-bottom:6px;" onclick="compararInventarios('cocina')">&#9658; Comparar inventarios</button>
            <button class="btn grn" style="width:100%;margin-bottom:6px;" id="btn-guard-dif-cocina" onclick="guardarDiferencias('cocina')">&#8595; Guardar reporte</button>
            <button class="btn" style="width:100%;font-size:11px;" onclick="guardarInventario('cocina')">Guardar solo f&iacute;sico</button>
          </div>
        </div>
        <div class="g2" style="margin-bottom:10px;">
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div class="cl">Fuente 1 &mdash; POS El Cheff</div><div id="ic-pos-badge" style="font-size:9px;color:var(--t3);font-family:'DM Mono',monospace;">Sin datos</div></div>
            <div style="display:flex;gap:6px;margin-bottom:8px;">
              <button class="btn pri" id="ic-pos-tab-xlsx" onclick="posInvTab('cocina','xlsx')" style="font-size:11px;padding:4px 9px;">&#128202; Excel</button>
              <button class="btn" id="ic-pos-tab-pdf" onclick="posInvTab('cocina','pdf')" style="font-size:11px;padding:4px 9px;">&#129302; PDF+IA</button>
            </div>
            <div id="ic-pos-xlsx-panel">
              <div class="upload-zone" onclick="document.getElementById('ic-pos-xlsx-file').click()"><input type="file" id="ic-pos-xlsx-file" accept=".xlsx,.xls" onchange="importPOSExcel(this,'cocina')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);">Excel POS El Cheff</div><div style="font-size:10px;color:var(--t3);margin-top:2px;">Columnas: PRODUCTO &middot; CANTIDAD &middot; UNIDAD</div></div>
            </div>
            <div id="ic-pos-pdf-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('ic-pos-pdf-file').click()"><input type="file" id="ic-pos-pdf-file" accept=".pdf" onchange="importPOSPDF(this,'cocina')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);">PDF reporte POS &mdash; Claude extrae productos</div></div>
            </div>
            <div id="ic-pos-status" style="font-size:10px;color:var(--t3);margin-top:4px;min-height:14px;"></div>
          </div>
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div class="cl">Fuente 2 &mdash; Inventario F&iacute;sico</div><div id="ic-fis-badge" style="font-size:9px;color:var(--t3);font-family:'DM Mono',monospace;">Sin datos</div></div>
            <div style="display:flex;gap:6px;margin-bottom:8px;">
              <button class="btn pri" id="ic-fis-tab-manual" onclick="fisInvTab('cocina','manual')" style="font-size:11px;padding:4px 9px;">&#9998; Manual</button>
              <button class="btn" id="ic-fis-tab-xlsx" onclick="fisInvTab('cocina','xlsx')" style="font-size:11px;padding:4px 9px;">&#128202; Excel</button>
            </div>
            <div id="ic-fis-manual-panel">
              <div id="ic-items"></div>
              <button class="btn" style="font-size:11px;width:100%;margin-bottom:6px;" onclick="addInvItem('ic-items')">+ Agregar ingrediente</button>
              <button class="btn" style="font-size:11px;width:100%;color:var(--a2);border-color:var(--a2);" onclick="capturarFisico('cocina')">Usar como inventario f&iacute;sico</button>
            </div>
            <div id="ic-fis-xlsx-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('ic-fis-xlsx-file').click()"><input type="file" id="ic-fis-xlsx-file" accept=".xlsx,.xls" onchange="importFisicoExcel(this,'cocina')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);">Excel inventario f&iacute;sico</div><div style="font-size:10px;color:var(--t3);margin-top:2px;">Columnas: PRODUCTO &middot; CANTIDAD &middot; UNIDAD</div></div>
            </div>
            <div id="ic-fis-status" style="font-size:10px;color:var(--t3);margin-top:4px;min-height:14px;"></div>
          </div>
        </div>
        <div id="ic-diff-result" style="margin-bottom:10px;"></div>
        <div class="card">
          <div class="cl" style="margin-bottom:8px;">&Uacute;ltimos registros</div>
          <div id="ic-historial"><div class="empty">Sin registros</div></div>
          <div style="margin-top:10px;"><div class="cl" style="margin-bottom:6px;">Cuadre vs ventas</div><div id="ic-cuadre"></div></div>
        </div>
      </div>'''

assert OLD_COCINA in html, "FAIL: sec-inv-cocina not found"
html = html.replace(OLD_COCINA, NEW_COCINA, 1)
print("OK sec-inv-cocina replaced")

# ═══════════════════════════════════════════════════════════════════
# 2. SEC-INV-BARRAS — replace with dual-source + diff comparison
# ═══════════════════════════════════════════════════════════════════
OLD_BARRAS = '''      <div class="sec" id="sec-inv-barras">
        <div class="abox info">🍹 Registra inventario de bebidas Y guarnición (berries, cerezas, limones, etc.)</div>
        <div class="g2">
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Inventario barras del día</div>
            <div class="fr"><label>Fecha</label><input type="date" id="ib-fecha"></div>
            <div class="cl" style="margin:8px 0 5px;color:var(--a4);">Bebidas</div>
            <div id="ib-bebidas"></div>
            <button class="btn" style="font-size:11px;width:100%;margin-bottom:8px;" onclick="addInvItem('ib-bebidas')">+ Agregar bebida</button>
            <div class="cl" style="margin:8px 0 5px;color:var(--a5);">Guarnición (berries, cerezas, limones, etc.)</div>
            <div id="ib-guarnicion"></div>
            <button class="btn" style="font-size:11px;width:100%;margin-bottom:8px;" onclick="addInvItem('ib-guarnicion')">+ Agregar guarnición</button>
            <div class="fr"><label>Notas</label><textarea id="ib-notas" placeholder="Observaciones barras..."></textarea></div>
            <button class="btn pri" style="width:100%;margin-top:4px;" onclick="guardarInventario('barras')">Guardar inventario barras</button>
          </div>
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Últimos registros</div>
            <div id="ib-historial"><div class="empty">Sin registros</div></div>
            <div style="margin-top:10px;"><div class="cl" style="margin-bottom:6px;">Cuadre vs ventas</div><div id="ib-cuadre"></div></div>
          </div>
        </div>
      </div>'''

NEW_BARRAS = '''      <div class="sec" id="sec-inv-barras">
        <div class="g2" style="margin-bottom:10px;">
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Datos del registro</div>
            <div class="fr"><label>Fecha</label><input type="date" id="ib-fecha"></div>
            <div class="fr"><label>Notas</label><textarea id="ib-notas" placeholder="Observaciones barras..."></textarea></div>
          </div>
          <div class="card">
            <div class="cl" style="margin-bottom:8px;">Comparar y guardar</div>
            <button class="btn pri" style="width:100%;margin-bottom:6px;" onclick="compararInventarios('barras')">&#9658; Comparar inventarios</button>
            <button class="btn grn" style="width:100%;margin-bottom:6px;" id="btn-guard-dif-barras" onclick="guardarDiferencias('barras')">&#8595; Guardar reporte</button>
            <button class="btn" style="width:100%;font-size:11px;" onclick="guardarInventario('barras')">Guardar solo f&iacute;sico</button>
          </div>
        </div>
        <div class="g2" style="margin-bottom:10px;">
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div class="cl">Fuente 1 &mdash; POS El Cheff</div><div id="ib-pos-badge" style="font-size:9px;color:var(--t3);font-family:'DM Mono',monospace;">Sin datos</div></div>
            <div style="display:flex;gap:6px;margin-bottom:8px;">
              <button class="btn pri" id="ib-pos-tab-xlsx" onclick="posInvTab('barras','xlsx')" style="font-size:11px;padding:4px 9px;">&#128202; Excel</button>
              <button class="btn" id="ib-pos-tab-pdf" onclick="posInvTab('barras','pdf')" style="font-size:11px;padding:4px 9px;">&#129302; PDF+IA</button>
            </div>
            <div id="ib-pos-xlsx-panel">
              <div class="upload-zone" onclick="document.getElementById('ib-pos-xlsx-file').click()"><input type="file" id="ib-pos-xlsx-file" accept=".xlsx,.xls" onchange="importPOSExcel(this,'barras')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);">Excel POS El Cheff</div><div style="font-size:10px;color:var(--t3);margin-top:2px;">Columnas: PRODUCTO &middot; CANTIDAD &middot; UNIDAD &middot; CATEGORIA</div></div>
            </div>
            <div id="ib-pos-pdf-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('ib-pos-pdf-file').click()"><input type="file" id="ib-pos-pdf-file" accept=".pdf" onchange="importPOSPDF(this,'barras')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);">PDF reporte POS barras</div></div>
            </div>
            <div id="ib-pos-status" style="font-size:10px;color:var(--t3);margin-top:4px;min-height:14px;"></div>
          </div>
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div class="cl">Fuente 2 &mdash; Inventario F&iacute;sico</div><div id="ib-fis-badge" style="font-size:9px;color:var(--t3);font-family:'DM Mono',monospace;">Sin datos</div></div>
            <div style="display:flex;gap:6px;margin-bottom:8px;">
              <button class="btn pri" id="ib-fis-tab-manual" onclick="fisInvTab('barras','manual')" style="font-size:11px;padding:4px 9px;">&#9998; Manual</button>
              <button class="btn" id="ib-fis-tab-xlsx" onclick="fisInvTab('barras','xlsx')" style="font-size:11px;padding:4px 9px;">&#128202; Excel</button>
            </div>
            <div id="ib-fis-manual-panel">
              <div class="cl" style="margin:0 0 5px;color:var(--a4);font-size:9px;">Bebidas</div>
              <div id="ib-bebidas"></div>
              <button class="btn" style="font-size:11px;width:100%;margin-bottom:6px;" onclick="addInvItem('ib-bebidas')">+ Bebida</button>
              <div class="cl" style="margin:4px 0 5px;color:var(--a5);font-size:9px;">Guarnici&oacute;n</div>
              <div id="ib-guarnicion"></div>
              <button class="btn" style="font-size:11px;width:100%;margin-bottom:6px;" onclick="addInvItem('ib-guarnicion')">+ Guarnici&oacute;n</button>
              <button class="btn" style="font-size:11px;width:100%;color:var(--a2);border-color:var(--a2);" onclick="capturarFisico('barras')">Usar como inventario f&iacute;sico</button>
            </div>
            <div id="ib-fis-xlsx-panel" style="display:none;">
              <div class="upload-zone" onclick="document.getElementById('ib-fis-xlsx-file').click()"><input type="file" id="ib-fis-xlsx-file" accept=".xlsx,.xls" onchange="importFisicoExcel(this,'barras')" style="display:none"><div style="font-size:18px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);">Excel inventario f&iacute;sico barras</div><div style="font-size:10px;color:var(--t3);margin-top:2px;">Columnas: PRODUCTO &middot; CANTIDAD &middot; UNIDAD &middot; CATEGORIA</div></div>
            </div>
            <div id="ib-fis-status" style="font-size:10px;color:var(--t3);margin-top:4px;min-height:14px;"></div>
          </div>
        </div>
        <div id="ib-diff-result" style="margin-bottom:10px;"></div>
        <div class="card">
          <div class="cl" style="margin-bottom:8px;">&Uacute;ltimos registros</div>
          <div id="ib-historial"><div class="empty">Sin registros</div></div>
          <div style="margin-top:10px;"><div class="cl" style="margin-bottom:6px;">Cuadre vs ventas</div><div id="ib-cuadre"></div></div>
        </div>
      </div>'''

assert OLD_BARRAS in html, "FAIL: sec-inv-barras not found"
html = html.replace(OLD_BARRAS, NEW_BARRAS, 1)
print("OK sec-inv-barras replaced")

# ═══════════════════════════════════════════════════════════════════
# 3. NOMINAS — replace 2-tab import with 3-tab (xnomina, xcatalogo, pdf)
# ═══════════════════════════════════════════════════════════════════
OLD_NOM_IMPORT = '''        <div class="card" style="margin-bottom:12px;">
          <div class="cl" style="margin-bottom:10px;">Importar n&oacute;mina</div>
          <div style="display:flex;gap:6px;margin-bottom:12px;">
            <button class="btn pri" id="nom-tab-xlsx" onclick="nomTab('xlsx')">&#128202; Excel empleados</button>
            <button class="btn" id="nom-tab-pdf" onclick="nomTab('pdf')">&#129302; PDF + IA</button>
          </div>
          <div id="nom-xlsx-panel">
            <div class="upload-zone" onclick="document.getElementById('nom-xlsx-file').click()"><input type="file" id="nom-xlsx-file" accept=".xlsx,.xls" onchange="importNomExcel(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Excel de empleados</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Columnas: NOMBRE &middot; PUESTO &middot; SALARIO &middot; TIPO</div></div>
            <div id="nom-xlsx-preview"></div>
          </div>
          <div id="nom-pdf-panel" style="display:none;">
            <div class="upload-zone" onclick="document.getElementById('nom-pdf-file').click()"><input type="file" id="nom-pdf-file" accept=".pdf" onchange="importNomPDF(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Comprobante n&oacute;mina PDF</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Claude extrae empleado, periodo y monto</div></div>
            <div id="nom-pdf-preview"></div>
          </div>
        </div>'''

NEW_NOM_IMPORT = '''        <div class="card" style="margin-bottom:12px;">
          <div class="cl" style="margin-bottom:10px;">Importar n&oacute;mina</div>
          <div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;">
            <button class="btn pri" id="nom-tab-xnomina" onclick="nomTab('xnomina')" style="font-size:11px;">&#128202; Excel n&oacute;mina</button>
            <button class="btn" id="nom-tab-xcatalogo" onclick="nomTab('xcatalogo')" style="font-size:11px;">&#128203; Cat&aacute;logo empleados</button>
            <button class="btn" id="nom-tab-pdf" onclick="nomTab('pdf')" style="font-size:11px;">&#129302; PDF + IA</button>
          </div>
          <div id="nom-xnomina-panel">
            <div class="upload-zone" onclick="document.getElementById('nom-xnomina-file').click()"><input type="file" id="nom-xnomina-file" accept=".xlsx,.xls" onchange="importNomPagoExcel(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Excel de pagos de n&oacute;mina</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Columnas: EMPLEADO &middot; PUESTO &middot; PERIODO &middot; MONTO &middot; DEDUCCIONES</div></div>
            <div id="nom-xnomina-preview"></div>
          </div>
          <div id="nom-xcatalogo-panel" style="display:none;">
            <div class="upload-zone" onclick="document.getElementById('nom-xlsx-file').click()"><input type="file" id="nom-xlsx-file" accept=".xlsx,.xls" onchange="importNomExcel(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#128203;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Excel cat&aacute;logo de empleados</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Columnas: NOMBRE &middot; PUESTO &middot; SALARIO &middot; TIPO</div></div>
            <div id="nom-xlsx-preview"></div>
          </div>
          <div id="nom-pdf-panel" style="display:none;">
            <div class="upload-zone" onclick="document.getElementById('nom-pdf-file').click()"><input type="file" id="nom-pdf-file" accept=".pdf" onchange="importNomPDF(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Comprobante n&oacute;mina PDF</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Claude extrae empleado, periodo y monto</div></div>
            <div id="nom-pdf-preview"></div>
          </div>
        </div>'''

assert OLD_NOM_IMPORT in html, "FAIL: nom import panel not found"
html = html.replace(OLD_NOM_IMPORT, NEW_NOM_IMPORT, 1)
print("OK nominas import panel updated")

# ═══════════════════════════════════════════════════════════════════
# 4. Update analizarReqPDF → extract proveedores list
# ═══════════════════════════════════════════════════════════════════
OLD_REQ_PDF = '''window.analizarReqPDF=async function(input){
  const file=input.files[0];if(!file)return;
  const apiKey=localStorage.getItem('ant_key')||'';
  const status=document.getElementById('mn-req-pdf-status');
  const zone=document.getElementById('mn-req-pdf-zone');
  if(!apiKey){
    status.textContent='Sin API Key guardada. Primero usa "PDF + IA" en Facturas para guardarla.';
    status.style.color='var(--a3)';return;
  }
  zone.style.borderColor='var(--a4)';
  status.style.color='var(--a4)';
  status.textContent='Analizando con Claude...';
  const reader=new FileReader();
  reader.onload=async function(e){
    try{
      const bytes=new Uint8Array(e.target.result);
      let b64='';const CHUNK=8192;
      for(let i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
      const resp=await fetch('https://api.anthropic.com/v1/messages',{
        method:'POST',
        headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},
        body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:500,messages:[{role:'user',content:[
          {type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},
          {type:'text',text:'Analiza este documento de gastos/facturas. Responde SOLO con JSON: {"total":0.00,"resumen":"descripcion breve de los gastos para usar como motivo de requisicion"}'}
        ]}]})
      });
      if(!resp.ok){const err=await resp.json().catch(function(){return{};});throw new Error(err.error?.message||'HTTP '+resp.status);}
      const data=await resp.json();
      const text=data.content?.[0]?.text||'';
      const match=text.match(/\\{[\\s\\S]*?\\}/);
      if(!match)throw new Error('Respuesta inesperada de Claude');
      const extracted=JSON.parse(match[0]);
      if(extracted.total>0)document.getElementById('mn-monto').value=extracted.total.toFixed(2);
      if(extracted.resumen)document.getElementById('mn-motivo').value=extracted.resumen;
      zone.style.borderColor='var(--a2)';
      status.style.color='var(--a2)';
      status.textContent='OK: '+file.name+' — datos pre-llenados. Revisa y corrige si es necesario.';
    }catch(err){
      zone.style.borderColor='var(--a3)';
      status.style.color='var(--a3)';
      status.textContent='Error: '+err.message;
    }
  };
  reader.readAsArrayBuffer(file);
};'''

NEW_REQ_PDF = r"""window.analizarReqPDF=async function(input){
  const file=input.files[0];if(!file)return;
  const apiKey=localStorage.getItem('ant_key')||'';
  const status=document.getElementById('mn-req-pdf-status');
  const zone=document.getElementById('mn-req-pdf-zone');
  if(!apiKey){status.textContent='Sin API Key. Primero usa PDF+IA en Facturas.';status.style.color='var(--a3)';return;}
  zone.style.borderColor='var(--a4)';status.style.color='var(--a4)';status.textContent='Analizando con Claude...';
  const reader=new FileReader();
  reader.onload=async function(e){
    try{
      const bytes=new Uint8Array(e.target.result);
      let b64='';const CHUNK=8192;
      for(let i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
      const resp=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:1000,messages:[{role:'user',content:[{type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},{type:'text',text:'Analiza este documento de gastos/facturas de la semana. Responde SOLO con JSON: {"total":0.00,"resumen":"descripcion breve para motivo de requisicion","proveedores":[{"nombre":"proveedor","concepto":"descripcion","monto":0.00}]}'}]}]})});
      if(!resp.ok){const err=await resp.json().catch(function(){return{};});throw new Error(err.error?.message||'HTTP '+resp.status);}
      const data=await resp.json();
      const text=data.content?.[0]?.text||'';
      const match=text.match(/\{[\s\S]*\}/);
      if(!match)throw new Error('Claude no devolvio JSON valido');
      const extracted=JSON.parse(match[0]);
      if(extracted.total>0)document.getElementById('mn-monto').value=extracted.total.toFixed(2);
      if(extracted.resumen)document.getElementById('mn-motivo').value=extracted.resumen;
      zone.style.borderColor='var(--a2)';status.style.color='var(--a2)';
      const provs=extracted.proveedores||[];
      let provHtml='OK: '+file.name+' — $'+((extracted.total||0).toFixed(2))+' total';
      if(provs.length){
        provHtml+='<div style="margin-top:6px;background:var(--s2);border-radius:5px;padding:6px 8px;">';
        provHtml+=provs.map(function(p){return '<div style="display:flex;justify-content:space-between;font-size:10px;padding:2px 0;border-bottom:1px solid var(--bd);"><span>'+p.nombre+'</span><span style="color:var(--a);">$'+((p.monto||0).toFixed(2))+'</span></div>';}).join('');
        provHtml+='</div>';
      }
      status.innerHTML=provHtml;
    }catch(err){
      zone.style.borderColor='var(--a3)';status.style.color='var(--a3)';status.textContent='Error: '+err.message;
    }
  };
  reader.readAsArrayBuffer(file);
};"""

assert 'window.analizarReqPDF=async function' in html, "FAIL: analizarReqPDF not found"
# Use regex replace with lambda to avoid backslash issues in replacement string
_repl_req = NEW_REQ_PDF + '\n\nwindow.guardarPDFFactura'
html = re.sub(
    r'window\.analizarReqPDF=async function\(input\)\{[\s\S]*?\};\n\nwindow\.guardarPDFFactura',
    lambda m: _repl_req,
    html, count=1
)
assert 'proveedores' in html, "FAIL: analizarReqPDF not updated"
print("OK analizarReqPDF updated")

# ═══════════════════════════════════════════════════════════════════
# 5. Update nomTab to handle 3 tabs
# ═══════════════════════════════════════════════════════════════════
OLD_NOMTAB = r"""window.nomTab=function(tab){
  ['xlsx','pdf'].forEach(function(t){
    const panel=document.getElementById('nom-'+t+'-panel');
    if(panel)panel.style.display=t===tab?'':'none';
    const btn=document.getElementById('nom-tab-'+t);
    if(btn)btn.className=t===tab?'btn pri':'btn';
  });
};"""

NEW_NOMTAB = r"""window.nomTab=function(tab){
  ['xnomina','xcatalogo','pdf'].forEach(function(t){
    const panel=document.getElementById('nom-'+t+'-panel');
    if(panel)panel.style.display=t===tab?'':'none';
    const btn=document.getElementById('nom-tab-'+t);
    if(btn)btn.className=t===tab?'btn pri':'btn';
  });
};"""

assert OLD_NOMTAB in html, "FAIL: nomTab not found"
html = html.replace(OLD_NOMTAB, NEW_NOMTAB, 1)
print("OK nomTab updated to 3 tabs")

# ═══════════════════════════════════════════════════════════════════
# 6. ADD ALL NEW JS FUNCTIONS before </script>
# ═══════════════════════════════════════════════════════════════════
NEW_JS = r"""
/* ── INVENTORY COMPARISON ────────────────────────────────────────── */

window.posInvTab=function(tipo,tab){
  var pre=tipo==='cocina'?'ic':'ib';
  ['xlsx','pdf'].forEach(function(t){
    var p=document.getElementById(pre+'-pos-'+t+'-panel');
    if(p)p.style.display=t===tab?'':'none';
    var b=document.getElementById(pre+'-pos-tab-'+t);
    if(b)b.className=t===tab?'btn pri':'btn';
  });
};

window.fisInvTab=function(tipo,tab){
  var pre=tipo==='cocina'?'ic':'ib';
  ['manual','xlsx'].forEach(function(t){
    var p=document.getElementById(pre+'-fis-'+t+'-panel');
    if(p)p.style.display=t===tab?'':'none';
    var b=document.getElementById(pre+'-fis-tab-'+t);
    if(b)b.className=t===tab?'btn pri':'btn';
  });
};

function parseInvExcel(file,onDone,onErr){
  if(typeof XLSX==='undefined'){onErr('SheetJS no cargo.');return;}
  const reader=new FileReader();
  reader.onload=function(e){
    try{
      const wb=XLSX.read(e.target.result,{type:'array',raw:false,defval:''});
      const ws=wb.Sheets[wb.SheetNames[0]];
      const rows=XLSX.utils.sheet_to_json(ws,{header:1,raw:false,defval:''});
      if(rows.length<2){onErr('Archivo vacio');return;}
      const hdrs=rows[0].map(function(h){return String(h||'').toUpperCase().trim();});
      const fi=function(kws){for(var k=0;k<kws.length;k++){var idx=hdrs.findIndex(function(h){return h.includes(kws[k]);});if(idx>-1)return idx;}return -1;};
      const cols={prod:fi(['PRODUCTO','NOMBRE','ITEM','ARTICULO','DESCRIPCI']),cant:fi(['CANTIDAD','CANT','QTY']),uni:fi(['UNIDAD','UNIT','MEDIDA']),cat:fi(['CATEG','TIPO'])};
      const fmtNum=function(v){return parseFloat(String(v||0).replace(/[$,\s]/g,''))||0;};
      const data=rows.slice(1).filter(function(r){return r.some(function(c){return String(c||'').trim();});}).map(function(r){
        return{producto:cols.prod>=0?String(r[cols.prod]||''):'',cantidad:fmtNum(cols.cant>=0?r[cols.cant]:0),unidad:cols.uni>=0?String(r[cols.uni]||'pieza'):'pieza',categoria:cols.cat>=0?String(r[cols.cat]||''):''};
      }).filter(function(r){return r.producto&&r.cantidad>0;});
      if(!data.length){onErr('No se detectaron productos');return;}
      onDone(data);
    }catch(err){onErr(err.message);}
  };
  reader.readAsArrayBuffer(file);
}

async function parsePOSPDF(file,tipo){
  const apiKey=localStorage.getItem('ant_key')||'';
  if(!apiKey)throw new Error('Sin API Key. Usala primero en Facturas > PDF+IA.');
  const bytes=new Uint8Array(await file.arrayBuffer());
  let b64='';const CHUNK=8192;
  for(let i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
  const resp=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:1000,messages:[{role:'user',content:[{type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},{type:'text',text:'Extrae el inventario de este reporte de POS. Responde SOLO con JSON: {"items":[{"producto":"nombre","cantidad":0.0,"unidad":"pieza","categoria":""}]}'}]}]})});
  if(!resp.ok){const err=await resp.json().catch(function(){return{};});throw new Error(err.error?.message||'HTTP '+resp.status);}
  const data=await resp.json();
  const text=data.content?.[0]?.text||'';
  const match=text.match(/\{[\s\S]*\}/);
  if(!match)throw new Error('Claude no devolvio JSON valido');
  const parsed=JSON.parse(match[0]);
  return (parsed.items||[]).filter(function(i){return i.producto&&i.cantidad>0;});
}

window.importPOSExcel=function(input,tipo){
  const file=input.files[0];if(!file)return;
  const pre=tipo==='cocina'?'ic':'ib';
  const statusEl=document.getElementById(pre+'-pos-status');
  const badgeEl=document.getElementById(pre+'-pos-badge');
  statusEl.textContent='Procesando...';statusEl.style.color='var(--a4)';
  parseInvExcel(file,function(data){
    window['_posInv_'+tipo]=data;
    statusEl.textContent='OK: '+data.length+' productos cargados de '+file.name;
    statusEl.style.color='var(--a2)';
    badgeEl.textContent=data.length+' prod.';badgeEl.style.color='var(--a2)';
  },function(err){statusEl.textContent='Error: '+err;statusEl.style.color='var(--a3)';});
};

window.importPOSPDF=async function(input,tipo){
  const file=input.files[0];if(!file)return;
  const pre=tipo==='cocina'?'ic':'ib';
  const statusEl=document.getElementById(pre+'-pos-status');
  const badgeEl=document.getElementById(pre+'-pos-badge');
  statusEl.textContent='Analizando PDF con Claude...';statusEl.style.color='var(--a4)';
  try{
    const data=await parsePOSPDF(file,tipo);
    window['_posInv_'+tipo]=data;
    statusEl.textContent='OK: '+data.length+' productos extraidos de '+file.name;
    statusEl.style.color='var(--a2)';
    badgeEl.textContent=data.length+' prod.';badgeEl.style.color='var(--a2)';
  }catch(err){statusEl.textContent='Error: '+err.message;statusEl.style.color='var(--a3)';}
};

window.capturarFisico=function(tipo){
  var pre=tipo==='cocina'?'ic':'ib';
  var items=[];
  if(tipo==='cocina'){
    items=getInvItems('ic-items').map(function(i){return{producto:i.producto,cantidad:i.cantidad,unidad:i.unidad,categoria:''};});
  } else {
    const beb=getInvItems('ib-bebidas').map(function(i){return{producto:i.producto,cantidad:i.cantidad,unidad:i.unidad,categoria:'bebida'};});
    const guar=getInvItems('ib-guarnicion').map(function(i){return{producto:i.producto,cantidad:i.cantidad,unidad:i.unidad,categoria:'guarnicion'};});
    items=[...beb,...guar];
  }
  if(!items.length){alert('Agrega al menos un producto');return;}
  window['_fisInv_'+tipo]=items;
  const statusEl=document.getElementById(pre+'-fis-status');
  const badgeEl=document.getElementById(pre+'-fis-badge');
  statusEl.textContent='OK: '+items.length+' productos capturados';
  statusEl.style.color='var(--a2)';
  badgeEl.textContent=items.length+' prod.';badgeEl.style.color='var(--a2)';
};

window.importFisicoExcel=function(input,tipo){
  const file=input.files[0];if(!file)return;
  const pre=tipo==='cocina'?'ic':'ib';
  const statusEl=document.getElementById(pre+'-fis-status');
  const badgeEl=document.getElementById(pre+'-fis-badge');
  statusEl.textContent='Procesando...';statusEl.style.color='var(--a4)';
  parseInvExcel(file,function(data){
    window['_fisInv_'+tipo]=data;
    statusEl.textContent='OK: '+data.length+' productos cargados de '+file.name;
    statusEl.style.color='var(--a2)';
    badgeEl.textContent=data.length+' prod.';badgeEl.style.color='var(--a2)';
  },function(err){statusEl.textContent='Error: '+err;statusEl.style.color='var(--a3)';});
};

window.compararInventarios=async function(tipo){
  const posInv=window['_posInv_'+tipo]||[];
  const fisInv=window['_fisInv_'+tipo]||[];
  const pre=tipo==='cocina'?'ic':'ib';
  const resultEl=document.getElementById(pre+'-diff-result');
  if(!posInv.length&&!fisInv.length){resultEl.innerHTML="<div class='abox warn'>Carga al menos una fuente para comparar</div>";return;}
  resultEl.innerHTML="<div class='abox info'><span class='spin'></span> Consultando precios en Firestore...</div>";
  const negId=userData.negocioId||negocios[0]?.id;
  try{
    const [facSnap,venSnap]=await Promise.all([
      getDocs(negId?query(collection(db,'facturas'),where('negocioId','==',negId)):query(collection(db,'facturas'),orderBy('creadoEn','desc'))),
      getDocs(negId?query(collection(db,'ventas'),where('negocioId','==',negId)):query(collection(db,'ventas'),orderBy('creadoEn','desc')))
    ]);
    const costMap={};
    facSnap.docs.forEach(function(d){
      const f=d.data();
      const key=(f.ingrediente||'').toLowerCase().trim();
      if(!key)return;
      const precio=f.precio||(f.cantidad>0?f.total/f.cantidad:0);
      if(!costMap[key]||precio>0)costMap[key]=precio;
    });
    const ventaSum={};const ventaCnt={};
    venSnap.docs.forEach(function(d){
      const v=d.data();
      const key=(v.platillo||'').toLowerCase().trim();
      if(!key)return;
      ventaSum[key]=(ventaSum[key]||0)+(v.precio||0);
      ventaCnt[key]=(ventaCnt[key]||0)+1;
    });
    const ventaMap={};
    Object.keys(ventaSum).forEach(function(k){ventaMap[k]=ventaCnt[k]>0?ventaSum[k]/ventaCnt[k]:0;});
    const posMap={};
    posInv.forEach(function(item){posMap[(item.producto||'').toLowerCase().trim()]=item;});
    const fisMap={};
    fisInv.forEach(function(item){fisMap[(item.producto||'').toLowerCase().trim()]=item;});
    const allKeys=new Set([...Object.keys(posMap),...Object.keys(fisMap)]);
    const diffs=[];
    allKeys.forEach(function(key){
      const pos=posMap[key];const fis=fisMap[key];
      const cantPos=pos?pos.cantidad:0;
      const cantFis=fis?fis.cantidad:0;
      const diff=cantFis-cantPos;
      const pct=cantPos>0?Math.abs(diff)/cantPos*100:(cantFis>0?100:0);
      const nomProd=pos?pos.producto:fis.producto;
      let costoU=null;
      const kLow=nomProd.toLowerCase().trim();
      if(costMap[kLow]!==undefined)costoU=costMap[kLow];
      else {
        const kParts=kLow.split(' ');
        Object.keys(costMap).forEach(function(ck){if(kParts.some(function(p){return p.length>3&&ck.includes(p);}))costoU=costMap[ck];});
      }
      let ventaU=null;
      if(ventaMap[kLow]!==undefined)ventaU=ventaMap[kLow];
      else {
        const kParts2=kLow.split(' ');
        Object.keys(ventaMap).forEach(function(vk){if(kParts2.some(function(p){return p.length>3&&vk.includes(p);}))ventaU=ventaMap[vk];});
      }
      diffs.push({producto:nomProd,cantPos,cantFis,diff,pct,alerta:pct>10,costoU,ventaU});
    });
    diffs.sort(function(a,b){return (b.alerta-a.alerta)||(b.pct-a.pct);});
    window['_diffs_'+tipo]=diffs;
    renderDiffTable(tipo,diffs,posInv.length,fisInv.length);
  }catch(err){resultEl.innerHTML="<div class='abox err'>Error al consultar precios: "+err.message+"</div>";}
};

function renderDiffTable(tipo,diffs,posCount,fisCount){
  const pre=tipo==='cocina'?'ic':'ib';
  const resultEl=document.getElementById(pre+'-diff-result');
  if(!diffs.length){resultEl.innerHTML="<div class='abox ok'>Sin diferencias detectadas</div>";return;}
  const alertas=diffs.filter(function(d){return d.alerta&&d.diff!==0;});
  let totCosto=0,totVenta=0;
  diffs.forEach(function(d){
    if(d.diff<0){
      if(d.costoU!==null)totCosto+=Math.abs(d.diff)*d.costoU;
      if(d.ventaU!==null)totVenta+=Math.abs(d.diff)*d.ventaU;
    }
  });
  let h="<div class='card'>";
  h+="<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>";
  h+="<div class='cl'>Reporte de diferencias</div>";
  h+="<div style='font-size:10px;color:var(--t3);'>POS: "+(posCount||'?')+" prod. &middot; F&iacute;sico: "+(fisCount||'?')+" prod.</div></div>";
  if(alertas.length){
    h+="<div class='abox err' style='margin-bottom:8px;'>&#9888; "+alertas.length+" producto"+(alertas.length!==1?'s':'')+' con diferencia &gt;10%: '+alertas.map(function(d){return d.producto;}).join(', ')+"</div>";
  }
  h+="<div style='overflow-x:auto;'><table><thead><tr>"
    +"<th>Producto</th><th>Cant. POS</th><th>Cant. F&iacute;sico</th><th>Diferencia</th><th>% Var.</th>"
    +"<th>P. Costo unit.</th><th>P&eacute;rdida costo</th><th>P. Venta unit.</th><th>P&eacute;rdida venta</th>"
    +"</tr></thead><tbody>";
  diffs.forEach(function(d){
    const diffColor=d.diff<0?'color:var(--a3)':d.diff>0?'color:var(--a2)':'';
    const pctColor=d.pct>10?'color:var(--a3);font-weight:500':'color:var(--t2)';
    const costoCell=d.costoU!==null?'$'+d.costoU.toFixed(2):'<span style="color:var(--t3);font-size:10px;">Sin precio</span>';
    const ventaCell=d.ventaU!==null?'$'+d.ventaU.toFixed(2):'<span style="color:var(--t3);font-size:10px;">Sin precio</span>';
    const perdCosto=d.diff<0&&d.costoU!==null?'<span style="color:var(--a3);">-$'+(Math.abs(d.diff)*d.costoU).toFixed(2)+'</span>':'<span style="color:var(--t3);font-size:10px;">—</span>';
    const perdVenta=d.diff<0&&d.ventaU!==null?'<span style="color:var(--a3);">-$'+(Math.abs(d.diff)*d.ventaU).toFixed(2)+'</span>':'<span style="color:var(--t3);font-size:10px;">—</span>';
    h+="<tr"+(d.alerta&&d.diff!==0?" style='background:rgba(232,122,122,.06);'":'')+">"
      +"<td>"+d.producto+(d.alerta&&d.diff!==0?" <span class='badge r' style='font-size:8px;'>!</span>":"")+"</td>"
      +"<td style='text-align:right;font-family:monospace;'>"+(d.cantPos>0?d.cantPos.toFixed(2):'<span style="color:var(--t3);">—</span>')+"</td>"
      +"<td style='text-align:right;font-family:monospace;'>"+(d.cantFis>0?d.cantFis.toFixed(2):'<span style="color:var(--t3);">—</span>')+"</td>"
      +"<td style='text-align:right;font-family:monospace;"+diffColor+";'>"+(d.diff>=0?'+':'')+d.diff.toFixed(2)+"</td>"
      +"<td style='text-align:right;"+pctColor+";'>"+d.pct.toFixed(1)+"%</td>"
      +"<td style='text-align:right;font-size:11px;'>"+costoCell+"</td>"
      +"<td style='text-align:right;font-size:11px;'>"+perdCosto+"</td>"
      +"<td style='text-align:right;font-size:11px;'>"+ventaCell+"</td>"
      +"<td style='text-align:right;font-size:11px;'>"+perdVenta+"</td>"
      +"</tr>";
  });
  h+="</tbody></table></div>";
  if(totCosto>0||totVenta>0){
    h+="<div style='display:flex;gap:10px;margin-top:10px;'>";
    if(totCosto>0)h+="<div class='card' style='flex:1;background:rgba(232,122,122,.08);border-color:rgba(232,122,122,.25);'><div class='cl'>P&eacute;rdida total a costo</div><div class='cv r' style='font-size:16px;'>-$"+totCosto.toFixed(2)+"</div></div>";
    if(totVenta>0)h+="<div class='card' style='flex:1;background:rgba(232,122,122,.08);border-color:rgba(232,122,122,.25);'><div class='cl'>P&eacute;rdida total a venta</div><div class='cv r' style='font-size:16px;'>-$"+totVenta.toFixed(2)+"</div></div>";
    h+="</div>";
  }
  h+="</div>";
  resultEl.innerHTML=h;
}

window.guardarDiferencias=async function(tipo){
  const diffs=window['_diffs_'+tipo];
  const posInv=window['_posInv_'+tipo]||[];
  const fisInv=window['_fisInv_'+tipo]||[];
  if(!diffs||!diffs.length){alert('Primero compara los inventarios');return;}
  const negId=userData.negocioId||negocios[0]?.id;
  const pre=tipo==='cocina'?'ic':'ib';
  const fecha=document.getElementById(pre+'-fecha')?.value||new Date().toISOString().split('T')[0];
  const notas=document.getElementById(pre+'-notas')?.value||'';
  const alertaCount=diffs.filter(function(d){return d.alerta&&d.diff!==0;}).length;
  try{
    await addDoc(collection(db,'inv_diferencias'),{negocioId:negId,tipo,fecha,notas,posInventario:posInv,fisicoInventario:fisInv,diferencias:diffs,alertas:alertaCount,registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    await addDoc(collection(db,'inventarios'),{negocioId:negId,tipo,fecha,items:fisInv,notas,registradoPor:userData.nombre,rol:userData.rol,creadoEn:serverTimestamp()});
    alert('Reporte guardado correctamente. '+alertaCount+' alerta'+(alertaCount!==1?'s':'')+'.');
    if(tipo==='cocina')renderInvCocina();else renderInvBarras();
  }catch(e){alert('Error: '+e.message);}
};

/* ── NOMINA PAGO EXCEL ───────────────────────────────────────────── */

window.importNomPagoExcel=function(input){
  const file=input.files[0];if(!file)return;
  if(typeof XLSX==='undefined'){alert('SheetJS no cargo.');return;}
  const prev=document.getElementById('nom-xnomina-preview');
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'>Procesando Excel...</div>";
  const reader=new FileReader();
  reader.onload=function(e){
    try{
      const wb=XLSX.read(e.target.result,{type:'array',cellDates:true,raw:false,defval:''});
      const ws=wb.Sheets[wb.SheetNames[0]];
      const rows=XLSX.utils.sheet_to_json(ws,{header:1,raw:false,defval:''});
      if(rows.length<2){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Archivo vacio</div>";return;}
      const hdrs=rows[0].map(function(h){return String(h||'').toUpperCase().trim();});
      const fi=function(kws){for(var k=0;k<kws.length;k++){var idx=hdrs.findIndex(function(h){return h.includes(kws[k]);});if(idx>-1)return idx;}return -1;};
      const cols={emp:fi(['EMPLEADO','NOMBRE','TRABAJADOR']),pues:fi(['PUESTO','CARGO']),per:fi(['PERIODO','SEMANA','FECHA']),monto:fi(['MONTO','BRUTO','SALARIO','PAGO']),ded:fi(['DEDUCCION','DESCUENTO','IMSS']),fecha:fi(['FECHA PAGO','FECHA_PAGO','PAGO'])};
      const fmtDate=function(v){if(!v)return '';const d=new Date(v);if(!isNaN(d.getTime()))return d.toISOString().split('T')[0];return String(v).substring(0,10);};
      const fmtNum=function(v){return parseFloat(String(v||0).replace(/[$,\s]/g,''))||0;};
      const data=rows.slice(1).filter(function(r){return r.some(function(c){return String(c||'').trim();});}).map(function(r){
        const monto=fmtNum(cols.monto>=0?r[cols.monto]:0);
        const ded=fmtNum(cols.ded>=0?r[cols.ded]:0);
        const per=cols.per>=0?String(r[cols.per]||''):'';
        const fPago=cols.fecha>=0?fmtDate(r[cols.fecha]):'';
        return{empleado:cols.emp>=0?String(r[cols.emp]||''):'',puesto:cols.pues>=0?String(r[cols.pues]||''):'',periodo:per,fechaPago:fPago,monto,deducciones:ded,neto:monto-ded};
      }).filter(function(r){return r.empleado&&r.monto>0;});
      if(!data.length){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>No se detectaron pagos de nomina</div>";return;}
      window._nomPagoXlsxData=data;
      const IS='padding:3px 5px;background:var(--s2);border:1px solid var(--bd);border-radius:4px;color:var(--t);font-size:11px;';
      const td=new Date().toISOString().split('T')[0];
      let h="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>&#10003; "+data.length+" pago"+(data.length!==1?'s':'')+" de nomina detectado"+(data.length!==1?'s':'')+"</div><div style='overflow-x:auto;'><table><thead><tr><th>Empleado</th><th>Puesto</th><th>Periodo</th><th>Fecha pago</th><th>Bruto</th><th>Deduc.</th><th>Neto</th></tr></thead><tbody>";
      data.forEach(function(r,i){
        h+="<tr>"
          +"<td><input id='np2-e-"+i+"' value=\""+r.empleado.replace(/"/g,'')+"\" style='width:110px;"+IS+"'></td>"
          +"<td><input id='np2-p-"+i+"' value=\""+r.puesto.replace(/"/g,'')+"\" style='width:90px;"+IS+"'></td>"
          +"<td><input id='np2-per-"+i+"' value=\""+r.periodo.replace(/"/g,'')+"\" style='width:100px;"+IS+"'></td>"
          +"<td><input type='date' id='np2-f-"+i+"' value='"+(r.fechaPago||td)+"' style='width:110px;"+IS+"'></td>"
          +"<td><input type='number' id='np2-m-"+i+"' value='"+r.monto.toFixed(2)+"' style='width:80px;"+IS+"'></td>"
          +"<td><input type='number' id='np2-d-"+i+"' value='"+r.deducciones.toFixed(2)+"' style='width:70px;"+IS+"'></td>"
          +"<td style='color:var(--a2);font-weight:500;'>$"+r.neto.toFixed(2)+"</td></tr>";
      });
      const totNeto=data.reduce(function(a,r){return a+r.neto;},0);
      h+="</tbody><tfoot><tr><td colspan='4' style='font-weight:500;color:var(--t);'>Total</td><td></td><td></td><td style='color:var(--a2);font-weight:600;font-family:monospace;'>$"+totNeto.toFixed(2)+"</td></tr></tfoot></table></div><button class='btn pri' style='width:100%;margin-top:10px;' onclick='guardarNomPagoExcel("+data.length+")'>Registrar "+data.length+" pago"+(data.length!==1?'s':'')+"</button></div>";
      prev.innerHTML=h;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarNomPagoExcel=async function(count){
  const negId=userData.negocioId||negocios[0]?.id;
  const btn=event.target;btn.textContent='Registrando...';btn.disabled=true;
  try{
    let saved=0;
    for(let i=0;i<count;i++){
      const emp=document.getElementById('np2-e-'+i)?.value||'';if(!emp)continue;
      const monto=parseFloat(document.getElementById('np2-m-'+i)?.value)||0;if(!monto)continue;
      const ded=parseFloat(document.getElementById('np2-d-'+i)?.value)||0;
      const neto=monto-ded;
      const f=document.getElementById('np2-f-'+i)?.value||'';
      const per=document.getElementById('np2-per-'+i)?.value||'';
      const pues=document.getElementById('np2-p-'+i)?.value||'';
      const empObj=(window._nomEmps||[]).find(function(e){return e.nombre.toLowerCase()===emp.toLowerCase();});
      await addDoc(collection(db,'nominas_pagos'),{empleadoId:empObj?.id||'',negocioId:empObj?.negocioId||negId,empleadoNombre:emp,puesto:pues||empObj?.puesto||'',periodo:per,fechaPago:f,monto,deducciones:ded,neto,comprobanteUrl:null,comprobante:null,notas:'Importado desde Excel',registradoPor:userData.nombre,creadoEn:serverTimestamp()});
      saved++;
    }
    document.getElementById('nom-xnomina-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>&#10003; "+saved+" pago"+(saved!==1?'s':'')+" registrado"+(saved!==1?'s':'')+"</div>";
    document.getElementById('nom-xnomina-file').value='';renderNominas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Registrar';btn.disabled=false;
};
"""

# Insert before the last </script> in the file
last_idx = html.rindex('</script>')
assert last_idx > 0, "FAIL: </script> not found"
html = html[:last_idx] + NEW_JS + "\n</script>" + html[last_idx+len('</script>'):]
print("OK new JS functions added")

# ═══════════════════════════════════════════════════════════════════
# 7. VERIFY
# ═══════════════════════════════════════════════════════════════════
bt = html.count('`')
print("Backticks:", bt)
if bt > 0:
    for i,line in enumerate(html.split('\n'),1):
        if '`' in line:
            print("  L"+str(i)+":", line[:120])

checks = [
    ('sec-inv-cocina dual', 'ic-pos-xlsx-panel' in html and 'ic-fis-manual-panel' in html),
    ('sec-inv-barras dual', 'ib-pos-xlsx-panel' in html and 'ib-fis-manual-panel' in html),
    ('compararInventarios', 'window.compararInventarios' in html),
    ('renderDiffTable', 'function renderDiffTable' in html),
    ('guardarDiferencias', 'window.guardarDiferencias' in html),
    ('posInvTab', 'window.posInvTab' in html),
    ('fisInvTab', 'window.fisInvTab' in html),
    ('importPOSExcel', 'window.importPOSExcel' in html),
    ('importPOSPDF', 'window.importPOSPDF' in html),
    ('capturarFisico', 'window.capturarFisico' in html),
    ('importFisicoExcel', 'window.importFisicoExcel' in html),
    ('importNomPagoExcel', 'window.importNomPagoExcel' in html),
    ('guardarNomPagoExcel', 'window.guardarNomPagoExcel' in html),
    ('nom-xnomina-panel', 'nom-xnomina-panel' in html),
    ('nom-xcatalogo-panel', 'nom-xcatalogo-panel' in html),
    ('nomTab 3 tabs', "['xnomina','xcatalogo','pdf']" in html),
    ('analizarReqPDF proveedores', 'proveedores' in html and 'proveedor","concepto"' in html),
    ('costo perdida table', 'rdida costo' in html and 'rdida venta' in html),
    ('totales costo venta', 'totCosto' in html and 'totVenta' in html),
    ('ic-diff-result', 'ic-diff-result' in html),
    ('ib-diff-result', 'ib-diff-result' in html),
]
all_ok = True
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
