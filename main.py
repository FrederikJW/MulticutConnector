import signal
import sys

from manager import Manager

manager = None


def main():
    global manager
    manager = Manager()
    
    # ----- TEST RUNS -----
    # manager.run_parallel_spm_solver()
    # manager.run_parallel_spm_solver_and_greedy_joining_after()
    # manager.run_external_spm_solver()
    # manager.run_parallel_edge_contraction_solver()
    # manager.run_andres_edge_contraction_solver_from_file()
    # manager.run_maximum_spanning_tree_continued_solver()
    # manager.run_maximum_spanning_tree_solver()
    # manager.run_maximum_matching_solver()
    # manager.run_greedy_edge_contraction_solver()
    # manager.run_spanning_tree_edge_contraction_solver()
    # manager.run_edge_contraction_solver()
    # manager.multithreading_test()

    # ----- TRACK HISTORY -----
    # manager.track_contractions_on_snemi()

    # ----- HISTORY VISUALIZATIONS -----
    # manager.play_history_shortest_path()
    # manager.play_history_edge_contraction()

    # ----- BENCHMARKS -----
    # manager.run_full_edge_contraction_benchmark_on_snemi()
    # manager.run_kernighanLin_on_snemi()
    # manager.count_contractions_on_snemi()
    # manager.run_shortest_path_benchmark_on_snemi()
    # manager.run_full_edge_contraction_benchmark_on_correlation()
    # manager.count_contractions_on_correlation()
    # manager.run_full_edge_contraction_benchmark_on_random()
    # manager.count_contractions_on_random()

    # ----- PLOTS -----
    # manager.shortest_path_eval_plot()
    # manager.edge_contraction_eval_plot()
    # manager.edge_contraction_eval_plot_on_correlation()
    # manager.edge_contraction_eval_plot_on_random()
    # manager.edge_contraction_contractions_plot()
    # manager.edge_contraction_contractions_plot_on_correlation()
    # manager.edge_contraction_contractions_plot_on_random()
    # manager.edge_contraction_iterations_plot()


def on_terminate(signum, frame):
    print("Received termination signal. Cleaning up...")

    global manager
    if manager is not None:
        manager.exit()

    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGTERM, on_terminate)
signal.signal(signal.SIGINT, on_terminate)


if __name__ == "__main__":
    main()
