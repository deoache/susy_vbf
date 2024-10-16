from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(name = "EWKWPlus2Jets_WToLNu",
                               process= "EWK",
                               query= "EWKWPlus2Jets_WToLNu_M-50_TuneCP5_withDipoleRecoil_13TeV-madgraph-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM",
                               year= "2018",
                               is_mc= "True"
                               xsec= 25.81,
                               partitions= {'nsplit': 3})