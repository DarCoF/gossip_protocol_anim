import argparse
import sys
import logging

# Configure the root logger
logger = logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def positive_integer(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue

def parse_args():
    parser = argparse.ArgumentParser(description="Select fanout and msg repetitions per node.")
    parser.add_argument("-n",
                        "--nodes",
                        required=True,
                        type=lambda fn: positive_integer(fn),
                        help="Number of nodes in the graph, V")
    parser.add_argument("-e",
                        "--edges",
                        required=True,
                        type=lambda fn: positive_integer(fn),
                        help="Number of edges in the graph, E.")
    parser.add_argument("-f",
                        "--fanout",
                        required=True,
                        type=lambda fn: positive_integer(fn),
                        help="Select fanout (number of forwarding nodes)")
    parser.add_argument("-r",
                        "--repetitions",
                        required=True,
                        type=lambda fn: positive_integer(fn),
                        help="Number of times the same message is sent by a single node.")
    
    # Parse arguments before further validation
    args = parser.parse_args()

    return args

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