
import numpy as np


def ordered_list_from_dict(input_dict):
    # Sort the dictionary keys, which are strings but represent integers
    sorted_node_ids = sorted(input_dict.keys(), key=int)
    
    # Create a list of 'state' values ordered by node_id
    ordered_status = [input_dict[node_id]['state'] for node_id in sorted_node_ids]
    
    return ordered_status


def ndarray_to_list(obj):
    """
    Recursively convert ndarray objects in the given structure to lists.
    This function is intended to be used with json.dumps.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [ndarray_to_list(v) for v in obj]
    else:
        return obj