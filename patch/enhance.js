/* RuleWatch 3D layer: a holographic Dubai skyline that rotates in true perspective while the watcher beam
   scans it (verdict markers: green allowed, amber check, red breach), a depth particle field, a perspective
   grid, 3D tilt on cards, scroll-in reveals and the rule calculators. Pure canvas + CSS transforms, no libraries.
   It only adds classes and inline styles, never changes the text or structure React renders. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var touch = window.matchMedia && window.matchMedia('(hover: none)').matches;
  var GOLD = [214, 170, 92], MINT = [94, 214, 170], ICE = [150, 205, 235];

  /* ---------------- canvas scene ---------------- */
  var cv = document.createElement('canvas');
  cv.id = 'rw3d';
  cv.setAttribute('aria-hidden', 'true');
  var ctx = cv.getContext('2d');
  var W = 0, H = 0, DPR = 1, mx = 0, my = 0, tx = 0, ty = 0, sy = 0, t0 = performance.now(), running = true, slowAvg = 16, frames = 0, lite = 0;

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 1.5);
    W = window.innerWidth; H = window.innerHeight;
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  var N = touch ? 80 : 200, P = [];
  function seed() {
    P = [];
    for (var i = 0; i < N; i++) {
      P.push({
        x: (Math.random() * 2 - 1) * 1.6, y: (Math.random() * 2 - 1) * 1.1, z: Math.random() * 1.9 + 0.15,
        s: Math.random() * 1.4 + 0.5, c: Math.random() < 0.62 ? GOLD : (Math.random() < 0.6 ? MINT : ICE),
        v: Math.random() * 0.00016 + 0.00005, ph: Math.random() * 6.28
      });
    }
  }

  function rgba(c, a) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a.toFixed(3) + ')'; }

  function drawGrid(time, fade) {
    /* perspective floor receding to a horizon, scrolling slowly toward the viewer */
    var hz = H * 0.60 + ty * 14 - Math.min(sy, H) * 0.25, cx = W * 0.5 + tx * 40, depth = H - hz;
    if (depth < 40 || fade <= 0.01) return;
    ctx.lineWidth = 1;
    var rows = 16, off = (time * 0.00022) % 1;
    for (var i = 0; i < rows; i++) {
      var k = (i + off) / rows, y = hz + depth * k * k, a = k * 0.16 * fade;
      ctx.strokeStyle = rgba(MINT, a);
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    var cols = 22;
    for (var j = -cols; j <= cols; j++) {
      var xb = cx + j * (W / 9);
      var g = ctx.createLinearGradient(0, hz, 0, H);
      g.addColorStop(0, rgba(MINT, 0)); g.addColorStop(1, rgba(MINT, 0.13 * fade));
      ctx.strokeStyle = g;
      ctx.beginPath(); ctx.moveTo(cx + j * 6, hz); ctx.lineTo(xb, H); ctx.stroke();
    }
  }

  /* ---- the holographic city: a rotating 3D skyline that the watcher beam scans, with verdict markers ---- */
  var CITY = null;
  function buildCity() {
    var seed = 7, towers = [];
    function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
    /* centre spire: stacked, tapering tiers */
    var tiers = [[0.30, 0, 0.55], [0.24, 0.55, 1.0], [0.18, 1.0, 1.38], [0.12, 1.38, 1.68], [0.065, 1.68, 1.92]];
    tiers.forEach(function (t) { towers.push({ x: 0, z: 0, w: t[0], d: t[0], y0: t[1], y1: t[2], spire: true }); });
    var verdicts = ['g', 'g', 'a', 'g', 'r', 'g', 'g', 'a', 'g', 'g', 'r', 'g'], vi = 0, tries = 0;
    while (towers.length < 5 + 30 && tries < 600) {
      tries++;
      var ang = rnd() * 6.2832, rad = 0.34 + Math.sqrt(rnd()) * 0.78, x = Math.cos(ang) * rad, z = Math.sin(ang) * rad;
      var w = 0.09 + rnd() * 0.10, d = 0.09 + rnd() * 0.10, ok = true;
      for (var i = 5; i < towers.length; i++) {
        if (Math.abs(towers[i].x - x) < (towers[i].w + w) * 0.62 && Math.abs(towers[i].z - z) < (towers[i].d + d) * 0.62) { ok = false; break; }
      }
      if (!ok) continue;
      var h = (0.22 + rnd() * 0.62) * (1.25 - rad * 0.55);
      towers.push({ x: x, z: z, w: w, d: d, y0: 0, y1: h, ang: Math.atan2(z, x), verdict: (towers.length % 3 === 0) ? verdicts[vi++ % verdicts.length] : null });
    }
    CITY = towers;
  }

  function drawSolid(time, fade) {
    if (fade <= 0.01 || W < 900) return;
    if (!CITY) buildCity();
    var S = Math.min(W * 0.158, H * 0.285), cx = W * 0.795 + tx * 22, cy = H * 0.63 + ty * 12 - sy * 0.35;
    var ay = time * 0.00016 + tx * 0.55, tilt = 0.50 + ty * 0.10, ca = Math.cos(ay), sa = Math.sin(ay), ct = Math.cos(tilt), st = Math.sin(tilt), D = 3.4;
    function pr(x, y, z) {
      var X = x * ca + z * sa, Z = -x * sa + z * ca, Y = y * ct - Z * st, Z2 = y * st + Z * ct, f = D / (D + Z2);
      return [cx + X * S * f, cy - Y * S * f, Z2];
    }
    var i, k;
    /* ground glow + platform rings */
    var c0 = pr(0, 0, 0), halo = ctx.createRadialGradient(c0[0], c0[1], 0, c0[0], c0[1], S * 1.5);
    halo.addColorStop(0, rgba(MINT, 0.13 * fade)); halo.addColorStop(0.6, rgba(GOLD, 0.045 * fade)); halo.addColorStop(1, rgba(GOLD, 0));
    ctx.fillStyle = halo; ctx.beginPath(); ctx.ellipse(c0[0], c0[1], S * 1.5, S * 0.85, 0, 0, 6.2832); ctx.fill();
    [0.45, 0.8, 1.18, 1.32].forEach(function (r, n) {
      ctx.beginPath();
      for (k = 0; k <= 64; k++) { var q = pr(Math.cos(k / 64 * 6.2832) * r, 0, Math.sin(k / 64 * 6.2832) * r); if (k) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); }
      ctx.strokeStyle = rgba(n === 3 ? GOLD : MINT, (n === 3 ? 0.42 : 0.16) * fade); ctx.lineWidth = n === 3 ? 1.3 : 1; ctx.stroke();
    });
    for (k = 0; k < 48; k++) {                      /* tick marks on the outer ring */
      var ta = k / 48 * 6.2832, t1 = pr(Math.cos(ta) * 1.32, 0, Math.sin(ta) * 1.32), t2 = pr(Math.cos(ta) * (k % 4 ? 1.36 : 1.42), 0, Math.sin(ta) * (k % 4 ? 1.36 : 1.42));
      ctx.strokeStyle = rgba(GOLD, 0.35 * fade); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(t1[0], t1[1]); ctx.lineTo(t2[0], t2[1]); ctx.stroke();
    }
    /* the scan beam: a radar sweep across the platform */
    var beam = (time * 0.00075) % 6.2832;
    for (k = 0; k < 26; k++) {
      var b1 = beam - k * 0.022, e1 = pr(Math.cos(b1) * 1.30, 0, Math.sin(b1) * 1.30), e2 = pr(Math.cos(b1 - 0.024) * 1.30, 0, Math.sin(b1 - 0.024) * 1.30);
      ctx.fillStyle = rgba(MINT, (0.20 - k * 0.0075) * fade);
      ctx.beginPath(); ctx.moveTo(c0[0], c0[1]); ctx.lineTo(e1[0], e1[1]); ctx.lineTo(e2[0], e2[1]); ctx.closePath(); ctx.fill();
    }
    var be = pr(Math.cos(beam) * 1.30, 0, Math.sin(beam) * 1.30);
    ctx.strokeStyle = rgba([190, 255, 228], 0.75 * fade); ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(c0[0], c0[1]); ctx.lineTo(be[0], be[1]); ctx.stroke();

    /* towers, far to near */
    var order = CITY.map(function (t, n) { return [pr(t.x, (t.y0 + t.y1) / 2, t.z)[2], n]; }).sort(function (a, b) { return b[0] - a[0]; });
    var marks = [];
    for (i = 0; i < order.length; i++) {
      var t = CITY[order[i][1]], hw = t.w / 2, hd = t.d / 2;
      var lit = 0;
      if (!t.spire) { var da = (beam - t.ang) % 6.2832; if (da < 0) da += 6.2832; lit = da < 1.5 ? 1 - da / 1.5 : 0; }
      var grow = Math.min(1, Math.max(0, (time - 300 - order[i][1] * 45) / 900)), y1 = t.y0 + (t.y1 - t.y0) * (1 - Math.pow(1 - grow, 3));
      var c = [[-hw, -hd], [hw, -hd], [hw, hd], [-hw, hd]], lo = [], hi = [];
      for (k = 0; k < 4; k++) { lo.push(pr(t.x + c[k][0], t.y0, t.z + c[k][1])); hi.push(pr(t.x + c[k][0], y1, t.z + c[k][1])); }
      var faces = [0, 1, 2, 3].map(function (n) { return [(lo[n][2] + lo[(n + 1) % 4][2]) / 2, n]; }).sort(function (a, b) { return b[0] - a[0]; });
      var line = t.spire ? GOLD : (lit > 0.05 ? [170, 255, 220] : MINT);
      for (k = 2; k < 4; k++) {                        /* the two faces turned to the viewer */
        var n = faces[k][1], m = (n + 1) % 4, g = ctx.createLinearGradient(0, hi[n][1], 0, lo[n][1]);
        g.addColorStop(0, rgba(t.spire ? [96, 76, 34] : [26, 92, 80], (0.42 + lit * 0.30) * fade));
        g.addColorStop(1, rgba([10, 34, 36], 0.30 * fade));
        ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(lo[n][0], lo[n][1]); ctx.lineTo(lo[m][0], lo[m][1]); ctx.lineTo(hi[m][0], hi[m][1]); ctx.lineTo(hi[n][0], hi[n][1]); ctx.closePath(); ctx.fill();
        ctx.strokeStyle = rgba(line, (0.50 + lit * 0.45 + (t.spire ? 0.2 : 0)) * fade); ctx.lineWidth = 1; ctx.stroke();
        var floors = Math.max(2, Math.round((y1 - t.y0) / 0.075));           /* floor lines = lit windows */
        ctx.strokeStyle = rgba(t.spire ? [255, 226, 166] : [150, 235, 205], (0.10 + lit * 0.32) * fade); ctx.lineWidth = 0.7;
        for (var fl = 1; fl < floors; fl++) {
          var u = fl / floors;
          ctx.beginPath(); ctx.moveTo(lo[n][0] + (hi[n][0] - lo[n][0]) * u, lo[n][1] + (hi[n][1] - lo[n][1]) * u);
          ctx.lineTo(lo[m][0] + (hi[m][0] - lo[m][0]) * u, lo[m][1] + (hi[m][1] - lo[m][1]) * u); ctx.stroke();
        }
      }
      ctx.fillStyle = rgba(t.spire ? [150, 118, 54] : [52, 150, 128], (0.42 + lit * 0.4) * fade);       /* roof */
      ctx.beginPath(); ctx.moveTo(hi[0][0], hi[0][1]); for (k = 1; k < 4; k++) ctx.lineTo(hi[k][0], hi[k][1]); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = rgba(line, (0.5 + lit * 0.5) * fade); ctx.lineWidth = 1; ctx.stroke();
      if (t.verdict && grow >= 1) marks.push([pr(t.x, y1, t.z), pr(t.x, y1 + 0.20, t.z), t.verdict, lit]);
    }
    /* antenna and beacon on the spire */
    var a0 = pr(0, 1.92, 0), a1 = pr(0, 2.42, 0), pulse = 0.5 + 0.5 * Math.sin(time * 0.004);
    ctx.strokeStyle = rgba([255, 236, 190], 0.85 * fade); ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(a0[0], a0[1]); ctx.lineTo(a1[0], a1[1]); ctx.stroke();
    var bg = ctx.createRadialGradient(a1[0], a1[1], 0, a1[0], a1[1], 26 + pulse * 16);
    bg.addColorStop(0, rgba([255, 240, 200], 0.95 * fade)); bg.addColorStop(0.25, rgba(GOLD, 0.45 * fade)); bg.addColorStop(1, rgba(GOLD, 0));
    ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(a1[0], a1[1], 26 + pulse * 16, 0, 6.2832); ctx.fill();
    /* verdict markers: green = allowed, amber = check, red = breach. They flare as the beam passes. */
    var COL = { g: [94, 226, 160], a: [246, 190, 84], r: [248, 104, 96] };
    for (i = 0; i < marks.length; i++) {
      var mk = marks[i], col = COL[mk[2]], top = mk[1], al = (0.55 + mk[3] * 0.45) * fade, r = 4.2 + mk[3] * 3.2;
      ctx.strokeStyle = rgba(col, al * 0.55); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(mk[0][0], mk[0][1]); ctx.lineTo(top[0], top[1] + r); ctx.stroke();
      var mg = ctx.createRadialGradient(top[0], top[1], 0, top[0], top[1], r * 4.5);
      mg.addColorStop(0, rgba(col, 0.42 * al)); mg.addColorStop(1, rgba(col, 0));
      ctx.fillStyle = mg; ctx.beginPath(); ctx.arc(top[0], top[1], r * 4.5, 0, 6.2832); ctx.fill();
      ctx.fillStyle = rgba(col, al); ctx.beginPath(); ctx.moveTo(top[0], top[1] - r); ctx.lineTo(top[0] + r, top[1]); ctx.lineTo(top[0], top[1] + r); ctx.lineTo(top[0] - r, top[1]); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = rgba([255, 255, 255], al * 0.75); ctx.lineWidth = 1; ctx.stroke();
    }
    /* a tilted orbit ring with a travelling node: the watcher making its rounds */
    var prev = null, sp = time * 0.0005;
    for (k = 0; k <= 80; k++) {
      var oa = k / 80 * 6.2832, o = pr(Math.cos(oa) * 1.62, 1.05 + Math.sin(oa) * 0.42, Math.sin(oa) * 1.62);
      if (prev) { ctx.strokeStyle = rgba(GOLD, (o[2] < 0 ? 0.34 : 0.10) * fade); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(o[0], o[1]); ctx.stroke(); }
      prev = o;
    }
    var nd = pr(Math.cos(sp) * 1.62, 1.05 + Math.sin(sp) * 0.42, Math.sin(sp) * 1.62);
    ctx.fillStyle = rgba([255, 240, 200], 0.95 * fade); ctx.beginPath(); ctx.arc(nd[0], nd[1], 3, 0, 6.2832); ctx.fill();
    ctx.fillStyle = rgba(GOLD, 0.25 * fade); ctx.beginPath(); ctx.arc(nd[0], nd[1], 9, 0, 6.2832); ctx.fill();
  }

  function drawParticles(time, dt) {
    var cx = W / 2, cy = H / 2, proj = [], i;
    for (i = 0; i < P.length; i++) {
      var p = P[i];
      p.z -= p.v * dt;                                   /* drift toward the viewer */
      if (p.z < 0.12) { p.z = 2.05; p.x = (Math.random() * 2 - 1) * 1.6; p.y = (Math.random() * 2 - 1) * 1.1; }
      var f = 1 / p.z, par = (1 / p.z - 0.45);
      var X = cx + (p.x + tx * 0.07 * par) * cx * f * 0.62;
      var Y = cy + (p.y + ty * 0.07 * par + Math.sin(time * 0.0004 + p.ph) * 0.012) * cy * f * 0.62 - sy * 0.06 * par;
      var near = Math.min(1, Math.max(0, (2.05 - p.z) / 0.5)) * Math.min(1, (p.z - 0.12) / 0.25);
      var a = Math.min(0.85, 0.17 + f * 0.16) * near, r = p.s * Math.min(3.2, f * 0.95);
      if (X < -20 || X > W + 20 || Y < -20 || Y > H + 20) continue;
      ctx.fillStyle = rgba(p.c, a);
      ctx.beginPath(); ctx.arc(X, Y, r, 0, 6.2832); ctx.fill();
      if (r > 1.9) { ctx.fillStyle = rgba(p.c, a * 0.16); ctx.beginPath(); ctx.arc(X, Y, r * 3.2, 0, 6.2832); ctx.fill(); }
      if (p.z < 1.25) proj.push([X, Y, p.c, a]);
    }
    /* faint links between nearby close particles: reads as a network of connected rules */
    if (lite) return;
    ctx.lineWidth = 0.6;
    for (i = 0; i < proj.length; i++) for (var j = i + 1; j < proj.length; j++) {
      var dx = proj[i][0] - proj[j][0], dy = proj[i][1] - proj[j][1], d2 = dx * dx + dy * dy;
      if (d2 < 15000) {
        ctx.strokeStyle = rgba(proj[i][2], (1 - d2 / 15000) * 0.13);
        ctx.beginPath(); ctx.moveTo(proj[i][0], proj[i][1]); ctx.lineTo(proj[j][0], proj[j][1]); ctx.stroke();
      }
    }
  }

  function frame(now) {
    if (!running) return;
    var raw = now - t0, dt = Math.min(50, raw); t0 = now;
    /* adaptive quality: if frames run slow on this machine, drop the particle links, then thin the particles */
    slowAvg = slowAvg * 0.94 + Math.min(120, raw) * 0.06; frames++;
    if (frames > 90 && slowAvg > 30 && lite < 2) { lite++; frames = 0; slowAvg = 16; if (lite === 2) P.length = Math.ceil(P.length / 2); }
    tx += (mx - tx) * 0.045; ty += (my - ty) * 0.045;
    sy = window.scrollY || 0;
    ctx.clearRect(0, 0, W, H);
    var heroFade = Math.max(0, 1 - sy / (H * 0.85));
    drawGrid(now, heroFade * 0.9 + 0.1);
    drawSolid(now, heroFade);
    drawParticles(now, dt);
    requestAnimationFrame(frame);
  }

  function start() {
    if (document.getElementById('rw3d')) return;
    document.body.appendChild(cv);
    resize(); seed();
    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('mousemove', function (e) {
      mx = (e.clientX / W) * 2 - 1; my = (e.clientY / H) * 2 - 1;
      document.documentElement.style.setProperty('--rw-mx', e.clientX + 'px');
      document.documentElement.style.setProperty('--rw-my', e.clientY + 'px');
    }, { passive: true });
    document.addEventListener('visibilitychange', function () {
      running = !document.hidden;
      if (running) { t0 = performance.now(); requestAnimationFrame(frame); }
    });
    if (reduce) { ctx.clearRect(0, 0, W, H); drawGrid(0, 1); drawSolid(5000, 1); drawParticles(0, 0); return; }
    requestAnimationFrame(frame);
  }

  /* ---------------- 3D tilt on cards ---------------- */
  var TILT = '.panel, [role="radio"], main a[href^="#/rules/"], .rw-tilt';
  var active = null;
  function tiltMove(e) {
    var el = e.target.closest ? e.target.closest(TILT) : null;
    if (active && active !== el) { active.style.transform = ''; active.classList.remove('rw-tilting'); active = null; }
    if (!el) return;
    var r = el.getBoundingClientRect();
    if (r.width < 60 || r.height < 40) return;
    var px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
    var big = r.width > 620 || r.height > 520, max = big ? 2.2 : 9;
    el.classList.add('rw-tilting');
    el.style.setProperty('--rw-gx', (px * 100).toFixed(1) + '%');
    el.style.setProperty('--rw-gy', (py * 100).toFixed(1) + '%');
    el.style.transform = 'perspective(900px) rotateX(' + ((0.5 - py) * max).toFixed(2) + 'deg) rotateY(' +
      ((px - 0.5) * max).toFixed(2) + 'deg) translateZ(' + (big ? 0 : 8) + 'px)';
    active = el;
  }
  function tiltOut() { if (active) { active.style.transform = ''; active.classList.remove('rw-tilting'); active = null; } }

  /* ---------------- scroll-in reveals ---------------- */
  var io = null;
  function watch(root) {
    if (!io) return;
    var list = (root.querySelectorAll ? root.querySelectorAll('main .panel, main [role="radio"], main section > div > h2, main h2, footer') : []);
    for (var i = 0; i < list.length; i++) {
      var el = list[i];
      if (el.dataset.rwSeen) continue;
      el.dataset.rwSeen = '1';
      var r = el.getBoundingClientRect();
      if (r.top > window.innerHeight * 0.92) { el.classList.add('rw-reveal'); io.observe(el); }
    }
  }

  function boot() {
    start();
    document.documentElement.classList.add('rw3d-on');
    if (!touch && !reduce) {
      document.addEventListener('mousemove', tiltMove, { passive: true });
      document.addEventListener('mouseleave', tiltOut, { passive: true });
    }
    if ('IntersectionObserver' in window && !reduce) {
      io = new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('rw-in'); io.unobserve(x.target); } });
      }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
      watch(document);
      var pend = false;
      new MutationObserver(function () {
        if (pend) return; pend = true;
        setTimeout(function () { pend = false; watch(document); }, 120);
      }).observe(document.getElementById('root') || document.body, { childList: true, subtree: true });
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
