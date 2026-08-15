"""
UI Templates for Universal Fuzzy Data Matcher
============================================
Provides HTML/CSS and SVG template generators inspired by the Lovable design system
for rendering custom KPI cards, Donut charts, Bar charts, Steppers, and Tables in Streamlit.
"""

import html
from typing import List, Dict, Any, Optional


def clean_html(raw_html: str) -> str:
    """Removes extra leading indents so HTML renders cleanly without markdown code blocks."""
    lines = [line.strip() for line in raw_html.strip().splitlines() if line.strip()]
    return "".join(lines)


def get_css_bundle() -> str:
    """
    Returns the complete CSS stylesheet adapted from Lovable tokens.css and styles.css
    with dark navy/indigo palette, glowing gradients, and custom Streamlit overrides.
    """
    return clean_html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ==================== ROOT TOKENS ==================== */
:root {
  --uma-bg:            #070b18;
  --uma-bg-2:          #0a1022;
  --uma-surface:       #0e152b;
  --uma-surface-2:     #131c38;
  --uma-surface-3:     #1a2547;
  --uma-glass:         rgba(20, 30, 62, 0.55);
  --uma-glass-2:       rgba(28, 40, 80, 0.38);

  --uma-primary:       #4f7cff;
  --uma-primary-soft:  #6f95ff;
  --uma-primary-deep:  #2b4fd6;
  --uma-indigo:        #7c5cff;
  --uma-cyan:          #35d0e8;

  --uma-success:       #2fd18a;
  --uma-success-bg:    rgba(47, 209, 138, 0.12);
  --uma-warning:       #f5b445;
  --uma-warning-bg:    rgba(245, 180, 69, 0.12);
  --uma-danger:        #ff6b6b;
  --uma-danger-bg:     rgba(255, 107, 107, 0.12);

  --uma-text:          #eef2ff;
  --uma-text-2:        #aab6d8;
  --uma-text-3:        #7683a6;

  --uma-border:        rgba(140, 165, 235, 0.14);
  --uma-border-strong: rgba(140, 165, 235, 0.28);

  --uma-grad-brand:    linear-gradient(135deg, #4f7cff 0%, #7c5cff 100%);
  --uma-grad-surface:  linear-gradient(160deg, rgba(79,124,255,.10), rgba(124,92,255,.04) 60%, transparent);
  --uma-grad-page:     radial-gradient(1100px 620px at 12% -8%, rgba(79,124,255,.16), transparent 60%),
                       radial-gradient(900px 560px at 92% 4%, rgba(124,92,255,.13), transparent 62%);

  --uma-shadow-sm:  0 1px 2px rgba(2,6,20,.4);
  --uma-shadow-md:  0 10px 28px -14px rgba(2,6,23,.85);
  --uma-shadow-lg:  0 28px 60px -28px rgba(2,6,23,.95);
  --uma-glow:       0 0 0 1px rgba(79,124,255,.35), 0 12px 36px -12px rgba(79,124,255,.45);

  --uma-r-xs: 8px;
  --uma-r-sm: 10px;
  --uma-r-md: 14px;
  --uma-r-lg: 18px;
  --uma-r-xl: 24px;
  --uma-r-pill: 999px;

  --uma-font: "Plus Jakarta Sans", "Inter", system-ui, -apple-system, sans-serif;
  --uma-font-mono: "JetBrains Mono", ui-monospace, monospace;
}

/* ==================== GLOBAL APP STYLING ==================== */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--uma-bg) !important;
  background-image: var(--uma-grad-page) !important;
  background-attachment: fixed !important;
  color: var(--uma-text) !important;
  font-family: var(--uma-font) !important;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(14,21,43,.96), rgba(8,12,26,.96)) !important;
  border-right: 1px solid var(--uma-border) !important;
}

/* Hide default streamlit decoration */
[data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--uma-font) !important;
  color: var(--uma-text) !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
}
p, span, label {
  font-family: var(--uma-font) !important;
}

/* Scrollbars */
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb { background: rgba(140,165,235,.2); border-radius: 99px; }
*::-webkit-scrollbar-thumb:hover { background: rgba(140,165,235,.35); }

