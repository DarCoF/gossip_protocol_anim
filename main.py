import logging
from threads.thread_manager import ThreadManager
from parser.parser import parse_args


# Configure the root logger
logger = logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Parse arguments and seed system.
args = parse_args()


# pseudo code
# event loop

# loop trough list of infected nodes
# IDEA: maybe spin up a thread for each available node. Common data space is  queue of messages to process by the middleservice.

# Each thread
# for node_i contact middleware and select f (fanout) forwarding nodes (select susceptible nodes only)
# node_i create message packagef and synchronize in data space
# lower repetition count
# if repetition count == 0: change node state to removed and send update to middleware service

# Middlewware service instantiates new gossipers with msg and states and updates dictionary of gossipers (state and instance)
# while queue not empty of msgs:
# if source infected or removed: skip msg (it's been contacted by another node)
# else:
# access graph and return position of newly infected node
# update node state list
# instantiates new node with msg and state

# Time to update the anim




# Example usage:
gossiper_dict = {
    'node1': ('SUSCEPTIBLE', 'Hello World 1', 3, 5, 'state_file_1.json'),
    'node2': ('SUSCEPTIBLE', 'Hello World 2', 3, 5, 'state_file_2.json'),
    # Add more nodes as needed
}

thread_manager = ThreadManager(gossiper_dict)
thread_manager.start_event_loop()