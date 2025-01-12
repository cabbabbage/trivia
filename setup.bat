@echo off

REM Step 0: Check for and upgrade pip
echo Checking for pip upgrade...
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade pip
echo Pip has been upgraded to the latest version.

REM Step 1: Check if Git is installed, if not, install it
git --version >nul 2>&1
if errorlevel 1 (
    echo Installing Git...
    winget install --id Git.Git -e --source winget
) else (
    echo Git is already installed.
)

REM Step 2: Create the "game_code" directory if it doesn't exist, then navigate into it
if not exist "game_code" mkdir game_code
cd game_code

REM Step 3: Clone the repository if not already cloned
if not exist "trivia" (
    echo Cloning repository...
    git clone "https://github.com/cabbabbage/trivia.git"
) else (
    echo Repository already exists.
)

REM Step 4: Navigate into the repo folder
cd trivia

REM Step 5: Create a virtual environment inside the repo if it doesn't exist
if not exist "env\Scripts\activate" (
    echo Creating virtual environment inside the repo...
    python -m venv env
) else (
    echo Virtual environment already exists.
)

REM Step 6: Activate the virtual environment
call env\Scripts\activate

REM Step 7: Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Step 8: Run the Python script
echo Running main.py...
python main.py || python3 main.py
