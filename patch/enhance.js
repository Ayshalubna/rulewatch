/* RuleWatch "Gulf morning" interface layer: a 3D showcase in the hero (the Dubai Marina photo as a tilted card with
   frosted verdict cards floating in front of it at different depths, following the pointer), a light 3D tilt on
   cards, and the rule calculators. Plain CSS transforms, no libraries. It never changes the text React renders. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var touch = window.matchMedia && window.matchMedia('(hover: none)').matches;
  var X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M7 7l10 10M17 7L7 17"/></svg>';
  var OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  var DOC = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3.5h7l4 4V20a.5.5 0 0 1-.5.5h-10A.5.5 0 0 1 7 20z"/><path d="M10 12h5M10 16h5"/></svg>';
  var TXT = {
    en: { tag: 'Rules watched live',
      a: ['Not allowed', 'Selling off-plan before escrow is open', 'Law No. 8 of 2007, escrow accounts'],
      b: ['Allowed', 'Advertising with a Trakheesi permit', 'RERA advertising rules'],
      c: ['Needs a licence', 'Selling tokenised property units', 'VARA rulebook'],
      pill: 'Every answer points to the clause' },
    ar: { tag: 'قواعد تُراقب مباشرة',
      a: ['غير مسموح', 'البيع على الخارطة قبل فتح حساب الضمان', 'القانون رقم 8 لسنة 2007'],
      b: ['مسموح', 'الإعلان بتصريح تراخيصي', 'قواعد الإعلان لدى ريرا'],
      c: ['يحتاج ترخيصاً', 'بيع وحدات عقارية مرمّزة', 'قواعد فارا'],
      pill: 'كل إجابة تشير إلى المادة' }
  };
  function glass(cls, icon, t) {
    return '<div class="rw-glass ' + cls + '"><div class="rw-float" style="display:flex;gap:.7rem;align-items:flex-start"><i>' + icon +
      '</i><span><em>' + t[0] + '</em><b>' + t[1] + '</b><small>' + t[2] + '</small></span></div></div>';
  }
  var stage = null, show = null, tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  function lang() { return document.documentElement.lang === 'ar' ? 'ar' : 'en'; }
  function build(section) {
    var old = section.querySelector('.rw-show');
    if (old && old.dataset.lang === lang()) return;
    if (old) old.remove();
    var t = TXT[lang()];
    show = document.createElement('div');
    show.className = 'rw-show'; show.dataset.lang = lang(); show.setAttribute('aria-hidden', 'true');
    show.innerHTML = '<div class="rw-stage"><div class="rw-photo"><img src="/img/hero.jpg" alt="" decoding="async"></div>' +
      '<div class="rw-tag">' + t.tag + '</div>' + glass('rw-no rw-g1', X, t.a) + glass('rw-ok rw-g2', OK, t.b) + glass('rw-lic rw-g3', DOC, t.c) +
      '<div class="rw-pill">' + OK + '<span>' + t.pill + '</span></div></div>';
    section.appendChild(show);
    stage = show.firstChild;
    var el = show;
    requestAnimationFrame(function () { requestAnimationFrame(function () { el.classList.add('rw-ready'); }); });
  }

  /* builder credit: under the hero buttons and in the footer of every page */
  var BY = {
    en: { lead: 'Designed and built by', role: 'AI Engineer, Dubai', foot: 'Built by Ayesha Lubna', port: 'Portfolio', code: 'Source code' },
    ar: { lead: 'تصميم وتطوير', role: 'مهندسة ذكاء اصطناعي، دبي', foot: 'من تطوير عائشة لبنى', port: 'الأعمال', code: 'الشيفرة المصدرية' }
  };
  var PORT = 'https://ayeshalubna-builds.netlify.app/', GH = 'https://github.com/Ayshalubna/rulewatch';
  function credits() {
    var t = BY[lang()];
    var hero = document.querySelector('section.grain');
    if (hero) {
      var old = hero.querySelector('.rw-by');
      if (!old || old.dataset.lang !== lang()) {
        if (old) old.remove();
        var cta = hero.querySelector('.btn-primary');
        var row = cta ? cta.parentElement : null;
        if (row) {
          var d = document.createElement('a');
          d.className = 'rw-by'; d.dataset.lang = lang(); d.href = PORT; d.target = '_blank'; d.rel = 'noopener';
          d.innerHTML = '<span class="rw-by-mono">AL</span><span><small>' + t.lead + '</small><b>Ayesha Lubna</b><em>' + t.role + '</em></span>';
          row.parentElement.insertBefore(d, row.nextSibling);
        }
      }
    }
    var f = document.querySelector('footer');
    if (f) {
      var o2 = f.querySelector('.rw-foot');
      if (!o2 || o2.dataset.lang !== lang()) {
        if (o2) o2.remove();
        var p = document.createElement('p');
        p.className = 'rw-foot'; p.dataset.lang = lang();
        p.innerHTML = '<b>' + t.foot + '</b><a href="' + PORT + '" target="_blank" rel="noopener">' + t.port + '</a><a href="' + GH + '" target="_blank" rel="noopener">' + t.code + '</a>';
        f.appendChild(p);
      }
    }
  }
  function scan() {
    credits();
    var s = document.querySelector('section.grain');
    if (s) build(s); else { stage = null; show = null; }
  }
  function tick() {
    raf = 0;
    if (!stage || !stage.isConnected) return;
    cx += (tx - cx) * 0.07; cy += (ty - cy) * 0.07;
    var rtl = document.documentElement.dir === 'rtl' ? -1 : 1;
    stage.style.transform = 'rotateX(' + (5 - cy * 7).toFixed(2) + 'deg) rotateY(' + (-15 * rtl + cx * 10).toFixed(2) + 'deg)';
    stage.style.setProperty('--rw-px', (-cx * 12).toFixed(1) + 'px');
    stage.style.setProperty('--rw-py', (-cy * 10).toFixed(1) + 'px');
    if (Math.abs(tx - cx) > 0.002 || Math.abs(ty - cy) > 0.002) raf = requestAnimationFrame(tick);
  }
  function onMove(e) {
    tx = e.clientX / window.innerWidth * 2 - 1; ty = e.clientY / window.innerHeight * 2 - 1;
    if (stage && !raf && window.scrollY < window.innerHeight) raf = requestAnimationFrame(tick);
    tiltMove(e);
  }

  /* light 3D tilt on cards */
  var TILT = '.panel, [role="radio"], main a[href^="#/rules/"]';
  var active = null;
  function tiltMove(e) {
    var el = e.target.closest ? e.target.closest(TILT) : null;
    if (active && active !== el) { active.style.transform = ''; active.classList.remove('rw-tilting'); active = null; }
    if (!el) return;
    var r = el.getBoundingClientRect();
    if (r.width < 60 || r.height < 40 || r.width > 620 || r.height > 520) return;
    var px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
    el.classList.add('rw-tilting');
    el.style.setProperty('--rw-gx', (px * 100).toFixed(1) + '%');
    el.style.setProperty('--rw-gy', (py * 100).toFixed(1) + '%');
    el.style.transform = 'perspective(900px) rotateX(' + ((0.5 - py) * 6).toFixed(2) + 'deg) rotateY(' + ((px - 0.5) * 6).toFixed(2) + 'deg) translateZ(6px)';
    active = el;
  }
  function tiltOut() { if (active) { active.style.transform = ''; active.classList.remove('rw-tilting'); active = null; } }

  function boot() {
    document.documentElement.classList.add('rw-day');
    scan();
    var pend = false;
    function later() { if (pend) return; pend = true; setTimeout(function () { pend = false; scan(); }, 80); }
    new MutationObserver(later).observe(document.getElementById('root') || document.body, { childList: true, subtree: true });
    new MutationObserver(later).observe(document.documentElement, { attributes: true, attributeFilter: ['lang', 'dir'] });
    if (!touch && !reduce) {
      document.addEventListener('mousemove', onMove, { passive: true });
      document.addEventListener('mouseleave', tiltOut, { passive: true });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();

/* ---------------- Rule calculators: quick, exact arithmetic from the rules in the library ---------------- */
(function () {
  'use strict';
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function num(id) { var v = parseFloat(String(document.getElementById(id).value).replace(/[, ]/g, '')); return isFinite(v) && v > 0 ? v : 0; }
  function aed(n) { return 'AED ' + Math.round(n).toLocaleString('en-US'); }
  function row(label, value, strong) { return '<div class="rwc-row' + (strong ? ' rwc-strong' : '') + '"><span>' + label + '</span><b>' + value + '</b></div>'; }

  var TABS = [
    { id: 'rent', name: 'Rent increase',
      form: '<label>Current yearly rent (AED)<input id="rwc-r1" inputmode="numeric" placeholder="e.g. 80,000"></label>' +
            '<label>Average market rent for similar units, from the RERA rental index (AED)<input id="rwc-r2" inputmode="numeric" placeholder="e.g. 110,000"></label>',
      calc: function () {
        var cur = num('rwc-r1'), avg = num('rwc-r2');
        if (!cur || !avg) return '<p class="rwc-hint">Enter both figures to see the highest increase the law allows on renewal.</p>';
        var gap = (avg - cur) / avg * 100, pct = gap <= 10 ? 0 : gap <= 20 ? 5 : gap <= 30 ? 10 : gap <= 40 ? 15 : 20;
        return row('Your rent is below the market average by', (gap > 0 ? gap.toFixed(1) : '0') + '%') +
          row('Highest increase allowed', pct + '%', true) +
          row('Highest new yearly rent', aed(cur * (1 + pct / 100)), true) +
          '<p class="rwc-note">Decree No. 43 of 2013: no increase up to 10% below the average, then 5%, 10%, 15% and at most 20% (more than 40% below). ' +
          'The landlord must give 90 days\' notice before the contract ends. Confirm the average with the official RERA rental index.</p>';
      } },
    { id: 'buy', name: 'Buying costs',
      form: '<label>Purchase price (AED)<input id="rwc-b1" inputmode="numeric" placeholder="e.g. 1,500,000"></label>' +
            '<label>Property type<select id="rwc-b2"><option value="unit">Ready apartment, villa or office</option><option value="land">Land</option><option value="offplan">Off-plan unit</option></select></label>' +
            '<label>Mortgage loan amount, if any (AED)<input id="rwc-b3" inputmode="numeric" placeholder="0"></label>' +
            '<label class="rwc-check"><input type="checkbox" id="rwc-b4" checked> Include broker commission (market standard 2% + VAT)</label>',
      calc: function () {
        var price = num('rwc-b1'), type = document.getElementById('rwc-b2').value, loan = num('rwc-b3'),
            agent = document.getElementById('rwc-b4').checked;
        if (!price) return '<p class="rwc-hint">Enter the price to see the government fees and the usual extra costs.</p>';
        var fee = price * 0.04, admin = type === 'land' ? 430 : type === 'offplan' ? 40 : 580, deed = type === 'offplan' ? 0 : 250,
            trustee = type === 'offplan' ? 0 : (price >= 500000 ? 4000 : 2000) * 1.05, mort = loan ? loan * 0.0025 + 290 : 0,
            comm = agent ? price * 0.02 * 1.05 : 0, total = fee + admin + deed + trustee + mort + comm, out = '';
        out += row(type === 'offplan' ? 'Off-plan (Oqood) registration fee, 4%' : 'DLD transfer fee, 4%', aed(fee));
        out += row('DLD administration fee', aed(admin));
        if (deed) out += row('Title deed issuance', aed(deed));
        if (trustee) out += row('Registration Trustee fee incl. VAT', aed(trustee));
        if (mort) out += row('Mortgage registration, 0.25% + AED 290', aed(mort));
        if (comm) out += row('Broker commission, 2% + 5% VAT', aed(comm));
        out += row('Estimated total on top of the price', aed(total), true) + row('That is', (total / price * 100).toFixed(2) + '% of the price');
        return out + '<p class="rwc-note">Government fees follow current Dubai Land Department practice; commission is set by your brokerage agreement. ' +
          'Fees can change, so confirm the amounts with DLD before closing.</p>';
      } },
    { id: 'rdc', name: 'Dispute fee',
      form: '<label>Yearly rent in the tenancy contract (AED)<input id="rwc-d1" inputmode="numeric" placeholder="e.g. 95,000"></label>',
      calc: function () {
        var rent = num('rwc-d1');
        if (!rent) return '<p class="rwc-hint">Enter the yearly rent to see the Rental Disputes Center filing fee.</p>';
        var fee = Math.min(20000, Math.max(500, rent * 0.035));
        return row('3.5% of the yearly rent', aed(rent * 0.035)) + row('Filing fee you pay', aed(fee), true) +
          '<p class="rwc-note">Rental Disputes Center (Decree No. 26 of 2013): 3.5% of the yearly rent, never less than AED 500 or more than AED 20,000, ' +
          'plus small administrative charges. An Ejari certificate is normally needed to file.</p>';
      } }
  ];

  function build() {
    if (document.getElementById('rwc-open')) return;
    var btn = el('button', '', '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2.5" width="16" height="19" rx="2.5"/><path d="M8 6.5h8M8 11h.01M12 11h.01M16 11h.01M8 14.5h.01M12 14.5h.01M16 14.5h.01M8 18h.01M12 18h4"/></svg><span>Calculators</span>');
    btn.id = 'rwc-open'; btn.type = 'button'; btn.setAttribute('aria-label', 'Open rule calculators');
    var panel = el('div'); panel.id = 'rwc-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Rule calculators'); panel.hidden = true;
    var head = el('div', 'rwc-head', '<strong>Rule calculators</strong><button type="button" id="rwc-close" aria-label="Close">&times;</button>');
    var tabs = el('div', 'rwc-tabs'), body = el('div', 'rwc-body');
    panel.appendChild(head); panel.appendChild(tabs); panel.appendChild(body);
    var current = 0;
    function show(i) {
      current = i;
      [].forEach.call(tabs.children, function (t, k) { t.classList.toggle('on', k === i); });
      body.innerHTML = '<div class="rwc-form">' + TABS[i].form + '</div><div class="rwc-out" id="rwc-out"></div>';
      update();
    }
    function update() { var o = document.getElementById('rwc-out'); if (o) o.innerHTML = TABS[current].calc(); }
    TABS.forEach(function (t, i) { var b = el('button', '', t.name); b.type = 'button'; b.onclick = function () { show(i); }; tabs.appendChild(b); });
    body.addEventListener('input', update); body.addEventListener('change', update);
    btn.onclick = function () { panel.hidden = !panel.hidden; if (!panel.hidden) { show(current); var f = panel.querySelector('input'); if (f) f.focus(); } };
    head.querySelector('#rwc-close').onclick = function () { panel.hidden = true; btn.focus(); };
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { panel.hidden = true; btn.focus(); } });
    document.body.appendChild(btn); document.body.appendChild(panel);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
