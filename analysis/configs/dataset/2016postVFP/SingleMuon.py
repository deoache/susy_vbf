from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="SingleMuon",
    process="Data",
    query="['SingleMuon/Run2016F-UL2016_MiniAODv2_NanoAODv9-v1/NANOAOD', 'SingleMuon/Run2016G-UL2016_MiniAODv2_NanoAODv9-v1/NANOAOD', 'SingleMuon/Run2016H-UL2016_MiniAODv2_NanoAODv9-v1/NANOAOD']",
    year="2016postVFP",
    is_mc="False",
    xsec=None,
    partitions=15,
)
