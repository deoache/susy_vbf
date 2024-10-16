from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(
    name="Tau",
    process="Data",
    query="['Tau/Run2017B-UL2017_MiniAODv2_NanoAODv9-v1/NANOAOD', 'Tau/Run2017C-UL2017_MiniAODv2_NanoAODv9-v1/NANOAOD', 'Tau/Run2017D-UL2017_MiniAODv2_NanoAODv9-v1/NANOAOD', 'Tau/Run2017E-UL2017_MiniAODv2_NanoAODv9-v2/NANOAOD', 'Tau/Run2017F-UL2017_MiniAODv2_NanoAODv9-v1/NANOAOD']",
    year="2017",
    is_mc="False",
    xsec=None,
    partitions=15,
)
