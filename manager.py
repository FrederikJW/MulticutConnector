import threading
import time

from graph import GraphFactory
from solver import ShortestPathSolver
from utils import generate_distinct_colors

# use a transaction lock to prevent drawing if the graph is changed
drawing_lock = threading.Lock()


class Manager:
    # class which manages everything
    def __init__(self):
        # run visualizer in new thread
        self.visualizer = None
        self.visualization_thread = threading.Thread(target=self.run_visualizer)

    def run(self):
        self.visualization_thread.start()

        graph = GraphFactory.generate_grid((100, 100))

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        search_graph = GraphFactory.generate_grid_search_graph(graph)
        solver = ShortestPathSolver(search_graph)
        components = solver.solve()
        node_to_value = {node: solver.get_lowest_cost_predecessor(node)[1] for node in search_graph.nodes}
        search_graph.load_value(node_to_value, "cost")
        colors = set(generate_distinct_colors(len(components)))
        component_to_color = dict(enumerate(colors))
        node_to_color = {}

        if len(colors) >= len(components):
            for component_id, component in components.items():
                for node in component:
                    node_to_color[node] = component_to_color[component_id]

        time.sleep(10)

        self.visualizer.set_graph(search_graph)
        self.visualizer.set_colors(node_to_color)

        while self.visualization_thread.is_alive():
            time.sleep(5)

    def run_visualizer(self):
        # pygame should be imported only in the new thread and not in the main thread
        # therefore the visualizer must be imported here

        from visualizer import Visualizer
        self.visualizer = Visualizer(drawing_lock)
        self.visualizer.run()
