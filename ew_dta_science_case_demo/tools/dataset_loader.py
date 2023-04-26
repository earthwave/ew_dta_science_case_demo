"""A module to load and plot datasets on the /dtadata drive."""
from __future__ import annotations


class DatasetLoader():
    """Class for loading a DTA dataset."""

    def __init__(self: DatasetLoader) -> None:
        self.base_dir = '/dtadata/open_science_case/open_science_common_grid/'
