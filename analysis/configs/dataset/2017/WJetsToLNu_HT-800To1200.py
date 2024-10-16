from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="WJetsToLNu_HT-800To1200",
    process="WJetsToLNu",
    query="WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v3/NANOAODSIM",
    year="2017",
    is_mc="True",
    xsec=5.366,
    partitions=3,
)
