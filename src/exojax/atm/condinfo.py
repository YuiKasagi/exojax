import pandas as pd
import pkgutil
from io import BytesIO
from exojax.utils.constants import Tc_water

"""condensate information.

- LF98 Lodders and Fegley (1998)
"""

# condensate density g/cm3
condensate_density = {
    # from LF98 Table 1.18 (p37)
    "Fe": 7.875,  # solid
    "Si": 2.33,  # solid
    "FeO": 5.987,
    "Fe2O3": 5.275,
    "Fe3O4": 5.200,
    "FeSiO4": 4.393,
    "Al2O3": 3.987,
    "SiO2": 2.648,
    "TiO2": 4.245,
    "MgSiO3": 3.194,
    "Mg2SiO4": 3.214,
}


name2formula = {
    "ferrous oxide": "FeO",
    "hematite": "Fe2O3",
    "magnetite": "Fe3O4",
    "fayalite": "FeSiO4",
    "corundum": "Al2O3",
    "quartz": "SiO2",
    "rutile": "TiO2",
    "enstatite": "MgSiO3",
    "forstelite": "Mg2SiO4",
}


def read_liquid_ammonia_density():
    """read liquid ammonia density file

    Returns:
        temperature in K
        liquid ammonia density in g/cm3 
    """
    amd = pkgutil.get_data("exojax", "data/clouds/ammonia_liquid_density.csv")
    amdlist = pd.read_csv(BytesIO(amd), delimiter=",", comment="#")
    temperature = amdlist["temperature (C)"] + Tc_water
    density = amdlist[" density (g/cm3)"]
    return temperature.values, density.values


if __name__ == "__main__":
    print(condensate_density["Fe"])
    t, rho = read_liquid_ammonia_density()
    print(rho)