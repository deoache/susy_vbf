from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="WJetsToLNu_HT-2500ToInf",
    process="WJetsToLNu",
    query="WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v2/NANOAODSIM",
    year="2017",
    is_mc="True",
    xsec=0.008001,
    partitions=2,
)
