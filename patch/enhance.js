/* RuleWatch 3D layer: a depth particle field, a perspective grid, a rotating wireframe seal,
   3D tilt on cards and scroll-in reveals. Pure canvas + CSS transforms, no libraries.
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
  var W = 0, H = 0, DPR = 1, mx = 0, my = 0, tx = 0, ty = 0, sy = 0, t0 = performance.now(), running = true;

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

  /* wireframe solid: an icosahedron, drawn as glowing edges with a tilted orbit ring */
  var PHI = (1 + Math.sqrt(5)) / 2;
  var V = [[-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0], [0, -1, PHI], [0, 1, PHI], [0, -1, -PHI], [0, 1, -PHI],
    [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1]];
  var E = [];
  (function () {
    for (var i = 0; i < V.length; i++) for (var j = i + 1; j < V.length; j++) {
      var dx = V[i][0] - V[j][0], dy = V[i][1] - V[j][1], dz = V[i][2] - V[j][2];
      if (Math.abs(Math.sqrt(dx * dx + dy * dy + dz * dz) - 2) < 0.01) E.push([i, j]);
    }
  })();

  function rot(p, ax, ay, az) {
    var x = p[0], y = p[1], z = p[2], c, s, a, b;
    c = Math.cos(ay); s = Math.sin(ay); a = x * c + z * s; b = -x * s + z * c; x = a; z = b;
    c = Math.cos(ax); s = Math.sin(ax); a = y * c - z * s; b = y * s + z * c; y = a; z = b;
    c = Math.cos(az); s = Math.sin(az); a = x * c - y * s; b = x * s + y * c; x = a; y = b;
    return [x, y, z];
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

  function drawSolid(time, fade) {
    if (fade <= 0.01 || W < 900) return;
    var cx = W * 0.80 + tx * 26, cy = H * 0.40 + ty * 18 - sy * 0.35, R = Math.min(W, H) * 0.115;
    var ax = time * 0.00021 + ty * 0.5, ay = time * 0.00033 + tx * 0.7, az = time * 0.00009, pts = [], i;
    for (i = 0; i < V.length; i++) {
      var p = rot(V[i], ax, ay, az), f = 4.2 / (4.2 + p[2]);
      pts.push([cx + p[0] * R * f * 0.62, cy + p[1] * R * f * 0.62, p[2]]);
    }
    var halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 2.4);
    halo.addColorStop(0, rgba(GOLD, 0.10 * fade)); halo.addColorStop(1, rgba(GOLD, 0));
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(cx, cy, R * 2.4, 0, 6.2832); ctx.fill();
    for (i = 0; i < E.length; i++) {
      var a = pts[E[i][0]], b = pts[E[i][1]], zf = 1 - ((a[2] + b[2]) / 2 + PHI) / (2 * PHI);
      ctx.strokeStyle = rgba(GOLD, (0.14 + zf * 0.5) * fade);
      ctx.lineWidth = 0.7 + zf * 1.1;
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    }
    for (i = 0; i < pts.length; i++) {
      var z = 1 - (pts[i][2] + PHI) / (2 * PHI);
      ctx.fillStyle = rgba(z > 0.5 ? [255, 236, 190] : GOLD, (0.25 + z * 0.7) * fade);
      ctx.beginPath(); ctx.arc(pts[i][0], pts[i][1], 1.2 + z * 1.8, 0, 6.2832); ctx.fill();
    }
    /* two tilted orbit rings with a travelling node each */
    for (var r = 0; r < 2; r++) {
      var rr = R * (1.55 + r * 0.42), tilt = 0.42 + r * 0.5 + ty * 0.3, sp = time * (0.0006 - r * 0.00025) + r * 2, prev = null;
      ctx.lineWidth = 1;
      for (var s = 0; s <= 72; s++) {
        var an = s / 72 * 6.2832, q = rot([Math.cos(an) * rr, 0, Math.sin(an) * rr], tilt, ay * 0.3, 0.25 - r * 0.6);
        var fq = 4.2 * R / (4.2 * R + q[2]), X = cx + q[0] * fq, Y = cy + q[1] * fq;
        if (prev) {
          ctx.strokeStyle = rgba(r ? MINT : GOLD, (q[2] < 0 ? 0.30 : 0.09) * fade);
          ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(X, Y); ctx.stroke();
        }
        prev = [X, Y];
      }
      var n = rot([Math.cos(sp) * rr, 0, Math.sin(sp) * rr], tilt, ay * 0.3, 0.25 - r * 0.6), fn = 4.2 * R / (4.2 * R + n[2]);
      ctx.fillStyle = rgba(r ? MINT : [255, 236, 190], 0.9 * fade);
      ctx.beginPath(); ctx.arc(cx + n[0] * fn, cy + n[1] * fn, 2.6, 0, 6.2832); ctx.fill();
    }
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
    var dt = Math.min(50, now - t0); t0 = now;
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
    if (reduce) { ctx.clearRect(0, 0, W, H); drawGrid(0, 1); drawSolid(0, 1); drawParticles(0, 0); return; }
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
