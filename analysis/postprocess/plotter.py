import yaml
import logging
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import ticker
from coffea.processor import accumulate
from hist.intervals import poisson_interval, ratio_uncertainty
from analysis.configs import ProcessorConfigBuilder
from analysis.postprocess.utils import setup_logger, divide_by_binwidth


np.seterr(invalid="ignore")
np.seterr(divide="ignore")


hep.style.use(hep.style.CMS)
plt.rcParams.update(
    {
        "font.size": 20,
        "axes.titlesize": 30,
        "axes.labelsize": 20,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,
        "lines.markersize": 30,
        "legend.fontsize": 12,
        "xtick.minor.width": 1,
        "xtick.minor.size": 4,
        "xtick.major.width": 1,
        "xtick.major.size": 6,
        "ytick.minor.width": 1,
        "ytick.minor.size": 4,
        "ytick.major.width": 1,
        "ytick.major.size": 6,
    }
)
mc_hist_kwargs = {
    "histtype": "fill",
    "stack": True,
    "sort": "yield",
    "linewidth": 0.7,
    "edgecolor": "k",
}
data_hist_kwargs = {
    "histtype": "errorbar",
    "color": "k",
    "linestyle": "none",
    "marker": ".",
    "markersize": 13,
    "elinewidth": 1,
    "yerr": True,
    "xerr": True,
    "linestyle": "none",
    "marker": ".",
}


