/* ============================================================
   MAIN.JS — Shared JavaScript for APN SIM Management
   Backspace Technologies
   ============================================================ */


/* ════════════════════════════════════════════════════════════
   SECTION 1 — GLOBAL UTILITIES (run on every page)
   ════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Auto-dismiss Bootstrap alerts after 5s ── */
  document.querySelectorAll('.alert').forEach(function (el) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });

  /* ── Animate usage bars on load ── */
  document.querySelectorAll('.usage-bar-fill').forEach(function (bar) {
    var target = bar.dataset.width || '0';
    bar.style.width = '0%';
    setTimeout(function () {
      bar.style.width = target + '%';
    }, 200);
  });

  /* ── Route to page-specific init functions ── */
  var body = document.body;

  if (document.getElementById('particleCanvas')) {
    initLoginPage();
  }

  if (document.getElementById('simTable')) {
    initDashboard();
  }

  if (document.getElementById('usageCircle')) {
    initSimDetail();
  }

  if (document.getElementById('strengthFill')) {
    initPasswordChange();
  }

});


/* ════════════════════════════════════════════════════════════
   SECTION 2 — LOGIN PAGE
   Particle network + password toggle
   ════════════════════════════════════════════════════════════ */

/* ── Password show/hide toggle ── */
function togglePwd() {
  var input = document.getElementById('id_password');
  var icon  = document.getElementById('pwd-eye');
  if (!input) return;
  input.type     = input.type === 'password' ? 'text' : 'password';
  icon.className = input.type === 'password' ? 'bi bi-eye-fill' : 'bi bi-eye-slash-fill';
}

