import os


def load_json():
    pass
class P2PService:
    def __init__(self, graph, filepath, message_queue) -> None:
        self.adjacency_list = graph.adjacency_list
        self.node_coordinates = graph.node_coordinates
        self.node_ids = graph.node_ids
        self.state_file_path = filepath
        self.state_file = {}
        self.message_queue = message_queue
        if not os.path.exists(self.state_file_path) or not os.path.getsize(self.state_file_path) > 0:
            self._create_state_file() 
  
    def _create_state_file(self):
        """Creates original state file and loads it as dict.
        """
        pass

    def _update_state_file(self):
        pass

    def update(self):
        pass

    def get_random_fanout(self):
        pass

    def _deserialize_message(self):
        pass
    
    def read_queue(self):
        pass

