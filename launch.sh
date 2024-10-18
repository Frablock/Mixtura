#!/bin/bash

# Vérifie si un environnement virtuel existe déjà
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python -m venv venv
else
    echo "L'environnement virtuel existe déjà. Activation..."
fi

# Active l'environnement virtuel
source ./venv/bin/activate

# Met à jour pip avant d'installer les dépendances
pip install --upgrade pip

# Installe les dépendances
pip install -r requirements.txt

# Exécute le script Python
python ui.py
