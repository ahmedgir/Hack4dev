#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

venv_dir="$repo_root/.venv"
python_version="3.10"

echo "== Hack4Dev lightweight local setup =="

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/ and rerun this script."
  exit 1
fi

echo "[1/4] Creating or reusing Python ${python_version} environment..."
uv venv --allow-existing --python "$python_version" "$venv_dir"

echo "[2/4] Installing pinned scientific dependencies..."
uv pip install --python "$venv_dir/bin/python" \
  "numpy==1.26.4" \
  "pandas==2.2.3" \
  "scipy==1.14.1" \
  "matplotlib==3.9.4" \
  "astropy==6.1.7" \
  "photutils==2.0.2" \
  "jupyterlab==4.6.3" \
  "ipywidgets==8.1.9" \
  requests pillow \
  "exotic==4.3.1" \
  "astroalign==2.6.2" \
  "plotly==7.0.0" \
  sep

echo "[3/4] Installing frontend dependencies..."
if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is unavailable; enabling the repository's pinned pnpm version via Corepack."
  if ! command -v corepack >/dev/null 2>&1; then
    echo "Corepack is unavailable; skipping frontend installation."
  else
    corepack enable
    corepack pnpm install --dir "$repo_root/webapp/frontend" --frozen-lockfile
  fi
else
  pnpm install --dir "$repo_root/webapp/frontend" --frozen-lockfile
fi

echo "[4/4] Checking installed tools..."
"$venv_dir/bin/python" - <<'PY'
import importlib

modules = {
    "exotic": "EXOTIC",
    "astropy": "Astropy",
    "photutils": "Photutils",
    "astroalign": "Astroalign",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "plotly": "Plotly",
    "jupyterlab": "JupyterLab",
    "ipywidgets": "ipywidgets",
    "requests": "Requests",
    "PIL": "Pillow",
    "sep": "SEP",
}

failed = []
for module, label in modules.items():
    try:
        imported = importlib.import_module(module)
        version = getattr(imported, "__version__", "available")
        print(f"OK   {label}: {version}")
    except Exception as exc:
        failed.append(label)
        print(f"FAIL {label}: {exc}")

if failed:
    raise SystemExit("Missing or broken imports: " + ", ".join(failed))
PY

if [ -d "$repo_root/webapp/frontend/node_modules" ]; then
  echo "OK   frontend dependencies: node_modules present"
else
  echo "WARN frontend dependencies: node_modules not present"
fi

echo
echo "Setup complete. Activate with: source .venv/bin/activate"
