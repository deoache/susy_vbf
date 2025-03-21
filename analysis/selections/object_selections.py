import vector
import inspect
import numpy as np
import awkward as ak
from analysis.working_points import working_points


def delta_r_mask(first, second, threshold=0.4):
    """select objects from 'first' which are at least 'threshold' away from all objects in 'second'."""
    mval = first.metric_table(second)
    return ak.all(mval > threshold, axis=-1)


class ObjectSelector:

    def __init__(self, object_selection_config, year):
        self.object_selection_config = object_selection_config
        self.year = year

    def select_objects(self, events):
        self.objects = {}
        self.events = events

        for obj_name, obj_config in self.object_selection_config.items():
            # check if object is defined from events or user defined function
            if "events" in obj_config["field"]:
                self.objects[obj_name] = eval(obj_config["field"])
            else:
                selection_function = getattr(self, obj_config["field"])
                selection_function()
            if "add_cut" in obj_config:
                for field_to_add in obj_config["add_cut"]:
                    selection_mask = self.get_selection_mask(
                        events=events,
                        obj_name=obj_name,
                        cuts=obj_config["add_cut"][field_to_add],
                    )
                    self.objects[obj_name][field_to_add] = selection_mask
            if "cuts" in obj_config:
                selection_mask = self.get_selection_mask(
                    events=events, obj_name=obj_name, cuts=obj_config["cuts"]
                )
                self.objects[obj_name] = self.objects[obj_name][selection_mask]
        return self.objects

    def get_selection_mask(self, events, obj_name, cuts):
        # bring objects and year to local scope
        objects = self.objects
        year = self.year
        # initialize selection mask
        selection_mask = ak.ones_like(self.objects[obj_name].pt, dtype=bool)
        # iterate over all cuts
        for str_mask in cuts:
            mask = eval(str_mask)
            selection_mask = np.logical_and(selection_mask, mask)
        return selection_mask

    def select_dijets(self):
        # create pair combinations with all jets (VBF selection)
        dijets = ak.combinations(self.objects["jets"], 2, fields=["j1", "j2"])
        # add dijet 4-momentum field
        dijets["p4"] = dijets.j1 + dijets.j2
        dijets["pt"] = dijets.p4.pt
        self.objects["dijets"] = dijets

    def select_dimuons(self):
        # create pair combinations with all muons
        dimuons = ak.combinations(self.objects["muons"], 2, fields=["mu1", "mu2"])
        # add dimuon 4-momentum field
        dimuons["p4"] = dimuons.mu1 + dimuons.mu2
        dimuons["pt"] = dimuons.p4.pt
        self.objects["dimuons"] = dimuons

    def select_met(self):
        # add muons pT to MET to simulate a 0-lepton final state
        all_muons = ak.sum(self.objects["muons"], axis=1)
        muons2D = ak.zip(
            {
                "pt": all_muons.pt,
                "phi": all_muons.phi,
            },
            with_name="Momentum2D",
            behavior=vector.backends.awkward.behavior,
        )
        met2D = ak.zip(
            {
                "pt": self.events.MET.pt,
                "phi": self.events.MET.phi,
            },
            with_name="Momentum2D",
            behavior=vector.backends.awkward.behavior,
        )
        self.objects["met"] = met2D + muons2D

    def select_max_mass_dijet(self):
        self.objects["max_dijet_mass"] = ak.max(self.objects["dijets"].p4.mass, axis=1)

    def select_max_mass_dijet_eta(self):
        dijets_idx = ak.local_index(self.objects["dijets"], axis=1)
        max_mass_idx = ak.argmax(self.objects["dijets"].p4.mass, axis=1)
        max_mass_dijet = self.objects["dijets"][max_mass_idx == dijets_idx]
        self.objects["max_dijet_mass_eta"] = ak.firsts(
            np.abs(max_mass_dijet.j1.eta - max_mass_dijet.j2.eta)
        )
