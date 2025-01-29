from src.dataset import FEMGraphDataset, LoadType
from src.utils import load_config

# Example Usage
if __name__ == "__main__":

    # Adjust Paths.
    config_file_path = 'config.yaml'

    # Get the config  
    config = load_config(config_file_path)
    dataset_config = config['dataset']
    base_dir = dataset_config['base_dir']

    # Specify what you want to load.
    geometries = ['blank', 'punch', 'binder','die']
    timesteps = [0, -1]
    load_type = LoadType.NODES_AND_FEATURES

    # Access dataset
    dataset = FEMGraphDataset(
        base_dir=base_dir,
        geometries=geometries,
        timesteps=timesteps,
        load_type=load_type
    )

    # Total information
    print("Dataset size:", len(dataset))
    
    # Information per simulation.
    (parameters, point_clouds, node_indices, features)  = dataset[0]
    
    for geometry, pc in zip(geometries, point_clouds):
        print(f"{geometry} shape: {pc.shape}")

    print(f"Node indices shape: {node_indices.shape}")
    print(f"Features shape: {features.shape}")