/* ==================== COMPONENT STYLES ==================== */
.uma-caps {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--uma-text-3);
  font-weight: 700;
}
.uma-mono {
  font-family: var(--uma-font-mono) !important;
  font-variant-numeric: tabular-nums;
}
.uma-muted { color: var(--uma-text-2); }

/* App Header Banner */
.uma-top-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(14, 21, 43, 0.7);
  border: 1px solid var(--uma-border);
  border-radius: var(--uma-r-lg);
  backdrop-filter: blur(14px);
  margin-bottom: 24px;
  box-shadow: var(--uma-shadow-md);
}
.uma-brand-group {
  display: flex;
  align-items: center;
  gap: 14px;
}
.uma-brand-logo {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--uma-grad-brand);
  display: grid;
  place-items: center;
  box-shadow: var(--uma-glow);
  flex: none;
}
.uma-brand-logo svg {
  width: 24px;
  height: 24px;
}
.uma-brand-title {
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.uma-brand-sub {
  font-size: 12px;
  color: var(--uma-text-2);
  margin-top: 3px;
}

/* Card Header Helper */
.uma-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(140,165,235,0.08);
}
.uma-card-head h3 {
  font-size: 17px;
  margin: 0;
  color: #fff;
}
.uma-card-head p {
  font-size: 12.5px;
  color: var(--uma-text-2);
  margin-top: 3px;
  margin-bottom: 0;
}

/* Stepper */
.uma-stepper {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.uma-step {
  position: relative;
  padding: 14px 16px;
  border-radius: var(--uma-r-md);
  border: 1px solid var(--uma-border);
  background: rgba(19,28,56,.5);
  transition: all 240ms cubic-bezier(.22,.61,.36,1);
  overflow: hidden;
  text-decoration: none;
  display: block;
}
.uma-step .idx {
  font-family: var(--uma-font-mono);
  font-size: 11px;
  color: var(--uma-text-3);
  letter-spacing: .1em;
  font-weight: 700;
}
.uma-step .nm {
  margin-top: 5px;
  font-weight: 700;
  font-size: 13.5px;
  color: var(--uma-text-2);
}
.uma-step .ds {
  margin-top: 3px;
  font-size: 11px;
  color: var(--uma-text-3);
}
.uma-step.is-active {
  background: linear-gradient(150deg, rgba(79,124,255,.18), rgba(124,92,255,.08));
  border-color: rgba(79,124,255,.5);
  box-shadow: var(--uma-shadow-md);
}
.uma-step.is-active .nm, .uma-step.is-active .idx { color: #fff; }
.uma-step.is-active::after {
  content: ""; position: absolute; left: 0; bottom: 0; height: 3px; width: 100%;
  background: var(--uma-grad-brand);
}
.uma-step.is-done {
  border-color: rgba(47,209,138,.3);
}
.uma-step.is-done .idx { color: var(--uma-success); }
.uma-step.is-done .nm { color: var(--uma-text); }
.uma-step.is-done::after {
  content: ""; position: absolute; left: 0; bottom: 0; height: 3px; width: 100%;
  background: linear-gradient(90deg,#24b478,var(--uma-success));
}

/* KPI Cards */
.uma-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0,1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.uma-kpi {
  position: relative;
  background: linear-gradient(180deg, rgba(19,28,56,.75), rgba(13,19,40,.75));
  border: 1px solid var(--uma-border);
  border-radius: var(--uma-r-lg);
  padding: 18px 20px;
  box-shadow: var(--uma-shadow-md);
  overflow: hidden;
}
.uma-kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.uma-kpi-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  background: rgba(79,124,255,.14);
  border: 1px solid rgba(79,124,255,.24);
  color: var(--uma-primary-soft);
}
.uma-kpi-icon svg { width: 18px; height: 18px; }
.uma-kpi-icon.is-success { background: var(--uma-success-bg); border-color: rgba(47,209,138,.3); color: var(--uma-success); }
.uma-kpi-icon.is-warning { background: var(--uma-warning-bg); border-color: rgba(245,180,69,.3); color: var(--uma-warning); }
.uma-kpi-icon.is-danger  { background: var(--uma-danger-bg);  border-color: rgba(255,107,107,.3); color: var(--uma-danger); }
.uma-kpi-value {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -.03em;
  margin-top: 12px;
  font-family: var(--uma-font-mono);
  color: var(--uma-text);
}
.uma-kpi-label {
  font-size: 12.5px;
  color: var(--uma-text-2);
  margin-top: 4px;
}
.uma-delta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--uma-r-pill);
}
.uma-delta.up { color: var(--uma-success); background: var(--uma-success-bg); }
.uma-delta.down { color: var(--uma-danger); background: var(--uma-danger-bg); }
.uma-delta.flat { color: var(--uma-text-2); background: rgba(140,165,235,.10); }

