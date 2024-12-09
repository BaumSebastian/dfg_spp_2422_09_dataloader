from lasso.dyna import D3plot, ArrayType, FilterType
from typing import Dict

def get_part_mapping(part: D3plot) -> Dict:
    """
    Get the mapping of part names to their corresponding ids.

    :part: the part with the names and their ids.
    :return: a dictionary mapping part names to their corresponding part ids.
    """
    if not isinstance(part, D3plot):
        raise TypeError()
        
    titles = part.arrays[ArrayType.part_titles]
    ids = part.arrays[ArrayType.part_titles_ids]

    # Clean the name and map the name to their ids
    clean_titles = map(lambda title: title.decode('utf8').strip(), titles)
    mappings = {title: id for title, id in zip(clean_titles, ids)}

    return mappings

def get_d3plot(file: str) -> D3plot:
    """
    Get the D3plot object from the file.

    :file: the path to the d3plot file.
    :return: the D3plot object.
    """