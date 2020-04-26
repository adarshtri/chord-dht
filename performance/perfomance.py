from abc import ABC, abstractmethod
import time
import matplotlib.pyplot as plt
import numpy as np


class Performance(ABC):

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        self.input_file = input_file
        self.sample_sizes = sample_sizes
        self.epochs_per_sample_size = epochs_per_sample_size
        self.chord_client = chord_client
        self.performance_output = None
        self.initialize_performance_metrics()

    @abstractmethod
    def initialize_performance_metrics(self):
        pass

    def set_performance_metric(self, metric):
        self.performance_output = metric

    def get_performance_metric(self):
        return self.performance_output

    @abstractmethod
    def plot(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def record_time():
        return time.time()

    def get_file_content(self):
        fp = open(self.input_file, 'r')
        content = fp.read()
        content = content.split(" ")
        return content