/* Badges */
.uma-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--uma-r-pill);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
  border: 1px solid transparent;
  white-space: nowrap;
}
.uma-badge .dot {
  width: 6px; height: 6px; border-radius: 50%; background: currentColor; box-shadow: 0 0 8px currentColor;
}
.uma-badge--high   { color: var(--uma-success); background: var(--uma-success-bg); border-color: rgba(47,209,138,.28); }
.uma-badge--review { color: var(--uma-warning); background: var(--uma-warning-bg); border-color: rgba(245,180,69,.28); }
.uma-badge--none   { color: var(--uma-danger);  background: var(--uma-danger-bg);  border-color: rgba(255,107,107,.28); }
.uma-badge--info   { color: var(--uma-primary-soft); background: rgba(79,124,255,.12); border-color: rgba(79,124,255,.28); }
.uma-badge--neutral{ color: var(--uma-text-2); background: rgba(140,165,235,.09); border-color: var(--uma-border); }

/* File Card */
.uma-file {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: var(--uma-r-md);
  border: 1px solid var(--uma-border);
  background: rgba(19,28,56,.6);
  margin-top: 8px;
  margin-bottom: 8px;
}
.uma-file-ico {
  width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center;
  background: rgba(47,209,138,.12); color: var(--uma-success); border: 1px solid rgba(47,209,138,.24); flex: none;
}
.uma-file-ico.is-blue { background: rgba(79,124,255,.13); color: var(--uma-primary-soft); border-color: rgba(79,124,255,.26); }
.uma-file-name { font-weight: 650; font-size: 13.5px; color: var(--uma-text); word-break: break-all; }
.uma-file-stats { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 3px; font-size: 11.5px; color: var(--uma-text-3); }

/* Weight Bar & Legend */
.uma-weightbar {
  display: flex;
  height: 14px;
  border-radius: 99px;
  overflow: hidden;
  border: 1px solid var(--uma-border);
  background: var(--uma-bg-2);
  margin-top: 8px;
}
.uma-weightbar > span { display: block; height: 100%; }
.uma-legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; margin-bottom: 12px; }
.uma-legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--uma-text-2); }
.uma-legend-item i { width: 10px; height: 10px; border-radius: 3px; display: block; }

