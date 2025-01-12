@echo off

REM Step 1: Navigate to the user's Documents folder and create "game_code" if it doesn't exist
set "project_folder=%USERPROFILE%\Documents\game_code"
if not exist "%project_folder%" (
    echo Creating project folder: "%project_folder%"...
    mkdir "%project_folder%"
) else (
    echo Project folder already exists: "%project_folder%".
)

cd "%project_folder%"

REM Step 2: Clone the repository if not already cloned
if not exist "trivia" (
    echo Cloning repository into "%project_folder%\trivia"...
    git clone "https://github.com/cabbabbage/trivia.git"
) else (
    echo Repository already exists in "%project_folder%\trivia".
)

REM Step 3: Navigate into the repo folder
cd trivia

REM Step 4: Create a virtual environment inside the repo if it doesn't exist
if not exist "env\Scripts\activate" (
    echo Creating virtual environment inside the repo...
    python -m venv env
) else (
    echo Virtual environment already exists.
)

REM Step 5: Activate the virtual environment
call env\Scripts\activate

REM Step 6: Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Step 7: Run the Python script
echo Running main.py...
python main.py || python3 main.py

REM Step 8: Open VS Code in the "game_code" folder
echo Opening Visual Studio Code in "%project_folder%"...
code "%project_folder%"

REM Step 9: Keep the virtual environment activated after the script ends
cmd /k "env\Scripts\activate"
