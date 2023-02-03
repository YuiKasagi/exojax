""" short integration tests for PreMODIT cross section

    Note:
        This tests compares the results by PreMODIT with thoses by MODIT.
        If you are interested more manual comparison, see integrations/premodit/line_strength_comparison_*****.py
        ***** = exomol or hitemp, which compares cross section and line strength, starting from molecular databases. 

"""
import pytest
import pkg_resources
import pandas as pd
import numpy as np
from exojax.spec.opacalc import OpaPremodit
from exojax.utils.grids import wavenumber_grid
from exojax.spec.premodit import xsvector_second, xsvector_first, xsvector_zeroth
from exojax.test.emulate_mdb import mock_mdbExomol
from exojax.test.emulate_mdb import mock_mdbHitemp
from exojax.spec import normalized_doppler_sigma

#The following data can be regenerated by tests/generate_xs.py
from exojax.test.data import TESTDATA_CO_EXOMOL_MODIT_XS_REF
from exojax.test.data import TESTDATA_CO_HITEMP_MODIT_XS_REF_AIR
import warnings


@pytest.mark.parametrize("diffmode", [0, 1, 2])
def test_xsection_premodit_hitemp(diffmode):
    from jax.config import config
    config.update("jax_enable_x64", True)
    ### DO NOT CHANGE ###
    Ttest = 1200  #fix to compare w/ precomputed xs by MODIT.
    #####################

    Ptest = 1.0
    Nx = 5000
    mdb = mock_mdbHitemp(multi_isotope=False)
    nu_grid, wav, res = wavenumber_grid(22800.0,
                                        23100.0,
                                        Nx,
                                        unit='AA',
                                        xsmode="premodit")
    opa = OpaPremodit(mdb=mdb,
                      nu_grid=nu_grid,
                      diffmode=diffmode,
                      auto_trange=[500.0, 1500.0],
                      dit_grid_resolution=0.1)
    lbd_coeff, multi_index_uniqgrid, elower_grid, \
        ngamma_ref_grid, n_Texp_grid, R, pmarray = opa.opainfo
    Mmol = mdb.molmass
    nsigmaD = normalized_doppler_sigma(Ttest, Mmol, R)
    qt = mdb.qr_interp(mdb.isotope, Ttest)
    message = "Here, we use a single partition function qt for isotope=1 despite of several isotopes."
    warnings.warn(message, UserWarning)
    if diffmode == 0:
        xsv = xsvector_zeroth(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref, R,
                              pmarray, opa.nu_grid, elower_grid,
                              multi_index_uniqgrid, ngamma_ref_grid,
                              n_Texp_grid, qt)
    elif diffmode == 1:
        xsv = xsvector_first(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref,
                             opa.Twt, R, pmarray, opa.nu_grid, elower_grid,
                             multi_index_uniqgrid, ngamma_ref_grid,
                             n_Texp_grid, qt)
    elif diffmode == 2:
        xsv = xsvector_second(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref,
                              opa.Twt, R, pmarray, opa.nu_grid, elower_grid,
                              multi_index_uniqgrid, ngamma_ref_grid,
                              n_Texp_grid, qt)

    filename = pkg_resources.resource_filename(
        'exojax', 'data/testdata/' + TESTDATA_CO_HITEMP_MODIT_XS_REF_AIR)
    dat = pd.read_csv(filename, delimiter=",", names=("nus", "xsv"))
    res = np.max(np.abs(1.0 - xsv / dat["xsv"].values))
    print(res)
    assert res < 0.01
    return opa.nu_grid, xsv, opa.dE, opa.Twt, opa.Tref, Ttest


