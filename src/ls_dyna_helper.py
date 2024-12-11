from lasso.dyna import D3plot, ArrayType, FilterType
from typing import Dict
from pathlib import Path
import numpy as np

def get_part_mapping(d3plot: D3plot) -> Dict:
    """
    Get the mapping of part names to their corresponding ids.

    :d3plot: the d3plot with the names and their ids.
    :return: a dictionary mapping part names to their corresponding part ids.
    """
    if not isinstance(d3plot, D3plot):
        raise TypeError()
        
    titles = d3plot.arrays[ArrayType.part_titles]
    ids = d3plot.arrays[ArrayType.part_titles_ids]

    # Clean the name and map the name to their ids
    clean_titles = map(lambda title: title.decode('utf8').strip(), titles)
    mappings = {title: id for title, id in zip(clean_titles, ids)}

    return mappings

def _get_d3plot(file: str, state_array_filter, state_filter) -> D3plot:
    """
    Get the D3plot object from the file.

    :file: the path to the d3plot file.
    :return: the D3plot object.
    """

    if not Path.is_file(file):
        raise FileNotFoundError()

    d3plot = D3plot(str(file),
                    state_array_filter=state_array_filter,
                    state_filter=state_filter,
                    buffered_reading=True)