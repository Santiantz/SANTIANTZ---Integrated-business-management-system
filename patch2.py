#!/usr/bin/env python3
import re, sys

with open('public/index.html','r',encoding='utf-8') as f:
    html = f.read()

# ── 1. Extract dead inline content from <script src="sheetjs"> tag ──────────
dead_m = re.search(
    r'<script src="https://cdn\.sheetjs[^"]*">([\s\S]*?)</script>\s*</head>',
    html
)
assert dead_m, "FAIL: SheetJS dead block not found"
dead_content = dead_m.group(1).strip()
print("OK extracted dead block")

# ── 2. Replace dead block with proper self-closing SheetJS tag ───────────────
html = re.sub(
    r'<script src="https://cdn\.sheetjs[^"]*">[\s\S]*?</script>\s*</head>',
    '<script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js"></script>\n</head>',
    html
)
assert '<script src="https://cdn.sheetjs' in html and 'showNegocioSelector' not in html[:html.index('<script type="module">')], \
    "FAIL: dead block still present"
print("OK fixed SheetJS tag")

# ── 3. NAV propietario — add all sections ────────────────────────────────────
OLD_NAV = "  propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}],"
NEW_NAV = "  propietario:[{s:'dashboard',i:'◈',l:'Dashboard',g:'Resumen'},{s:'requisiciones',i:'◇',l:'Requisiciones',g:'Operación'},{s:'nominas',i:'◑',l:'Nóminas',g:'Operación'},{s:'mi-negocio',i:'◈',l:'Mi negocio',g:'Operación'},{s:'inv-cocina',i:'🍽',l:'Cocina',g:'Operación'},{s:'inv-barras',i:'🍹',l:'Barras',g:'Operación'},{s:'cierre-caja',i:'💰',l:'Caja',g:'Operación'},{s:'negocios',i:'◎',l:'Negocios',g:'Config'},{s:'facturas',i:'▣',l:'Facturas',g:'Datos'},{s:'ventas',i:'◐',l:'Ventas',g:'Datos'},{s:'usuarios',i:'⊙',l:'Usuarios',g:'Config'}],"
assert OLD_NAV in html, "FAIL: propietario NAV not found"
html = html.replace(OLD_NAV, NEW_NAV, 1)
print("OK NAV propietario updated")

# ── 4. propietario negocioId fallback in showApp ─────────────────────────────
OLD_SA = "function showApp(){\n  if(['director','compras'].includes(userData.rol)&&negocios.length>1&&!userData.negocioId){showNegocioSelector();return;}"
NEW_SA = "function showApp(){\n  if(['director','compras'].includes(userData.rol)&&negocios.length>1&&!userData.negocioId){showNegocioSelector();return;}\n  if(userData.rol==='propietario'&&!userData.negocioId&&negocios.length>0)userData.negocioId=negocios[0].id;"
assert OLD_SA in html, "FAIL: showApp not found"
html = html.replace(OLD_SA, NEW_SA, 1)
print("OK propietario negocioId fallback")

# ── 5. Ventas import panel HTML ───────────────────────────────────────────────
OLD_VEN_TABLE = '        <div class="card"><table><thead><tr><th>Fecha</th><th>Platillo</th><th>Uds</th><th>Total</th><th>Por</th><th></th></tr></thead><tbody id="ven-tb"></tbody></table></div>'
NEW_VEN_TABLE = '''        <div class="card" style="margin-bottom:12px;">
          <div class="cl" style="margin-bottom:10px;">Importar ventas</div>
          <div style="display:flex;gap:6px;margin-bottom:12px;">
            <button class="btn pri" id="ven-tab-xlsx" onclick="venTab('xlsx')">&#128202; Excel</button>
            <button class="btn" id="ven-tab-pdf" onclick="venTab('pdf')">&#129302; PDF + IA</button>
          </div>
          <div id="ven-xlsx-panel">
            <div class="upload-zone" onclick="document.getElementById('ven-xlsx-file').click()"><input type="file" id="ven-xlsx-file" accept=".xlsx,.xls" onchange="importVentasXLSX(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#128202;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Excel de ventas</div><div style="font-size:10px;color:var(--t3);margin-top:3px;">Columnas: FECHA &middot; PLATILLO &middot; CANTIDAD &middot; PRECIO</div></div>
            <div id="ven-xlsx-preview"></div>
          </div>
          <div id="ven-pdf-panel" style="display:none;">
            <div class="fr" style="margin-bottom:10px;"><label>API Key Anthropic</label><input type="password" id="ven-api-key" placeholder="sk-ant-api03-..." style="width:100%;padding:8px 10px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;"></div>
            <div class="upload-zone" onclick="document.getElementById('ven-pdf-file').click()"><input type="file" id="ven-pdf-file" accept=".pdf" onchange="importVentasPDF(this)" style="display:none"><div style="font-size:24px;color:var(--t3);">&#129302;</div><div style="font-size:11px;color:var(--t2);margin-top:4px;">Reporte de ventas PDF</div></div>
            <div id="ven-pdf-preview"></div>
          </div>
        </div>
        <div class="card"><table><thead><tr><th>Fecha</th><th>Platillo</th><th>Uds</th><th>Total</th><th>Por</th><th></th></tr></thead><tbody id="ven-tb"></tbody></table></div>'''
