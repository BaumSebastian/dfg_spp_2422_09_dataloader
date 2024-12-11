import os
import numpy as np
import torch
from torch.utils.data import Dataset
from enum import Enum
import pandas as pd
from typing import Optional, Union



class LoadType(Enum):
    NODES = "nodes"
    NODES_AND_FEATURES = "nodes_and_features"


class FEMGraphDataset(Dataset):
    def __init__(self, base_dir : str, geometries : Optional[Union[str]]=None, timestep : Optional[Union[int]] = [0, -1], load_type : LoadType=LoadType.NODES_AND_FEATURES):
        """
        FEMGraphDataset for loading FEM simulation data stored as point clouds and edge features.

        Args:
            base_dir (str): Path to the base dataset directory.
            geometries (list, optional): List of geometry IDs to load. Defaults to None (loads all geometries).
            timestep (list, optional): List of timesteps expressed as integer. Also supports "-1" for last timestep.
            load_type (LoadType, optional): Enum specifying what data to load.
                                            Choices are NODES (only point clouds) or
                                            NODES_AND_FEATURES (point clouds and edge features).
                                            Defaults to LoadType.NODES_AND_FEATURES.
        """
        self.base_dir = base_dir
        self.geometries = geometries
        self.load_type = load_type
        self.timestep = timestep

        # Validate input arguments
        self._validate_inputs()

        # Load metadata
        metadata_path = os.path.join(base_dir, "metadata.csv")
        self.metadata = self._load_metadata(metadata_path)

        # Filter geometries if a list is provided
        if geometries is None:
            self.geometries = self.get_all_parts()

        # Validate geometries
        self._validate_geometries()

        # Create a list of data file paths
        self.data_paths = self._build_data_paths()
    
    def get_all_parts(self):
        # Assuming parts are defined in the metadata or can be derived from the file structure
        return ['blank', 'binder', 'punch', 'die']  # Replace with actual part names if available
    
    def _validate_inputs(self):
        """Validate the base directory and input arguments."""
        # Check if the base directory exists
        if not os.path.exists(self.base_dir):
            raise FileNotFoundError(f"Base directory '{self.base_dir}' does not exist.")

        # Check if the required subdirectories exist
        pc_dir = os.path.join(self.base_dir, "pc")
        ef_dir = os.path.join(self.base_dir, "ef")
        if not os.path.exists(pc_dir) or not os.path.isdir(pc_dir):
            raise FileNotFoundError(f"Point cloud directory '{pc_dir}' does not exist.")
        if not os.path.exists(ef_dir) or not os.path.isdir(ef_dir):
            raise FileNotFoundError(f"Edge feature directory '{ef_dir}' does not exist.")

        # Validate load_type
        if not isinstance(self.load_type, LoadType):
            raise ValueError(f"Invalid load_type '{self.load_type}'. Must be a member of LoadType Enum.")

    def _load_metadata(self, metadata_path):
        """Load metadata from the CSV file."""
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at '{metadata_path}'.")

        metadata = pd.read_csv(metadata_path)

        if "id" not in metadata.columns:
            raise ValueError("Metadata file must contain an 'id' column.")
        
        return metadata

    def _validate_geometries(self):
            
            if not isinstance(self.geometries, list):
                raise TypeError("The argument geometries need to be of type list.")

            for geo in self.geometries:
                if geo not in self.get_all_parts():
                    raise ValueError(f"The geometry {geo} is not supported. Please selected one of: {self.get_all_parts()}")

    def _build_data_paths(self):
        
        """Build a list of paths to data files for the specified geometries."""
        data_paths = []

        for sim_id in self.metadata['id']:
            
            pc_dir = os.path.join(self.base_dir, "pc", str(sim_id))
            ef_dir = os.path.join(self.base_dir, "ef", str(sim_id))

            # Validate geometry directories
            if not os.path.exists(pc_dir) or not os.path.isdir(pc_dir):
                raise FileNotFoundError(f"Point cloud directory '{pc_dir}' does not exist for geometry ID '{geom_id}'.")
            if not os.path.exists(ef_dir) or not os.path.isdir(ef_dir):
                raise FileNotFoundError(f"Edge feature directory '{ef_dir}' does not exist for geometry ID '{geom_id}'.")

            # Gather all point cloud and edge feature files for this geometry
            pc_files = sorted([os.path.join(pc_dir, f) for f in os.listdir(pc_dir) if f.endswith(".npy")])
            ef_files = sorted([os.path.join(ef_dir, f) for f in os.listdir(ef_dir) if f.endswith(".npy")])

            # Ensure equal number of files for point clouds and edge features
            if len(pc_files) != len(ef_files):
                raise ValueError(f"Mismatch in number of point cloud and edge feature files for geometry ID '{geom_id}'.")

            # Match files by timestep index
            for pc_file, ef_file in zip(pc_files, ef_files):
                data_paths.append((pc_file, ef_file))

        return data_paths

    def __len__(self):
        return len(self.data_paths)

    def __getitem__(self, idx):
        """
        Load a single data point (graph) based on the specified load_type.

        Args:
            idx (int): Index of the data point to load.

        Returns:
            dict: A dictionary containing the loaded data.
        """
        pc_file, ef_file = self.data_paths[idx]

        # Load point cloud (nodes)
        nodes = np.load(pc_file)

        if self.load_type == LoadType.NODES:
            return {"nodes": torch.tensor(nodes, dtype=torch.float32)}

        # Load edge features
        edge_features = np.load(ef_file)

        return {
            "nodes": torch.tensor(nodes, dtype=torch.float32),
            "edge_features": torch.tensor(edge_features, dtype=torch.float32),
        }


# Example Usage
if __name__ == "__main__":
    dataset = FEMGraphDataset(
        base_dir=r"/your/path/to/dataset",
        geometries=None,  # Replace with actual IDs
        timestep=[0,-1],
        load_type=LoadType.NODES_AND_FEATURES
    )

    print("Dataset size:", len(dataset))
    sample = dataset[0]
    print("Sample keys:", sample.keys())
    print("Nodes shape:", sample["nodes"].shape)
    print("Edge features shape:", sample["edge_features"].shape)
