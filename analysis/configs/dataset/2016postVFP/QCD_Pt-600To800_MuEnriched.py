from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="QCD_Pt-600To800_MuEnriched",
    process="QCD",
    query="QCD_Pt-600To800_MuEnrichedPt5_TuneCP5_13TeV-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM",
    year="2016postVFP",
    is_mc="True",
    xsec=25.1,
    partitions=6,
)