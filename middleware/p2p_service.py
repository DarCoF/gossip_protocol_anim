import os
import json
import sys
import logging
import random
from threading import Lock
import time
from threading import Semaphore

current_script_path = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.abspath(os.path.join(current_script_path, ".."))  # Go up one level
sys.path.append(root_directory)

from anim.graph_anim import Graph2D
from utils.utils import ndarray_to_list

class P2PService:
    def __init__(self, graph, filepath, message_queue, *args) -> None:
        self.adjacency_list = graph.adjacency_list
        self.node_coordinates = graph.node_coordinates
        self.node_ids = graph.node_ids
        self.state_file_path = filepath
        self.fanout = 3
        self.repetitions = 4
        self._state_file_lock = Lock()
        self._semaphore = Semaphore()
        self.message_queue = message_queue
        if not os.path.exists(self.state_file_path) or not os.path.getsize(self.state_file_path) > 0:
            self._create_state_file() 
            self.state_file = self._load_state_file()
  
    def _create_state_file(self):
        """Creates original state file and loads it as dict.
        """
        # Initialize the gossipers section with default data for each node
        gossipers = {str(node_id): {'state': 'SUSCEPTIBLE',
                                    'message': '',
                                    'fanout': self.fanout,
                                    'repetitions': self.repetitions}
                     for node_id in self.node_ids}
        node_coordinates = ndarray_to_list(self.node_coordinates)
        self.state_file = {
            'gossipers': gossipers,  # Initialize as empty, not clear how it should be populated
            'coordinates': node_coordinates,  # Use the coordinates from the constructor
            'adjacency_list': self.adjacency_list  # Use the adjacency list from the constructor
        }
        # Write the state file to the specified path
        with open(self.state_file_path, 'w') as f:
            json.dump(self.state_file, f, indent=4)

    def _load_state_file(self):
        # Load the state file into the instance attribute
        with open(self.state_file_path, 'r') as f:
            return json.load(f)
    
    def update_state_file(self, target_node_id: int, payload: str):
        """Updates the state_file based on the target_node_id."""
        with self._state_file_lock:
            node_id_str = str(target_node_id)  # Ensure the node ID is a string for JSON keys
            if node_id_str not in self.state_file['gossipers']:
                # Initialize the gossiper state if it doesn't exist
                self.state_file['gossipers'][node_id_str] = {
                    'state': 'SUSCEPTIBLE',
                    'message': '',
                    'fanout': self.fanout,
                    'repetitions': self.repetitions
                }
            # Update the message for the gossiper
            self.state_file['gossipers'][node_id_str]['message'] = payload
            self.state_file['gossipers'][node_id_str]['state'] = 'INFECTED'
        
        # Write the updated state file to the specified path
        with open(self.state_file_path, 'w') as f:
            json.dump(self.state_file, f, indent=4)

    def get_random_fanout(self, source_node_id: int):
        """Returns a list of nodes that are in the SUSCEPTIBLE state and can be reached from the source node."""
        with self._semaphore:
            
            # Get the neighbors of the source node from the adjacency list
            neighbors = self.adjacency_list.get(source_node_id, [])
            
            # Filter the neighbors to include only those in SUSCEPTIBLE state
            susceptible_neighbors = [node for node in neighbors if self.state_file['gossipers'].get(str(node), {}).get('state') == 'SUSCEPTIBLE']
            
            # Determine the number of nodes to sample
            num_to_sample = min(len(susceptible_neighbors), self.fanout)
            
            # Randomly select nodes from the susceptible neighbors
            selected_nodes = random.sample(susceptible_neighbors, num_to_sample) if susceptible_neighbors else []
            
            return selected_nodes

    def _deserialize_message(self, payload: str):
        """Unpacks the message structure and returns its components."""
        message, source_node_id, target_node_id = payload
        return message, source_node_id, target_node_id
    
    def read_queue(self, min_messages = 5, timeout = 10):
        """Reads messages from the queue and processes them, waits for the queue to have at least min_messages or until timeout."""
        start_time = time.time()
        while True:
            # Check if the queue has enough messages
            if self.message_queue.qsize() >= min_messages:
                break
            # Check if the timeout has been reached
            if time.time() - start_time > timeout:
                logging.warning(f"Timeout reached waiting for messages. Proceeding with {self.message_queue.qsize()} messages.")
                break            
            # Wait a bit before checking again
            time.sleep(0.1)  # Sleep for 100ms

        while not self.message_queue.empty():
            try:
                # Get the next message from the queue
                message_data = self.message_queue.get_nowait()
                
                # Deserialize the message
                message, source_node_id, target_node_id = self._deserialize_message(message_data)
                
                # Update the state file based on the target node_id
                self.update_state_file(target_node_id, message)
            except self.message_queue.Empty:
                break  # Exit if the queue is empty
            except Exception as e:
                # Print the error message and exit
                logging.error(f"Error processing message: {e}")



graph = Graph2D(300, 5000)

middleman = P2PService(graph, 'F:\\TheRabbitHole\\VlogDeUnNerd\\Video-15\\animations-code\\state_file', 0)
print(middleman.state_file_path)
print(middleman.state_file)