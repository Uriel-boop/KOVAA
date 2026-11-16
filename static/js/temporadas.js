/* KOVA: decoración navideña y saludo animado, independiente de los formularios. */
(function () {
 'use strict';
 const KEY = 'kova-temporada-navidad';
 const MUTE_KEY = 'kova-saludo-oculto-sesion';
 const preview = new URLSearchParams(location.search).get('kova_navidad') === '1';
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const now = new Date();
 let setting = 'auto';
 try { setting = localStorage.getItem(KEY) || 'auto'; } catch (_) {}
 let active = setting === 'on' || (setting === 'auto' && (now.getMonth() === 11 || preview));
 const firstDelay = 15000, interval = 180000, visibleFor = 8000;
 let firstTimer = null, repeatTimer = null, hideTimer = null;
 let muted = false;
 try { muted = sessionStorage.getItem(MUTE_KEY) === '1'; } catch (_) {}
 function modalOpen() {
   return [...document.querySelectorAll('.modal, [role="dialog"]')].some(el => {
     const s = getComputedStyle(el);
     return s.display !== 'none' && s.visibility !== 'hidden' && el.getBoundingClientRect().width > 0;
   });
 }
 function hideGreeting() {
   clearTimeout(hideTimer);
   document.getElementById('kova-festive-greeting')?.classList.remove('kova-visible');
 }
 function showGreeting() {
   if (!active || muted || reduced || document.hidden || modalOpen()) return;
   const el = document.getElementById('kova-festive-greeting');
   if (!el) return;
   el.classList.add('kova-visible');
   clearTimeout(hideTimer);
   hideTimer = setTimeout(hideGreeting, visibleFor);
 }
 function stop() {
   clearTimeout(firstTimer); clearInterval(repeatTimer); clearTimeout(hideTimer);
   firstTimer = repeatTimer = hideTimer = null;
   document.getElementById('kova-festive-layer')?.remove();
   document.getElementById('kova-festive-greeting')?.remove();
 }
 function render() {
   stop();
   if (!active) return;
   const layer = document.createElement('div');
   layer.id = 'kova-festive-layer'; layer.setAttribute('aria-hidden', 'true');
   const garland = document.createElement('div'); garland.className = 'kova-garland'; layer.append(garland);
   if (!reduced) for (let i = 0; i < 26; i++) {
     const s = document.createElement('span'); s.className = 'kova-snow'; s.textContent = i % 3 === 0 ? '✦' : '❄';
     s.style.setProperty('--snow-x', ((i * 37 + 11) % 100) + '%');
     s.style.setProperty('--snow-size', (10 + i % 4 * 4) + 'px');
     s.style.setProperty('--snow-duration', (10 + i % 8 * 2) + 's');
     s.style.setProperty('--snow-delay', (-i * 1.7) + 's');
     s.style.setProperty('--snow-drift', ((i % 2 ? 1 : -1) * (25 + i % 5 * 12)) + 'px');
     layer.append(s);
   }
   document.body.append(layer);
   const greeting = document.createElement('aside');
   greeting.id = 'kova-festive-greeting'; greeting.setAttribute('aria-label', 'Saludo navideño de Kova');
   const close = document.createElement('button'); close.type = 'button'; close.className = 'kova-greeting-close';
   close.textContent = '×'; close.setAttribute('aria-label', 'Ocultar saludos de Kova durante esta sesión');
   close.addEventListener('click', () => { muted = true; try { sessionStorage.setItem(MUTE_KEY, '1'); } catch (_) {} hideGreeting(); });
   const img = document.createElement('img');
   img.src = '/static/img/kova_navidad.webp'; img.alt = 'Kova saludando con su traje navideño';
   img.width = 108; img.height = 108;
   const msg = document.createElement('span'); msg.textContent = '🎄 ¡Kova te desea felices fiestas!';
   greeting.append(close, img, msg); document.body.append(greeting);
   if (!muted && !reduced) {
     firstTimer = setTimeout(showGreeting, firstDelay);
     repeatTimer = setInterval(showGreeting, interval);
   }
 }
 function start() {
   const toggle = document.createElement('button'); toggle.type = 'button'; toggle.id = 'kova-festive-toggle';
   function label() { toggle.textContent = active ? '🎄 Ocultar Navidad' : '🎄 Mostrar Navidad'; toggle.setAttribute('aria-pressed', String(active)); }
   label(); toggle.addEventListener('click', () => {
     active = !active; try { localStorage.setItem(KEY, active ? 'on' : 'off'); } catch (_) {}
     render(); label();
   }); document.body.append(toggle); render();
   document.addEventListener('visibilitychange', () => { if (document.hidden) hideGreeting(); });
 }
 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true}); else start();
})();
