/* Contact launcher for makemoney.gobizit.ai (test build, 2026-11-18)
 *
 * One floating button that opens a menu:
 *   Chat             -> Zoho SalesIQ chat window (the site's Zia agent)
 *   Email us         -> mailto
 *   WhatsApp         -> wa.me link
 *   Call us by web   -> ElevenLabs voice agent, in the browser (NOT SalesIQ calls)
 *   Call us by phone -> tel: link (this number is answered by Eva, the gobizit.ai voice agent)
 *
 * Must be loaded BEFORE the SalesIQ snippet (both "defer"), so the default
 * SalesIQ float button is hidden as soon as the widget is ready.
 * To remove the launcher: delete the <script src="/contact-launcher.js"> line from the pages.
 */
(function () {
  'use strict';
  if (window.__gbContactLauncher) return;
  window.__gbContactLauncher = true;

  var CONFIG = {
    email: 'makemoney@gobizit.ai',
    whatsapp: '6421330266',                       // digits only, international format
    phoneHref: '+12132123101',
    phoneLabel: '+1 (213) 212-3101',
    elevenAgentId: 'agent_2501m7qh1w30e59tm2z36hdmwmy0', // "Ethan - MakeMoney Voice Agent"
    elevenSdk: 'https://cdn.jsdelivr.net/npm/@elevenlabs/client/+esm',
    elevenWidget: 'https://unpkg.com/@elevenlabs/convai-widget-embed'
  };

  var TEXT = {
    en: { open: 'Contact us', chat: 'Chat', email: 'Email us', wa: 'WhatsApp', web: 'Call us by web',
          phone: 'Call us by phone', close: 'Close', connecting: 'Connecting…', end: 'End call',
          listening: 'Listening…', speaking: 'Agent speaking…', mic: 'Microphone access is needed for the call.',
          chatWait: 'Chat is loading…' },
    es: { open: 'Contáctanos', chat: 'Chat', email: 'Escríbenos', wa: 'WhatsApp', web: 'Llámanos por web',
          phone: 'Llámanos por teléfono', close: 'Cerrar', connecting: 'Conectando…', end: 'Finalizar llamada',
          listening: 'Escuchando…', speaking: 'El agente habla…', mic: 'Se necesita acceso al micrófono para la llamada.',
          chatWait: 'Cargando el chat…' },
    fr: { open: 'Contactez-nous', chat: 'Chat', email: 'Écrivez-nous', wa: 'WhatsApp', web: 'Appelez-nous en ligne',
          phone: 'Appelez-nous par téléphone', close: 'Fermer', connecting: 'Connexion…', end: 'Terminer l’appel',
          listening: 'À l’écoute…', speaking: 'L’agent parle…', mic: 'L’accès au microphone est nécessaire pour l’appel.',
          chatWait: 'Chargement du chat…' }
  };

  function lang() {
    var l = 'en';
    try { l = localStorage.getItem('lang') || document.documentElement.lang || 'en'; } catch (e) {}
    l = String(l).slice(0, 2).toLowerCase();
    return TEXT[l] ? l : 'en';
  }
  function t(key) { return TEXT[lang()][key]; }

  /* ---------- Zoho SalesIQ: hide the default float button, open the window on demand ---------- */
  window.$zoho = window.$zoho || {};
  window.$zoho.salesiq = window.$zoho.salesiq || { ready: function () {} };
  var siqReady = false;

  function hideSiqFloat() {
    try { window.$zoho.salesiq.floatbutton.visible('hide'); } catch (e) {}
  }
  function onSiqReady() {
    siqReady = true;
    hideSiqFloat();
    try { window.$zoho.salesiq.floatwindow.minimize(hideSiqFloat); } catch (e) {}
    try { window.$zoho.salesiq.floatwindow.close(hideSiqFloat); } catch (e) {}
  }
  if (window.$zoho.salesiq.floatbutton) {
    onSiqReady();                                   // widget already loaded
  } else {
    var prevReady = window.$zoho.salesiq.ready;
    window.$zoho.salesiq.ready = function () {
      try { if (typeof prevReady === 'function') prevReady.apply(this, arguments); } catch (e) {}
      onSiqReady();
    };
  }

  function openChat() {
    var tries = 0;
    (function attempt() {
      if (siqReady || (window.$zoho.salesiq && window.$zoho.salesiq.floatwindow)) {
        try { window.$zoho.salesiq.floatwindow.visible('show'); } catch (e) {}
        setNote('');
        setOpen(false);
        return;
      }
      setNote(t('chatWait'));
      if (++tries < 20) setTimeout(attempt, 300); else setNote('');
    })();
  }

  /* ---------- ElevenLabs voice agent: one-click web call ---------- */
  var conversation = null;
  var callState = 'idle';                            // idle | connecting | live

  function setCall(state, statusKey) {
    callState = state;
    var row = root.querySelector('[data-act="web"]');
    if (!row) return;
    row.classList.toggle('gbcl-live', state === 'live');
    row.classList.toggle('gbcl-busy', state === 'connecting');
    var label = state === 'idle' ? t('web') : state === 'connecting' ? t('connecting') : t('end');
    row.querySelector('.gbcl-label').textContent = label;
    row.querySelector('.gbcl-sub').textContent = state === 'live' && statusKey ? t(statusKey) : '';
  }

  function fallbackToWidget() {
    // The SDK could not start (blocked CDN, old browser…): load ElevenLabs' own widget instead.
    setCall('idle');
    if (document.querySelector('elevenlabs-convai')) return;
    var el = document.createElement('elevenlabs-convai');
    el.setAttribute('agent-id', CONFIG.elevenAgentId);
    document.body.appendChild(el);
    var s = document.createElement('script');
    s.src = CONFIG.elevenWidget; s.async = true; s.type = 'text/javascript';
    document.body.appendChild(s);
    setOpen(false);
  }

  function toggleWebCall() {
    if (callState === 'connecting') return;
    if (callState === 'live') {
      var c = conversation; conversation = null;
      setCall('idle');
      try { if (c) c.endSession(); } catch (e) {}
      return;
    }
    setCall('connecting');
    setNote('');
    var micOk = true;
    Promise.resolve()
      .then(function () {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
        return navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
          stream.getTracks().forEach(function (tr) { tr.stop(); });
        }, function () { micOk = false; throw new Error('mic-denied'); });
      })
      .then(function () { return import(CONFIG.elevenSdk); })
      .then(function (mod) {
        return mod.Conversation.startSession({
          agentId: CONFIG.elevenAgentId,
          connectionType: 'webrtc',
          onConnect: function () { setCall('live', 'listening'); },
          onDisconnect: function () { conversation = null; setCall('idle'); },
          onError: function () {},
          onModeChange: function (m) {
            if (callState === 'live') setCall('live', m && m.mode === 'speaking' ? 'speaking' : 'listening');
          }
        });
      })
      .then(function (c) {
        conversation = c;
        if (callState !== 'live') setCall('live', 'listening');
      })
      .catch(function () {
        conversation = null;
        if (!micOk) { setCall('idle'); setNote(t('mic')); return; }
        fallbackToWidget();
      });
  }

  /* ---------- UI ---------- */
  var ICON = {
    chat: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3h14a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-7.2L7 21.2V17H5a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3z"/><circle cx="8" cy="10" r="1.4" fill="#ff5a1f"/><circle cx="12" cy="10" r="1.4" fill="#ff5a1f"/><circle cx="16" cy="10" r="1.4" fill="#ff5a1f"/></svg>',
    email: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 7.5l8 6 8-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#25D366" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/><path fill="#fff" d="M16.6 14.2c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1-1.2-.6-2.1-1.300-2.900-2.600-.1-.2 0-.4.1-.5l.4-.5c.1-.1.2-.3.2-.4 0-.2 0-.3-.1-.4l-.7-1.700c-.2-.4-.4-.4-.5-.4h-.5c-.2 0-.4.1-.6.3-.6.6-.9 1.300-.9 2.100 0 .5.2 1.300.8 2.100 1 1.400 2.300 2.600 4 3.300 1.300.5 1.900.5 2.600.3.500-.1 1.400-.6 1.600-1.200.2-.5.2-1 .1-1.100 0-.1-.2-.2-.4-.3z"/></svg>',
    web: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.500" y="4" width="19" height="12.500" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 16.500V20M8 20.500h8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    phone: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.600 2.500l2.600-.5c.5-.1 1 .2 1.200.7l1.200 3.100c.2.4 0 .9-.3 1.200L9.600 8.500a12 12 0 0 0 5.900 5.900l1.500-1.700c.3-.3.8-.5 1.200-.3l3.100 1.200c.5.2.8.7.7 1.200l-.5 2.600c-.1.600-.6 1-1.200 1C10.900 18.400 5.600 13.100 5.600 3.700c0-.6.4-1.100 1-1.200z"/></svg>',
    close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.600" stroke-linecap="round"/></svg>'
  };

  var CSS = [
    '.gbcl{position:fixed;right:18px;bottom:18px;z-index:150;font-family:"DM Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;flex-direction:column;align-items:flex-end;gap:10px;}',
    '.gbcl *{box-sizing:border-box;}',
    '.gbcl-menu{display:none;flex-direction:column;gap:10px;width:270px;max-width:calc(100vw - 36px);}',
    '.gbcl.gbcl-open .gbcl-menu{display:flex;}',
    '.gbcl.gbcl-open .gbcl-toggle{display:none;}',
    '.gbcl-row,.gbcl-toggle,.gbcl-x{appearance:none;-webkit-appearance:none;cursor:pointer;text-decoration:none;font:inherit;color:#111;background:#fff;border:2.500px solid #ff8a1f;border-radius:999px;box-shadow:0 0 0 3px rgba(255,138,31,.18),0 6px 16px rgba(255,110,20,.28);transition:transform .12s ease,box-shadow .12s ease;}',
    '.gbcl-row{display:flex;align-items:center;gap:14px;min-height:60px;padding:8px 22px 8px 26px;text-align:left;width:100%;}',
    '.gbcl-row:hover,.gbcl-toggle:hover,.gbcl-x:hover{transform:translateY(-1px);box-shadow:0 0 0 4px rgba(255,138,31,.26),0 8px 20px rgba(255,110,20,.36);}',
    '.gbcl-row:focus-visible,.gbcl-toggle:focus-visible,.gbcl-x:focus-visible{outline:3px solid #0B1B3D;outline-offset:2px;}',
    '.gbcl-ico{flex:0 0 34px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;}',
    '.gbcl-ico svg{width:34px;height:34px;display:block;}',
    '.gbcl-txt{display:flex;flex-direction:column;line-height:1.150;min-width:0;}',
    '.gbcl-label{font-size:1.180rem;font-weight:700;letter-spacing:-.01em;}',
    '.gbcl-sub{font-size:.900rem;font-weight:500;}',
    '.gbcl-sub:empty{display:none;}',
    '.gbcl-primary,.gbcl-toggle{background:linear-gradient(180deg,#ffb22e 0%,#ff7a1a 45%,#ff4d0d 100%);border-color:#ffb347;}',
    '.gbcl-primary .gbcl-ico,.gbcl-toggle .gbcl-ico{color:#fff;}',
    '.gbcl-toggle{display:flex;align-items:center;gap:10px;min-height:54px;padding:8px 22px 8px 18px;font-size:1.050rem;font-weight:700;}',
    '.gbcl-toggle .gbcl-ico,.gbcl-toggle .gbcl-ico svg{width:28px;height:28px;flex-basis:28px;}',
    '.gbcl-x{align-self:flex-end;width:62px;height:44px;display:flex;align-items:center;justify-content:center;padding:0;}',
    '.gbcl-x svg{width:22px;height:22px;}',
    '.gbcl-busy{opacity:.750;cursor:progress;}',
    '.gbcl-live{background:#fff1f0;border-color:#e02424;box-shadow:0 0 0 3px rgba(224,36,36,.18),0 6px 16px rgba(224,36,36,.25);}',
    '.gbcl-live .gbcl-ico{color:#e02424;}',
    '.gbcl-note{font-size:.850rem;color:#0B1B3D;background:#fff;border:1px solid #e3e7f0;border-radius:12px;padding:8px 12px;max-width:270px;box-shadow:0 4px 12px rgba(5,16,32,.12);}',
    '.gbcl-note:empty{display:none;}',
    '@media (max-width:480px){.gbcl{right:12px;bottom:12px;}.gbcl-menu{width:240px;}.gbcl-row{min-height:52px;padding:6px 16px 6px 18px;gap:10px;}.gbcl-label{font-size:1.050rem;}.gbcl-ico,.gbcl-ico svg{width:28px;height:28px;flex-basis:28px;}}',
    '@media (prefers-reduced-motion:reduce){.gbcl-row,.gbcl-toggle,.gbcl-x{transition:none;}}',
    '@media print{.gbcl{display:none;}}'
  ].join('');

  var root = document.createElement('div');
  root.className = 'gbcl';

  function rowHtml(act, tag, attrs, icon, sub, extraClass) {
    return '<' + tag + ' class="gbcl-row' + (extraClass ? ' ' + extraClass : '') + '" data-act="' + act + '" ' + attrs + '>' +
      '<span class="gbcl-ico">' + ICON[icon] + '</span>' +
      '<span class="gbcl-txt"><span class="gbcl-label"></span><span class="gbcl-sub">' + (sub || '') + '</span></span>' +
      '</' + tag + '>';
  }

  function render() {
    root.innerHTML =
      '<div class="gbcl-menu" id="gbcl-menu">' +
        rowHtml('chat', 'button', 'type="button"', 'chat', '', 'gbcl-primary') +
        rowHtml('email', 'a', 'href="mailto:' + CONFIG.email + '"', 'email') +
        rowHtml('wa', 'a', 'href="https://wa.me/' + CONFIG.whatsapp + '" target="_blank" rel="noopener"', 'wa') +
        rowHtml('web', 'button', 'type="button"', 'web') +
        rowHtml('phone', 'a', 'href="tel:' + CONFIG.phoneHref + '"', 'phone', CONFIG.phoneLabel) +
        '<div class="gbcl-note" role="status" aria-live="polite"></div>' +
        '<button type="button" class="gbcl-x" data-act="close">' + ICON.close + '</button>' +
      '</div>' +
      '<button type="button" class="gbcl-toggle" data-act="open" aria-expanded="false" aria-controls="gbcl-menu">' +
        '<span class="gbcl-ico">' + ICON.chat + '</span><span class="gbcl-open-label"></span>' +
      '</button>';
    applyText();
  }

  function applyText() {
    ['chat', 'email', 'wa', 'phone'].forEach(function (k) {
      root.querySelector('[data-act="' + k + '"] .gbcl-label').textContent = t(k);
    });
    root.querySelector('.gbcl-open-label').textContent = t('open');
    root.querySelector('.gbcl-x').setAttribute('aria-label', t('close'));
    setCall(callState, callState === 'live' ? 'listening' : null);
  }

  function setNote(msg) {
    var n = root.querySelector('.gbcl-note');
    if (n) n.textContent = msg || '';
  }

  function setOpen(open) {
    root.classList.toggle('gbcl-open', !!open);
    var tg = root.querySelector('.gbcl-toggle');
    if (tg) tg.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open) setNote('');
  }

  root.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('[data-act]') : null;
    if (!el) return;
    var act = el.getAttribute('data-act');
    if (act === 'open') setOpen(true);
    else if (act === 'close') setOpen(false);
    else if (act === 'chat') openChat();
    else if (act === 'web') toggleWebCall();
    else setOpen(false);                             // email / wa / phone: plain links
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && root.classList.contains('gbcl-open') && callState === 'idle') setOpen(false);
  });

  // Follow the site's EN / ES / FR toggle.
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.lang-toggle')) setTimeout(applyText, 0);
  });

  function mount() {
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);
    render();
    document.body.appendChild(root);
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
