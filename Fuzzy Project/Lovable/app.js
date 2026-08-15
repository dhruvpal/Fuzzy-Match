/* ==========================================================================
   Universal Match AI — UI interactions ONLY (no business logic)
   Reads window.UMA_DATA (see data.js). Streamlit can overwrite that object
   before this script runs, or call UMA.render() again after updating it.
   ========================================================================== */
(function () {
  "use strict";

  var D = window.UMA_DATA;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var icon = function (id, cls) { return '<svg viewBox="0 0 24 24"' + (cls ? ' class="' + cls + '"' : "") + '><use href="#' + id + '"/></svg>'; };
  var esc = function (v) { return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); };

  /* ---------- Token interpolation: {{key}} -> mock/Streamlit value ---------- */
  function fillTokens(root) {
    var t = D.tokens || {};
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [], n;
    while ((n = walker.nextNode())) if (n.nodeValue.indexOf("{{") > -1) nodes.push(n);
    nodes.forEach(function (node) {
      node.nodeValue = node.nodeValue.replace(/\{\{(\w+)\}\}/g, function (m, k) {
        return t[k] != null ? t[k] : m;
      });
    });
  }

  /* ---------- Page navigation ---------- */
  var TITLES = {
    dashboard: ["Dashboard", "Find the right record from messy data."],
    "new-match": ["New Match", "Upload, configure, run and review in four steps."],
    history: ["Match History", "All matching jobs in this workspace."],
    review: ["Review Center", "Resolve uncertain matches with full context."],
    settings: ["Settings", "Defaults for engine, thresholds and exports."],
  };
  function go(page) {
    $$("[data-page]").forEach(function (p) { p.classList.toggle("uma-hidden", p.dataset.page !== page); });
    $$(".uma-nav-item").forEach(function (b) { b.classList.toggle("is-active", b.dataset.nav === page); });
    var t = TITLES[page] || TITLES.dashboard;
    $("#pageTitle").textContent = t[0];
    $("#pageSub").textContent = t[1];
    $("#sidebar").classList.remove("is-open");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  document.addEventListener("click", function (e) {
    var nav = e.target.closest("[data-nav]");
    if (nav) go(nav.dataset.nav);
  });
  $("#menuBtn").addEventListener("click", function () { $("#sidebar").classList.toggle("is-open"); });

  /* ---------- Segmented controls ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".uma-seg button");
    if (!b) return;
    $$("button", b.parentElement).forEach(function (x) { x.classList.remove("is-active"); });
    b.classList.add("is-active");
  });

  /* ---------- Stepper ---------- */
  var step = 1;
  function setStep(s) {
    step = s;
    $$(".uma-step").forEach(function (el) {
      var i = +el.dataset.step;
      el.classList.toggle("is-active", i === s);
      el.classList.toggle("is-done", i < s);
    });
    $$(".uma-step-panel").forEach(function (p) { p.classList.toggle("uma-hidden", +p.dataset.panel !== s); });
    if (s === 3) runProcessing();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  document.addEventListener("click", function (e) {
    var s = e.target.closest("[data-step]");
    if (s) return setStep(+s.dataset.step);
    var g = e.target.closest("[data-goto]");
    if (g) setStep(+g.dataset.goto);
  });

  /* ---------- Donut chart ---------- */
  function donut(el, pct, label, size) {
    size = size || 168;
    var r = size / 2 - 12, c = 2 * Math.PI * r;
    el.innerHTML =
      '<svg width="' + size + '" height="' + size + '">' +
      '<circle class="track" cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" stroke-width="12"/>' +
      '<circle cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" stroke="url(#umaGrad)" stroke-width="12" ' +
      'stroke-dasharray="' + c + '" stroke-dashoffset="' + c + '"/>' +
      '<defs><linearGradient id="umaGrad" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0%" stop-color="#4f7cff"/><stop offset="100%" stop-color="#7c5cff"/></linearGradient></defs></svg>' +
      '<div class="uma-donut-center"><div class="big">' + esc(pct) + '%</div><div class="small">' + esc(label) + '</div></div>';
    var ring = el.querySelectorAll("circle")[1];
    requestAnimationFrame(function () {
      ring.style.transition = "stroke-dashoffset 900ms cubic-bezier(.22,.61,.36,1)";
      ring.style.strokeDashoffset = c * (1 - Math.min(100, pct) / 100);
    });
  }

  /* ---------- Bar chart ---------- */
  function bars(el, rows) {
    var max = Math.max.apply(null, rows.map(function (r) { return r.value; })) || 1;
    el.innerHTML = rows.map(function (r, i) {
      var h = Math.max(6, Math.round((r.value / max) * 130));
      return '<div class="col" title="' + esc(r.label) + ": " + esc(r.value) + '">' +
        '<span class="val">' + r.value.toLocaleString() + "</span>" +
        '<div class="stack" data-tone="' + esc(r.tone) + '" style="height:' + h + "px;animation-delay:" + i * 60 + 'ms"></div>' +
        '<span class="lab">' + esc(r.label) + "</span></div>";
    }).join("");
  }

  /* ---------- Jobs table ---------- */
  var STATUS = { high: ["uma-badge--high", "High confidence"], review: ["uma-badge--review", "Review"], none: ["uma-badge--none", "No match"] };
  function badge(s) {
    var m = STATUS[s] || STATUS.review;
    return '<span class="uma-badge ' + m[0] + '"><span class="dot"></span>' + m[1] + "</span>";
  }
  function conf(pct) {
    var tone = pct >= 90 ? "is-success" : pct >= 75 ? "is-warning" : "is-danger";
    return '<div class="uma-conf"><div class="uma-bar uma-bar--thin ' + tone + '"><span style="width:' + pct + '%"></span></div>' +
      '<span class="num">' + pct + "%</span></div>";
  }
  function renderJobs(tbody) {
    tbody.innerHTML = D.jobs.map(function (j) {
      return "<tr><td class='strong'>" + esc(j.name) + "</td><td class='uma-mono'>" + esc(j.ref) + "</td><td class='uma-mono'>" + esc(j.rows) +
        "</td><td>" + conf(j.rate) + "</td><td>" + badge(j.status) + "</td><td>" + esc(j.created) + "</td></tr>";
    }).join("");
  }

  /* ---------- File cards ---------- */
  function renderFiles(kind) {
    var wrap = $('[data-files="' + kind + '"]');
    var list = D.files[kind] || [];
    if (!list.length) { wrap.innerHTML = '<p class="uma-empty">No files yet.</p>'; return; }
    wrap.innerHTML = list.map(function (f, i) {
      return '<div class="uma-file" data-file="' + i + '" style="animation-delay:' + i * 70 + 'ms">' +
        '<div class="uma-file-ico' + (kind === "master" ? " is-blue" : "") + '">' + icon("i-file") + "</div>" +
        '<div class="uma-file-meta"><div class="uma-file-name">' + esc(f.name) + "</div>" +
        '<div class="uma-file-stats"><span>' + esc(f.size) + "</span><span>" + icon("i-rows") + esc(f.rows) + " rows</span><span>" +
        icon("i-cols") + esc(f.cols) + " columns</span></div></div>" +
        '<button class="uma-x" aria-label="Remove file"><svg viewBox="0 0 20 20"><use href="#i-x"/></svg></button></div>';
    }).join("");
    $$(".uma-x", wrap).forEach(function (btn, i) {
      btn.addEventListener("click", function () { D.files[kind].splice(i, 1); renderFiles(kind); });
    });
    $$(".uma-file-ico svg, .uma-file-stats svg", wrap).forEach(function (s) { s.style.width = "12px"; s.style.height = "12px"; });
    $$(".uma-file-ico svg", wrap).forEach(function (s) { s.style.width = "17px"; s.style.height = "17px"; });
  }
  // Dropzone visuals only — real upload stays in Streamlit's file_uploader
  $$("[data-dz]").forEach(function (dz) {
    ["dragenter", "dragover"].forEach(function (ev) {
      dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.add("is-over"); });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.remove("is-over"); });
    });
    dz.addEventListener("drop", function () { demoAdd(dz.dataset.dz); });
    dz.addEventListener("click", function () { demoAdd(dz.dataset.dz); });
  });
  function demoAdd(kind) {
    var n = (D.files[kind] || []).length + 1;
    D.files[kind].push({ name: kind + "_sample_" + n + ".csv", size: "1.8 MB", rows: "3,204", cols: "7" });
    renderFiles(kind);
  }

  /* ---------- Mapping rules + weights ---------- */
  function opts(list, sel) {
    return list.map(function (o) { return '<option' + (o === sel ? " selected" : "") + ">" + esc(o) + "</option>"; }).join("");
  }
  function renderRules() {
    var wrap = $("#rulesWrap");
    wrap.innerHTML = D.rules.map(function (r, i) {
      return '<div class="uma-rule" data-rule="' + i + '">' +
        '<div class="uma-field"><span class="uma-label">Reference column</span><select class="uma-select">' + opts(D.referenceColumns, r.ref) + "</select></div>" +
        '<div class="uma-rule-arrow">' + icon("i-arrow-down") + "</div>" +
        '<div class="uma-field"><span class="uma-label">Master column</span><select class="uma-select">' + opts(D.masterColumns, r.master) + "</select></div>" +
        '<div class="uma-field"><div class="uma-weight-val"><span class="uma-label">Weight</span><b class="uma-mono">' + r.weight + '%</b></div>' +
        '<input type="range" class="uma-range" min="0" max="100" value="' + r.weight + '" /></div>' +
        '<button class="uma-x" aria-label="Remove rule"><svg viewBox="0 0 20 20"><use href="#i-x"/></svg></button></div>';
    }).join("");
    $$(".uma-rule").forEach(function (row, i) {
      var range = $('input[type="range"]', row), val = $(".uma-weight-val b", row);
      range.addEventListener("input", function () {
        D.rules[i].weight = +range.value; val.textContent = range.value + "%"; renderWeights();
      });
      $(".uma-x", row).addEventListener("click", function () { D.rules.splice(i, 1); renderRules(); });
      var sels = $$("select", row);
      sels[0].addEventListener("change", function () { D.rules[i].ref = sels[0].value; renderWeights(); });
      sels[1].addEventListener("change", function () { D.rules[i].master = sels[1].value; });
    });
    renderWeights();
  }
  function renderWeights() {
    var total = D.rules.reduce(function (a, r) { return a + r.weight; }, 0) || 1;
    $("#weightBar").innerHTML = D.rules.map(function (r) {
      return '<span style="width:' + (r.weight / total) * 100 + '%"></span>';
    }).join("");
    var colors = ["#4f7cff", "#7c5cff", "#35d0e8", "#2fd18a"];
    $("#weightLegend").innerHTML = D.rules.map(function (r, i) {
      return '<span class="uma-legend-item"><i style="background:' + colors[i % 4] + '"></i>' + esc(r.ref) +
        ' <b class="uma-mono" style="color:var(--uma-text)">' + r.weight + "%</b></span>";
    }).join("");
    var sum = D.rules.reduce(function (a, r) { return a + r.weight; }, 0);
    var b = $("#weightTotalBadge");
    b.className = "uma-badge " + (sum === 100 ? "uma-badge--high" : "uma-badge--review");
    b.innerHTML = '<span class="dot"></span>Total ' + sum + "%";
  }
  $("#addRule").addEventListener("click", function () {
    D.rules.push({ ref: D.referenceColumns[D.rules.length % D.referenceColumns.length], master: D.masterColumns[D.rules.length % D.masterColumns.length], weight: 20 });
    renderRules();
  });

  /* ---------- Return column chips ---------- */
  function renderChips() {
    $("#returnChips").innerHTML = D.returnColumns.map(function (c, i) {
      return '<button class="uma-chip' + (c.on ? " is-on" : "") + '" data-chip="' + i + '">' +
        '<span class="box"><svg viewBox="0 0 16 16"><use href="#i-check"/></svg></span>' + esc(c.name) + "</button>";
    }).join("");
  }
  document.addEventListener("click", function (e) {
    var chip = e.target.closest(".uma-chip");
    if (!chip) return;
    chip.classList.toggle("is-on");
    if (chip.dataset.chip != null) D.returnColumns[+chip.dataset.chip].on = chip.classList.contains("is-on");
  });
  $("#selectAllCols").addEventListener("click", function () {
    var allOn = D.returnColumns.every(function (c) { return c.on; });
    D.returnColumns.forEach(function (c) { c.on = !allOn; });
    renderChips();
  });

  /* ---------- Threshold sliders ---------- */
  [["thHigh", "thHighVal"], ["thReview", "thReviewVal"], ["setHigh", "setHighVal"]].forEach(function (p) {
    var input = $("#" + p[0]), out = $("#" + p[1]);
    if (input) input.addEventListener("input", function () { out.textContent = input.value + "%"; });
  });

  /* ---------- Step 3: processing animation (placeholder values) ---------- */
  var procTimer = null;
  function runProcessing() {
    var tasksEl = $("#procTasks");
    tasksEl.innerHTML = D.tasks.map(function (t, i) {
      return '<div class="uma-task" data-task="' + i + '"><span class="tick"><svg viewBox="0 0 16 16"><use href="#i-check"/></svg></span>' +
        '<span class="nm">' + esc(t.name) + '</span><span class="uma-muted" style="margin-left:auto;font-size:12px">' + esc(t.note) + "</span></div>";
    }).join("");
    donut($("#procDonut"), 0, "Progress", 200);
    clearInterval(procTimer);
    var pct = 0;
    procTimer = setInterval(function () {
      pct = Math.min(100, pct + 2);
      $("#procBar").firstElementChild.style.width = pct + "%";
      $("#procProgress").textContent = pct + "%";
      $("#procProcessed").textContent = Math.round((pct / 100) * 12540).toLocaleString() + " / 12,540";
      $("#procRate").textContent = (D.matchRate * (pct / 100)).toFixed(1) + "%";
      var donutEl = $("#procDonut .uma-donut-center .big");
      if (donutEl) donutEl.textContent = pct + "%";
      var ring = $("#procDonut svg").querySelectorAll("circle")[1];
      var r = ring.getAttribute("r"), c = 2 * Math.PI * r;
      ring.style.strokeDashoffset = c * (1 - pct / 100);
      var active = Math.min(D.tasks.length - 1, Math.floor(pct / 25));
      $$(".uma-task").forEach(function (el, i) {
        el.classList.toggle("is-done", i < active || pct === 100);
        el.classList.toggle("is-active", i === active && pct < 100);
        var tick = $(".tick", el);
        if (i === active && pct < 100 && !$(".uma-spin", tick)) tick.innerHTML = '<span class="uma-spin"></span>';
        if (i < active || pct === 100) tick.innerHTML = '<svg viewBox="0 0 16 16" style="width:13px;height:13px"><use href="#i-check"/></svg>';
      });
      if (pct >= 100) clearInterval(procTimer);
    }, 90);
  }

  /* ---------- Step 4: results table ---------- */
  function renderResults() {
    $("#resultsBody").innerHTML = D.results.map(function (r, i) {
      return '<tr data-result="' + i + '"><td class="strong">' + esc(r.sample) + "</td><td>" + esc(r.best) +
        '</td><td class="uma-mono">' + esc(r.id) + "</td><td>" + conf(r.confidence) + "</td><td>" + badge(r.status) + "</td></tr>";
    }).join("");
    $$("#resultsBody tr").forEach(function (tr) {
      tr.addEventListener("click", function () { openDrawer(D.results[+tr.dataset.result]); });
    });
  }

  /* ---------- Match detail drawer ---------- */
  function openDrawer(r) {
    $("#dTitle").textContent = r.sample;
    $("#dBadge").innerHTML = badge(r.status);
    $("#dId").textContent = "Returned ID · " + r.id;
    var keys = Object.keys(r.original), mkeys = Object.keys(r.matched);
    $("#dKv").innerHTML = keys.map(function (k, i) {
      return '<div class="uma-kv-box"><div class="k">Original · ' + esc(k) + '</div><div class="v">' + esc(r.original[k]) + "</div></div>" +
        '<div class="uma-kv-box"><div class="k">Matched · ' + esc(mkeys[i]) + '</div><div class="v">' + esc(r.matched[mkeys[i]]) + "</div></div>";
    }).join("");
    $("#dScores").innerHTML = r.scores.map(function (s) {
      var tone = s.score >= 90 ? "is-success" : s.score >= 75 ? "is-warning" : "is-danger";
      return '<div class="uma-score-row"><span class="uma-muted">' + esc(s.col) + '</span>' +
        '<div class="uma-bar uma-bar--thin ' + tone + '"><span style="width:' + s.score + '%"></span></div>' +
        '<b class="uma-mono" style="text-align:right">' + s.score + "%</b></div>";
    }).join("");
    $("#dFinal").textContent = r.confidence + "%";
    $("#dFinalBar").firstElementChild.style.width = r.confidence + "%";
    $("#dCands").innerHTML = r.candidates.map(function (c, i) {
      return '<div class="uma-cand"><div><div style="font-weight:620">Candidate ' + (i + 1) + "</div>" +
        '<div class="uma-muted" style="font-size:12.5px;margin-top:3px">' + esc(c.label) + "</div></div>" +
        '<b class="uma-mono">' + c.score + "%</b></div>";
    }).join("");
    $("#drawer").classList.add("is-open");
    $("#drawer").setAttribute("aria-hidden", "false");
    $("#scrim").classList.add("is-open");
  }
  function closeDrawer() {
    $("#drawer").classList.remove("is-open");
    $("#drawer").setAttribute("aria-hidden", "true");
    $("#scrim").classList.remove("is-open");
  }
  $("#scrim").addEventListener("click", closeDrawer);
  $("#drawerClose").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  /* ---------- Review center ---------- */
  function renderReview() {
    var items = D.results.filter(function (r) { return r.status !== "high"; });
    $("#reviewWrap").innerHTML = items.map(function (r) {
      return '<section class="uma-card">' +
        '<div class="uma-card-head"><div><h2>' + esc(r.sample) + "</h2><p>Uncertain match · needs a human decision</p></div>" +
        badge(r.status) + "</div>" +
        '<div class="uma-review">' +
          '<div class="uma-compare"><div class="uma-caps">Original record</div>' +
            Object.keys(r.original).map(function (k) {
              return '<div class="uma-between" style="margin-top:10px"><span class="uma-muted">' + esc(k) + '</span><b>' + esc(r.original[k]) + "</b></div>";
            }).join("") + "</div>" +
          '<div class="uma-compare is-match"><div class="uma-caps">Best match · ' + r.confidence + "%</div>" +
            Object.keys(r.matched).map(function (k) {
              return '<div class="uma-between" style="margin-top:10px"><span class="uma-muted">' + esc(k) + '</span><b>' + esc(r.matched[k]) + "</b></div>";
            }).join("") +
            '<div class="uma-bar uma-bar--thin is-warning" style="margin-top:14px"><span style="width:' + r.confidence + '%"></span></div></div>' +
        "</div>" +
        '<hr class="uma-divider" />' +
        '<div class="uma-caps" style="margin-bottom:10px">Alternative matches</div>' +
        '<div style="display:flex;flex-direction:column;gap:10px">' +
          r.candidates.map(function (c, i) {
            return '<div class="uma-cand"><div><div style="font-weight:620">' + esc(c.label) + "</div>" +
              '<div class="uma-muted" style="font-size:12.5px;margin-top:3px">Candidate ' + (i + 1) + "</div></div>" +
              '<div class="uma-row"><div class="uma-bar uma-bar--thin" style="width:110px"><span style="width:' + c.score + '%"></span></div>' +
              '<b class="uma-mono">' + c.score + "%</b></div></div>";
          }).join("") +
        "</div>" +
        '<div class="uma-row" style="margin-top:20px;flex-wrap:wrap">' +
          '<button class="uma-btn uma-btn--success">' + icon("i-check") + "Accept Match</button>" +
          '<button class="uma-btn uma-btn--ghost">' + icon("i-swap") + "Choose Alternative</button>" +
          '<button class="uma-btn uma-btn--danger">' + icon("i-ban") + "Reject Match</button>" +
        "</div></section>";
    }).join("");
  }

  /* ---------- Boot ---------- */
  function render() {
    D = window.UMA_DATA;
    fillTokens(document.body);
    bars($("#qualityChart"), D.qualityChart);
    bars($("#confChart"), D.confChart);
    donut($("#dashDonut"), D.matchRate, "Match rate");
    donut($("#resDonut"), D.matchRate, "Match rate");
    renderJobs($("#jobsBody"));
    renderJobs($("#historyBody"));
    renderFiles("reference");
    renderFiles("master");
    renderRules();
    renderChips();
    renderResults();
    renderReview();
  }
  window.UMA = { render: render, goToPage: go, setStep: setStep };
  render();
})();
