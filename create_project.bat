@echo off
cd /d "C:\Users\itsme\Downloads"

echo Creating JobQueue-CLI project structure...

mkdir jobqueue-cli
cd jobqueue-cli
mkdir jobqueue_cli
mkdir tests

cd jobqueue_cli
type nul > __init__.py
type nul > cli.py
type nul > core.py
type nul > models.py
type nul > storage.py
type nul > worker.py
type nul > config.py

cd ..\tests
type nul > __init__.py
type nul > test_core.py
type nul > test_storage.py
type nul > test_worker.py

cd ..
type nul > setup.py
type nul > requirements.txt
type nul > README.md
type nul > demo_script.py

echo Project structure created successfully!
echo Open the jobqueue-cli folder in VS Code to start editing.
pause