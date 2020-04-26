from performance.perfomance import Performance, plt, np


class ReadWritePerformance(Performance):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)

    def plot(self):
        x, y_read, y_write = [], [], []
        for key in sorted(self.performance_output):
            x.append(key)
            y_read.append(self.performance_output[key][0])
            y_write.append(self.performance_output[key][1])
        y_pos = np.arange(len(x))
        plt.bar(y_pos, y_read, 0.35, alpha=0.8, label='Read', color='b')
        plt.bar(y_pos+0.35, y_write, 0.35, alpha=0.8, label='Write', color='g')
        plt.xticks(y_pos, x)
        plt.xlabel("Sample Size")
        plt.ylabel("Time taken in seconds")
        plt.title("ReadWrite performance")
        plt.legend()
        plt.show()

    def run(self):
        content = self.get_file_content()
        sample_size_wise_performance_values = dict()
        for sample_size in self.sample_sizes:
            performance_values_write = []
            performance_values_read = []
            epoch_counter = 0
            while epoch_counter < self.epochs_per_sample_size:
                start_time_write = self.record_time()
                for i in range(sample_size):
                    self.chord_client.set(content[i])
                end_time_write = self.record_time()
                performance_values_write.append(end_time_write-start_time_write)
                print("Write\nSample Size: {}\nEpoch Counter: {}\nTime take: {}\n".format(sample_size, epoch_counter,
                                                                                         end_time_write - start_time_write))
                start_time_read = self.record_time()
                for i in range(sample_size):
                    self.chord_client.get(content[i])
                end_time_read = self.record_time()
                performance_values_read.append(end_time_read - start_time_read)
                print("Read\nSample Size: {}\nEpoch Counter: {}\nTime take: {}\n".format(sample_size, epoch_counter,
                                                                                         end_time_read-start_time_read))
                epoch_counter += 1
            sample_size_wise_performance_values[sample_size] = []
            sample_size_wise_performance_values[sample_size].append(
                sum(performance_values_read)/len(performance_values_read))
            sample_size_wise_performance_values[sample_size].append(
                sum(performance_values_write) / len(performance_values_write))
        self.set_performance_metric(sample_size_wise_performance_values)

    def initialize_performance_metrics(self):
        self.performance_output = dict()


class WritePerformance(Performance):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        super().__init__(input_file, chord_client, sample_sizes, epochs_per_sample_size)

    def plot(self):
        x, y = [], []
        for key in sorted(self.performance_output):
            x.append(key)
            y.append(self.performance_output[key])
        y_pos = np.arange(len(x))
        plt.bar(y_pos, y)
        plt.xticks(y_pos, x)
        plt.xlabel("Sample Size")
        plt.ylabel("Time taken in seconds")
        plt.title("Write performance")
        plt.show()

    def run(self):
        content = self.get_file_content()
        sample_size_wise_performance_values = dict()
        for sample_size in self.sample_sizes:
            performance_values = []
            epoch_counter = 0
            while epoch_counter < self.epochs_per_sample_size:
                start_time = self.record_time()
                for i in range(sample_size):
                    self.chord_client.set(content[i])
                end_time = self.record_time()
                performance_values.append(end_time-start_time)
                epoch_counter += 1
                print("Sample Size: {}\nEpoch Counter: {}\nTime take: {}\n".format(sample_size, epoch_counter, end_time-start_time))
            sample_size_wise_performance_values[sample_size] = sum(performance_values)/len(performance_values)
        self.set_performance_metric(sample_size_wise_performance_values)

    def initialize_performance_metrics(self):
        self.performance_output = dict()
