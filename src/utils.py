import yaml
from typing import Dict
import pathlib

# Function to load the configuration from a YAML file
def load_config(file_path :str) -> Dict:
    
    if not pathlib.Path(file_path).is_file() or not file_path.endswith('yaml'):
        raise ValueError(f"Path needs to be a yaml file: {file_path}")
    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config