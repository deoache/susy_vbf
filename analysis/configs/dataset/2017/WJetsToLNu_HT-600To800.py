from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="WJetsToLNu_HT-600To800",
    process="WJetsToLNu",
    query="WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM",
    year="2017",
    is_mc="True",
    xsec=12.87,
    partitions=2,
)