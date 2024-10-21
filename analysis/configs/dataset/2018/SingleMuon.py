from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="SingleMuon",
    process="Data",
    query="['SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD']",
    year="2018",
    is_mc="False",
    xsec=None,
    partitions=15,
)