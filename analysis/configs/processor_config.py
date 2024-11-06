import yaml

class ProcessorConfig:
    """
    Attributes:
    -----------
        goldenjson:
        hlt_paths:
        object_selection:
        event_selection:
    """
    def __init__(
        self, goldenjson, hlt_paths, object_selection, event_selection, histogram_config
    ):
        self.goldenjson = goldenjson
        self.hlt_paths = hlt_paths
        self.object_selection = object_selection
        self.event_selection = event_selection
        self.histogram_config = histogram_config

    def to_dict(self):
        """Convert ProcessorConfig to a dictionary."""
        return {
            "goldenjson": self.goldenjson,
            "hlt_paths": self.hlt_paths,
            "object_selection": self.object_selection,
            "event_selection": self.event_selection,
            "histogram_config": self.histogram_config.to_dict(),
        }

    def to_yaml(self):
        """Convert ProcessorConfig to a YAML string."""
        return yaml.dump(self.to_dict(), sort_keys=False, default_flow_style=False)