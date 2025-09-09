# Predictive Vehicle Maintenance — Quickstart

Flask backend + React frontend for a predictive vehicle maintenance demo. This README focuses on **running the backend** and gives **light pointers** for the frontend.

---

## Clone this repo

```bash
git clone https://github.com/ImperaLuna/techfest.git
cd techfest
```

---

## Project structure (relevant bits)

```
backend/
  pyproject.toml
  src/
    pvmt/
      main.py                # Flask entrypoint
      app/
        routes.py            # /home/post-data endpoint
      ml/
        inference.py         # ML orchestrator
        features.py          # DO NOT MOVE (pickle dependency)
        artifacts/           # *.pkl artifacts live here
      utils/
frontend-dashboard/
  package.json
```

---

## First run (fresh clone)

### 1) Backend setup

```bash
# create & activate venv
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
# source .venv/bin/activate
python -m pip install --upgrade pip

# install backend (editable)
cd backend
pip install -e .
```

### 2) Start the backend API

```bash
python -m pvmt.main
```

Serves on **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

### 3) Frontend (minimal)

```bash
# in another terminal from repo root
cd frontend-dashboard
# use Node 20 LTS, then install deps
npm ci   # or: npm install
npm start  # CRA; or: npm run dev for Vite
```

Frontend on **[http://localhost:3000](http://localhost:3000)**.


---

## Subsequent runs (already installed)

### Backend

```bash
# from repo root
. .venv/Scripts/Activate.ps1      # Windows PowerShell
# source .venv/bin/activate        # macOS/Linux
cd backend
python -m pvmt.main
```

### Frontend

```bash
cd frontend-dashboard
npm start   # or: npm run dev
```

---

## API smoke test (optional)

```bash
curl -X POST http://127.0.0.1:5000/home/post-data \
  -H "Content-Type: application/json" \
  -d '{
        "brand": "BMW",
        "odometer": 100000,
        "vehicletype": "combustion",
        "year": 2017,
        "timebudget": 60
      }'
```

