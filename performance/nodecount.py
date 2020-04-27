from performance.perfomance import Performance, plt, np


class NodeCount(Performance):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)

    def initialize_performance_metrics(self):
        self.performance_output = dict()

    def plot(self):
        pass

    def run(self):
        pass


class WriteNodeCount(NodeCount):
    """
    Author: Adarsh Trivedi
    This class compares write latency with respect to number of nodes present in the network.
    This is important to understand how increasing number of nodes can increase latency.
    """

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)

    def run(self):
        content = self.get_file_content()
        try:
            while True:
                n = int(input("New number of nodes (make sure these many nodes are in the ring for accurate results):"))
                sample_size_wise_performance_values = dict()
                for sample_size in self.sample_sizes:
                    performance_values = []
                    epoch_counter = 0
                    while epoch_counter < self.epochs_per_sample_size:
                        start_time = self.record_time()
                        for i in range(sample_size):
                            self.chord_client.set(content[i])
                        end_time = self.record_time()
                        performance_values.append(end_time - start_time)
                        epoch_counter += 1
                        print("Sample Size: {}\nEpoch Counter: {}\nTime take: {}\n".format(sample_size, epoch_counter,
                                                                                           end_time - start_time))
                    sample_size_wise_performance_values[sample_size] = sum(performance_values) / len(performance_values)
                self.performance_output[n] = sample_size_wise_performance_values
        except:
            pass

    def plot(self):
        x_ticks = sorted(self.sample_sizes)
        pos = np.arange(len(x_ticks))
        plt.xticks(pos, x_ticks)
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        cnt = 0
        for key in sorted(self.get_performance_metric()):
            y_val = []
            for sample_size in sorted(self.performance_output[key]):
                y_val.append(self.performance_output[key][sample_size])
            plt.bar(pos+(cnt*0.1), y_val, 0.1, label="Node Count: {}".format(key),
                    color=colors[cnt % len(colors)])
            cnt += 1
        plt.title("Write performance wrt node count")
        plt.xlabel("Sample Size")
        plt.ylabel("Time (sec)")
        plt.legend()
        plt.show()
