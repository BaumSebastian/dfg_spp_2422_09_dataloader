import os
import numpy as np
import torch
from torch.utils.data import Dataset
from enum import Enum
import pandas as pd
from typing import Optional, Union
import warnings


class LoadType(Enum):
    """
    Enum for specifying the type of data to load. Select between NODES (point cloud) and NODES_AND_FEATURES (mesh with edge features)
    """
    NODES = "nodes"
    NODES_AND_FEATURES = "nodes_and_features"


class FEMGraphDataset(Dataset):
    def __init__(self, base_dir : str, geometries : Optional[Union[str]]=None, timesteps : Optional[Union[int]] = [0, -1], load_type : LoadType=LoadType.NODES_AND_FEATURES, return_sim_id :bool = False):
        """
        FEMGraphDataset for loading FEM simulation data stored as point clouds and edge features.

        Args:
            base_dir (str): Path to the base dataset directory.
            geometries (list, optional): List of geometry IDs to load. Defaults to None (loads all geometries).
            timesteps (list, optional): List of timesteps expressed as integer. Also supports "-1" for last timestep.
            load_type (LoadType, optional): Enum specifying what data to load.
                                            Choices are NODES (only point clouds) or
                                            NODES_AND_FEATURES (point clouds and edge features).
                                            Defaults to LoadType.NODES_AND_FEATURES.
            return_sim_id (bool, optional): If True, returns the geometry simulation ID along with the data as metadata.
        """
        self.base_dir = base_dir
        self.geometries = geometries
        self.load_type = load_type
        self.timesteps = timesteps
        self.return_sim_id = return_sim_id

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
        """
        Returns a list of all geometry IDs in the dataset.
        
        Returns:
            list: List of geometry IDs.
        """
        return ['blank', 'binder', 'punch', 'die'] 
    
    def _geometries_with_features(self):
        """
        Returns a list of geometries that have edge features available.

        Returns:
            list: List of geometry IDs with available edge features.
        """
        return ["blank"]
    
    def _feature_ids(self):
        """
        Returns a list of feature IDs for the geometries with available edge features.

        Returns:
            list: List of feature IDs.
        """
        return ['mieses', 'strain', 'thickness']
    
    def _validate_inputs(self):
        """
        Validates the input arguments for the dataset.
        """
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
        
        # Validate timesteps
        if not isinstance(self.timesteps, list) or not all(isinstance(t, int) for t
                                                           in self.timesteps):
            raise ValueError(f"Invalid timesteps '{self.timesteps}'. Must be a list of integers.")
                
        # If the user wants to load features, at least select blank geometry
        if self.load_type == LoadType.NODES_AND_FEATURES and not any(geometry in self._geometries_with_features() for geometry in self.geometries):
            raise ValueError(f"Can not load features if not a geometry with features is selected. Please select one of: {self._geometries_with_features()}")


    def _load_metadata(self, metadata_path : str) -> pd.DataFrame:
        """
        Loads metadata from a file.

        Args:
            metadata_path (str): Path to the metadata file.
        
        Returns:
            pd.DataFrame: Metadata DataFrame.
        """
    
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at '{metadata_path}'.")

        metadata = pd.read_csv(metadata_path)

        if "id" not in metadata.columns:
            raise ValueError("Metadata file must contain an 'id' column.")
        
        return metadata

    def _validate_geometries(self):
        if not isinstance(self.geometries, list):
            raise TypeError("The argument geometries need to be of type list.")

        valid_part = self.get_all_parts()
        # Check if the selected geometry can be loaded.
        for geo in self.geometries:
            if geo not in valid_part:
                raise ValueError(f"The geometry {geo} is not supported. Please selected one of: {self.get_all_parts()}")

        # No duplicates are allowed in order to optimize memory usage.
        if len(set(self.geometries)) != len(self.geometries):
            raise ValueError("No duplicates allowed in geometry list.")

    def _build_data_paths(self):
        
        """Build a list of paths to data files for the specified geometries."""
        data_paths = []

        for sim_id in self.metadata['id']:

            pc_dir = os.path.join(self.base_dir, "pc", str(sim_id))
            ef_dir = os.path.join(self.base_dir, "ef", str(sim_id))

            # Validate geometry directories
            if not os.path.exists(pc_dir):
                raise FileNotFoundError(f"Point cloud directory '{pc_dir}' does not exist for simulation ID '{sim_id}'.")
            
            if self.load_type == LoadType.NODES_AND_FEATURES and not os.path.exists(ef_dir):
                raise FileNotFoundError(f"Edge feature directory '{ef_dir}' does not exist for simulation ID '{sim_id}'.")

            paths = {}
            for geometry in self.geometries:
                
                paths[geometry] = [None, None]
                
                # Gather all point cloud and edge feature files for this geometry
                pc_files = sorted([os.path.join(pc_dir, f) for f in os.listdir(pc_dir) if f.endswith(".npy") and f.startswith(geometry)])
                paths[geometry][0] = [pc_files[i] for i in self.timesteps]
                
                if geometry in self._geometries_with_features() and self.load_type == LoadType.NODES_AND_FEATURES:
                    ef_files = sorted([os.path.join(ef_dir, f) for f in os.listdir(ef_dir) if f.endswith(".npy") and f.startswith(geometry)])
                    
                    # Get the indices file
                    f_paths = [ef_files[0]]
                    features = []

                    for feature in self._feature_ids():
                        f_files = [f for f in ef_files if feature in f] 
                        features.extend([f_files[i] for i in self.timesteps])
                    
                    f_paths.extend(features)
                    paths[geometry][1] = f_paths

                
            data_paths.append(paths)
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
        data = self.data_paths[idx]
        metadata = self.metadata.iloc[idx].values

        if not self.return_sim_id:
            metadata = metadata[1:]

        # Load point cloud (nodes)
        pc_tensors = []
        ef_tensors = []
        node_indices = []
        n_timesteps = len(self.timesteps)

        # Iterate through the dictionary
        for geometry , (pc_paths, ef_paths) in data.items():
            # Convert point clouds and features to tensors
            pc_tensors.append(torch.tensor(np.stack([np.load(pc_path) for pc_path in pc_paths])))
            
            if geometry in self._geometries_with_features() and self.load_type == LoadType.NODES_AND_FEATURES:
                ef_tensors.append(np.load(ef_paths[0]))
                for t in range(1, +len(self.timesteps) +1, 1):
                    ef_tensors.append(np.concatenate([np.load(ef_path) for ef_path in ef_paths[t::n_timesteps]], axis=-1))
        
                node_indices = torch.tensor(ef_tensors[0], dtype=torch.int32)
                ef_tensors = torch.tensor(np.stack(ef_tensors[1:]))

        if self.load_type == LoadType.NODES:
            return (
                torch.tensor(metadata, dtype=torch.float32),
                pc_tensors)
        else:
            return (
                torch.tensor(metadata, dtype=torch.float32),
                pc_tensors,
                node_indices,
                ef_tensors)