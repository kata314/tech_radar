# Tech Radar

A technology radar for the ML team covering search, recommendations, agentic shopping, and fraud detection.

The radar organises technologies into four **quadrants** and four **rings**:

| Quadrant         | What it covers                                      |
|------------------|-----------------------------------------------------|
| Models           | Model architectures and approaches (e.g. two-tower, GNNs) |
| Infrastructure   | Platforms and serving (e.g. Ray, Kubernetes, vLLM)  |
| Libraries        | Frameworks and libraries (e.g. PyTorch, FAISS)      |
| Techniques       | Methods and practices (e.g. RAG, contrastive learning) |

| Ring   | Meaning                                    |
|--------|--------------------------------------------|
| Adopt  | Proven, default choice for the team        |
| Trial  | Worth pursuing, used in production pilots  |
| Assess | Worth exploring, not yet trialled           |
| Hold   | Proceed with caution, moving away from     |

## Updating the radar

All radar data lives in a single file: **`radar.yaml`**. Each entry has four fields:

```yaml
- name: Qdrant
  quadrant: infrastructure    # models | infrastructure | libraries | techniques
  ring: assess                # adopt | trial | assess | hold
  description: >
    Vector database for semantic search. Evaluating as
    managed alternative to FAISS for production workloads.
```

### How to make a change

1. **Edit `radar.yaml`** directly — add, remove, or update entries.
2. Update the `last_updated` date at the top of the file.
3. Open a pull request. CI will validate your changes automatically.
4. Once merged to `main`, the radar is deployed to GitHub Pages.

You can also use the CLI tool:

```bash
# Set up (one time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add a new entry
python radar.py add "Qdrant" \
  -q infrastructure \
  -r assess \
  -d "Vector database for semantic search."

# Move an entry to a different ring
python radar.py move "Qdrant" -r trial

# Remove an entry
python radar.py remove "Qdrant"

# Validate the file (same check CI runs)
python radar.py validate

# List all entries
python radar.py list
```

The `add` and `move` commands automatically update the `last_updated` date.

## Viewing the radar

The radar is a static site — `index.html` loads `radar.yaml` directly in the browser.

- **Deployed**: via GitHub Pages (auto-deployed on merge to `main`)
- **Locally**: `python3 -m http.server 8080` then open http://localhost:8080

## File overview

| File | Purpose |
|------|---------|
| `radar.yaml` | Radar entries — the only file you need to edit |
| `index.html` | Frontend — single-file interactive radar visualisation |
| `radar.py` | CLI tool — validate, list, add, move, remove entries |
| `requirements.txt` | Python dependencies |
| `.github/workflows/deploy.yml` | CI/CD — validates on PR, deploys on merge |
