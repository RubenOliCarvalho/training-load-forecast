# Command Reference

## Git — version control (local history)
- `git --version` — check git is installed
- `git init` — turns a folder into a git repository (creates the hidden `.git` folder)
- `git status` — shows what's changed, staged, or untracked right now
- `git add <file>` — stages a file: marks it to be included in the *next* commit
- `git commit -m "message"` — permanently saves a snapshot of everything staged
- `git config --global user.name "..."` / `user.email "..."` — sets the identity attached to your commits, once, for every repo on this machine
- `git log` — lists past commits (viewing only, doesn't change anything)

## Python environment — uv, venv, pip
- `python --version` / `pip --version` — check what's installed and where
- `python -m venv venv` — creates an isolated copy of Python just for this project (before we knew 3.14 would cause problems)
- `venv\Scripts\Activate.ps1` — activates that isolated environment for the current terminal, so `python`/`pip` point inside the project instead of your global install
- `deactivate` — exits the venv, back to your global Python
- `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` — one-time Windows setting allowing locally-written scripts (like venv activation) to run; PowerShell blocks this by default for security
- `uv --version` — checked whether `uv` (a fast Python version/package manager) was already installed
- `uv python install 3.12` — installs Python 3.12 via `uv`, independent of your existing 3.14
- `py -0` — lists every Python version the Windows launcher knows about
- `uv venv --python 3.12 venv` — rebuilt the project's venv pinned specifically to 3.12
- `uv pip install -r requirements.txt` — installs everything listed in `requirements.txt` into the active venv (we use `uv pip`, not plain `pip`, because `uv`-created venvs don't include a standalone pip binary)
- `python -c "import sys; print(sys.executable)"` — diagnostic one-liner confirming exactly which Python is currently active

## PowerShell / file basics
- `mkdir` — create a folder
- `cd` — change directory
- `Get-ChildItem -Force` — list files in a folder, including hidden ones (like `.env`)
- `type <file>` — print a file's contents to the screen
- `@"..."@ | Out-File -Encoding utf8 <file>` — a PowerShell trick for writing multi-line text straight into a file from the command line (used for `.gitignore`, `requirements.txt`)
- `where.exe <command>` — shows every location on your system where a command's program actually lives, in the order it'll be found — used to debug why `pip` was resolving to the wrong Python

## Postgres
- `psql -U <user> -h localhost -p 5432` — connects to Postgres from the command line as a given user
- `CREATE ROLE ... WITH LOGIN PASSWORD ...` — creates a new database user
- `CREATE DATABASE ... OWNER ...` — creates a new database owned by that user
- `ALTER ROLE ... WITH PASSWORD ...` — changes a user's password