/* Donut Chart */
.uma-donut {
  display: grid;
  place-items: center;
  position: relative;
  margin: 8px auto;
}
.uma-donut svg { transform: rotate(-90deg); }
.uma-donut circle { fill: none; stroke-linecap: round; }
.uma-donut .track { stroke: rgba(140,165,235,.12); }
.uma-donut-center { position: absolute; text-align: center; }
.uma-donut-center .big { font-size: 24px; font-weight: 800; font-family: var(--uma-font-mono); color: #fff; }
.uma-donut-center .small { font-size: 10.5px; color: var(--uma-text-3); text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; }

/* Bar Chart */
.uma-chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 140px;
  padding-top: 10px;
  margin-bottom: 8px;
}
.uma-chart-bars .col {
  flex: 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 6px; height: 100%;
}
.uma-chart-bars .stack {
  width: 100%; max-width: 40px; border-radius: 5px 5px 2px 2px; background: var(--uma-grad-brand);
}
.uma-chart-bars .stack[data-tone="success"] { background: linear-gradient(180deg,#4fe3ab,#22a86e); }
.uma-chart-bars .stack[data-tone="warning"] { background: linear-gradient(180deg,#ffd07a,#dd9420); }
.uma-chart-bars .stack[data-tone="danger"]  { background: linear-gradient(180deg,#ff9b9b,#d64b4b); }
.uma-chart-bars .lab { font-size: 10.5px; color: var(--uma-text-3); white-space: nowrap; font-family: var(--uma-font-mono); }
.uma-chart-bars .val { font-size: 10.5px; color: var(--uma-text-2); font-family: var(--uma-font-mono); }

/* Review Compare Box */
.uma-compare-card {
  background: rgba(13,19,40,.6);
  border: 1px solid var(--uma-border);
  border-radius: var(--uma-r-md);
  padding: 16px;
  margin-bottom: 14px;
}
.uma-kv-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 10px;
}
.uma-kv-box {
  padding: 12px;
  border-radius: var(--uma-r-sm);
  border: 1px solid var(--uma-border);
  background: rgba(19,28,56,.4);
}
.uma-kv-box .k {
  font-size: 11px;
  color: var(--uma-text-3);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
}
.uma-kv-box .v {
  margin-top: 4px;
  font-weight: 600;
  font-size: 13px;
  color: var(--uma-text);
  word-break: break-word;
}

/* Streamlit Button & Widget Reskins */
div[data-testid="stButton"] > button {
  background: var(--uma-grad-brand) !important;
  color: #ffffff !important;
  border: 1px solid transparent !important;
  border-radius: var(--uma-r-sm) !important;
  font-family: var(--uma-font) !important;
  font-weight: 700 !important;
  padding: 0.55rem 1.2rem !important;
  box-shadow: 0 10px 24px -12px rgba(79,124,255,.9) !important;
  transition: all 140ms ease !important;
}
div[data-testid="stButton"] > button:hover {
  filter: brightness(1.08) !important;
  box-shadow: 0 14px 30px -10px rgba(79,124,255,1) !important;
  transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[disabled] {
  opacity: 0.45 !important;
  pointer-events: none !important;
}

/* Form Controls */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
  background-color: var(--uma-bg-2) !important;
  border-color: var(--uma-border) !important;
  border-radius: var(--uma-r-sm) !important;
  color: var(--uma-text) !important;
}
div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover {
  border-color: var(--uma-border-strong) !important;
}

/* Expander styling */
details[data-testid="stExpander"] {
  background: rgba(19,28,56,.5) !important;
  border: 1px solid var(--uma-border) !important;
  border-radius: var(--uma-r-md) !important;
}
summary[data-testid="stExpanderSummary"] {
  color: var(--uma-text) !important;
  font-weight: 600 !important;
}

/* Slider */
div[data-testid="stSlider"] [role="slider"] {
  background-color: #fff !important;
  border: 4px solid var(--uma-primary) !important;
  box-shadow: 0 0 0 6px rgba(79,124,255,.16) !important;
}

/* Native Table styling */
[data-testid="stDataFrame"] {
  border-radius: var(--uma-r-md) !important;
  border: 1px solid var(--uma-border) !important;
}
</style>
""")


def render_svg_sprite() -> str:
    """Returns SVG symbol sprite for high performance vector icon usage."""
    return clean_html("""
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <g id="i-logo" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h6l2 5 2-10 2 5h4"/></g>
    <g id="i-dash" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><rect x="3" y="3" width="7" height="8" rx="2"/><rect x="14" y="3" width="7" height="5" rx="2"/><rect x="3" y="15" width="7" height="6" rx="2"/><rect x="14" y="11" width="7" height="10" rx="2"/></g>
    <g id="i-spark" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 4.6L18.5 9.5 13.9 11.4 12 16l-1.9-4.6L5.5 9.5l4.6-1.9z"/><path d="M18 16.5l.8 1.9 1.9.8-1.9.8-.8 1.9-.8-1.9-1.9-.8 1.9-.8z"/></g>
    <g id="i-upload" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4"/><path d="M7.5 8.5L12 4l4.5 4.5"/><path d="M4 15v3a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-3"/></g>
    <g id="i-layers" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4.5-8 4.5-8-4.5z"/><path d="M4 12l8 4.5 8-4.5"/><path d="M4 16.5L12 21l8-4.5"/></g>
    <g id="i-file" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></g>
    <g id="i-db" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><ellipse cx="12" cy="5.5" rx="7" ry="2.8"/><path d="M5 5.5v13c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-13"/><path d="M5 12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8"/></g>
    <g id="i-target" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.4"/></g>
    <g id="i-alert" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M12 4l8.5 15H3.5z"/><path d="M12 9.5v4M12 16.5h.01"/></g>
    <g id="i-ban" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="8"/><path d="M6.5 17.5l11-11"/></g>
    <g id="i-check" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.5l3 3 6-7"/></g>
    <g id="i-download" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v12"/><path d="M7.5 11.5L12 16l4.5-4.5"/><path d="M4 19h16"/></g>
  </defs>
</svg>
""")


def render_top_banner(active_page_name: str, subtitle: str) -> str:
    """Generates the Lovable app header banner with logo and page titles."""
    return clean_html(f"""
{render_svg_sprite()}
<div class="uma-top-banner">
  <div class="uma-brand-group">
    <div class="uma-brand-logo">
      <svg viewBox="0 0 24 24"><use href="#i-logo"/></svg>
    </div>
    <div>
      <div class="uma-brand-title">Universal Match AI</div>
      <div class="uma-brand-sub">{html.escape(subtitle)}</div>
    </div>
  </div>
  <div class="uma-badge uma-badge--info">
    <span class="dot"></span>{html.escape(active_page_name)}
  </div>
</div>
""")


def render_card_header(title: str, subtitle: str, badge_text: str = "", badge_type: str = "info") -> str:
    """Renders a standard clean Lovable card header."""
    badge_html = ""
    if badge_text:
        badge_cls = f"uma-badge--{badge_type}"
        badge_html = f'<span class="uma-badge {badge_cls}"><span class="dot"></span>{html.escape(badge_text)}</span>'
    return clean_html(f"""
<div class="uma-card-head">
  <div>
    <h3>{html.escape(title)}</h3>
    <p>{html.escape(subtitle)}</p>
  </div>
  {badge_html}
</div>
""")


def render_stepper(current_step: int) -> str:
    """Renders the 4-step progress header in New Match."""
    steps = [
        ("01", "Upload Data", "Reference & master files"),
        ("02", "Configure Matching", "Columns, weights, thresholds"),
        ("03", "Run Matching", "Fuzzy engine execution"),
        ("04", "Results", "Review & export")
    ]
    html_out = '<div class="uma-stepper">'
    for idx, (num, name, desc) in enumerate(steps, 1):
        is_active = "is-active" if idx == current_step else ""
        is_done = "is-done" if idx < current_step else ""
        html_out += f'<div class="uma-step {is_active} {is_done}"><div class="idx">{num}</div><div class="nm">{html.escape(name)}</div><div class="ds">{html.escape(desc)}</div></div>'
    html_out += '</div>'
    return clean_html(html_out)


def render_kpi_cards(
    total: int,
    matched: int,
    review: int,
    no_match: int,
    match_rate: float
) -> str:
    """Generates the 4 prominent Lovable KPI cards with glowing icons and values."""
    matched_pct = f"{(matched / total * 100):.1f}%" if total > 0 else "0%"
    review_pct = f"{(review / total * 100):.1f}%" if total > 0 else "0%"
    no_match_pct = f"{(no_match / total * 100):.1f}%" if total > 0 else "0%"

    return clean_html(f"""
<div class="uma-kpis">
  <article class="uma-kpi">
    <div class="uma-kpi-top">
      <div class="uma-kpi-icon"><svg viewBox="0 0 24 24"><use href="#i-db"/></svg></div>
      <span class="uma-delta up">{match_rate:.1f}% Rate</span>
    </div>
    <div class="uma-kpi-value">{total:,}</div>
    <div class="uma-kpi-label">Total Records</div>
  </article>

  <article class="uma-kpi">
    <div class="uma-kpi-top">
      <div class="uma-kpi-icon is-success"><svg viewBox="0 0 24 24"><use href="#i-target"/></svg></div>
      <span class="uma-delta up">{matched_pct}</span>
    </div>
    <div class="uma-kpi-value" style="color:var(--uma-success);">{matched:,}</div>
    <div class="uma-kpi-label">High Confidence (≥ 90%)</div>
  </article>

  <article class="uma-kpi">
    <div class="uma-kpi-top">
      <div class="uma-kpi-icon is-warning"><svg viewBox="0 0 24 24"><use href="#i-alert"/></svg></div>
      <span class="uma-delta flat">{review_pct}</span>
    </div>
    <div class="uma-kpi-value" style="color:var(--uma-warning);">{review:,}</div>
    <div class="uma-kpi-label">Review Required (75–89%)</div>
  </article>

  <article class="uma-kpi">
    <div class="uma-kpi-top">
      <div class="uma-kpi-icon is-danger"><svg viewBox="0 0 24 24"><use href="#i-ban"/></svg></div>
      <span class="uma-delta down">{no_match_pct}</span>
    </div>
    <div class="uma-kpi-value" style="color:var(--uma-danger);">{no_match:,}</div>
    <div class="uma-kpi-label">No Match (&lt; 75%)</div>
  </article>
</div>
""")


def render_donut_chart(pct: float, label: str = "Match Rate", size: int = 150) -> str:
    """Renders pure SVG gradient circular progress chart."""
    radius = size / 2 - 12
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1.0 - min(100.0, max(0.0, pct)) / 100.0)

    return clean_html(f"""
<div class="uma-donut">
  <svg width="{size}" height="{size}">
    <circle class="track" cx="{size/2}" cy="{size/2}" r="{radius}" stroke-width="12"/>
    <circle cx="{size/2}" cy="{size/2}" r="{radius}" stroke="url(#umaDonutGrad)" stroke-width="12"
      stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"/>
    <defs>
      <linearGradient id="umaDonutGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4f7cff"/>
        <stop offset="100%" stop-color="#7c5cff"/>
      </linearGradient>
    </defs>
  </svg>
  <div class="uma-donut-center">
    <div class="big">{pct:.1f}%</div>
    <div class="small">{html.escape(label)}</div>
  </div>
</div>
""")


def render_confidence_barchart(distribution: List[Dict[str, Any]]) -> str:
    """
    Renders pure SVG/CSS bar chart for confidence score distribution.
    """
    max_val = max([item['value'] for item in distribution], default=1) or 1
    
    cols_html = ""
    for item in distribution:
        h = max(6, int((item['value'] / max_val) * 110))
        cols_html += f'<div class="col" title="{item["label"]}: {item["value"]}"><span class="val">{item["value"]}</span><div class="stack" data-tone="{item.get("tone", "success")}" style="height:{h}px;"></div><span class="lab">{item["label"]}</span></div>'

    return clean_html(f'<div class="uma-chart-bars">{cols_html}</div>')


def render_file_card(
    filename: str,
    rows_count: int,
    cols_count: int,
    is_master: bool = False
) -> str:
    """Generates a Lovable file badge card showing name and dataset properties."""
    ico_class = "is-blue" if is_master else ""
    return clean_html(f"""
<div class="uma-file">
  <div class="uma-file-ico {ico_class}">
    <svg viewBox="0 0 24 24"><use href="#i-file"/></svg>
  </div>
  <div style="flex:1;min-width:0;">
    <div class="uma-file-name">{html.escape(filename)}</div>
    <div class="uma-file-stats">
      <span><b>{rows_count:,}</b> rows</span>
      <span>•</span>
      <span><b>{cols_count}</b> columns</span>
    </div>
  </div>
</div>
""")


def render_weight_bar(rules_data: List[Dict[str, Any]]) -> str:
    """
    Renders the dynamic color-coded weight allocation bar.
    """
    total = sum(r['weight'] for r in rules_data) or 1
    colors = ["#4f7cff", "#7c5cff", "#35d0e8", "#2fd18a", "#f5b445"]

    spans_html = ""
    legend_html = ""
    for i, r in enumerate(rules_data):
        w_pct = (r['weight'] / total) * 100
        c = colors[i % len(colors)]
        spans_html += f'<span style="width:{w_pct}%;background:{c};"></span>'
        legend_html += f'<span class="uma-legend-item"><i style="background:{c};"></i>{html.escape(r["name"])} <b class="uma-mono" style="color:var(--uma-text);">{r["weight"]}%</b></span>'

    return clean_html(f"""
<div class="uma-caps" style="margin-top:14px;">Weight Allocation</div>
<div class="uma-weightbar">{spans_html}</div>
<div class="uma-legend">{legend_html}</div>
""")
