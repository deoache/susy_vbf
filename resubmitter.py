import glob
import yaml
import argparse
import subprocess
from pathlib import Path
from analysis.helpers import get_output_directory


def main(args):
    """Helper function to resubmit condor jobs"""
    # get outputs directory
    output_dir = get_output_directory(vars(args))
    print(f"Reading outputs from: {output_dir}")

    # get datasets key names
    main_dir = Path.cwd()
    print(f'{main_dir=}')
    print(f"{output_dir}")
    fileset_path = Path(f"{main_dir}/analysis/filesets")
    with open(f"{fileset_path}/{args.year}_fileset.yaml", "r") as f:
        datasets = yaml.safe_load(f)

    # get jobs done
    jobs_done = []
    for sample in datasets:
        output_list = glob.glob(f"{output_dir}/{sample}*.coffea")
        for output in output_list:
            jobs_done.append(output.split("/")[-1].replace(".coffea", ""))
    n_jobs_done = len(jobs_done)

    # get jobs to be run
    condor_path = f"{main_dir}/condor/{args.processor}"
    if args.label:
        condor_path += f"/{args.label}"
    condor_path += f"/{args.year}"
    print(f"Reading condor files from: {condor_path}")
    condor_files = glob.glob(f"{condor_path}/*/*.sub", recursive=True)
    n_jobs = len(condor_files)

    # get jobs names
    to_replace = f"{args.processor}_"
    condor_files_keys = [
        f.split("/")[-1].replace(to_replace, "").replace(".sub", "")
        for f in condor_files
    ]
    for job, sub_file in zip(condor_files_keys, condor_files):
        if job not in jobs_done:
            # missing job
            print(job)
            if args.resubmit:
                # resubmit missing job
                subprocess.run(["condor_submit", sub_file])

    print("")
    print(f"{n_jobs=}")
    print(f"{n_jobs_done=}")
    print(f"missing jobs: {n_jobs - n_jobs_done}", "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processor",
        dest="processor",
        type=str,
        default="ztojets",
        help="processor to be used",
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
        help="label of the run",
    )
    parser.add_argument(
        "--resubmit",
        action="store_true",
        help="if True resubmit the jobs. if False only print the missing jobs",
    )
    parser.add_argument(
        "--eos",
        action="store_true",
        help="Enable reading outputs from /eos",
    )
    args = parser.parse_args()
    main(args)
