import os
import glob
import yaml
import logging
import argparse
from analysis.helpers import get_output_directory
from analysis.configs import ProcessorConfigBuilder
from analysis.postprocess.plotter import Plotter
from analysis.postprocess.postprocessor import Postprocessor
from analysis.postprocess.utils import print_header, setup_logger


def main(args):
    if not args.output_dir:
        args.output_dir = get_output_directory(vars(args))

    setup_logger(args.output_dir)

    # load and save processor config
    config_builder = ProcessorConfigBuilder(
        processor=args.processor,
        year=args.year,
        channel=args.channel,
        lepton_flavor=args.lepton_flavor,
    )
    processor_config = config_builder.build_processor_config()
    logging.info(processor_config.to_yaml())

    # process (group and accumulate) outputs
    postprocessor = Postprocessor(
        processor=args.processor,
        year=args.year,
        output_dir=args.output_dir,
        lepton_flavor=args.lepton_flavor,
        channel=args.channel,
    )
    processed_histograms = postprocessor.histograms
    lumi = postprocessor.luminosities[args.year]

    # plot processed histograms
    print_header("Plots")
    plotter = Plotter(
        processor=args.processor,
        processed_histograms=processed_histograms,
        year=args.year,
        lumi=lumi,
        output_dir=args.output_dir,
        channel=args.channel,
        lepton_flavor=args.lepton_flavor,
    )
    for category in postprocessor.categories:
        logging.info(f"plotting histograms for category: {category}")
        for variable in processor_config.histogram_config.variables:
            logging.info(variable)
            plotter.plot_histograms(
                variable=variable,
                category=category,
                yratio_limits=args.yratio_limits,
                log_scale=args.log_scale,
                savefig=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processor",
        dest="processor",
        type=str,
        default="ttbar",
        help="processor to be used {ttbar}",
    )
    parser.add_argument(
        "--year",
        dest="year",
        type=str,
        default="2017",
        help="year of the data {2016preVFP, 2016postVFP, 2017, 2018} (default 2017)",
    )
    parser.add_argument(
        "--label",
        dest="label",
        type=str,
        help="Label of the output directory",
    )
    parser.add_argument(
        "--eos",
        action="store_true",
        help="Enable reading outputs from /eos",
    )
    parser.add_argument(
        "--log_scale",
        action="store_true",
        help="Enable log scale for y-axis",
    )
    parser.add_argument(
        "--yratio_limits",
        dest="yratio_limits",
        type=float,
        nargs=2,
        default=(0, 2),
        help="Set y-axis ratio limits as a tuple (e.g., --yratio_limits 0.5 1.5) (default 0 2)",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        type=str,
        default="",
        help="Path to the outputs directory (optional)",
    )
    parser.add_argument(
        "--lepton_flavor",
        dest="lepton_flavor",
        type=str,
        default="mu",
        help="lepton flavor to be processed (mu)",
    )
    parser.add_argument(
        "--channel",
        dest="channel",
        type=str,
        default="2b1l",
        help="channel to be processed (1b1l, 2b1l)",
    )
    args = parser.parse_args()
    main(args)
