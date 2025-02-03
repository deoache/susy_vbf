import copy
import numpy as np
import awkward as ak
from coffea import processor
from coffea.analysis_tools import PackedSelection, Weights
from analysis.configs import ProcessorConfigBuilder
from analysis.histograms import HistBuilder, fill_histogram
from analysis.corrections.jec import apply_jet_corrections
from analysis.corrections.rochester import apply_rochester_corrections
from analysis.corrections.tau_energy import apply_tau_energy_scale_corrections
from analysis.corrections.pileup import add_pileup_weight
from analysis.corrections.l1prefiring import add_l1prefiring_weight
from analysis.corrections.pujetid import add_pujetid_weight
from analysis.corrections.btag import BTagCorrector
from analysis.corrections.muon_highpt import MuonHighPtCorrector
from analysis.corrections.tau import TauCorrector
from analysis.corrections.electron import ElectronCorrector
from analysis.corrections.met import apply_met_phi_corrections, update_met_jet_veto
from analysis.selections import (
    ObjectSelector,
    get_lumi_mask,
    get_trigger_mask,
    get_trigger_match_mask,
    get_metfilters_mask,
    get_stitching_mask,
    get_hemcleaning_mask,
)


def update(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items():
        out = ak.with_field(out, value, name)
    return out


class Ttbar(processor.ProcessorABC):
    def __init__(
        self,
        year: str = "2017",
        channel: str = "1b1l",
        lepton_flavor: str = "mu",
        flow: bool = True,
        systematics: bool = False,
    ):
        self.year = year
        self.channel = channel
        self.lepton_flavor = lepton_flavor
        self.flow = flow
        self.systematics = systematics

        config_builder = ProcessorConfigBuilder(
            processor="ttbar", channel=channel, lepton_flavor=lepton_flavor, year=year
        )
        self.processor_config = config_builder.build_processor_config()
        self.histogram_config = self.processor_config.histogram_config
        self.histograms = HistBuilder(self.processor_config).build_histogram()

    def process(self, events):
        # check if sample is MC
        self.is_mc = hasattr(events, "genWeight")
        if not self.is_mc:
            # nominal JEC are already applied in data
            return self.process_shift(events, None)

        # apply JEC/JER corrections to jets (in data, the corrections are already applied)
        apply_jet_corrections(events, self.year)
        # define Jet/MET shifts
        shifts = [({"Jet": events.Jet, "MET": events.MET}, None)]
        if self.systematics:
            shifts.extend(
                [
                    (
                        {"Jet": events.Jet.JES_jes.up, "MET": events.MET.JES_jes.up},
                        "JESUp",
                    ),
                    (
                        {
                            "Jet": events.Jet.JES_jes.down,
                            "MET": events.MET.JES_jes.down,
                        },
                        "JESDown",
                    ),
                    (
                        {"Jet": events.Jet, "MET": events.MET.MET_UnclusteredEnergy.up},
                        "UESUp",
                    ),
                    (
                        {
                            "Jet": events.Jet,
                            "MET": events.MET.MET_UnclusteredEnergy.down,
                        },
                        "UESDown",
                    ),
                    ({"Jet": events.Jet.JER.up, "MET": events.MET.JER.up}, "JERUp"),
                    (
                        {"Jet": events.Jet.JER.down, "MET": events.MET.JER.down},
                        "JERDown",
                    ),
                ]
            )
        return processor.accumulate(
            self.process_shift(update(events, collections), name)
            for collections, name in shifts
        )

    def process_shift(self, events, shift_name):
        # get systematic variation
        syst_var = "nominal" if (shift_name is None) else shift_name
        # get year and number of events
        year = self.year
        nevents = len(events)
        # get dataset name
        dataset = events.metadata["dataset"]
        # check if sample is MC
        is_mc = self.is_mc
        # get golden json, HLT paths and selections
        goldenjson = self.processor_config.goldenjson
        hlt_paths = self.processor_config.hlt_paths
        object_selection = self.processor_config.object_selection
        event_selection = self.processor_config.event_selection
        # create copies of histogram objects
        hist_dict = copy.deepcopy(self.histograms)
        # initialize output dictionary
        output = {}
        output["metadata"] = {}
        if syst_var == "nominal":
            output["metadata"].update({"raw_initial_nevents": nevents})

        if is_mc:
            # apply energy corrections to taus (only to MC)
            apply_tau_energy_scale_corrections(
                events=events, year=year, variation=syst_var
            )
        # apply rochester corretions to muons
        apply_rochester_corrections(
            events=events, is_mc=is_mc, year=year, variation=syst_var
        )
        # apply MET phi modulation corrections
        apply_met_phi_corrections(
            events=events,
            is_mc=is_mc,
            year=year,
        )
        # propagate jet_veto maps to MET
        if "jetsvetomaps" in object_selection["bjets"]["cuts"]:
            update_met_jet_veto(events, year)

        # -------------------------------------------------------------
        # event SF/weights computation
        # -------------------------------------------------------------
        # set weights container
        weights_container = Weights(len(events), storeIndividual=True)
        if is_mc:
            # add gen weigths
            weights_container.add("genweight", events.genWeight)
            # add l1prefiring weigths
            add_l1prefiring_weight(events, weights_container, year, syst_var)
            # add pileup weigths
            add_pileup_weight(events, weights_container, year, syst_var)
            # add pujetid weigths
            add_pujetid_weight(
                jets=events.Jet,
                weights=weights_container,
                year=year,
                working_point=object_selection["bjets"]["cuts"]["jets_pileup_id"],
                variation=syst_var,
            )
            # b-tagging corrector
            btag_corrector = BTagCorrector(
                events=events,
                weights=weights_container,
                sf_type="comb",
                worging_point=object_selection["bjets"]["cuts"]["jets_deepjet_b"],
                year=year,
                full_run=False,
                variation=syst_var,
            )
            # add b-tagging weights
            btag_corrector.add_btag_weights(flavor="bc")
            btag_corrector.add_btag_weights(flavor="light")
            # electron corrector
            electron_corrector = ElectronCorrector(
                electrons=events.Electron,
                weights=weights_container,
                year=year,
            )
            # add electron ID weights
            electron_corrector.add_id_weight(
                id_working_point=object_selection["electrons"]["cuts"]["electrons_id"],
            )
            # add electron reco weights
            electron_corrector.add_reco_weight("RecoAbove20")
            electron_corrector.add_reco_weight("RecoBelow20")

            # muon corrector
            muon_corrector = MuonHighPtCorrector(
                events=events,
                weights=weights_container,
                year=year,
                variation=syst_var,
                id_wp=object_selection["muons"]["cuts"]["muons_id"],
                iso_wp=object_selection["muons"]["cuts"]["muons_iso"],
            )
            # add muon RECO weights
            muon_corrector.add_reco_weight()
            # add muon ID weights
            muon_corrector.add_id_weight()
            # add muon iso weights
            muon_corrector.add_iso_weight()
            # add trigger weights
            muon_corrector.add_triggeriso_weight(hlt_paths)

            # add tau weights
            tau_corrector = TauCorrector(
                events=events,
                weights=weights_container,
                year=year,
                tau_vs_jet=object_selection["taus"]["cuts"]["taus_vs_jet"],
                tau_vs_ele=object_selection["taus"]["cuts"]["taus_vs_ele"],
                tau_vs_mu=object_selection["taus"]["cuts"]["taus_vs_mu"],
                variation=syst_var,
            )
            tau_corrector.add_id_weight_deeptauvse()
            tau_corrector.add_id_weight_deeptauvsmu()
            tau_corrector.add_id_weight_deeptauvsjet()
        if syst_var == "nominal":
            # save sum of weights before object_selection
            output["metadata"].update({"sumw": ak.sum(weights_container.weight())})

        # -------------------------------------------------------------
        # object selection
        # -------------------------------------------------------------
        object_selector = ObjectSelector(object_selection, year)
        objects = object_selector.select_objects(events)
        # -------------------------------------------------------------
        # event selection
        # -------------------------------------------------------------
        # itinialize selection manager
        selection_manager = PackedSelection()
        # add all selections to selector manager
        for selection, mask in event_selection["selections"].items():
            selection_manager.add(selection, eval(mask))

        categories = event_selection["categories"]
        for category, category_cuts in categories.items():
            # get selection mask by category
            category_mask = selection_manager.all(*category_cuts)
            nevents_after = ak.sum(category_mask)

            if syst_var == "nominal":
                # save cutflow to metadata
                output["metadata"][category] = {"cutflow": {}}
                selections = []
                for cut_name in category_cuts:
                    selections.append(cut_name)
                    current_selection = selection_manager.all(*selections)
                    output["metadata"][category]["cutflow"][cut_name] = ak.sum(
                        weights_container.weight()[current_selection]
                    )
                # save number of events after selection to metadata
                output["metadata"][category].update(
                    {
                        "weighted_final_nevents": ak.sum(
                            weights_container.weight()[category_mask]
                        ),
                        "raw_final_nevents": nevents_after,
                    }
                )
            # -------------------------------------------------------------
            # analysis variables
            # -------------------------------------------------------------
            # check that there are events left after selection
            if nevents_after > 0:
                # build analysis variables map
                variables_map = {}
                for variable, axis in self.histogram_config.axes.items():
                    variables_map[variable] = eval(axis.expression)[category_mask]
                # -------------------------------------------------------------
                # histogram filling
                # -------------------------------------------------------------
                # break up the histogram filling for event-wise variations and object-wise variations
                # apply event-wise variations only for nominal
                if is_mc and syst_var == "nominal":
                    # get event weight systematic variations for MC samples
                    variations = ["nominal"] + list(weights_container.variations)
                    for variation in variations:
                        if variation == "nominal":
                            category_weight = weights_container.weight()[category_mask]
                        else:
                            category_weight = weights_container.weight(
                                modifier=variation
                            )[category_mask]
                        fill_histogram(
                            histograms=hist_dict,
                            histogram_config=self.histogram_config,
                            variables_map=variables_map,
                            weights=category_weight,
                            variation=variation,
                            category=category,
                            flow=self.flow,
                        )
                else:
                    # fill Data/object-wise variations for MC samples
                    category_weight = weights_container.weight()[category_mask]
                    fill_histogram(
                        histograms=hist_dict,
                        histogram_config=self.histogram_config,
                        variables_map=variables_map,
                        weights=category_weight,
                        variation=syst_var,
                        category=category,
                        flow=self.flow,
                    )
        # define output dictionary accumulator
        output["histograms"] = hist_dict
        return output

    def postprocess(self, accumulator):
        return accumulator