import threading
import logging
import json
import os


gossiper_states = ['SUSCEPTIBLE', 'INFECTED', 'REMOVED']

class Gossiper:
    def __init__(self, id: int, state: str, message: str, fanout: int , repetitions: int, state_file: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        self.state_file = state_file
        if os.path.exists(self.state_file) and os.path.getsize(self.state_file) > 0:
            self._load_state()
        else:
            self.id = id
            self.state = state
            self.message = message
            self.fanout = fanout
            self.repetitions = repetitions
            self._persist_state()
        
    def _load_state(self):
        """Load the gossiper's state from a file."""
        with self.lock:
            try:
                with open(self.state_file, 'r') as file:
                    data = json.load(file)
                    self.state = data['state']
                    self.message = data['message']
                    self.fanout = data['fanout']
                    self.repetitions = data['repetitions']
                self.logger.info(f"State loaded from {self.state_file}")
            except IOError as e:
                self.logger.error(f"Failed to load state: {e}")
    
    def _persist_state(self):
        """Save the gossiper's state to a file."""
        with self.lock:
            try:
                with open(self.state_file, 'w') as file:
                    json.dump({
                        'state': self.state,
                        'message': self.message,
                        'fanout': self.fanout,
                        'repetitions': self.repetitions
                    }, file)
                self.logger.info(f"State persisted to {self.state_file}")
            except IOError as e:
                self.logger.error(f"Failed to persist state: {e}")
    
    def _retrieve_fanout_nodes(self):
        """A simple method that contacts Middleservice and retrieves a set of susceptible nodes.
        """
        pass
    
    def _serialize(self, target_id):
        """Encapsulates a message with its corresponding source and target nodes.
        """
        return (self.message, self.id, target_id)

    def send_message(self, target_id):
        """Broadcasts the gossiper's message to a single node.
        """
        message = self._serialize(target_id)
        with self.lock:
            # Existing message sending logic goes here
            # After sending a message, persist the state
            self._persist_state()
            self.logger.info("Message sent and state persisted.")

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

    def run(self) -> None:
        """Main function to trigger gossiper function per event cycle.
        """
        fanout_node_ids = self._retrieve_fanout_nodes()

        for node in range(len(fanout_node_ids)):
            self.send_message(node)        
        
        self._lower_rep_count()

        if self.repetitions == 0:
            self.udpate_state(gossiper_states[2])