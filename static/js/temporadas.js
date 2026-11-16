/* KOVA Christmas 2026. No changes to existing page logic. */
(function(){'use strict';
 const KEY='kova-temporada-navidad';
 const params=new URLSearchParams(location.search);
 const preview=params.get('kova_navidad')==='1';
 const now=new Date();
 const scheduled=now.getMonth()===11;
 const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 let setting='auto';try{setting=localStorage.getItem(KEY)||'auto'}catch(e){}
 let active=setting==='on'||(setting==='auto'&&(scheduled||preview));
 const asset='/static/img/img_kova.jpeg';
 function remove(){document.getElementById('kova-festive-layer')?.remove();document.getElementById('kova-festive-greeting')?.remove()}
 function render(){remove();if(!active)return;
 const layer=document.createElement('div');layer.id='kova-festive-layer';layer.setAttribute('aria-hidden','true');
 const garland=document.createElement('div');garland.className='kova-garland';layer.appendChild(garland);
 if(!reduced){for(let i=0;i<26;i++){let s=document.createElement('span');s.className='kova-snow';s.textContent=i%3===0?'✦':'❄';s.style.setProperty('--snow-x',((i*37+11)%100)+'%');s.style.setProperty('--snow-size',(10+i%4*4)+'px');s.style.setProperty('--snow-duration',(10+i%8*2)+'s');s.style.setProperty('--snow-delay',(-i*1.7)+'s');s.style.setProperty('--snow-drift',((i%2?1:-1)*(25+i%5*12))+'px');layer.appendChild(s)}}document.body.appendChild(layer);
 const msg=document.createElement('div');msg.id='kova-festive-greeting';msg.setAttribute('role','note');const img=document.createElement('img');img.src=asset;img.alt='';img.onerror=()=>img.remove();msg.appendChild(img);msg.appendChild(document.createTextNode('🎄 ¡Sofía te desea felices fiestas!'));document.body.appendChild(msg);
 }
 function button(){const b=document.createElement('button');b.type='button';b.id='kova-festive-toggle';b.setAttribute('aria-label','Activar o desactivar decoración navideña de KOVA');function label(){b.textContent=active?'🎄 Ocultar Navidad':'🎄 Mostrar Navidad';b.setAttribute('aria-pressed',String(active))}label();b.addEventListener('click',()=>{active=!active;try{localStorage.setItem(KEY,active?'on':'off')}catch(e){}render();label()});document.body.appendChild(b)}
 function start(){render();button()}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
