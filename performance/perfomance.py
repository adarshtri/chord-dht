"""
Author: Adarsh Trivedi
This module defines a base abstract Performance class.
"""


from abc import ABC, abstractmethod
import time
import matplotlib.pyplot as plt
import numpy as np


class Performance(ABC):

    """
    Abstract performance class with basic methods and abstract methods to be
    implemented by child classes.
    """

    def __init__(self, input_file, chord_client, sample_sizes, epochs_per_sample_size):
        """
        Author: Adarsh Trivedi
        :param input_file: Input file to take data from.
        :param chord_client: Chord Application client to perform store, get and delete.
        :param sample_sizes: list, sizes of sample (number of keys) to be used for performance measure.
        :param epochs_per_sample_size: Number of rounds to perform per sample size to take average of values.
        """
        self.input_file = input_file
        self.sample_sizes = sample_sizes
        self.epochs_per_sample_size = epochs_per_sample_size
        self.chord_client = chord_client
        self.performance_output = None
        self.initialize_performance_metrics()

    @abstractmethod
    def initialize_performance_metrics(self):
        """
        Author: Adarsh Trivedi
        Every child class can have different type for attribute performance_output. Hence every child class
        implements this method to initialize the performance_output variable to appropriate data structure.
        :return: None
        """
        pass

    def set_performance_metric(self, metric):
        self.performance_output = metric

    def get_performance_metric(self):
        return self.performance_output

    @abstractmethod
    def plot(self):
        """
        Author: Adarsh Trivedi (for all the child class implementations as well)
        Implemented method plots the output after performing performance measurements.
        :return: None
        """
        pass

    @abstractmethod
    def run(self):
        """
        Author: Adarsh Trivedi (for all the child class implementations as well)
        Implemented method run the performance measurement tasks and stores the output
        in the attribute performance_output attribute.
        :return: None
        """
        pass

    @staticmethod
    def record_time():
        return time.time()

    def get_file_content(self):
        """
        Author: Adarsh Trivedi
        Helper function to read input file to get samples to be used during performance measurement.
        :return: Words in file as list.
        """
        fp = open(self.input_file, 'r')
        content = fp.read()
        content = content.split(" ")
        return content
