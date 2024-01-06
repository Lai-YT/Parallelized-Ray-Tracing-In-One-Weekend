#!/usr/bin/env python

"""This program shows parametrized `hyperfine` benchmark results as an
errorbar plot."""

import argparse
import json
import warnings

import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="JSON file with benchmark results", type=str)
    parser.add_argument(
        "--parameter-name",
        metavar="name",
        type=str,
        help="Deprecated; parameter names are now inferred from benchmark files",
    )
    parser.add_argument(
        "--log-x", help="Use a logarithmic x (parameter) axis", action="store_true"
    )
    parser.add_argument(
        "--log-time", help="Use a logarithmic time axis", action="store_true"
    )
    parser.add_argument(
        "--titles", help="Comma-separated list of titles for the plot legend"
    )
    parser.add_argument("-o", "--output", help="Save image to the given filename.")
    args = parser.parse_args()
    if args.parameter_name is not None:
        warnings.warn(
            "warning: --parameter-name is deprecated; names are inferred from benchmark results\n",
            stacklevel=1,
        )
    return args


def die(msg):
    raise RuntimeError(f"fatal: {msg}")


def extract_parameters(results):
    """Return `(parameter_name: str, parameter_values: List[float])`."""
    if not results:
        die("no benchmark data to plot")
    (names, values) = zip(*(unique_parameter(b) for b in results))
    names = frozenset(names)
    if len(names) != 1:
        die(
            "benchmarks must all have the same parameter name, but found: %s"
            % sorted(names)
        )
    return (next(iter(names)), list(values))


def unique_parameter(benchmark):
    """Return the unique parameter `(name: str, value: float)`, or die."""
    params_dict = benchmark.get("parameters", {})
    if not params_dict:
        die("benchmarks must have exactly one parameter, but found none")
    if len(params_dict) > 1:
        die(
            "benchmarks must have exactly one parameter, but found multiple: %s"
            % sorted(params_dict)
        )
    [(name, value)] = params_dict.items()
    return (name, float(value))


def main(args):
    parameter_name = None

    with open(args.file) as f:
        results = json.load(f)["results"]

    (this_parameter_name, parameter_values) = extract_parameters(results)
    if parameter_name is not None and this_parameter_name != parameter_name:
        die(
            "files must all have the same parameter name, but found %r vs. %r"
            % (parameter_name, this_parameter_name)
        )
    parameter_name = this_parameter_name

    number_of_cmds = parameter_values.count(parameter_values[0])
    parameter_values = sorted(list(set(parameter_values)))[1::2]
    parameter_values = [parameter_value**2 for parameter_value in parameter_values]
    for i in range(number_of_cmds):
        results_ = results[i + number_of_cmds :: 2 * number_of_cmds]
        times_mean = [b["mean"] for b in results_]
        times_stddev = [b["stddev"] for b in results_]

        plt.errorbar(x=parameter_values, y=times_mean, yerr=times_stddev, capsize=2)

    plt.title("Execution time")
    plt.xlabel(parameter_name)
    plt.ylabel("Time [s]")

    if args.log_time:
        plt.yscale("log")
    else:
        plt.ylim(0, None)

    if args.log_x:
        plt.xscale("log")

    if args.titles:
        plt.legend(args.titles.split(","))
    else:
        plt.legend([results[i]["command"] for i in range(number_of_cmds)])

    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()


if __name__ == "__main__":
    args = parse_args()
    main(args)
