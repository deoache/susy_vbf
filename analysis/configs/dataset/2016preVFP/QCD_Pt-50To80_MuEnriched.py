from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="QCD_Pt-50To80_MuEnriched",
    process="QCD",
    query="QCD_Pt-50To80_MuEnrichedPt5_TuneCP5_13TeV-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v2/NANOAODSIM",
    year="2016preVFP",
    is_mc="True",
    xsec=437504.5,
    partitions=5,
)