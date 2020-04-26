import argparse
from performance.readwrite import *
from client.chord_client import ChordClient


def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--type",
                        choices=['write', 'readwrite', 'nodecount'],
                        required=True,
                        dest='type',
                        type=str,
                        help="Type of performance testing. Valid values ['write', 'readwrite', 'nodecount'].")

    parser.add_argument("--input-file",
                        required=False,
                        dest='input_file',
                        type=str,
                        help="Input file to pick data to store on chord.")

    parser.add_argument("--bootstrap-server",
                        required=True,
                        dest='bootstrap_server',
                        type=str,
                        help="Any running chord server in format localhost:5000.")

    parser.add_argument("--sample-size",
                        required=False,
                        type=int,
                        dest="sample_size",
                        action="append",
                        help="Sample sizes to run performance against.")

    parser.add_argument("--epochs-per-sample",
                        dest="e_per_sample",
                        type=int,
                        default=3,
                        required=False,
                        help="Number of epochs to run per sample size.")

    parser.add_argument("--display-performance-output",
                        default=False,
                        action="store_true",
                        required=False,
                        dest='d_p_o',
                        help="Set to print the performance output.")

    parser.add_argument("--plot-performance-output",
                        default=False,
                        action="store_true",
                        required=False,
                        dest="p_p_o",
                        help="Set to display the performance output as plot.")

    args = parser.parse_args()
    return args.type, args.input_file, args.bootstrap_server, args.d_p_o, args.p_p_o, args.sample_size, args.e_per_sample


def main():

    run_type, input_file, bootstrap_server, d_p_o, p_p_o, sample_size, e_per_sample = get_arguments()
    performance_object = None

    client = None
    try:
        client = ChordClient(bootstrap_server=bootstrap_server)
    except:
        print("Something went wrong creating chord client.")
        exit(1)

    if run_type == "write":
        performance_object = WritePerformance(input_file=input_file,
                                              chord_client=client,
                                              sample_sizes=sample_size,
                                              epochs_per_sample_size=e_per_sample)

    elif run_type == "readwrite":
        performance_object = ReadWritePerformance(input_file=input_file,
                                                  chord_client=client,
                                                  sample_sizes=sample_size,
                                                  epochs_per_sample_size=e_per_sample)

    elif run_type == "nodecount":
        performance_object = None

    else:
        print("--type parameter not handled at present.")

    performance_object.run()

    if d_p_o:
        print(performance_object.get_performance_metric())

    if p_p_o:
        performance_object.plot()


if __name__ == "__main__":
    main()