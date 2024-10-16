from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(name = "WJetsToLNu_HT-400To600",
                               process= "WJetsToLNu",
                               query= "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
                               year= "2018",
                               is_mc= "True"
                               xsec= 57.48,
                               partitions= {'nsplit': 5})