import threading
import logging
import json
import os
import traceback
import tempfile


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
        """Save the gossiper's state to the state file in an atomic way."""
        self.lock.acquire()
        try:
            # Read the existing state if the file isn't empty
            if os.path.exists(self.state_filepath) and os.path.getsize(self.state_filepath) > 0:
                with open(self.state_filepath, 'r') as file:
                    state_file = json.load(file)
            else:
                state_file = {'gossipers': {}}

            # Update this gossiper's state
            state_file['gossipers'][str(self.node_id)] = {
                'state': self.state,
                'message': self.message,
                'fanout': self.fanout,
                'repetitions': self.repetitions
            }

            # Write the updated state to a temporary file
            fd, temp_file_path = tempfile.mkstemp(dir=os.path.dirname(self.state_filepath))
            with os.fdopen(fd, 'w') as temp_file:
                json.dump(state_file, temp_file, indent=4)

            # Atomically rename the temporary file to the original filename
            os.replace(temp_file_path, self.state_filepath)

            self.logger.info(f"State persisted to {self.state_filepath}")

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error while reading state file: {e}")
        except IOError as e:
            self.logger.error(f"IO error while accessing state file: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while persisting state: {e}")
        finally:
            self.lock.release()

    def _retrieve_fanout_nodes(self):
        """A simple method that contacts the middleware for a list of nodes."""
        try:
            return self.middleware.get_random_fanout(source_node_id = int(self.node_id))
        except Exception as e:
            self.logger.error(f"Failed to retrieve fanout nodes for node {self.node_id}: {e}")
            self.logger.error(traceback.format_exc()) 
            # Handle the exception, for example, by retrying or performing some fallback operation

    
    def _serialize(self, target_id):
        """Encapsulates a message with its corresponding source and target nodes.
        """
        return (self.message, self.node_id, target_id)

    def send_message(self, target_id):
        """Broadcasts the gossiper's message to a single node.
        """
        message = self._serialize(target_id)
        self.lock.acquire()
        try:
            # Existing message sending logic goes here
            # After sending a message, persist the state
            self.msg_queue.put(message)
        finally:
            self.lock.release()
        self.logger.info(f"Gossiper {self.node_id} sent message to {target_id} and added it to queue")

    def udpate_state(self, new_state):
        """Swaps node state from the list of potential states under two conditions:
        - Node instantiated -> susceptible to infected
        - Node out of repetitions -> infected to removed
        """
        if self.repetitions == 0 and self.state == gossiper_states[1]:
            self.state = new_state

    def _lower_rep_count(self):
        """Lower repetition count by 1 after each event cycle down until reaching 0.
        """
        if self.state == gossiper_states[1] and self.repetitions > 0:
            self.repetitions -= 1
            self.logger.info("Repetition count lowered.")

    def run(self):
        """Main function to trigger gossiper function per event cycle.
        """
        fanout_node_ids = self._retrieve_fanout_nodes()

        print(f'-----------------FANOUT NODES: {fanout_node_ids}---------------')

        for node in fanout_node_ids:
            self.send_message(node)        
        
        self._lower_rep_count()

        if self.repetitions == 0:
            self.udpate_state(gossiper_states[2])

        self._persist_state()

        return self.logger.info(f"Gossiper {self.node_id} finished running")