class Plotter:
    def __init__(
        self,
        processor: str,
        processed_histograms: dict,
        year: str,
        lumi: int,
        output_dir: str = None,
    ):
        self.processor = processor
        self.processed_histograms = processed_histograms
        self.year = year
        self.lumi = lumi
        self.output_dir = output_dir
        self.set_color_map()

        # get histogram config
        config_builder = ProcessorConfigBuilder(processor=processor, year=year)
        processor_config = config_builder.build_processor_config()
        self.histogram_config = processor_config.histogram_config

    def set_color_map(self):
        # set color map
        # https://cms-analysis.docs.cern.ch/guidelines/plotting/colors/
        colors = [
            "#3f90da",
            "#ffa90e",
            "#bd1f01",
            "#94a4a2",
            "#832db6",
            "#a96b59",
            "#e76300",
            "#b9ac70",
            "#717581",
            "#92dadd",
        ]
        with open(f"{Path.cwd()}/analysis/filesets/{self.year}_fileset.yaml", "r") as f:
            dataset_configs = yaml.safe_load(f)
        processes = sorted(
            set(
                dataset_configs[sample]["process"]
                for sample in dataset_configs
                if dataset_configs[sample]["process"] != "Data"
            )
        )
        self.color_map = {process: color for process, color in zip(processes, colors)}

    def get_variable_label(self, variable):
        if variable in self.histogram_config.axes:
            variable_label = self.histogram_config.axes[variable]["label"]
        else:
            for key in self.histogram_config.axes:
                if variable in self.histogram_config[key]:
                    variable_label = self.histogram_config[key][variable]["label"]
                    break
        return variable_label

    def get_axis_type(self, variable):
        if variable in self.histogram_config.axes:
            axis_type = self.histogram_config.axes[variable]["type"]
        else:
            for key in self.histogram_config.axes:
                if variable in self.histogram_config[key]:
                    axis_type = self.histogram_config[key][variable]["type"]
                    break
        return axis_type

    def get_histogram(
        self,
        process,
        variable,
        variation,
        category,
        histogram_dict,
    ):
        """returns histogram by processes/variable/category"""

        # get histogram from histogram dictionary
        if variable in histogram_dict:
            histogram = histogram_dict[variable]
        else:
            for key in histogram_dict:
                if variable in histogram_dict[key].axes.name:
                    histogram = histogram_dict[key]
                    break

        # get variable histogram for nominal variation and category
        histogram = histogram[{"variation": variation, "category": category}].project(
            variable
        )

        # check if axis is variable type
        if self.get_axis_type(variable) == "Variable":
            histogram = divide_by_binwidth(histogram)
        return histogram

    def get_variations_keys(self):
        variations = {}
        for process, histogram_dict in self.processed_histograms.items():
            for feature in histogram_dict:
                helper_histogram = histogram_dict[feature]
                variations = [
                    var
                    for var in helper_histogram.axes["variation"]
                    if var != "nominal"
                ]
                break
            break
        variations = list(
            set([var.replace("Up", "").replace("Down", "") for var in variations])
        )
        return variations

    def get_variations(
        self,
        process,
        variable,
        category,
        variation,
        histogram_dict,
    ):
        """returns variation histogram by processes/variable/category"""
        # get histogram from histogram dictionary
        if variable in histogram_dict:
            histogram = histogram_dict[variable]
        else:
            for key in histogram_dict:
                if variable in histogram_dict[key].axes.name:
                    histogram = histogram_dict[key]
                    break

        # get variable histogram for nominal variation and category
        histogram_up = histogram[
            {"variation": f"{variation}Up", "category": category}
        ].project(variable)
        histogram_down = histogram[
            {"variation": f"{variation}Down", "category": category}
        ].project(variable)

        # check if axis is variable type
        if self.get_axis_type(variable) == "Variable":
            histogram_up = divide_by_binwidth(histogram_up)
            histogram_down = divide_by_binwidth(histogram_down)

        return histogram_up, histogram_down

    def get_histogram_config(self, variable, category):
        histogram_info = {"nominal": {}, "variations": {}}
        for process, histogram_dict in self.processed_histograms.items():
            if process == "Data":
                histogram_info["data"] = self.get_histogram(
                    process=process,
                    variable=variable,
                    category=category,
                    variation="nominal",
                    histogram_dict=histogram_dict,
                )
            else:
                # save nominal histogram
                histogram = self.get_histogram(
                    process=process,
                    variable=variable,
                    category=category,
                    variation="nominal",
                    histogram_dict=histogram_dict,
                )
                histogram_info["nominal"][process] = histogram

                # save variations histograms
                for variation in self.get_variations_keys():
                    up, down = self.get_variations(
                        process=process,
                        variable=variable,
                        category=category,
                        variation=variation,
                        histogram_dict=histogram_dict,
                    )
                    if f"{variation}Up" in histogram_info["variations"]:
                        histogram_info["variations"][f"{variation}Up"] += up
                        histogram_info["variations"][f"{variation}Down"] += up
                    else:
                        histogram_info["variations"][f"{variation}Up"] = up
                        histogram_info["variations"][f"{variation}Down"] = down

        return histogram_info

    def get_colors_and_labels(self, histogram_info):
        colors, labels = [], []
        for process in histogram_info["nominal"]:
            labels.append(process)
            colors.append(self.color_map[process])
        return labels, colors

    def plot_uncert_band(self, histogram_info, ax):
        # get up and down stat uncertainty per bin
        nom_stat_down, nom_stat_up = poisson_interval(
            values=self.nominal_values, variances=self.nominal_variances
        )
        # initialize up and down errors per bin
        bin_error_up = np.abs(nom_stat_up - self.nominal_values) ** 2
        bin_error_down = np.abs(nom_stat_down - self.nominal_values) ** 2
        # add variation errors to bin errors
        variations_mc_hists = histogram_info["variations"]
        for variation, variation_hist in variations_mc_hists.items():
            variation_values = variation_hist.values()
            if "Up" in variation:
                # add up variation
                max_values = np.max(
                    np.stack([self.nominal_values, variation_values]), axis=0
                )
                up_variation_values = np.abs(max_values - self.nominal_values)
                bin_error_up += up_variation_values**2
            else:
                # add down variation
                min_values = np.min(
                    np.stack([self.nominal_values, variation_values]), axis=0
                )
                down_variation_values = np.abs(min_values - self.nominal_values)
                bin_error_down += down_variation_values**2
        self.band_up = self.nominal_values + np.sqrt(bin_error_up)
        self.band_down = self.nominal_values - np.sqrt(bin_error_down)
        # plot stat + syst uncertainty band
        ax.bar(
            x=self.centers,
            height=self.band_up - self.band_down,
            width=self.widths,
            bottom=self.band_down,
            color="lightgray",
            alpha=0.6,
            label="Stat + Syst unc.",
            hatch="/" * 3,
            edgecolor="black",
            linewidth=0,
        )

    def plot_ratio(self, rax):
        # compute Data/MC ratio
        ratio = self.data_values / self.nominal_values
        # plot ratio x error bar
        xerr = self.edges[1:] - self.edges[:-1]
        rax.errorbar(
            x=self.centers,
            y=ratio,
            xerr=xerr / 2,
            fmt=f"ko",
            markersize=6,
        )
        # plot ratio y error bar
        try:
            ratio_error_down, ratio_error_up = ratio_uncertainty(
                num=self.data_values,
                denom=self.nominal_values,
                uncertainty_type="poisson-ratio",
            )
            rax.vlines(
                self.centers,
                ratio + ratio_error_up,
                ratio - ratio_error_down,
                color="k",
            )
        except ValueError:
            logging.info(f"(no poisson-ratio error for {feature})")

        # plot ratio uncertaity band
        ratio_up = np.concatenate([[0], self.band_up / self.nominal_values])
        ratio_down = np.concatenate([[0], self.band_down / self.nominal_values])
        ratio_uncertainty_band = rax.fill_between(
            self.edges,
            ratio_up,
            ratio_down,
            step="pre",
            color="lightgray",
            hatch="////",
            alpha=0.6,
            edgecolor="k",
            linewidth=0,
        )
        # plot horizontal reference lines
        xmin, xmax = rax.get_xlim()
        rax.hlines(1, xmin, xmax, color="k", linestyle=":")

    def plot_histograms(
        self,
        variable: str,
        category: str,
        yratio_limits: str = None,
        log_scale: bool = False,
        savefig: bool = True,
    ):
        setup_logger(self.output_dir)

        histogram_info = self.get_histogram_config(variable, category)
        # get nominal MC histograms
        nominal_mc_hists = list(histogram_info["nominal"].values())
        mc_histogram = accumulate(nominal_mc_hists)
        self.nominal_values = mc_histogram.values()
        self.nominal_variances = mc_histogram.variances()
        self.edges = mc_histogram.axes.edges[0]
        self.centers = mc_histogram.axes.centers[0]
        self.widths = mc_histogram.axes.widths[0]
        labels, colors = self.get_colors_and_labels(histogram_info)
        # get variation histograms
        variation_histograms = histogram_info["variations"]
        # get Data histogram
        data_histogram = histogram_info["data"]
        self.data_values = data_histogram.values()

        # plot stacked MC and Data histograms
        fig, (ax, rax) = plt.subplots(
            nrows=2,
            ncols=1,
            figsize=(9, 10),
            tight_layout=True,
            gridspec_kw={"height_ratios": (4, 1)},
            sharex=True,
        )
        hep.histplot(
            nominal_mc_hists,
            label=labels,
            color=colors,
            flow="none",
            ax=ax,
            **mc_hist_kwargs,
        )
        hep.histplot(
            data_histogram, label="Data", flow="none", ax=ax, **data_hist_kwargs
        )
        # plot uncertainty band
        self.plot_uncert_band(histogram_info, ax)

        # plot ratio
        self.plot_ratio(rax)

        # set limits
        hist_edges = np.array([[i, j] for i, j in zip(self.edges[:-1], self.edges[1:])])
        xlimits = np.min(hist_edges[self.nominal_values > 0]), np.max(
            hist_edges[self.nominal_values > 0]
        )
        ax.set_xlim(xlimits)
        rax.set_xlim(xlimits)
        rax.set_ylim(yratio_limits)

        # set legend layout
        if log_scale:
            ax.legend(loc="lower left", frameon=True)
        elif ("eta" in variable) or ("phi" in variable):
            ax.legend(loc="lower left", frameon=True)
        else:
            ax.legend()

        # set axes labels
        ylabel = "Events"
        if self.get_axis_type(variable) == "Variable":
            ylabel += " / bin width"
        ax.set(xlabel=None, ylabel=ylabel)
        formatter = ticker.ScalarFormatter()
        formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(formatter)
        rax.set(
            xlabel=self.get_variable_label(variable),
            ylabel="Data / Pred",
            facecolor="white",
        )

        # set log scale
        if log_scale:
            ax.set_yscale("log")

        # add CMS info
        hep.cms.lumitext(
            f"{self.lumi * 1e-3:.1f} fb$^{{-1}}$ ({self.year}, 13 TeV)",
            ax=ax,
        )
        hep.cms.text("Preliminary", ax=ax)

        # save histograms
        if savefig:
            output_path = Path(f"{self.output_dir}/{category}")
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            fig.savefig(
                f"{str(output_path)}/{self.processor}_{variable}_{category}_{self.year}.png"
            )
        plt.close()