assert OLD_VEN_TABLE in html, "FAIL: ventas table anchor not found"
html = html.replace(OLD_VEN_TABLE, NEW_VEN_TABLE, 1)
print("OK ventas import panel HTML")

# ── 6. Nominas import panel HTML ─────────────────────────────────────────────
OLD_NOM_G2 = '        <div id="nom-filt" style="margin-bottom:10px;"></div>\n        <div class="g2" style="margin-bottom:12px;">'
NEW_NOM_G2 = '''        <div id="nom-filt" style="margin-bottom:10px;"></div>
        <div class="card" style="margin-bottom:12px;">
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
        </div>
        <div class="g2" style="margin-bottom:12px;">'''
assert OLD_NOM_G2 in html, "FAIL: nom-filt anchor not found"
html = html.replace(OLD_NOM_G2, NEW_NOM_G2, 1)
print("OK nominas import panel HTML")

# ── 7. New JS to add to module script ────────────────────────────────────────
NEW_JS = r"""
window.venTab=function(tab){
  ['xlsx','pdf'].forEach(function(t){
    const panel=document.getElementById('ven-'+t+'-panel');
    if(panel)panel.style.display=t===tab?'':'none';
    const btn=document.getElementById('ven-tab-'+t);
    if(btn)btn.className=t===tab?'btn pri':'btn';
  });
  if(tab==='pdf'){const k=localStorage.getItem('ant_key');const inp=document.getElementById('ven-api-key');if(k&&inp&&!inp.value)inp.value=k;}
};

window.importVentasXLSX=function(input){
  const file=input.files[0];if(!file)return;
  if(typeof XLSX==='undefined'){alert('SheetJS no cargo.');return;}
  const prev=document.getElementById('ven-xlsx-preview');
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'>Procesando Excel...</div>";
  const reader=new FileReader();
  reader.onload=function(e){
    try{
      const wb=XLSX.read(e.target.result,{type:'array',cellDates:true});
      const ws=wb.Sheets[wb.SheetNames[0]];
      const rows=XLSX.utils.sheet_to_json(ws,{header:1,raw:false,defval:''});
      if(rows.length<2){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Archivo vacio</div>";return;}
      const hdrs=rows[0].map(function(h){return String(h||'').toUpperCase().trim();});
      const fi=function(kws){for(let k=0;k<kws.length;k++){const idx=hdrs.findIndex(function(h){return h.includes(kws[k]);});if(idx>-1)return idx;}return -1;};
      const cols={fecha:fi(['FECHA','DATE']),plat:fi(['PLATILLO','PRODUCTO','PLATO','ITEM','DESCRIPCI']),cant:fi(['CANT','QTY','CANTIDAD','UNIDADES']),prec:fi(['PRECIO','PRICE','UNIT','VALOR']),tot:fi(['TOTAL','IMPORTE','AMOUNT'])};
      const fmtDate=function(v){if(!v)return '';const d=new Date(v);if(!isNaN(d.getTime()))return d.toISOString().split('T')[0];return String(v).substring(0,10);};
      const fmtNum=function(v){return parseFloat(String(v||0).replace(/[$,\s]/g,''))||0;};
      const data=rows.slice(1).filter(function(r){return r.some(function(c){return String(c||'').trim();});}).map(function(r){
        const cant=fmtNum(cols.cant>=0?r[cols.cant]:1)||1;
        const prec=fmtNum(cols.prec>=0?r[cols.prec]:0);
        const tot=fmtNum(cols.tot>=0?r[cols.tot]:0)||cant*prec;
        return{fecha:fmtDate(cols.fecha>=0?r[cols.fecha]:''),plat:cols.plat>=0?String(r[cols.plat]||''):'',cant,prec,tot};
      }).filter(function(r){return r.plat;});
      if(!data.length){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>No se detectaron ventas</div>";return;}
      window._venXlsxData=data;
      const IS='padding:3px 5px;background:var(--s2);border:1px solid var(--bd);border-radius:4px;color:var(--t);font-size:11px;';
      let h="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>&#10003; "+data.length+" venta"+(data.length!==1?'s':'')+" detectada"+(data.length!==1?'s':'')+"</div><div style='overflow-x:auto;'><table><thead><tr><th>Fecha</th><th>Platillo</th><th>Cant.</th><th>Precio</th><th>Total</th></tr></thead><tbody>";
      data.forEach(function(r,i){
        h+="<tr>"
          +"<td><input id='vx-f-"+i+"' value='"+r.fecha+"' style='width:92px;"+IS+"'></td>"
          +"<td><input id='vx-p-"+i+"' value=\""+r.plat.replace(/"/g,'')+"\" style='width:140px;"+IS+"'></td>"
          +"<td><input type='number' id='vx-c-"+i+"' value='"+r.cant+"' style='width:55px;"+IS+"'></td>"
          +"<td><input type='number' id='vx-pr-"+i+"' value='"+r.prec.toFixed(2)+"' style='width:80px;"+IS+"'></td>"
          +"<td style='color:var(--a2);font-weight:500;'>$"+r.tot.toFixed(2)+"</td></tr>";
      });
      h+="</tbody></table></div><button class='btn pri' style='width:100%;margin-top:10px;' onclick='guardarVentasXLSX("+data.length+")'>Importar "+data.length+" venta"+(data.length!==1?'s':'')+"</button></div>";
      prev.innerHTML=h;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarVentasXLSX=async function(count){
  const negId=userData.negocioId||negocios[0]?.id;
  const btn=event.target;btn.textContent='Importando...';btn.disabled=true;
  try{
    let saved=0;
    for(let i=0;i<count;i++){
      const plat=document.getElementById('vx-p-'+i)?.value||'';if(!plat)continue;
      const cant=parseFloat(document.getElementById('vx-c-'+i)?.value)||1;
      const prec=parseFloat(document.getElementById('vx-pr-'+i)?.value)||0;
      await addDoc(collection(db,'ventas'),{negocioId:negId,platillo:plat,fecha:document.getElementById('vx-f-'+i)?.value||'',cantidad:cant,precio:prec,total:cant*prec,registradoPor:userData.nombre,rol:userData.rol,creadoEn:serverTimestamp()});
      saved++;
    }
    document.getElementById('ven-xlsx-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>&#10003; "+saved+" venta"+(saved!==1?'s':'')+" importada"+(saved!==1?'s':'')+"</div>";
    document.getElementById('ven-xlsx-file').value='';renderVentas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Importar';btn.disabled=false;
};

window.importVentasPDF=async function(input){
  const file=input.files[0];if(!file)return;
  const apiKey=(document.getElementById('ven-api-key').value.trim())||localStorage.getItem('ant_key')||'';
  const prev=document.getElementById('ven-pdf-preview');
  if(!apiKey){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Ingresa tu API Key de Anthropic primero</div>";return;}
  localStorage.setItem('ant_key',apiKey);
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'><span class='spin'></span> Analizando PDF con Claude...</div>";
  const reader=new FileReader();
  reader.onload=async function(e){
    try{
      const bytes=new Uint8Array(e.target.result);
      let b64='';const CHUNK=8192;
      for(let i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
      const resp=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:1500,messages:[{role:'user',content:[{type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},{type:'text',text:'Extrae las ventas de este documento. Responde SOLO con JSON: {"ventas":[{"fecha":"YYYY-MM-DD","platillo":"nombre","cantidad":1,"precio":0.00,"total":0.00}]}'}]}]})});
      if(!resp.ok){const err=await resp.json().catch(function(){return{};});throw new Error(err.error?.message||'HTTP '+resp.status);}
      const data=await resp.json();
      const text=data.content?.[0]?.text||'';
      const match=text.match(/\{[\s\S]*\}/);
      if(!match)throw new Error('Claude no devolvio JSON valido');
      const parsed=JSON.parse(match[0]);
      const ventas=parsed.ventas||[];
      if(!ventas.length)throw new Error('No se encontraron ventas en el PDF');
      const INP='width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;';
      let h="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>&#10003; "+ventas.length+" venta"+(ventas.length!==1?'s':'')+" extraida"+(ventas.length!==1?'s':'')+" por Claude</div>";
      ventas.forEach(function(v,i){
        h+="<div class='card' style='margin-bottom:6px;padding:8px;'><div class='fg3'>"
          +"<div class='fr'><label>Fecha</label><input type='date' id='vp-f-"+i+"' value='"+(v.fecha||'')+"' style='"+INP+"'></div>"
          +"<div class='fr'><label>Platillo</label><input id='vp-p-"+i+"' value=\""+String(v.platillo||'').replace(/"/g,'')+"\" style='"+INP+"'></div>"
          +"<div class='fr'><label>Cant.</label><input type='number' id='vp-c-"+i+"' value='"+(v.cantidad||1)+"' style='"+INP+"'></div>"
          +"</div><div class='fg2'>"
          +"<div class='fr'><label>Precio ($)</label><input type='number' id='vp-pr-"+i+"' value='"+(v.precio||0).toFixed(2)+"' step='0.01' style='"+INP+"'></div>"
          +"<div class='fr'><label>Total ($)</label><input type='number' id='vp-t-"+i+"' value='"+(v.total||0).toFixed(2)+"' step='0.01' style='"+INP+"'></div>"
          +"</div></div>";
      });
      h+="<button class='btn pri' style='width:100%;margin-top:4px;' onclick='guardarVentasPDF("+ventas.length+")'>Guardar "+ventas.length+" venta"+(ventas.length!==1?'s':'')+"</button></div>";
      prev.innerHTML=h;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarVentasPDF=async function(count){
  const negId=userData.negocioId||negocios[0]?.id;
  const btn=event.target;btn.textContent='Guardando...';btn.disabled=true;
  try{
    let saved=0;
    for(let i=0;i<count;i++){
      const plat=document.getElementById('vp-p-'+i)?.value||'';if(!plat)continue;
      const cant=parseFloat(document.getElementById('vp-c-'+i)?.value)||1;
      const prec=parseFloat(document.getElementById('vp-pr-'+i)?.value)||0;
      const tot=parseFloat(document.getElementById('vp-t-'+i)?.value)||cant*prec;
      await addDoc(collection(db,'ventas'),{negocioId:negId,platillo:plat,fecha:document.getElementById('vp-f-'+i)?.value||'',cantidad:cant,precio:prec,total:tot,registradoPor:userData.nombre,rol:userData.rol,creadoEn:serverTimestamp()});
      saved++;
    }
    document.getElementById('ven-pdf-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>&#10003; "+saved+" venta"+(saved!==1?'s':'')+" guardada"+(saved!==1?'s':'')+"</div>";
    document.getElementById('ven-pdf-file').value='';renderVentas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Guardar';btn.disabled=false;
};

window.nomTab=function(tab){
  ['xlsx','pdf'].forEach(function(t){
    const panel=document.getElementById('nom-'+t+'-panel');
    if(panel)panel.style.display=t===tab?'':'none';
    const btn=document.getElementById('nom-tab-'+t);
    if(btn)btn.className=t===tab?'btn pri':'btn';
  });
};

window.importNomExcel=function(input){
  const file=input.files[0];if(!file)return;
  if(typeof XLSX==='undefined'){alert('SheetJS no cargo.');return;}
  const prev=document.getElementById('nom-xlsx-preview');
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'>Procesando Excel...</div>";
  const reader=new FileReader();
  reader.onload=function(e){
    try{
      const wb=XLSX.read(e.target.result,{type:'array',raw:false,defval:''});
      const ws=wb.Sheets[wb.SheetNames[0]];
      const rows=XLSX.utils.sheet_to_json(ws,{header:1,raw:false,defval:''});
      if(rows.length<2){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Archivo vacio</div>";return;}
      const hdrs=rows[0].map(function(h){return String(h||'').toUpperCase().trim();});
      const fi=function(kws){for(let k=0;k<kws.length;k++){const idx=hdrs.findIndex(function(h){return h.includes(kws[k]);});if(idx>-1)return idx;}return -1;};
      const cols={nom:fi(['NOMBRE','NAME']),pues:fi(['PUESTO','CARGO','POSICION','ROL']),sal:fi(['SALARIO','SUELDO','MONTO','AMOUNT']),tipo:fi(['TIPO','TYPE','PERIODO','FRECUENCIA'])};
      const fmtNum=function(v){return parseFloat(String(v||0).replace(/[$,\s]/g,''))||0;};
      const data=rows.slice(1).filter(function(r){return r.some(function(c){return String(c||'').trim();});}).map(function(r){
        const tipoRaw=cols.tipo>=0?String(r[cols.tipo]||'').toLowerCase():'';
        const tipo=tipoRaw.includes('quin')?'quincenal':tipoRaw.includes('mens')?'mensual':'semanal';
        return{nom:cols.nom>=0?String(r[cols.nom]||''):'',pues:cols.pues>=0?String(r[cols.pues]||''):'',sal:fmtNum(cols.sal>=0?r[cols.sal]:0),tipo};
      }).filter(function(r){return r.nom;});
      if(!data.length){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>No se detectaron empleados</div>";return;}
      window._nomXlsxData=data;
      const IS='padding:3px 5px;background:var(--s2);border:1px solid var(--bd);border-radius:4px;color:var(--t);font-size:11px;';
      const esBoss=userData.rol==='propietario';
      const negOpts=negocios.map(function(n){return "<option value='"+n.id+"'>"+n.nombre+"</option>";}).join('');
      let h="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>&#10003; "+data.length+" empleado"+(data.length!==1?'s':'')+" detectado"+(data.length!==1?'s':'')+"</div>";
      if(esBoss)h+="<div class='fr' style='margin-bottom:8px;'><label>Negocio para todos</label><select id='nom-xl-neg' style='"+IS+"'>"+negOpts+"</select></div>";
      h+="<div style='overflow-x:auto;'><table><thead><tr><th>Nombre</th><th>Puesto</th><th>Salario</th><th>Tipo</th></tr></thead><tbody>";
      data.forEach(function(r,i){
        const tipoOpts="<option value='semanal'"+(r.tipo==='semanal'?' selected':'')+">Semanal</option><option value='quincenal'"+(r.tipo==='quincenal'?' selected':'')+">Quincenal</option><option value='mensual'"+(r.tipo==='mensual'?' selected':'')+">Mensual</option>";
        h+="<tr>"
          +"<td><input id='nx-n-"+i+"' value=\""+r.nom.replace(/"/g,'')+"\" style='width:130px;"+IS+"'></td>"
          +"<td><input id='nx-p-"+i+"' value=\""+r.pues.replace(/"/g,'')+"\" style='width:110px;"+IS+"'></td>"
          +"<td><input type='number' id='nx-s-"+i+"' value='"+r.sal.toFixed(2)+"' style='width:90px;"+IS+"'></td>"
          +"<td><select id='nx-t-"+i+"' style='width:90px;"+IS+"'>"+tipoOpts+"</select></td></tr>";
      });
      h+="</tbody></table></div><button class='btn pri' style='width:100%;margin-top:10px;' onclick='guardarNomExcel("+data.length+")'>Registrar "+data.length+" empleado"+(data.length!==1?'s':'')+"</button></div>";
      prev.innerHTML=h;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarNomExcel=async function(count){
  const esBoss=userData.rol==='propietario';
  const negEl=document.getElementById('nom-xl-neg');
  const defNeg=negEl?negEl.value:(userData.negocioId||negocios[0]?.id);
  const btn=event.target;btn.textContent='Registrando...';btn.disabled=true;
  try{
    let saved=0;
    for(let i=0;i<count;i++){
      const nom=document.getElementById('nx-n-'+i)?.value||'';if(!nom)continue;
      const pues=document.getElementById('nx-p-'+i)?.value||'';
      const sal=parseFloat(document.getElementById('nx-s-'+i)?.value)||0;
      const tipo=document.getElementById('nx-t-'+i)?.value||'semanal';
      await addDoc(collection(db,'empleados'),{nombre:nom,puesto:pues,salarioBase:sal,tipo,negocioId:defNeg,activo:true,creadoPor:userData.nombre,creadoEn:serverTimestamp()});
      saved++;
    }
    document.getElementById('nom-xlsx-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>&#10003; "+saved+" empleado"+(saved!==1?'s':'')+" registrado"+(saved!==1?'s':'')+"</div>";
    document.getElementById('nom-xlsx-file').value='';renderNominas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Registrar';btn.disabled=false;
};

window.importNomPDF=async function(input){
  const file=input.files[0];if(!file)return;
  const apiKey=localStorage.getItem('ant_key')||'';
  const prev=document.getElementById('nom-pdf-preview');
  if(!apiKey){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Sin API Key. Usala primero en Facturas &gt; PDF+IA.</div>";return;}
  prev.innerHTML="<div class='abox info' style='margin-top:10px;'><span class='spin'></span> Analizando con Claude...</div>";
  const reader=new FileReader();
  reader.onload=async function(e){
    try{
      const bytes=new Uint8Array(e.target.result);
      let b64='';const CHUNK=8192;
      for(let i=0;i<bytes.length;i+=CHUNK)b64+=btoa(String.fromCharCode(...bytes.subarray(i,Math.min(i+CHUNK,bytes.length))));
      const resp=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','content-type':'application/json','anthropic-dangerous-allow-browser':'true'},body:JSON.stringify({model:'claude-sonnet-4-20250514',max_tokens:800,messages:[{role:'user',content:[{type:'document',source:{type:'base64',media_type:'application/pdf',data:b64}},{type:'text',text:'Extrae datos del comprobante de nomina. Responde SOLO con JSON: {"empleado":"nombre","puesto":"","periodo":"","fechaPago":"YYYY-MM-DD","monto":0.00,"deducciones":0.00,"neto":0.00,"notas":""}'}]}]})});
      if(!resp.ok){const err=await resp.json().catch(function(){return{};});throw new Error(err.error?.message||'HTTP '+resp.status);}
      const data=await resp.json();
      const text=data.content?.[0]?.text||'';
      const match=text.match(/\{[\s\S]*?\}/);
      if(!match)throw new Error('Claude no devolvio JSON valido');
      const nom=JSON.parse(match[0]);
      const INP='width:100%;padding:7px;background:var(--s2);border:1px solid var(--bd);border-radius:5px;color:var(--t);font-size:12px;';
      const empOpts=(window._nomEmps||[]).map(function(e){return "<option value='"+e.id+"'"+(e.nombre===nom.empleado?' selected':'')+">"+e.nombre+"</option>";}).join('');
      prev.innerHTML="<div style='margin-top:10px;'><div class='abox ok' style='margin-bottom:8px;'>&#10003; Datos extraidos por Claude</div>"
        +"<div class='fr'><label>Empleado</label><select id='np-emp' style='"+INP+"'><option value=''>Selecciona...</option>"+empOpts+"</select></div>"
        +"<div class='fg2'><div class='fr'><label>Periodo</label><input id='np-per' value=\""+String(nom.periodo||'').replace(/"/g,'')+"\" style='"+INP+"'></div>"
        +"<div class='fr'><label>Fecha de pago</label><input type='date' id='np-f' value='"+(nom.fechaPago||'')+"' style='"+INP+"'></div></div>"
        +"<div class='fg3'><div class='fr'><label>Bruto ($)</label><input type='number' id='np-m' value='"+(nom.monto||0).toFixed(2)+"' step='0.01' style='"+INP+"'></div>"
        +"<div class='fr'><label>Deducciones ($)</label><input type='number' id='np-x' value='"+(nom.deducciones||0).toFixed(2)+"' step='0.01' style='"+INP+"'></div>"
        +"<div class='fr'><label>Neto ($)</label><input type='number' id='np-ne' value='"+(nom.neto||nom.monto||0).toFixed(2)+"' step='0.01' style='"+INP+"'></div></div>"
        +"<div class='fr'><label>Notas</label><input id='np-n' value=\""+String(nom.notas||'').replace(/"/g,'')+"\" style='"+INP+"'></div>"
        +"<button class='btn pri' style='width:100%;margin-top:6px;' onclick='guardarNomPDF()'>Guardar pago de nomina</button></div>";
      window._nomPDFFile=file;
    }catch(err){prev.innerHTML="<div class='abox err' style='margin-top:8px;'>Error: "+err.message+"</div>";}
  };
  reader.readAsArrayBuffer(file);
};

window.guardarNomPDF=async function(){
  const empId=document.getElementById('np-emp')?.value||'';
  const m=parseFloat(document.getElementById('np-m')?.value)||0;
  const x=parseFloat(document.getElementById('np-x')?.value)||0;
  const neto=parseFloat(document.getElementById('np-ne')?.value)||m-x;
  const f=document.getElementById('np-f')?.value||'';
  if(!empId||!m||!f)return alert('Completa empleado, monto y fecha');
  const emp=(window._nomEmps||[]).find(function(e){return e.id===empId;});
  const nid=emp?.negocioId||userData.negocioId||negocios[0]?.id;
  const btn=event.target;btn.textContent='Guardando...';btn.disabled=true;
  try{
    let url=null,nom2=null;
    if(window._nomPDFFile){
      const r2=ref(storage,'nominas/'+(nid||'g')+'/'+f+'_'+window._nomPDFFile.name);
      await uploadBytes(r2,window._nomPDFFile);url=await getDownloadURL(r2);nom2=window._nomPDFFile.name;
    }
    await addDoc(collection(db,'nominas_pagos'),{empleadoId:empId,negocioId:nid,empleadoNombre:emp?.nombre||'',puesto:emp?.puesto||'',periodo:document.getElementById('np-per')?.value||'',fechaPago:f,monto:m,deducciones:x,neto,comprobanteUrl:url,comprobante:nom2,notas:document.getElementById('np-n')?.value||'',registradoPor:userData.nombre,creadoEn:serverTimestamp()});
    document.getElementById('nom-pdf-preview').innerHTML="<div class='abox ok' style='margin-top:8px;'>&#10003; Pago registrado correctamente</div>";
    document.getElementById('nom-pdf-file').value='';window._nomPDFFile=null;renderNominas();
  }catch(e){alert('Error: '+e.message);}
  btn.textContent='Guardar pago de nomina';btn.disabled=false;
};
"""

