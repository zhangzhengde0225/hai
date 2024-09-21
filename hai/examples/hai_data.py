
import pdg
import matplotlib.pyplot as plt
import numpy

api = pdg.connect(f"sqlite:///pdgall-2024-v0.1.2.sqlite")

xs, ys, yerrs = [], [], []
# for edition in api.editions:
    # p = edition.