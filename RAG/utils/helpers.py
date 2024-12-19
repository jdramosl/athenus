import logging
import json

def load_json(filepath: str):
    """
    Carga un archivo JSON y lo retorna como un diccionario.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error("Error cargando JSON desde %s: %s", filepath, str(e))
        return {}

def save_json(data: dict, filepath: str):
    """
    Guarda un diccionario en un archivo JSON.
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error("Error guardando JSON en %s: %s", filepath, str(e))