/* ── Particle network initialiser ── */
function initLoginPage() {
  var canvas = document.getElementById('particleCanvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var W, H, particles;
  var mouse = { x: -9999, y: -9999 };

  var CONFIG = {
    count:       90,
    maxDist:     160,
    mouseRadius: 180,
    nodeRadius:  2.5,
    speed:       0.35,
    lineOpacity: 0.55,
    color:       '0, 200, 255',
    bgColor:     '#000000'
  };

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function Particle() {
    this.x  = Math.random() * W;
    this.y  = Math.random() * H;
    this.vx = (Math.random() - 0.5) * CONFIG.speed;
    this.vy = (Math.random() - 0.5) * CONFIG.speed;
    this.r  = Math.random() * CONFIG.nodeRadius + 1;
  }

  Particle.prototype.update = function () {
    var dx   = this.x - mouse.x;
    var dy   = this.y - mouse.y;
    var dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < CONFIG.mouseRadius && dist > 0) {
      var force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius;
      this.vx += (dx / dist) * force * 0.8;
      this.vy += (dy / dist) * force * 0.8;
    }

    var speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
    if (speed > 2) {
      this.vx = (this.vx / speed) * 2;
      this.vy = (this.vy / speed) * 2;
    }

    this.vx *= 0.99;
    this.vy *= 0.99;

    if (speed < CONFIG.speed * 0.5) {
      this.vx += (Math.random() - 0.5) * 0.05;
      this.vy += (Math.random() - 0.5) * 0.05;
    }

    this.x += this.vx;
    this.y += this.vy;

    if (this.x < 0) this.x = W;
    if (this.x > W) this.x = 0;
    if (this.y < 0) this.y = H;
    if (this.y > H) this.y = 0;
  };

  function init() {
    resize();
    particles = Array.from({ length: CONFIG.count }, function () {
      return new Particle();
    });
  }

  function draw() {
    ctx.fillStyle = CONFIG.bgColor;
    ctx.fillRect(0, 0, W, H);

    /* Lines between close particles */
    for (var i = 0; i < particles.length; i++) {
      for (var j = i + 1; j < particles.length; j++) {
        var a  = particles[i];
        var b  = particles[j];
        var dx = a.x - b.x;
        var dy = a.y - b.y;
        var d  = Math.sqrt(dx * dx + dy * dy);

        if (d < CONFIG.maxDist) {
          var alpha = (1 - d / CONFIG.maxDist) * CONFIG.lineOpacity;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = 'rgba(' + CONFIG.color + ', ' + alpha + ')';
          ctx.lineWidth   = 0.8;
          ctx.stroke();
        }
      }
    }

    /* Lines from particles to mouse */
    for (var k = 0; k < particles.length; k++) {
      var p  = particles[k];
      var mx = p.x - mouse.x;
      var my = p.y - mouse.y;
      var md = Math.sqrt(mx * mx + my * my);

      if (md < CONFIG.mouseRadius) {
        var ma = (1 - md / CONFIG.mouseRadius) * 0.8;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.strokeStyle = 'rgba(' + CONFIG.color + ', ' + ma + ')';
        ctx.lineWidth   = 0.8;
        ctx.stroke();
      }
    }

    /* Draw nodes */
    for (var n = 0; n < particles.length; n++) {
      var node = particles[n];

      var grd = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.r * 3);
      grd.addColorStop(0, 'rgba(' + CONFIG.color + ', 0.5)');
      grd.addColorStop(1, 'rgba(' + CONFIG.color + ', 0)');

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r * 3, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(' + CONFIG.color + ', 0.9)';
      ctx.fill();

      node.update();
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('mousemove', function (e) {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseleave', function () {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  window.addEventListener('resize', function () {
    resize();
    particles.forEach(function (p) {
      if (p.x > W) p.x = Math.random() * W;
      if (p.y > H) p.y = Math.random() * H;
    });
  });

  init();
  draw();
}


/* ════════════════════════════════════════════════════════════
   SECTION 3 — DASHBOARD PAGE
   SIM table search + filter + live clock + auto-refresh
   ════════════════════════════════════════════════════════════ */

function initDashboard() {
  var currentFilter = 'all';

  /* Live clock */
  function updateClock() {
    var el = document.getElementById('last-update');
    if (el) el.textContent = new Date().toLocaleTimeString();
  }
  setInterval(updateClock, 1000);

  /* Auto-refresh page every 60s */
  setTimeout(function () { location.reload(); }, 60000);

  /* Expose filter functions to global scope for onclick handlers */
  window.filterTable = function () {
    var query = document.getElementById('simSearch').value.toLowerCase();
    var rows  = document.querySelectorAll('#simTable tbody tr[data-status]');
    rows.forEach(function (row) {
      var text        = row.textContent.toLowerCase();
      var status      = row.dataset.status;
      var matchSearch = text.includes(query);
      var matchFilter = currentFilter === 'all' || status === currentFilter;
      row.style.display = matchSearch && matchFilter ? '' : 'none';
    });
  };

  window.setFilter = function (status, btn) {
    currentFilter = status;
    document.querySelectorAll('.filter-btn').forEach(function (b) {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    window.filterTable();
  };
}


/* ════════════════════════════════════════════════════════════
   SECTION 4 — SIM DETAIL PAGE
   Animated SVG usage ring
   ════════════════════════════════════════════════════════════ */

function initSimDetail() {
  var circle = document.getElementById('usageCircle');
  if (!circle) return;

  var pct          = parseFloat(circle.dataset.targetPct) || 0;
  var circumference = 427;
  var offset        = circumference - (pct / 100) * circumference;

  /* Start at empty, then animate to target */
  circle.style.strokeDashoffset = circumference;

  setTimeout(function () {
    circle.style.transition       = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
    circle.style.strokeDashoffset = offset;
  }, 300);
}


/* ════════════════════════════════════════════════════════════
   SECTION 5 — PASSWORD CHANGE PAGE
   Strength meter + match checker
   ════════════════════════════════════════════════════════════ */

function initPasswordChange() {

  var p1Input = document.getElementById('id_new_password1');
  var p2Input = document.getElementById('id_new_password2');

  if (p1Input) {
    p1Input.addEventListener('input', function () {
      checkStrength(this.value);
    });
  }

  if (p2Input) {
    p2Input.addEventListener('input', checkMatch);
  }
}

function checkStrength(val) {
  var fill  = document.getElementById('strengthFill');
  var label = document.getElementById('strengthLabel');
  if (!fill || !label) return;

  var score = 0;
  if (val.length >= 8)           score++;
  if (/[A-Z]/.test(val))         score++;
  if (/[0-9]/.test(val))         score++;
  if (/[^A-Za-z0-9]/.test(val))  score++;

  var levels = [
    { pct: '0%',   color: 'var(--text-muted)',  text: 'Enter a password' },
    { pct: '25%',  color: 'var(--red-danger)',   text: 'Weak' },
    { pct: '50%',  color: 'var(--orange-warn)',  text: 'Fair' },
    { pct: '75%',  color: 'var(--blue-bright)',  text: 'Good' },
    { pct: '100%', color: 'var(--green-ok)',      text: 'Strong ✓' }
  ];

  var level = levels[val.length === 0 ? 0 : score];
  fill.style.width      = level.pct;
  fill.style.background = level.color;
  label.style.color     = level.color;
  label.textContent     = level.text;
}

function checkMatch() {
  var p1    = document.getElementById('id_new_password1');
  var p2    = document.getElementById('id_new_password2');
  var label = document.getElementById('matchLabel');
  if (!p1 || !p2 || !label) return;

  if (!p2.value) { label.textContent = ''; return; }

  if (p1.value === p2.value) {
    label.style.color = 'var(--green-ok)';
    label.textContent = '✓ Passwords match';
  } else {
    label.style.color = 'var(--red-danger)';
    label.textContent = '✗ Passwords do not match';
  }
}