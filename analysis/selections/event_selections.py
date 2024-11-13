import json
import numpy as np
import awkward as ak
import importlib.resources
from coffea.lumi_tools import LumiMask
from analysis.selections import trigger_match
from coffea.analysis_tools import PackedSelection


def get_metfilters_mask(events, year):
    with importlib.resources.path("analysis.data", "metfilters.json") as path:
        with open(path, "r") as handle:
            metfilters = json.load(handle)[year]
    metfilters_mask = np.ones(len(events), dtype="bool")
    metfilterkey = "mc" if hasattr(events, "genWeight") else "data"
    for mf in metfilters[metfilterkey]:
        if mf in events.Flag.fields:
            metfilters_mask = metfilters_mask & events.Flag[mf]
    return metfilters_mask


def get_lumi_mask(events, goldenjson):
    if hasattr(events, "genWeight"):
        lumi_mask = np.ones(len(events), dtype="bool")
    else:
        lumi_info = LumiMask(goldenjson)
        lumi_mask = lumi_info(events.run, events.luminosityBlock)
    return lumi_mask


def get_trigger_mask(events, hlt_paths):
    trigger_mask = np.zeros(len(events), dtype="bool")
    
    for hlt_path in hlt_paths:
        if hlt_path in events.HLT.fields:
            trigger_mask = trigger_mask | events.HLT[hlt_path]
    return trigger_mask


def get_trigger_match_mask(events, hlt_paths, lepton="Muon"):
    trigger_match_mask = np.zeros(len(events), dtype="bool")
    for hlt_path in hlt_paths:
        trig_match = trigger_match(
            leptons=events[lepton],
            trigobjs=events.TrigObj,
            trigger_path=hlt_path,
        )
        trigger_match_mask = trigger_match_mask | trig_match
    return ak.sum(trigger_match_mask, axis=-1) > 0


def get_stitching_mask(events, dataset, dataset_key, ht_value):
    stitching_mask = np.ones(len(events), dtype="bool")
    if dataset.startswith(dataset_key):
        stitching_mask = events.LHE.HT < ht_value
    return stitching_mask


def get_hemcleaning_mask(events):
    # hem-cleaning selection
    # https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html
    # Due to the HEM issue in year 2018, we veto the events with jets and electrons in the
    # region -3 < eta <-1.3 and -1.57 < phi < -0.87 to remove fake MET
    hem_veto = ak.any(
        (
            (events.Jet.eta > -3.2)
            & (events.Jet.eta < -1.3)
            & (events.Jet.phi > -1.57)
            & (events.Jet.phi < -0.87)
        ),
        -1,
    ) | ak.any(
        (
            (events.Electron.pt > 30)
            & (events.Electron.eta > -3.2)
            & (events.Electron.eta < -1.3)
            & (events.Electron.phi > -1.57)
            & (events.Electron.phi < -0.87)
        ),
        -1,
    )
    hem_cleaning = (
        (
            (events.run >= 319077) & (not hasattr(events, "genWeight"))
        )  # if data check if in Runs C or D
        # else for MC randomly cut based on lumi fraction of C&D
        | ((np.random.rand(len(events)) < 0.632) & hasattr(events, "genWeight"))
    ) & (hem_veto)

    return ~hem_cleaning           