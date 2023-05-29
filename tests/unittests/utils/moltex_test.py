import pytest
from exojax.utils.moltex import format_molecule, format_molecules_list, format_molecules_lists

def test_format_molecule():
    assert format_molecule("H2O") == "$\\mathrm{H_2O}$"
    assert format_molecule("CH4") == "$\\mathrm{CH_4}$"
    assert format_molecule("CO") == "$\\mathrm{CO}$"
    assert format_molecule("NH3") == "$\\mathrm{NH_3}$"

def test_format_molecules_list():
    assert format_molecules_list(["H2O", "CH4", "CO"]) == ["$\\mathrm{H_2O}$", "$\\mathrm{CH_4}$", "$\\mathrm{CO}$"]
    assert format_molecules_list(["NH3", "NO2"]) == ["$\\mathrm{NH_3}$", "$\\mathrm{NO_2}$"]

def test_format_molecules_lists():
    assert format_molecules_lists([["H2O", "CH4", "CO"], ["H2O", "CH4", "CO"]]) == [["$\\mathrm{H_2O}$", "$\\mathrm{CH_4}$", "$\\mathrm{CO}$"], ["$\\mathrm{H_2O}$", "$\\mathrm{CH_4}$", "$\\mathrm{CO}$"]]
    assert format_molecules_lists([["NH3", "NO2"], ["H2O", "CH4"]]) == [["$\\mathrm{NH_3}$", "$\\mathrm{NO_2}$"], ["$\\mathrm{H_2O}$", "$\\mathrm{CH_4}$"]]