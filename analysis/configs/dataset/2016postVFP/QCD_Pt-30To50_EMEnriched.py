from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="QCD_Pt-30To50_EMEnriched",
    process="QCD",
    query="QCD_Pt-30to50_EMEnriched_TuneCP5_13TeV-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v2/NANOAODSIM",
    year="2016postVFP",
    is_mc="True",
    xsec=9928000.0,
    partitions=3,
)
