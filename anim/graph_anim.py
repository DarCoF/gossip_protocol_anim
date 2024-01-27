import os
import sys


current_script_path = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.abspath(os.path.join(current_script_path, ".."))  # Go up one level
sys.path.append(root_directory)

from manim import *
from manim.utils.utils import slides_text
from graph.graph import RandomGraph
import logging

def is_subset(list_to_check, predefined_values):
    return set(list_to_check).issubset(set(predefined_values))


def diff_arrays(list1, list2):
    if len(list1) != len(list2):
        raise ValueError("Both lists must be of the same length")

    return [1 if list1[i] != list2[i] else 0 for i in range(len(list1))]


NODE_STATUS = {1: 'SUSCEPTIBLE', 2: 'INFECTED', 3: 'REMOVED'}
class Node(Circle):
    def __init__(self,
        radius: float = 0.06,
        fill_color: Color = ORANGE,
        fill_opacity: float = 0.65,
        stroke_color: Color = "#B03608",
        stroke_width: float = 1,
        stroke_opacity: float = 1,
        label: str = '') -> None:

        super().__init__(radius=radius, fill_color=fill_color, fill_opacity=fill_opacity, 
                         stroke_color=stroke_color, stroke_width=stroke_width, stroke_opacity=stroke_opacity)


        self.label = slides_text(label, font_size=12)
        self.label.next_to(self, UP, buff=0.5)


class Graph2D(Scene):

    def __init__(self,
        n_nodes: int, 
        n_edges: int, 
        is_directed: bool = False
        ):
        
        super().__init__()

        self._n_nodes = n_nodes
        self._n_edges = n_edges
        self.random_graph = RandomGraph(n_nodes, n_edges, is_directed)
        self.adjacency_list = self.random_graph.adjacency_list
        self.logger = logging.getLogger(__name__)

        if len(self.random_graph.get_nodes) > 0:
            self.node_status: list[str] = [NODE_STATUS[1] for _ in range(len(self.random_graph.get_nodes))]
            self.node_coordinates: dict = self.random_graph.random_layout(dim=3)
            self.node_ids : list[int] = [key for key in self.node_coordinates.keys()]
        else:
            raise ValueError('Number of nodes in graph must be at least 1. Please provide a different value for n_nodes')        
        self.queue = []
        self.nodes_2s: list[VMobject] = []
        
        self.is_new_graph = True
        self.is_first = True
    
    def draw_initial_map(self):
        # Create as many nodes objects as nodes are in random_graph
        for node_id in self.node_ids:
            node = Node(label=str(node_id))
            node.set_x(0)
            node.set_y(0)
            self.nodes_2s.append(node)

        # Animate the node spheres. At the beginning of the anim they appear in the origin and each move concurrently to their respective positions.
        print(self.node_coordinates[0][0], self.nodes_2s[0])
        animations = [self.nodes_2s[node].animate.move_to(self.node_coordinates[node]) for node in self.node_ids]
       
        self.play(AnimationGroup(*animations))
        self.wait(1)
            
    def _update_graph(self):
        cache_nodes = ['SUSCEPTIBLE' for _ in range(len(self.random_graph.get_nodes))]
        # Draw a map
        def redraw_map():
            nonlocal cache_nodes
            self.logger.info(f"Start updating nodes. Chill...")
            node_animation = []
            diff_nodes = diff_arrays(self.node_status, cache_nodes) # Mask function -> Compares two lists of str and returns a binary list
            for i, mask in zip(self.node_ids, diff_nodes):
                if mask == 1:
                    if cache_nodes[i] == NODE_STATUS[1]:
                        node_animation.append(self.nodes_2s[i].animate.set_style(fill_color=GREEN, fill_opacity=0.65, stroke_color ="#013220" , stroke_opacity=1))
                    else: 
                        node_animation.append(self.nodes_2s[i].animate.set_style(fill_color=GREY, fill_opacity=0.65, stroke_color = "#343d46", stroke_opacity = 1))
            self.play(AnimationGroup(*node_animation))
            cache_nodes = self.node_status.copy()
            self.logger.info(f"Finish updating nodes!")   
        return redraw_map

    def update_node_status(self, update_node_status: list = []):        
        if is_subset(update_node_status, ['SUSCEPTIBLE', 'INFECTED', 'REMOVED']) and len(update_node_status) == len(self.node_status):
            self.node_status = update_node_status
        else:
            raise ValueError('Updated node status list lenght does not match current node status lenght')

    def construct(self):
        # Create initial map
        if self.is_new_graph:
            self.draw_initial_map()
            self.is_new_graph = False
        else:
            if self.is_first:
                self.redraw = self._update_graph()
                self.redraw()
                self.is_first = False
                self.wait(2)
            else:
                self.redraw()
                self.wait(2)



if __name__ == "__main__":
    config.pixel_height = 1080  # Set the pixel height of the output video 2160
    config.pixel_width = 1920  # Set the pixel width of the output video 3840
    config.media_dir = "F:\\TheRabbitHole\\VlogDeUnNerd\\animations-code\\video-15"
    config.disable_caching = True
    nodes = 200
    edges = 400
    print('Number of nodes {} and number of edges {}'.format(nodes, edges))
    scene = Graph2D(n_nodes=nodes, n_edges=edges, is_directed=False)
    scene.construct()

    node_status = scene.node_status
    node_status[0] = 'INFECTED'
    node_status[7] = 'INFECTED'
    node_status[15] = 'INFECTED'
    node_status[20] = 'INFECTED'
    node_status[100] = 'INFECTED'
    node_status[23] = 'INFECTED'
    node_status[199] = 'INFECTED'
    node_status[10] = 'INFECTED'
    node_status[63] = 'INFECTED'
    node_status[150] = 'INFECTED'

    scene.update_node_status(node_status)
    scene.construct()

    node_status = scene.node_status
    node_status[10] = 'REMOVED'
    node_status[63] = 'REMOVED'
    node_status[150] = 'REMOVED'

    scene.update_node_status(node_status)
    scene.construct()

    scene.render(preview=True)