# ── 8. Append dead_content + new JS before module script closing tag ──────────
GETWEEK = "function getWeekStart(d){if(!d)return null;const dt=new Date(d+'T00:00:00');const day=dt.getDay();const mon=new Date(dt);mon.setDate(dt.getDate()-day+(day===0?-6:1));return mon.toISOString().split('T')[0];}\n</script>"
assert GETWEEK in html, "FAIL: getWeekStart/</script> anchor not found"
html = html.replace(
    GETWEEK,
    "function getWeekStart(d){if(!d)return null;const dt=new Date(d+'T00:00:00');const day=dt.getDay();const mon=new Date(dt);mon.setDate(dt.getDate()-day+(day===0?-6:1));return mon.toISOString().split('T')[0];}\n\n"
    + dead_content + "\n" + NEW_JS + "\n</script>",
    1
)
print("OK moved dead content + new JS to module script")

# ── 9. Verify ────────────────────────────────────────────────────────────────
bt = html.count('`')
print("Backticks:", bt)
if bt > 0:
    # find lines with backticks
    for i, line in enumerate(html.split('\n'), 1):
        if '`' in line:
            print("  Line", i, ":", line[:120])

checks = [
    ('showNegocioSelector in module', 'function showNegocioSelector' in html[html.index('<script type="module">'):]),
    ('renderNominas in module', 'async function renderNominas' in html[html.index('<script type="module">'):]),
    ('importXML in module', 'window.importXML' in html[html.index('<script type="module">'):]),
    ('venTab in module', 'window.venTab' in html[html.index('<script type="module">'):]),
    ('importVentasXLSX', 'window.importVentasXLSX' in html),
    ('importNomExcel', 'window.importNomExcel' in html),
    ('importNomPDF', 'window.importNomPDF' in html),
    ('ventas import panel', 'ven-xlsx-panel' in html),
    ('nominas import panel', 'nom-xlsx-panel' in html),
    ('propietario full nav', 'inv-cocina' in html[html.index('propietario:['):html.index('propietario:[')+500]),
    ('propietario negocioId fallback', "userData.rol==='propietario'&&!userData.negocioId&&negocios.length>0" in html),
]
all_ok = True
for name, ok in checks:
    print(("OK " if ok else "FAIL ") + name)
    if not ok: all_ok = False

lines = html.count('\n') + 1
print("Lines:", lines)

if not all_ok or bt > 0:
    print("ERRORS — not saving")
    sys.exit(1)

with open('public/index.html','w',encoding='utf-8') as f:
    f.write(html)
print("SAVED")
