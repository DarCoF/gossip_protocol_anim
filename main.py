import logging
from threads.thread_manager import ThreadManager
from parser.parser import parse_args
from gossip.gossiper import Gossiper
from middleware.p2p_service import *
from anim.proyectile import Projectile
from anim.graph_anim import Graph2D
import random
from manim import *
from middleware.p2p_service import P2PService
from utils.utils import ordered_list_from_dict
import queue
import time

# Some render configs
config.pixel_height = 1080  # Set the pixel height of the output video 2160
config.pixel_width = 1920  # Set the pixel width of the output video 3840
config.media_dir = "F:\\TheRabbitHole\\VlogDeUnNerd\\animations-code\\video-15"
config.disable_caching = True

# Configure the root logger
logger = logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Parse arguments and seed system.
args = parse_args()

message_queue = queue.Queue()

# Helper function
def is_susceptible(node_status):
    if 'SUSCEPTIBLE' in node_status:
        return True
    else:
        return False

if __name__ == "__main__":
    # Instantiate starting graph
    graph = Graph2D(args.nodes, args.edges)
    # Bring middleware alive! Wake up princess.
    middleservice = P2PService(graph=graph, filepath='./', message_queue=message_queue)
    # Instantiate original gossiper
    message = 'Pim!!!'
    seed = Gossiper(node_id= random.choice(graph.node_ids), message=message, fanout=args.fanout, repetitions=args.repetitions)
    # Draw starting graph
    graph.construct()
    # State file persisted by OG gossiper. Dump to dict and pass to redraw graph
    middleservice.update()
    # Update graph with original gossiper
    graph.update_node_status(ordered_list_from_dict(middleservice.state_file['gossipers']))
    # Redraw graph
    graph.construct()

    # Start event loop -> GOSSIP PROTOCOL starts here!!!

    while is_susceptible(graph.node_status):
        # Bring threadmanager
        thread_manager = ThreadManager(middleservice.state_file['gossipers'], middleservice.state_file_path, message_queue)
        thread_manager.start_event_loop()

        time.sleep(2)

        middleservice.read_queue()

        node_status_i = ordered_list_from_dict(middleservice.state_file['gossipers'])

        # Update graph
        graph.update_node_status(node_status_i)
        graph.construct()
    

    graph.render(preview=True)