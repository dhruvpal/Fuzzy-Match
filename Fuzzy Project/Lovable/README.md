# Universal Match AI — Frontend design source

Pure HTML + CSS + JS. No backend, no auth, no APIs, no matching logic.

## Files
| File | Purpose |
| --- | --- |
| `index.html` | Full UI structure: shell, sidebar nav, Dashboard, New Match (4 steps), Match History, Review Center, Settings, match-detail drawer. Icons are an inline SVG sprite (`<use href="#i-...">`) — no icon library. |
| `tokens.css` | Design tokens: colors, gradients, shadows, radius, 4pt spacing scale, typography scale, motion. |
| `styles.css` | Component system: cards, buttons, badges, inputs, sliders, segmented controls, chips, tables, stepper, dropzones, file cards, mapping rules, charts, drawer, review compare, responsive rules. |
| `data.js` | **Mock data only.** Replace with Python-injected JSON. |
| `app.js` | UI interactions only: nav, stepper, chart drawing, chips, sliders, drawer, processing animation, token interpolation. |

## Fonts
Plus Jakarta Sans (UI) + JetBrains Mono (numbers/IDs), loaded via Google Fonts `<link>` in `index.html`.

## Streamlit integration
1. Inject values by replacing the `{{...}}` tokens (already used in the markup):
   `{{total_records}}`, `{{matched_records}}`, `{{review_records}}`, `{{no_match_records}}`,
   `{{match_rate}}`, `{{records_processed}}`, `{{progress}}`, `{{rows_used}}`, `{{rows_quota}}`,
   `{{recent_jobs}}`, `{{result_rows}}`.

```python
import json, pathlib, streamlit.components.v1 as components

html = pathlib.Path("uma/index.html").read_text()
payload = {"tokens": {...}, "results": df.to_dict("records"), "jobs": [...], "matchRate": 87.6, ...}
html = html.replace("<script src=\"./data.js\"></script>",
                    f"<script>window.UMA_DATA = {json.dumps(payload)}</script>")
components.html(html, height=1600, scrolling=True)
```
   Or keep `data.js` and simply overwrite `window.UMA_DATA` then call `UMA.render()`.

2. Tables are rendered from arrays (`UMA_DATA.jobs`, `UMA_DATA.results`), so Python can inject rows directly — each result row supports `sample, best, id, confidence, status ("high"|"review"|"none"), original, matched, scores, candidates`.

3. The dropzones are **visual only**. Keep `st.file_uploader` for real uploads and feed the resulting metadata into `UMA_DATA.files.reference / .master` (`name, size, rows, cols`).

4. If you prefer native Streamlit widgets, keep the CSS: inject `tokens.css` + `styles.css` via `st.markdown("<style>…</style>", unsafe_allow_html=True)` and reuse the class names (`uma-card`, `uma-btn uma-btn--primary`, `uma-badge uma-badge--high`, `uma-table`, `uma-chip`, …).

## Public API of `app.js`
- `UMA.render()` — re-render everything from `window.UMA_DATA`
- `UMA.goToPage("dashboard" | "new-match" | "history" | "review" | "settings")`
- `UMA.setStep(1..4)`