@pytest.mark.parametrize("diffmode", [0, 1, 2])
def test_xsection_premodit_exomol(diffmode):
    from jax.config import config
    config.update("jax_enable_x64", True)

    ### DO NOT CHANGE ###
    Ttest = 1200  #fix to compare w/ precomputed xs by MODIT.
    #####################
    Ptest = 1.0
    mdb = mock_mdbExomol()
    Nx = 5000
    nu_grid, wav, res = wavenumber_grid(22800.0,
                                        23100.0,
                                        Nx,
                                        unit='AA',
                                        xsmode="premodit")
    from exojax.utils.constants import Tref_original
    opa = OpaPremodit(mdb=mdb,
                      nu_grid=nu_grid,
                      diffmode=diffmode,
                      auto_trange=[500.0, 2000.0])
    #                      manual_params=[100.0,Tref_original,1000.0])
    lbd_coeff, multi_index_uniqgrid, elower_grid, \
        ngamma_ref_grid, n_Texp_grid, R, pmarray = opa.opainfo
    Mmol = mdb.molmass
    #opa.Tref
    #Ttest = opa.Tref

    nsigmaD = normalized_doppler_sigma(Ttest, Mmol, R)
    qt = mdb.qr_interp(Ttest)
    if diffmode == 0:
        xsv = xsvector_zeroth(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref, R,
                              pmarray, opa.nu_grid, elower_grid,
                              multi_index_uniqgrid, ngamma_ref_grid,
                              n_Texp_grid, qt)
    elif diffmode == 1:
        xsv = xsvector_first(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref,
                             opa.Twt, R, pmarray, opa.nu_grid, elower_grid,
                             multi_index_uniqgrid, ngamma_ref_grid,
                             n_Texp_grid, qt)
    elif diffmode == 2:
        xsv = xsvector_second(Ttest, Ptest, nsigmaD, lbd_coeff, opa.Tref,
                              opa.Twt, R, pmarray, opa.nu_grid, elower_grid,
                              multi_index_uniqgrid, ngamma_ref_grid,
                              n_Texp_grid, qt)
    filename = pkg_resources.resource_filename(
        'exojax', 'data/testdata/' + TESTDATA_CO_EXOMOL_MODIT_XS_REF)
    dat = pd.read_csv(filename, delimiter=",", names=("nus", "xsv"))
    res = np.max(np.abs(1.0 - xsv / dat["xsv"].values))
    #print(res)
    assert res < 0.012
    return opa.nu_grid, xsv, opa.dE, opa.Twt, opa.Tref, Ttest


if __name__ == "__main__":
    #comparison with MODIT
    from exojax.test.data import TESTDATA_CO_EXOMOL_MODIT_XS_REF
    from exojax.test.data import TESTDATA_CO_HITEMP_MODIT_XS_REF_AIR
    import matplotlib.pyplot as plt
    
    
    db = "hitemp"
    #db = "exomol"

    diffmode = 2
    if db == "exomol":
        nus, xs, dE, Twt, Tref, Tin = test_xsection_premodit_exomol(diffmode)
        filename = pkg_resources.resource_filename(
            'exojax', 'data/testdata/' + TESTDATA_CO_EXOMOL_MODIT_XS_REF)
    elif db == "hitemp":
        nus, xs, dE, Twt, Tref, Tin = test_xsection_premodit_hitemp(diffmode)
        filename = pkg_resources.resource_filename(
            'exojax', 'data/testdata/' + TESTDATA_CO_HITEMP_MODIT_XS_REF_AIR)

    dat = pd.read_csv(filename, delimiter=",", names=("nus", "xsv"))
    fig = plt.figure()
    ax = fig.add_subplot(211)
    #plt.title("premodit_xsection_test.py diffmode=" + str(diffmode))
    plt.title("diffmode=" + str(diffmode) + " T=" + str(Tin) + " Tref=" +
              str(np.round(Tref, 1)) + " Twt=" + str(np.round(Twt, 1)) +
              " dE=" + str(np.round(dE, 1)))
    ax.plot(nus, xs, label="PreMODIT", ls="dashed")
    ax.plot(nus, dat["xsv"], label="MODIT")
    plt.legend()
    plt.yscale("log")
    plt.ylabel("cross section (cm2)")
    ax = fig.add_subplot(212)
    ax.plot(nus, 1.0 - xs / dat["xsv"], label="dif = (MODIT - PreMODIT)/MODIT")
    plt.ylabel("dif")
    plt.xlabel("wavenumber cm-1")
    plt.axhline(0.01, color="gray", lw=0.5)
    plt.axhline(-0.01, color="gray", lw=0.5)
    #plt.ylim(-0.05, 0.05)
    plt.legend()
    plt.savefig("premodit" + str(diffmode) + ".png")
    plt.show()
