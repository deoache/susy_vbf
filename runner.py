import os
import argparse

data_samples = {
    "ztojets": {
        "2017": ["SingleMuonB", "SingleMuonC", "SingleMuonD", "SingleMuonE", "SingleMuonF"],
    },
    "ttbar": {
        "2017": ["SingleMuonB", "SingleMuonC", "SingleMuonD", "SingleMuonE", "SingleMuonF"],
    }
}
background_samples = {
    "ztojets": [
        # DYJetsToLL
        "DYJetsToLL_M-4to50_HT-100to200",
        "DYJetsToLL_M-4to50_HT-200to400",
        "DYJetsToLL_M-4to50_HT-400to600",
        "DYJetsToLL_M-4to50_HT-600toInf",
        "DYJetsToLL_M-50_HT-100to200",
        "DYJetsToLL_M-50_HT-1200to2500",
        "DYJetsToLL_M-50_HT-200to400",
        "DYJetsToLL_M-50_HT-2500toInf",
        "DYJetsToLL_M-50_HT-400to600",
        "DYJetsToLL_M-50_HT-600to800",
        "DYJetsToLL_M-50_HT-70to100",
        "DYJetsToLL_M-50_HT-800to1200",
        "DYJetsToLL_inclusive_10to50",
        "DYJetsToLL_inclusive_50",
        # EWK
        "EWKWMinus2Jets_WToLNu",
        "EWKWPlus2Jets_WToLNu",
        "EWKZ2Jets_ZToLL",
        "EWKZ2Jets_ZToNuNu",
        # Higgs
        "GluGluHToWWToLNuQQ",
        "VBFHToWWTo2L2Nu",
        "VBFHToWWToLNuQQ",
        # SingleTop
        "ST_s-channel_4f_leptonDecays",
        "ST_t-channel_antitop_4f_InclusiveDecays",
        "ST_t-channel_top_4f_InclusiveDecays",
        "ST_tW_antitop_5f_inclusiveDecays",
        "ST_tW_top_5f_inclusiveDecays",
        # tt
        "TTTo2L2Nu",
        "TTToHadronic",
        "TTToSemiLeptonic",
        # WJetsToLNu
        "WJetsToLNu_HT-100To200",
        "WJetsToLNu_HT-1200To2500",
        "WJetsToLNu_HT-200To400",
        "WJetsToLNu_HT-2500ToInf",
        "WJetsToLNu_HT-400To600",
        "WJetsToLNu_HT-600To800",
        "WJetsToLNu_HT-800To1200",
        "WJetsToLNu_inclusive",
        # Diboson
        "WW",
        "WZ",
        "ZZ",
    ],
    "ttbar": [
        # DYJetsToLL
        "DYJetsToLL_M-4to50_HT-100to200",
        "DYJetsToLL_M-4to50_HT-200to400",
        "DYJetsToLL_M-4to50_HT-400to600",
        "DYJetsToLL_M-4to50_HT-600toInf",
        "DYJetsToLL_M-50_HT-100to200",
        "DYJetsToLL_M-50_HT-1200to2500",
        "DYJetsToLL_M-50_HT-200to400",
        "DYJetsToLL_M-50_HT-2500toInf",
        "DYJetsToLL_M-50_HT-400to600",
        "DYJetsToLL_M-50_HT-600to800",
        "DYJetsToLL_M-50_HT-70to100",
        "DYJetsToLL_M-50_HT-800to1200",
        "DYJetsToLL_inclusive_10to50",
        "DYJetsToLL_inclusive_50",
        # Higgs
        "GluGluHToWWToLNuQQ",
        "VBFHToWWTo2L2Nu",
        "VBFHToWWToLNuQQ",
        # SingleTop
        "ST_s-channel_4f_leptonDecays",
        "ST_t-channel_antitop_5f_InclusiveDecays",
        "ST_t-channel_top_5f_InclusiveDecays",
        "ST_tW_antitop_5f_inclusiveDecays",
        "ST_tW_top_5f_inclusiveDecays",
        # tt
        "TTTo2L2Nu",
        "TTToHadronic",
        "TTToSemiLeptonic",
        # WJetsToLNu
        "WJetsToLNu_HT-100To200",
        "WJetsToLNu_HT-1200To2500",
        "WJetsToLNu_HT-200To400",
        "WJetsToLNu_HT-2500ToInf",
        "WJetsToLNu_HT-400To600",
        "WJetsToLNu_HT-600To800",
        "WJetsToLNu_HT-800To1200",
        # Diboson
        "WW",
        "WZ",
        "ZZ",
    ]
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processor",
        dest="processor",
        type=str,
        default="ttbar",
        help="processor to be used {ztojets} (default ztojets)",
    )
    parser.add_argument(
        "--year",
        dest="year",
        type=str,
        default="2017",
        help="dataset year {2017} (default 2017)",
    )
    parser.add_argument(
        "--nfiles",
        dest="nfiles",
        type=int,
        default=5,
        help="number of root files to include in each dataset partition (default 7)",
    )
    parser.add_argument(
        "--label",
        dest="label",
        type=str,
        default="test",
        help="Tag to label the run (default ztojets_CR)",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Enable Condor job submission. If not provided, it just builds condor files",
    )
    parser.add_argument(
        "--eos",
        action="store_true",
        help="Enable saving outputs to /eos",
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
        default="1b1l",
        help="channel to be processed (1b1l, 2b1l)",
    )
    parser.add_argument(
        "--systematics",
        action="store_true",
        help="Enable applying jerc systematics",
    )
    args = parser.parse_args()

    datasets = background_samples[args.processor] + data_samples[args.processor][args.year]
    for dataset in datasets:
        cmd = f"python3 submit_condor.py --processor {args.processor} --year {args.year} --dataset {dataset} --label {args.label} --nfiles {args.nfiles} --channel {args.channel} --lepton_flavor {args.lepton_flavor} --nfiles {args.nfiles} --flow"
        if args.submit:
            cmd += " --submit"
        if args.eos:
            cmd += " --eos"
        if args.systematics:
            cmd += " --systematics"
        os.system(cmd)