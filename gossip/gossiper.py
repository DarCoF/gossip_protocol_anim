import threading
import logging
import json
import os


gossiper_states = ['SUSCEPTIBLE', 'INFECTED', 'REMOVED']

class Gossiper:
    def __init__(self, node_id: int, state: str, message: str, fanout: int , repetitions: int, state_filepath: str, msg_queue, middleware):
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.state_filepath = state_filepath
        self.msg_queue = msg_queue
        self.node_id = node_id
        self.state = state
        self.message = message
        self.fanout = fanout
        self.repetitions = repetitions
        self.middleware = middleware
    
    def _persist_state(self):
        """Save the gossiper's state to the state file."""
        with self.lock:  # Ensure thread-safe access to the state file
            try:
                # Load the current state from the file
                with open(self.state_filepath, 'r') as file:
                    state_file = json.load(file)
                
                # Update this gossiper's state
                state_file['gossipers'][str(self.node_id)] = {
                    'state': self.state,
                    'message': self.message,
                    'fanout': self.fanout,
                    'repetitions': self.repetitions
                }

                # Write the updated state back to the file
                with open(self.state_filepath, 'w') as file:
                    json.dump(state_file, file, indent=4)

                self.logger.info(f"State persisted to {self.state_filepath}")
            except IOError as e:
                self.logger.error(f"Failed to persist state: {e}")
    
    def _retrieve_fanout_nodes(self):
        """A simple method that contacts the middleware for a list of nodes."""
        try:
            return self.middleware.get_random_fanout(self.node_id)
        except Exception as e:
            self.logger.error(f"Failed to retrieve fanout nodes for node {self.node_id}: {e}")
            # Handle the exception, for example, by retrying or performing some fallback operation

    
    def _serialize(self, target_id):
        """Encapsulates a message with its corresponding source and target nodes.
        """
        return (self.message, self.node_id, target_id)

    def send_message(self, target_id):
        """Broadcasts the gossiper's message to a single node.
        """
        message = self._serialize(target_id)
        with self.lock:
            # Existing message sending logic goes here
            # After sending a message, persist the state
            self.msg_queue.put(message)
            self._persist_state()
        self.logger.info(f"Gossiper {self.node_id} added message to queue and persisted state")

    def udpate_state(self, new_state):
        """Swaps node state from the list of potential states under two conditions:
        - Node instantiated -> susceptible to infected
        - Node out of repetitions -> infected to removed
        """
        if self.repetitions == 0 and self.state == gossiper_states[1]:
            self.state = new_state        
        with self.lock:
            # Existing state updating logic goes here
            # After updating the state, persist the state
            self._persist_state()
            self.logger.info("State updated.")

    def _lower_rep_count(self):
        """Lower repetition count by 1 after each event cycle down until reaching 0.
        """
        if self.lock:
            if self.state == gossiper_states[1] and self.repetitions > 0:
                self.repetitions -= 1

        with self.lock:
            # Existing repetition lowering logic goes here
            # After lowering the count, persist the state
            self._persist_state()
            self.logger.info("Repetition count lowered.")

    def run(self):
        """Main function to trigger gossiper function per event cycle.
        """
        fanout_node_ids = self._retrieve_fanout_nodes()

        for node in range(len(fanout_node_ids)):
            self.send_message(node)        
        
        self._lower_rep_count()

        if self.repetitions == 0:
            self.udpate_state(gossiper_states[2])
        
        self.logger.info(f"Gossiper {self.node_id} finished running")