import glob
import json
from pathlib import Path


def divide_list(lst: list, nfiles) -> list:
    """Divide a list into sublists such that each sublist has at least 20 elements."""
    if len(lst) < nfiles:
        return [lst]

    # Dynamically calculate the number of sublists such that each has at least 20 elements
    n = len(lst) // nfiles  # This gives the number of groups with at least 20 elements
    if len(lst) % nfiles != 0:
        n += 1  # Increase n by 1 if there is a remainder, to accommodate extra elements

    # Divide the list into 'n' sublists
    size = len(lst) // n
    remainder = len(lst) % n
    result = []
    start = 0

    for i in range(n):
        if i < remainder:
            end = start + size + 1
        else:
            end = start + size
        result.append(lst[start:end])
        start = end

    return result


def get_dataset_key(dataset):
    datasets = ["SingleMuon", "SingleElectron"]
    for dataset_key in datasets:
        if dataset.startswith(dataset_key):
            return dataset_key
    return "MC"