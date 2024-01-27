

def ordered_list_from_dict(input_dict):
    # Sort the dictionary keys, which are strings but represent integers
    sorted_node_ids = sorted(input_dict.keys(), key=int)
    
    # Create a list of 'state' values ordered by node_id
    ordered_status = [input_dict[node_id]['state'] for node_id in sorted_node_ids]
    
    return ordered_status