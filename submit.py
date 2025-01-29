import json
import time
import pickle
import argparse
from coffea import processor
from humanfriendly import format_timespan
from analysis.processors.ztojets import ZToJets
from analysis.processors.ttbar import Ttbar


def main(args):
    processors = {
        "ztojets": ZToJets(year=args.year, flow=eval(args.flow)),
        "ttbar": Ttbar(year=args.year, flow=eval(args.flow)),
    }
    t0 = time.monotonic()
    out = processor.run_uproot_job(
        args.partition_fileset,
        treename="Events",
        processor_instance=processors[args.processor],
        executor=processor.futures_executor,
        executor_args={"schema": processor.NanoAODSchema, "workers": 4},
    )
    exec_time = format_timespan(time.monotonic() - t0)

    print(f"Execution time: {exec_time}")
    with open(f"{args.output_path}/{args.dataset_key}.pkl", "wb") as handle:
        pickle.dump(out, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processor",
        dest="processor",
        type=str,
        default="ztojets",
        help="processor to be used {ztojets}",
    )
    parser.add_argument(
        "--dataset_key",
        dest="dataset_key",
        type=str,
        default="",
        help="dataset_key",
    )
    parser.add_argument(
        "--partition_fileset",
        dest="partition_fileset",
        type=json.loads,
        help="partition_fileset needed to preprocess a fileset",
    )
    parser.add_argument(
        "--year",
        dest="year",
        type=str,
        default="",
        help="year of the data {2016preVFP, 2016postVFP, 2017, 2018}",
    )
    parser.add_argument(
        "--output_path",
        dest="output_path",
        type=str,
        help="output path",
    )
    parser.add_argument(
        "--flow",
        dest="flow",
        type=str,
        default="True",
        help="whether to include underflow/overflow to first/last bin {True, False}",
    )
    args = parser.parse_args()
    main(args)
