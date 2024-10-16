from analysis.configs.dataset_config import DatasetConfig


dataset_config = DatasetConfig(name = "TTToSemiLeptonic",
                               process= "tt",
                               query= "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM",
                               year= "2016",
                               is_mc= "True"
                               xsec= 365.34,
                               partitions= {'nsplit': 12})