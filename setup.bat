@echo off
REM Step 1: Check if the virtual environment "game" exists. If not, create it.
if not exist "game\Scripts\activate" (
    echo Creating virtual environment "game"...
    python -m venv game
) else (
    echo Virtual environment "game" already exists.
)

REM Step 2: Activate the virtual environment
call game\Scripts\activate

REM Step 3: Create the "game" directory if it doesn't exist, then navigate into it
if not exist "game" mkdir game
cd game

REM Step 4: Check if Git is installed, if not, install it
git --version >nul 2>&1
if errorlevel 1 (
    echo Installing Git...
    winget install --id Git.Git -e --source winget
) else (
    echo Git is already installed.
)

REM Step 5: Clone the repository if not already cloned
if not exist "repo-folder-name" (
    echo Cloning repository...
    git clone "your-repo-url"
) else (
    echo Repository already exists.
)

REM Step 6: Navigate into the repo folder
cd repo-folder-name

REM Step 7: Install dependencies if not already installed
if not exist "game\Lib\site-packages" (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Dependencies already installed.
)

REM Step 8: Run the Python script
echo Running main.py...
python main.py || python3 main.py
