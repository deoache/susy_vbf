# susy_vbf

#### How to submit jobs

Connect to lxplus and clone the repository (if you have not done it yet)
```
# connect to lxplus 
ssh <your_username>@lxplus.cern.ch

# clone the repository 
git clone https://github.com/deoache/susy_vbf.git
cd susy_vbf
```

You need to have a valid grid proxy in the CMS VO. (see [here](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideLcgAccess) for details on how to register in the CMS VO). The needed grid proxy is obtained via the usual command
```
voms-proxy-init --voms cms
```

Use the [make_filesets.py](https://github.com/deoache/susy_vbf/blob/main/analysis/fileset/make_filesets.py) script to build the input filesets with xrootd endpoints:
```
# get the singularity shell 
singularity shell -B /afs -B /eos -B /cvmfs /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest-py3.10

# move to the fileset directory
cd analysis/fileset/

# run the 'make_filesets' script
python make_filesets.py --year <year>

# exit the singularity
exit
```

Jobs are submitted via the `submit_condor.py` script:
```
usage: submit_condor.py [-h] [--processor PROCESSOR] [--dataset DATASET] [--year YEAR] [--flow FLOW] [--submit SUBMIT] [--label LABEL] [--eos EOS]

optional arguments:
  -h, --help            show this help message and exit
  --processor PROCESSOR
                        processor to be used (default ztojets)
  --dataset DATASET     sample key to be processed
  --year YEAR           year of the data {2016preVFP, 2016postVFP, 2017, 2018} (default 2017)
  --flow FLOW           whether to include underflow/overflow to first/last bin {True, False} (default True)
  --submit SUBMIT       if True submit job to Condor. If False, it just builds datasets and condor files (default True)
  --label LABEL         Tag to label the run (default ztojets_CR)
  --eos EOS             if True save outputs to /eos (default True)
```
Example:
```
python3 submit_condor.py --processor ztojets --dataset <sample> --year 2017 --label test
```
Outputs will be save to `/eos/user/<username first letter>/<username>/susy_vbf/outs/<processor>/<label>/<year>`