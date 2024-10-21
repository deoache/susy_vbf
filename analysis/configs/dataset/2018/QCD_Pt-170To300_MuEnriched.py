from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="QCD_Pt-170To300_MuEnriched",
    process="QCD",
    query="QCD_Pt-170To300_MuEnrichedPt5_TuneCP5_13TeV-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM",
    year="2018",
    is_mc="True",
    xsec=8654.5,
    partitions=10,
)