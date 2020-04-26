from performance.perfomance import Performance, plt, np
from collections import defaultdict


class NodeCount(Performance):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)

    def initialize_performance_metrics(self):
        self.performance_output = defaultdict(dict)

    def plot(self):
        pass

    def run(self):
        pass


class WriteNodeCount(NodeCount):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)
