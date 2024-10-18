import json
import glob
import os

MODELS_PATHS = "./models"
models={}
models_name_and_tag = {}

def loadModels():
    # Find all JSON files in the folder
    json_files = glob.glob(os.path.join(MODELS_PATHS, '*.json'))

    # Process each JSON file
    for file in json_files:
        with open(file, 'r') as json_file:
            data = json.load(json_file)
            models[data.get("model_name", "Modèle sans nom")] = data

def getAllModelsName():
    return tuple(models.keys())

def getAllModelsNameAndTag():
    global models_name_and_tag
    if models_name_and_tag != {}:
        return models_name_and_tag
    a = {}
    for key, item in models.items():
        a[item["tag"][0]+" ⋄ "+key] = key
    models_name_and_tag = a
    return a

loadModels()
