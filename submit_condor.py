import json
import yaml
import argparse
from pathlib import Path
from condor import submit_condor
from analysis.filesets import divide_list
from analysis.helpers import get_output_directory


def main(args):
    args = vars(args)
    submit = args["submit"]
    args["output_path"] = get_output_directory(args)
    del args["eos"]
    del args["submit"]

    # split dataset into batches
    fileset_path = Path(f"{Path.cwd()}/analysis/filesets")
    with open(f"{fileset_path}/fileset_{args['year']}_NANO_lxplus.json", "r") as f:
        root_files = json.load(f)[args["dataset"]]
    root_files_list = divide_list(root_files, args["nfiles"])
    del args["nfiles"]

    # submit job for each partition
    for i, partition in enumerate(root_files_list, start=1):
        if len(root_files_list) == 1:
            args["dataset_key"] = args["dataset"]
            args["partition_fileset"] = {args["dataset"]: partition}
        else:
            args["nsample"] = i
            dataset_key = f'{args["dataset"]}_{i}'
            args["dataset_key"] = dataset_key
            args["partition_fileset"] = {dataset_key: partition}
        submit_condor(args, submit=submit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processor",
        dest="processor",
        type=str,
        default="ztojets",
        help="processor to be used (default ztojets)",
    )
    parser.add_argument(
        "--dataset",
        dest="dataset",
        type=str,
        default="",
        help="sample key to be processed",
    )
    parser.add_argument(
        "--year",
        dest="year",
        type=str,
        default="2017",
        help="year of the data {2016preVFP, 2016postVFP, 2017, 2018} (default 2017)",
    )
    arser.add_argument(
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
        default="1b1l",
        help="channel to be processed (1b1l, 2b1l)",
    )
    parser.add_argument(
        "--flow",
        action="store_true",
        help="whether to include underflow/overflow to first/last bin {True, False}",
    )
    parser.add_argument(
        "--systematics",
        action="store_true",
        help="Enable applying jerc systematics",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Enable Condor job submission. If not provided, it just builds condor files",
    )
    parser.add_argument(
        "--label",
        dest="label",
        type=str,
        default="ztojets_CR",
        help="Tag to label the run (default ztojets_CR)",
    )
    parser.add_argument(
        "--eos",
        action="store_true",
        help="Enable saving outputs to /eos",
    )
    parser.add_argument(
        "--nfiles",
        dest="nfiles",
        type=int,
        default=20,
        help="number of root files to include in each dataset partition (default 20)",
    )
    args = parser.parse_args()
    main(args)
