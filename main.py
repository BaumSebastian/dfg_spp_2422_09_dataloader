from src.dataset import FEMGraphDataset, LoadType
from src.utils import load_config

# Example Usage
if __name__ == "__main__":

    # Adjust Paths.
    config_file_path = 'config.yaml'

    # Get the config  
    config = load_config(config_file_path)
    dataset_config = config['dataset']
    print(dataset_config)
    base_dir = dataset_config['base_dir']
    geometries = dataset_config['geometries']

    # Specify what you want to load.
    timesteps = [0, -1]
    load_type = LoadType.NODES_AND_FEATURES

    # Access dataset
    dataset = FEMGraphDataset(
        base_dir=base_dir,
        geometries=geometries,  # Replace with actual IDs
        timestep=timesteps,
        load_type=load_type
    )

    print("Dataset size:", len(dataset))
    sample = dataset[0]
    print("Sample keys:", sample.keys())
    print("Nodes shape:", sample["nodes"].shape)
    print("Edge features shape:", sample["edge_features"].shape)
