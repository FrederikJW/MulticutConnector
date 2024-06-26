import sys
import threading
import time
import csv
import matplotlib.pyplot as plt
import pandas as pd

import networkx as nx

from graph import GraphFactory
from solver import ShortestPathSolver
from utils import generate_distinct_colors

sys.path.append("C:/Users/FreBe/projects/ShortestPathMulticut/build/Release")
import spm_solver

sys.path.append("C:/Users/FreBe/projects/EdgeContractionMulticut/build/Release")
from edge_contraction_solver import EdgeContractionSolver

# use a transaction lock to prevent drawing if the graph is changed
drawing_lock = threading.Lock()


class Manager:
    # class which manages everything
    def __init__(self):
        # run visualizer in new thread
        self.visualizer = None
        self.visualization_thread = threading.Thread(target=self.run_visualizer)

    def play_history_shortest_path(self):
        self.visualization_thread.start()
        while self.visualizer is None:
            time.sleep(1)

        graph = GraphFactory.read_slice_from_snemi3d(3)
        self.visualizer.set_graph(graph)
        solver = spm_solver.Solver()
        solver.activate_track_history()
        solver.load_graph(*(graph.export()))
        nodes, edges, components, node_to_predecessor = solver.get_state()
        graph = GraphFactory.construct_from_values(nodes, edges)
        self.visualizer.set_graph(graph)

        input("waiting for input")

        self.visualizer.set_history_file("histories\\snemi\\slice3\\shortest_path.txt", 1)

    def play_history_edge_contraction(self):
        self.visualization_thread.start()
        while self.visualizer is None:
            time.sleep(1)

        graph = GraphFactory.generate_bad_example()
        self.visualizer.set_graph(graph)

        input("Waiting for input")

        self.visualizer.set_history_file("histories\\bad_example\\greedy_joining.txt", 2, 0.01)

    def multithreading_test(self):
        self.visualization_thread.start()
        while self.visualizer is None:
            time.sleep(1)

        graph = GraphFactory.read_slice_from_snemi3d(3)
        # graph = GraphFactory.generate_grid((30, 30))
        self.visualizer.set_graph(graph)
        solver = spm_solver.Solver()
        solver.activate_track_history()
        solver.load_graph(*(graph.export()))
        nodes, edges, components, node_to_predecessor = solver.get_state()

        graph = GraphFactory.construct_from_values(nodes, edges)
        self.visualizer.set_graph(graph)
        print("start solving")
        solver_thread = threading.Thread(target=solver.solve)
        solver_thread.start()

        # self.visualizer.set_history_getter(solver.get_history)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def test(self):
        self.visualization_thread.start()
        while self.visualizer is None:
            time.sleep(1)

        graph = GraphFactory.read_slice_from_snemi3d(3)
        # graph = GraphFactory.generate_grid((5, 5))
        self.visualizer.set_graph(graph)

        solver = spm_solver.Solver()
        solver.activate_track_history()
        solver.load_graph(*(graph.export()))
        nodes, edges, components, node_to_predecessor = solver.get_state()

        graph = GraphFactory.construct_from_values(nodes, edges)
        self.visualizer.set_graph(graph)
        print("finished")
        while self.visualization_thread.is_alive():
            time.sleep(1)

    def greedy_additive_edge_contraction_test(self):
        multicut, _ = greedyAdditiveEdgeContraction(6, [(0, 1, 5), (0, 3, -20), (1, 2, 5), (1, 4, 5), (2, 5, -20), (3, 4, 5), (4, 5, 5)])
        print("result:")
        print([edge_id for edge_id in multicut])

    def run_andres_edge_contraction_solver(self):
        self.visualization_thread.start()

        # graph = GraphFactory.generate_grid((50, 50))
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        multicut, elapsed = greedyAdditiveEdgeContraction(*(graph.standard_export()))

        print("execution Time: ", elapsed, "ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def edge_contraction_eval_plot(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "maximum_matching_with_cutoff",
            "greedy_matchings_edge_contraction"
        ]

        solving_method_verbose = {
            "largest_positive_cost_edge_contraction": "Greedy Additive",
            "spanning_tree_edge_contraction": "Maximum Spanning Tree",
            "maximum_matching": "Maximum Matching",
            "maximum_matching_with_cutoff": "Maximum Matching with cutoff",
            "greedy_matchings_edge_contraction": "Greedy Matching"
        }

        time_data_dict = {}
        score_data_dict = {}

        for solving_method_name in solving_method_names:

            # Load the CSV file
            file_path = f'benchmark/snemi/{solving_method_name}.csv'
            data = pd.read_csv(file_path)

            time_data_dict[solving_method_verbose[solving_method_name]] = data['time']
            score_data_dict[solving_method_verbose[solving_method_name]] = data['score']

        time_data = pd.DataFrame(time_data_dict)
        score_data = pd.DataFrame(score_data_dict)
        positions = list(range(1, len(solving_method_names) + 1))

        fig, ax = plt.subplots(1, 2, figsize=(10, 6))

        # Box Plot 1: Time
        ax[0].boxplot(time_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
        ax[0].set_xticks(positions)
        ax[0].set_xticklabels(time_data_dict.keys())
        ax[0].set_title('Comparison of Time Distributions')
        ax[0].set_xlabel('Algorithm')
        ax[0].set_ylabel('Milliseconds')
        ax[0].grid(True)

        # Box Plot 2: Score
        ax[1].boxplot(score_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
        ax[1].set_xticks(positions)
        ax[1].set_xticklabels(time_data_dict.keys())
        ax[1].set_title('Comparison of Score Distributions')
        ax[1].set_xlabel('Algorithm')
        ax[1].set_ylabel('Value')
        ax[1].grid(True)

        plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.setp(ax[1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Adjust layout to not overlap
        plt.tight_layout()

        # Show the plots
        plt.show()

    def edge_contraction_eval_plot_on_correlation(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "maximum_matching_with_cutoff",
            "greedy_matchings_edge_contraction"
        ]

        solving_method_verbose = {
            "largest_positive_cost_edge_contraction": "Greedy Additive",
            "spanning_tree_edge_contraction": "Maximum Spanning Tree",
            "maximum_matching": "Maximum Matching",
            "maximum_matching_with_cutoff": "Maximum Matching with cutoff",
            "greedy_matchings_edge_contraction": "Greedy Matching"
        }

        file_names = {
            "corr40": list(map(str, range(1, 11))),
            "corr60": list(map(str, range(1, 11))),
            "corr80": list(map(str, range(1, 11))),
        }

        for file_name in file_names:

            time_data_dict = {}
            score_data_dict = {}

            for solving_method_name in solving_method_names:

                # Load the CSV file
                file_path = f'benchmark\\correlation\\{solving_method_name}-{file_name}.csv'
                data = pd.read_csv(file_path)

                time_data_dict[solving_method_verbose[solving_method_name]] = data['time']
                score_data_dict[solving_method_verbose[solving_method_name]] = data['score']

            time_data = pd.DataFrame(time_data_dict)
            score_data = pd.DataFrame(score_data_dict)
            positions = list(range(1, len(solving_method_names) + 1))

            fig, ax = plt.subplots(1, 2, figsize=(10, 6))

            # Box Plot 1: Time
            ax[0].boxplot(time_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
            ax[0].set_xticks(positions)
            ax[0].set_xticklabels(time_data_dict.keys())
            ax[0].set_title('Comparison of Time Distributions')
            ax[0].set_xlabel('Algorithm')
            ax[0].set_ylabel('Milliseconds')
            ax[0].grid(True)

            # Box Plot 2: Score
            ax[1].boxplot(score_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
            ax[1].set_xticks(positions)
            ax[1].set_xticklabels(time_data_dict.keys())
            ax[1].set_title('Comparison of Score Distributions')
            ax[1].set_xlabel('Algorithm')
            ax[1].set_ylabel('Value')
            ax[1].grid(True)

            plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            plt.setp(ax[1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

            fig.suptitle(f"Comparison on {file_name}")

            # Adjust layout to not overlap
            plt.tight_layout()

            # Show the plots
            plt.show()

    def edge_contraction_eval_plot_on_random(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "maximum_matching_with_cutoff",
            "greedy_matchings_edge_contraction"
        ]

        solving_method_verbose = {
            "largest_positive_cost_edge_contraction": "Greedy Additive",
            "spanning_tree_edge_contraction": "Maximum Spanning Tree",
            "maximum_matching": "Maximum Matching",
            "maximum_matching_with_cutoff": "Maximum Matching with cutoff",
            "greedy_matchings_edge_contraction": "Greedy Matching"
        }

        file_names = {
            "p500-5": list(map(str, range(1, 11))),
            "p500-100": list(map(str, range(1, 11))),
            "p1000": list(map(str, range(1, 6))),
            "p1500": list(map(str, range(1, 6))),
            "p2000": list(map(str, range(1, 6))),
        }

        for file_name in file_names:

            time_data_dict = {}
            score_data_dict = {}

            for solving_method_name in solving_method_names:

                # Load the CSV file
                file_path = f'benchmark\\random\\{solving_method_name}-{file_name}.csv'
                data = pd.read_csv(file_path)

                time_data_dict[solving_method_verbose[solving_method_name]] = data['time']
                score_data_dict[solving_method_verbose[solving_method_name]] = data['score']

            time_data = pd.DataFrame(time_data_dict)
            score_data = pd.DataFrame(score_data_dict)
            positions = list(range(1, len(solving_method_names) + 1))

            fig, ax = plt.subplots(1, 2, figsize=(10, 6))

            # Box Plot 1: Time
            ax[0].boxplot(time_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
            ax[0].set_xticks(positions)
            ax[0].set_xticklabels(time_data_dict.keys())
            ax[0].set_title('Comparison of Time Distributions')
            ax[0].set_xlabel('Algorithm')
            ax[0].set_ylabel('Milliseconds')
            ax[0].grid(True)

            # Box Plot 2: Score
            ax[1].boxplot(score_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
            ax[1].set_xticks(positions)
            ax[1].set_xticklabels(time_data_dict.keys())
            ax[1].set_title('Comparison of Score Distributions')
            ax[1].set_xlabel('Algorithm')
            ax[1].set_ylabel('Value')
            ax[1].grid(True)

            plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            plt.setp(ax[1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

            fig.suptitle(f"Comparison on {file_name}")

            # Adjust layout to not overlap
            plt.tight_layout()

            # Show the plots
            plt.show()

    def edge_contraction_iterations_plot(self):
        files = [
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "greedy_matchings_edge_contraction"
        ]

        fig, ax = plt.subplots(1, len(files), figsize=(10, 6))

        for i in range(len(files)):
            solving_method_name = files[i]
            file_path = f'benchmark/snemi/{solving_method_name}_contractions.csv'

            # Reload the CSV, assuming no header and filling missing values directly
            data = pd.read_csv(file_path, header=None, na_filter=False, on_bad_lines='skip')

            # Replace non-numeric values (including empty strings) with zero
            data = data.apply(pd.to_numeric, errors='coerce').fillna(0)

            # Calculate the number of non-zero values per row
            num_values_per_row = data.apply(lambda row: (row != 0).sum(), axis=1)[1:]

            # Generate the boxplot for the number of non-zero values per row
            ax[i].boxplot(num_values_per_row, vert=True, patch_artist=True)
            ax[i].set_title(solving_method_name)
            ax[i].set_ylabel('Number of Iterations')

        # Display the boxplot
        plt.show()

    def edge_contraction_contractions_plot(self):
        files = [
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "greedy_matchings_edge_contraction"
        ]

        fig, ax = plt.subplots(1, len(files), figsize=(10, 6))

        for i in range(len(files)):
            solving_method_name = files[i]
            file_path = f'benchmark/snemi/{solving_method_name}_contractions.csv'

            # Reload the CSV, assuming no header and filling missing values directly
            data = pd.read_csv(file_path, header=None, na_filter=False, on_bad_lines='skip')

            # Replace non-numeric values (including empty strings) with zero
            data = data.apply(pd.to_numeric, errors='coerce').fillna(0)

            # Each row will be plotted as a separate series
            for index, row in data.iterrows():
                ax[i].plot(row.index + 1, row, marker='o', linestyle='-')

            ax[i].set_title(solving_method_name)
            ax[i].set_xlabel('Iteration')
            ax[i].set_ylabel('Number of Contractions')
            ax[i].set_yscale('log')
            if i > 0:
                ax[i].set_xscale('log')

        # Show the plot
        plt.show()

    def edge_contraction_contractions_plot_on_correlation(self):
        files = [
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "greedy_matchings_edge_contraction"
        ]

        file_names = {
            "corr40": list(map(str, range(1, 11))),
            "corr60": list(map(str, range(1, 11))),
            "corr80": list(map(str, range(1, 11))),
        }

        for file_name in file_names:
            fig, ax = plt.subplots(1, len(files), figsize=(10, 6))

            for i in range(len(files)):
                solving_method_name = files[i]
                file_path = f'benchmark\\correlation\\{solving_method_name}-{file_name}_contractions.csv'

                # Reload the CSV, assuming no header and filling missing values directly
                data = pd.read_csv(file_path, header=None, na_filter=False, on_bad_lines='skip')

                # Replace non-numeric values (including empty strings) with zero
                data = data.apply(pd.to_numeric, errors='coerce').fillna(0)

                # Each row will be plotted as a separate series
                for index, row in data.iterrows():
                    ax[i].plot(row.index + 1, row, marker='o', linestyle='-')

                ax[i].set_title(solving_method_name)
                ax[i].set_xlabel('Iteration')
                ax[i].set_ylabel(f'Number of Contractions')

            fig.suptitle(f"Number of Contractions on {file_name}")

            # Show the plot
            plt.show()

    def edge_contraction_contractions_plot_on_random(self):
        files = [
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "greedy_matchings_edge_contraction"
        ]

        file_names = {
            "p500-5": list(map(str, range(1, 11))),
            "p500-100": list(map(str, range(1, 11))),
            "p1000": list(map(str, range(1, 6))),
            "p1500": list(map(str, range(1, 6))),
            "p2000": list(map(str, range(1, 6))),
        }

        for file_name in file_names:
            fig, ax = plt.subplots(1, len(files), figsize=(10, 6))

            for i in range(len(files)):
                solving_method_name = files[i]
                file_path = f'benchmark\\random\\{solving_method_name}-{file_name}_contractions.csv'

                # Reload the CSV, assuming no header and filling missing values directly
                data = pd.read_csv(file_path, header=None, na_filter=False, on_bad_lines='skip')

                # Replace non-numeric values (including empty strings) with zero
                data = data.apply(pd.to_numeric, errors='coerce').fillna(0)

                # Each row will be plotted as a separate series
                for index, row in data.iterrows():
                    ax[i].plot(row.index + 1, row, marker='o', linestyle='-')

                ax[i].set_title(solving_method_name)
                ax[i].set_xlabel('Iteration')
                ax[i].set_ylabel(f'Number of Contractions')

            fig.suptitle(f"Number of Contractions on {file_name}")

            # Show the plot
            plt.show()

    def shortest_path_eval_plot(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "shortest_path",
            "kernighanLin"
        ]

        solving_method_verbose = {
            "largest_positive_cost_edge_contraction": "Greedy Additive",
            "shortest_path": "Shortest Path",
            "kernighanLin": "Kernighan Lin"
        }

        time_data_dict = {}
        score_data_dict = {}

        for solving_method_name in solving_method_names:

            # Load the CSV file
            file_path = f'benchmark/snemi/{solving_method_name}.csv'
            data = pd.read_csv(file_path)

            time_data_dict[solving_method_verbose[solving_method_name]] = data['time'][:50]
            score_data_dict[solving_method_verbose[solving_method_name]] = data['score'][:50]

        time_data = pd.DataFrame(time_data_dict)
        score_data = pd.DataFrame(score_data_dict)
        positions = list(range(1, len(solving_method_names) + 1))

        fig, ax = plt.subplots(1, 2, figsize=(10, 6))

        # Box Plot 1: Time
        ax[0].boxplot(time_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
        ax[0].set_xticks(positions)
        ax[0].set_xticklabels(time_data_dict.keys())
        ax[0].set_title('Comparison of Time Distributions')
        ax[0].set_xlabel('Algorithm')
        ax[0].set_ylabel('Milliseconds')
        ax[0].grid(True)

        # Box Plot 2: Score
        ax[1].boxplot(score_data, positions=positions, widths=0.6, patch_artist=True, vert=True)
        ax[1].set_xticks(positions)
        ax[1].set_xticklabels(time_data_dict.keys())
        ax[1].set_title('Comparison of Score Distributions')
        ax[1].set_xlabel('Algorithm')
        ax[1].set_ylabel('Value')
        ax[1].grid(True)

        plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.setp(ax[1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Adjust layout to not overlap
        plt.tight_layout()

        # Show the plots
        plt.show()

    def run_full_edge_contraction_benchmark_on_snemi(self):
        solving_method_names = [
            "kernighanLin"
        ]

        header = ["slice", "score", "time"]
        data = {name: [] for name in solving_method_names}
        number_of_slices = 100

        for i in range(number_of_slices):
            graph = GraphFactory.read_slice_from_snemi3d(i)
            solver = EdgeContractionSolver()
            solver.load(*(graph.standard_export()))

            for solving_method_name in solving_method_names:
                solving_method = getattr(solver, solving_method_name)

                solving_method()

                data[solving_method_name].append([i, solver.get_score(), solver.get_elapsed_time()])

        for solving_method_name in solving_method_names:
            with open(f"benchmark\\snemi\\{solving_method_name}.csv", "w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow(header)

                writer.writerows(data[solving_method_name])

                average_score = sum([line[1] for line in data[solving_method_name]]) / number_of_slices
                average_time = sum([line[2] for line in data[solving_method_name]]) / number_of_slices
                writer.writerow(["average", average_score, average_time])

    def run_full_edge_contraction_benchmark_on_correlation(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "greedy_matchings_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "maximum_matching_with_cutoff"
        ]

        file_names = {
            "corr40": list(map(str, range(1, 11))),
            "corr60": list(map(str, range(1, 11))),
            "corr80": list(map(str, range(1, 11))),
        }

        header = ["instance", "score", "time"]
        data = {name: {file_name: [] for file_name in file_names} for name in solving_method_names}

        for file_name in file_names.keys():
            for instance in file_names[file_name]:
                solver = EdgeContractionSolver()
                solver.load_from_file(f"graphs\\CP-Lib\\Correlation\\{file_name}-{instance}.txt")

                for solving_method_name in solving_method_names:
                    solving_method = getattr(solver, solving_method_name)

                    solving_method()

                    data[solving_method_name][file_name].append([instance, solver.get_score(), solver.get_elapsed_time()])

        for solving_method_name in solving_method_names:
            for file_name in file_names:
                with open(f"benchmark\\correlation\\{solving_method_name}-{file_name}.csv", "w", newline="") as file:
                    writer = csv.writer(file)

                    writer.writerow(header)

                    writer.writerows(data[solving_method_name][file_name])

    def run_full_edge_contraction_benchmark_on_random(self):
        solving_method_names = [
            "largest_positive_cost_edge_contraction",
            "greedy_matchings_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
            "maximum_matching_with_cutoff"
        ]

        file_names = {
            "p500-5": list(map(str, range(1, 11))),
            "p500-100": list(map(str, range(1, 11))),
            "p1000": list(map(str, range(1, 6))),
            "p1500": list(map(str, range(1, 6))),
            "p2000": list(map(str, range(1, 6))),
        }

        header = ["instance", "score", "time"]
        data = {name: {file_name: [] for file_name in file_names} for name in solving_method_names}

        for file_name in file_names.keys():
            for instance in file_names[file_name]:
                solver = EdgeContractionSolver()
                solver.load_from_file(f"graphs\\CP-Lib\\Random\\{file_name}-{instance}.txt")

                for solving_method_name in solving_method_names:
                    solving_method = getattr(solver, solving_method_name)

                    solving_method()

                    data[solving_method_name][file_name].append([instance, solver.get_score(), solver.get_elapsed_time()])

        for solving_method_name in solving_method_names:
            for file_name in file_names:
                with open(f"benchmark\\random\\{solving_method_name}-{file_name}.csv", "w", newline="") as file:
                    writer = csv.writer(file)

                    writer.writerow(header)

                    writer.writerows(data[solving_method_name][file_name])

    def count_contractions_on_snemi(self):
        solving_method_names = [
            "greedy_matchings_edge_contraction"
        ]

        data = {name: [] for name in solving_method_names}
        number_of_slices = 100

        for i in range(number_of_slices):
            graph = GraphFactory.read_slice_from_snemi3d(i)
            solver = EdgeContractionSolver()
            solver.load(*(graph.standard_export()))

            for solving_method_name in solving_method_names:
                solving_method = getattr(solver, solving_method_name)

                solving_method()

                data[solving_method_name].append(solver.get_contraction_history())

        for solving_method_name in solving_method_names:
            with open(f"benchmark\\snemi\\{solving_method_name}_contractions.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(data[solving_method_name])

    def count_contractions_on_correlation(self):
        solving_method_names = [
            "greedy_matchings_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
        ]

        file_names = {
            "corr40": list(map(str, range(1, 11))),
            "corr60": list(map(str, range(1, 11))),
            "corr80": list(map(str, range(1, 11))),
        }

        data = {name: {file_name: [] for file_name in file_names} for name in solving_method_names}

        for file_name in file_names.keys():
            for instance in file_names[file_name]:
                solver = EdgeContractionSolver()
                solver.load_from_file(f"graphs\\CP-Lib\\Correlation\\{file_name}-{instance}.txt")

                for solving_method_name in solving_method_names:
                    solving_method = getattr(solver, solving_method_name)

                    solving_method()

                    data[solving_method_name][file_name].append(solver.get_contraction_history())

        for solving_method_name in solving_method_names:
            for file_name in file_names:
                with open(f"benchmark\\correlation\\{solving_method_name}-{file_name}_contractions.csv", "w", newline="") as file:
                    writer = csv.writer(file)

                    writer.writerow(max(map(len, data[solving_method_name][file_name])) * [None])

                    writer.writerows(data[solving_method_name][file_name])

    def count_contractions_on_random(self):
        solving_method_names = [
            "greedy_matchings_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching",
        ]

        file_names = {
            "p500-5": list(map(str, range(1, 11))),
            "p500-100": list(map(str, range(1, 11))),
            "p1000": list(map(str, range(1, 6))),
            "p1500": list(map(str, range(1, 6))),
            "p2000": list(map(str, range(1, 6))),
        }

        data = {name: {file_name: [] for file_name in file_names} for name in solving_method_names}

        for file_name in file_names.keys():
            for instance in file_names[file_name]:
                solver = EdgeContractionSolver()
                solver.load_from_file(f"graphs\\CP-Lib\\Random\\{file_name}-{instance}.txt")

                for solving_method_name in solving_method_names:
                    solving_method = getattr(solver, solving_method_name)

                    solving_method()

                    data[solving_method_name][file_name].append(solver.get_contraction_history())

        for solving_method_name in solving_method_names:
            for file_name in file_names:
                with open(f"benchmark\\random\\{solving_method_name}-{file_name}_contractions.csv", "w",
                          newline="") as file:
                    writer = csv.writer(file)

                    writer.writerow(max(map(len, data[solving_method_name][file_name])) * [None])

                    writer.writerows(data[solving_method_name][file_name])

    def track_contractions_on_snemi(self):
        solving_method_names = [
            "greedy_matchings_edge_contraction",
            "spanning_tree_edge_contraction",
            "maximum_matching"
        ]

        graph = GraphFactory.generate_bad_example()
        solver = EdgeContractionSolver()
        solver.load(*(graph.standard_export()))
        solver.activate_track_history()

        solver.greedy_matchings_edge_contraction(1)

        # for solving_method_name in solving_method_names:
        #
        #     solving_method = getattr(solver, solving_method_name)
        #
        #     solving_method()

    def run_kernighanLin_on_snemi(self):
        header = ["slice", "score", "time"]
        data = []
        number_of_slices = 100

        with open(f"benchmark\\snemi\\kernighanLin.csv", "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(header)

        for i in range(number_of_slices):
            graph = GraphFactory.read_slice_from_snemi3d(i)
            solver = EdgeContractionSolver()
            solver.load(*(graph.standard_export()))

            try:
                solver.kernighanLin()
            except Exception as e:
                print(e)
            else:
                line = [i, solver.get_score(), solver.get_elapsed_time()]
                with open(f"benchmark\\snemi\\kernighanLin.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(line)
                data.append(line)


    def run_shortest_path_benchmark_on_snemi(self):
        header = ["slice", "score", "time"]
        data = []
        number_of_slices = 100

        with open(f"benchmark\\snemi\\shortest_path.csv", "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(header)

        for i in range(number_of_slices):
            graph = GraphFactory.read_slice_from_snemi3d(i)
            solver = spm_solver.Solver()
            solver.load_graph(*(graph.export()))

            try:
                solver.parallel_search_solve()
            except Exception as e:
                print(e)
            else:
                line = [i, solver.get_score(), solver.get_elapsed_time()]
                with open(f"benchmark\\snemi\\shortest_path.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(line)
                data.append(line)

        # with open(f"benchmark\\snemi\\shortest_path.csv", "a", newline="") as file:
        #     writer = csv.writer(file)
        #
        #     average_score = sum([line[1] for line in data]) / number_of_slices
        #     average_time = sum([line[2] for line in data]) / number_of_slices
        #     writer.writerow(["average", average_score, average_time])


    def run_andres_edge_contraction_solver_from_file(self):
        solver = EdgeContractionSolver()
        solver.load_from_file("graphs\\CP-Lib\\Random\\p2000-1.txt")
        solver.largest_positive_cost_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

    def run_greedy_edge_contraction_solver(self):
        solver = EdgeContractionSolver()

        self.visualization_thread.start()

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)
        self.visualizer.set_graph(graph)

        solver.load(*(graph.standard_export()))

        print("test maximum spanning tree")
        solver.largest_positive_cost_edge_contraction()
        multicut = solver.get_multicut()
        print(f"multicut length: {len(multicut)}")
        print(f"Score: {solver.get_score()}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)


    def run_maximum_spanning_tree_solver(self):
        solver = EdgeContractionSolver()

        self.visualization_thread.start()

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)
        self.visualizer.set_graph(graph)

        solver.load(*(graph.standard_export()))

        print("test maximum spanning tree")
        solver.spanning_tree_edge_contraction()
        multicut = solver.get_multicut()
        print(f"multicut length: {len(multicut)}")
        print(f"Score: {solver.get_score()}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_maximum_spanning_tree_continued_solver(self):
        solver = EdgeContractionSolver()

        self.visualization_thread.start()

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)
        self.visualizer.set_graph(graph)

        solver.load(*(graph.standard_export()))

        print("test maximum spanning tree")
        solver.spanning_tree_edge_contraction_continued()
        multicut = solver.get_multicut()
        print(f"multicut length: {len(multicut)}")
        print(f"Score: {solver.get_score()}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_maximum_matching_solver(self):
        solver = EdgeContractionSolver()

        self.visualization_thread.start()

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)
        self.visualizer.set_graph(graph)

        solver.load(*(graph.standard_export()))

        print("test maximum matching")
        solver.maximum_matching()
        multicut = solver.get_multicut()
        print(f"multicut length: {len(multicut)}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")
        print(f"Score: {solver.get_score()}")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_maximum_matching_with_cutoff_solver(self):
        solver = EdgeContractionSolver()

        self.visualization_thread.start()

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)
        self.visualizer.set_graph(graph)

        solver.load(*(graph.standard_export()))

        print("test maximum matching")
        solver.maximum_matching_with_cutoff()
        multicut = solver.get_multicut()
        print(f"multicut length: {len(multicut)}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")
        print(f"Score: {solver.get_score()}")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def full_edge_contraction_test(self):
        solver = EdgeContractionSolver()

        print("loading from file")
        solver.load_from_file("graphs\\CP-Lib\\Random\\p2000-1.txt")

        print("test largest positive cost")
        solver.largest_positive_cost_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        print("test greedy matching")
        solver.greedy_matchings_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        print("test maximum spanning tree")
        solver.spanning_tree_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        print("loading from parameters")
        graph = GraphFactory.read_slice_from_snemi3d(3)
        solver.load(*(graph.standard_export()))

        print("test largest positive cost")
        solver.largest_positive_cost_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        print("test greedy matching")
        solver.greedy_matchings_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

        print("test maximum spanning tree")
        solver.spanning_tree_edge_contraction()
        print(f"multicut length: {len(solver.get_multicut())}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

    def run_parallel_edge_contraction_solver(self):
        self.visualization_thread.start()

        # graph = GraphFactory.generate_grid((50, 50))
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        multicut, elapsed = greedyParallelAdditiveEdgeContraction(*(graph.standard_export()))

        print("execution Time: ", elapsed, "ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_spanning_tree_edge_contraction_solver(self):
        self.visualization_thread.start()

        # graph = GraphFactory.generate_grid((50, 50))
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        multicut, elapsed = spanningTreeEdgeContraction(*(graph.standard_export()))

        print("execution Time: ", elapsed, "ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_edge_contraction_solver(self):
        self.visualization_thread.start()

        graph = GraphFactory.generate_grid((50, 50))

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        solver = LargestPositiveCost()
        solver.load_graph(*(graph.export()))
        multicut, elapsed = solver.solve()

        print("execution Time: ", elapsed, "ms")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_parallel_spm_solver(self):
        self.visualization_thread.start()

        # graph = GraphFactory.generate_grid((60, 60))
        graph = GraphFactory.generate_bad_example()

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        solver = spm_solver.Solver()
        solver.activate_track_history()
        solver.load_graph(*(graph.export()))
        nodes, edges, components, node_to_predecessor = solver.get_state()
        graph = GraphFactory.construct_from_values(nodes, edges)

        self.visualizer.set_graph(graph)

        multicut = solver.parallel_search_solve()

        print(f"Score: {solver.get_score()}")
        print(f"Time: {solver.get_elapsed_time()}")

        input("Waiting for input")

        self.visualizer.set_multicut(multicut)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_parallel_spm_solver_and_greedy_joining_after(self):
        self.visualization_thread.start()

        # graph = GraphFactory.generate_grid((60, 60))
        graph = GraphFactory.read_slice_from_snemi3d(3)

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        input("Waiting for input")

        solver = spm_solver.Solver()
        # solver.activate_track_history()
        solver.load_graph(*(graph.export()))
        nodes, edges, components, node_to_predecessor = solver.get_state()
        search_graph = GraphFactory.construct_from_values(nodes, edges)

        self.visualizer.set_graph(search_graph)

        multicut = solver.parallel_search_solve()

        score = 0
        for _, _, data in graph.edges(data=True):
            if data["id"] in multicut:
                score += data["cost"]

        print(f"new score: {score}")

        print(f"Score: {solver.get_score()}")
        print(f"Time: {solver.get_elapsed_time()}")

        input("Waiting for input")

        self.visualizer.set_multicut(multicut)

        solver = EdgeContractionSolver()
        solver.load(*(graph.standard_export()))
        solver.greedy_matchings_edge_contraction_with_multicut_applied(set(multicut))

        multicut = solver.get_multicut()

        input("waiting for input")

        self.visualizer.set_multicut(multicut)
        self.visualizer.set_graph(search_graph)

        print(f"multicut length: {len(multicut)}")
        print(f"Score: {solver.get_score()}")
        print(f"execution Time: {solver.get_elapsed_time()}ms")

    def run_external_spm_solver(self):
        self.visualization_thread.start()

        graph = GraphFactory.generate_grid((80, 80))

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        search_graph = GraphFactory.generate_grid_search_graph(graph)
        visual_graph = search_graph.copy()

        time.sleep(1)
        # input("Waiting for input")

        self.visualizer.set_graph(visual_graph)

        time.sleep(1)
        # input("Waiting for input")

        solver = spm_solver.get_solver()
        solver.load_search_graph(*(search_graph.export()))
        multicut = solver.solve()

        self.visualizer.set_multicut(multicut)

        time.sleep(1)
        # input("Waiting for input")

        self.visualizer.set_graph(graph)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run(self):
        self.visualization_thread.start()

        graph = GraphFactory.generate_grid((20, 20))

        while self.visualizer is None:
            time.sleep(1)

        self.visualizer.set_graph(graph)

        # generate graphs to solve and visualize
        search_graph = GraphFactory.generate_grid_search_graph(graph)
        visual_graph = search_graph.copy()
        nx.set_edge_attributes(visual_graph, 0, "cut")

        # solve
        solver = ShortestPathSolver(search_graph)
        multicut = solver.solve()
        components = solver.get_components()

        colors = set(generate_distinct_colors(len(components)))
        component_to_color = dict(enumerate(colors))
        node_to_color = {}
        node_to_value = {}

        color_id = 0
        if len(colors) >= len(components):
            for component_id, component in components.items():
                for node in component:
                    node_to_color[node] = component_to_color[color_id]
                color_id += 1

        for node, mapped_node in solver.get_node_remap().items():
            node_to_value[node] = solver.get_lowest_cost_predecessor(mapped_node)[1]
            node_to_color[node] = node_to_color[mapped_node]

        node_to_value.update({node: solver.get_lowest_cost_predecessor(node)[1] for node in visual_graph.nodes if
                              node not in node_to_value})

        input("Waiting for input")

        self.visualizer.set_graph(visual_graph)

        input("Waiting for input")

        visual_graph.load_values(node_to_value, "cost")
        visual_graph.load_values(node_to_color, "color")

        self.visualizer.set_multicut(multicut)

        input("Waiting for input")

        self.visualizer.set_graph(graph)

        while self.visualization_thread.is_alive():
            time.sleep(1)

    def run_visualizer(self):
        # pygame should be imported only in the new thread and not in the main thread
        # therefore the visualizer must be imported here

        from visualizer import Visualizer
        self.visualizer = Visualizer(drawing_lock)
        self.visualizer.run()

    def exit(self):
        self.visualizer.exit_flag = True
        self.visualization_thread.join()
