from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(name = "SingleMuon",
                               process= "Data",
                               query= "['SingleMuon/Run2016B-ver1_HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2016B-ver2_HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2016C-HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2016D-HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2016E-HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD', 'SingleMuon/Run2016F-HIPM_UL2016_MiniAODv2_NanoAODv9-v2/NANOAOD']",
                               year= "2016APV",
                               is_mc= "False"
                               xsec= None,
                               partitions= {'nsplit': 15})