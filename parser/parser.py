import argparse

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