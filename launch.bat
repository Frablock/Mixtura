@echo off

REM Vérifie si un environnement virtuel existe déjà
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Création de l'environnement virtuel...
    python -m venv venv
) ELSE (
    echo L'environnement virtuel existe déjà. Activation...
)

REM Active l'environnement virtuel
call venv\Scripts\activate.bat

REM Met à jour pip avant d'installer les dépendances
pip install --upgrade pip

REM Installe les dépendances
pip install -r requirements.txt

REM Exécute le script Python
python ui.py
