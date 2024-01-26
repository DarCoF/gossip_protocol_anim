import threading
import time
from gossip.gossiper import Gossiper
import logging



def thread_function(node_id, gossiper_params, message_queue):
    logging.info(f"Thread {node_id} started")
    gossiper = Gossiper(*gossiper_params, message_queue, node_id)
    gossiper.run()
    logging.info(f"Thread {node_id} finished")

class ThreadManager:
    def __init__(self, gossiper_dict, message_queue):
        self.gossiper_dict = gossiper_dict
        self.logger = logging.getLogger('ThreadManager')
        self.msg_queue = message_queue

    def start_event_loop(self):
        self.logger.info("Starting event loop")
        try:
            while True:
                threads = []
                for node_id, gossiper_params in self.gossiper_dict.items():
                    thread = threading.Thread(target=thread_function, args=(node_id, gossiper_params, self.msg_queue))
                    thread.start()
                    threads.append(thread)
                    self.logger.info(f"Thread {thread.name} for node {node_id} started")

                # Wait for all threads to complete before starting the next event cycle
                for thread in threads:
                    thread.join()
                    self.logger.info(f"Thread {thread.name} joined")

                # Sleep for a bit before starting the next event cycle to simulate time between cycles
                time.sleep(1)  # Sleep time could be adjusted as needed

                self.logger.info("Event cycle completed, starting next cycle after delay")

        except KeyboardInterrupt:
            self.logger.info("Event loop stopped by user")
        
        self.logger.info("Event loop terminated")