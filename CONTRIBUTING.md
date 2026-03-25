# Contributing

## Prerequisites

- Python 3.10+
- A virtual environment with `ruamel.yaml` installed:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Making changes to radar entries

### Branch naming convention

Use quarterly branches for radar updates:

```
radar/2026-q1       ← Q1 main update (first of the quarter)
radar/2026-q1.2     ← second update within Q1
radar/2026-q1.3     ← third update within Q1
radar/2026-q2       ← Q2 starts
```

- The first update each quarter uses `radar/YYYY-qN` (no suffix).
- Subsequent updates within the same quarter append `.2`, `.3`, etc.
- For non-radar changes (frontend fixes, CLI updates), use any descriptive branch name
  (e.g. `fix/tooltip-overflow`). The quarterly convention applies only to radar entry updates.

### Workflow

1. Create a branch from `main` following the naming convention above.
2. Edit `radar.yaml` — add, update, move, or remove entries. Multiple team members can
   push commits to the same quarterly branch.
3. Run validation locally before pushing:

```bash
python radar.py validate
```

4. Open a pull request targeting `main`.
5. CI runs `python radar.py validate` automatically. The PR cannot be merged if validation fails.
6. On merge to `main`, the site is deployed to GitHub Pages automatically.

### What validation checks

- Every entry has `name`, `quadrant`, `ring`, and `description` fields.
- `quadrant` is one of: `models`, `infrastructure`, `libraries`, `techniques`.
- `ring` is one of: `adopt`, `trial`, `assess`, `hold`.
- No duplicate entry names (case-insensitive).

### Editing tips

- Keep entries grouped by quadrant using the section comments in `radar.yaml`.
- Use the `>` (folded block scalar) style for multi-line descriptions — it keeps the YAML readable and produces clean single-paragraph text in the UI.
- Update `last_updated` at the top of the file when making manual edits (the CLI does this automatically).

## Making changes to the frontend or CLI

### Frontend (`index.html`)

The radar is a single self-contained HTML file. It loads `radar.yaml` at runtime using
[js-yaml](https://github.com/nodeca/js-yaml) from a CDN and renders an SVG radar.

To test locally:

```bash
python3 -m http.server 8080
# Open http://localhost:8080
```

There is no build step. Edit `index.html`, refresh the browser.

### CLI (`radar.py`)

The CLI uses **`ruamel.yaml`** (not PyYAML). This is deliberate: `ruamel.yaml` preserves
comments, formatting, and YAML block scalar style (`>`) on round-trip read/write. PyYAML
strips all of this, producing noisy diffs and less readable files. **Do not switch to PyYAML.**

If you add new CLI commands that write to `radar.yaml`, use the existing `load_radar()` /
`save_radar()` functions to ensure formatting is preserved.

### CI/CD (`.github/workflows/deploy.yml`)

The workflow has two jobs:

| Job | Trigger | What it does |
|-----|---------|--------------|
| `validate` | Every push and PR to `main` | Runs `python radar.py validate` |
| `deploy` | Push to `main` only (after validation passes) | Deploys `index.html` and `radar.yaml` to GitHub Pages |

#### GitHub Pages setup (one-time)

In your repo settings:

1. Go to **Settings > Pages**.
2. Set **Source** to **GitHub Actions**.

No other configuration is needed.

#### Adding new checks

If you add new validation logic (e.g. description length limits, required fields), add it
to the `validate()` function in `radar.py`. CI will pick it up automatically — no workflow
changes needed.
