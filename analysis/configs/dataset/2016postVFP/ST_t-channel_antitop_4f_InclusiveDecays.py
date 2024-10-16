from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="ST_t-channel_antitop_4f_InclusiveDecays",
    process="SingleTop",
    query="ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM",
    year="2016postVFP",
    is_mc="True",
    xsec=71.74,
    partitions=5,
)
