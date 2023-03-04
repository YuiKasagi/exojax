import pytest
import pkg_resources
import pandas as pd
import numpy as np
from exojax.spec.modit import xsvector
from exojax.test.data import TESTDATA_CO_EXOMOL_MODIT_XS_REF
from exojax.spec import normalized_doppler_sigma, gamma_natural
from exojax.spec.hitran import line_strength
from exojax.spec.exomol import gamma_exomol
from exojax.spec.initspec import init_modit
from exojax.spec.set_ditgrid import ditgrid_log_interval
from exojax.test.emulate_mdb import mock_mdbExomol
from exojax.test.emulate_mdb import mock_wavenumber_grid

from jax.config import config

config.update("jax_enable_x64", True)


def test_xs_exomol():
    Tfix = 1200.0
    Pfix = 1.0
    mdbCO = mock_mdbExomol()
    nus, wav, res = mock_wavenumber_grid()
    Mmol = mdbCO.molmass
    
    cont_nu, index_nu, R, pmarray = init_modit(mdbCO.nu_lines, nus)
    qt = mdbCO.qr_interp(Tfix)
    gammaL = gamma_exomol(Pfix, Tfix, mdbCO.n_Texp,
                          mdbCO.alpha_ref) + gamma_natural(mdbCO.A)
    dv_lines = mdbCO.nu_lines / R
    ngammaL = gammaL / dv_lines
    nsigmaD = normalized_doppler_sigma(Tfix, Mmol, R)
    Sij = line_strength(Tfix, mdbCO.logsij0, mdbCO.nu_lines, mdbCO.elower, qt)

    ngammaL_grid = ditgrid_log_interval(ngammaL, dit_grid_resolution=0.1)
    xsv = xsvector(cont_nu, index_nu, R, pmarray, nsigmaD, ngammaL, Sij, nus,
                   ngammaL_grid)
    
    filename = pkg_resources.resource_filename(
        'exojax', 'data/testdata/' + TESTDATA_CO_EXOMOL_MODIT_XS_REF)
    dat = pd.read_csv(filename, delimiter=",", names=("nus", "xsv"))
    assert np.all(xsv == pytest.approx(dat["xsv"].values))


def test_rt_exomol():
    """The original spectrum file can be generated by generate_rt.py"""
    import jax.numpy as jnp
    from exojax.spec import rtransfer as rt
    from exojax.spec.modit import exomol
    from exojax.spec.modit import xsmatrix
    from exojax.spec.rtransfer import dtauM
    from exojax.spec.rtransfer import rtrun
    from exojax.spec.planck import piBarr
    from exojax.spec.modit import set_ditgrid_matrix_exomol
    from exojax.test.data import TESTDATA_CO_EXOMOL_MODIT_EMISSION_REF

    Parr, dParr, k = rt.pressure_layer(NP=100, numpy=True)
    T0_in = 1300.0
    alpha_in = 0.1
    Tarr = T0_in * (Parr)**alpha_in
    Tarr[Tarr<400.0] = 400.0 #lower limit
    Tarr[Tarr>1500.0] = 1500.0 #upper limit
    nus, wav, res = mock_wavenumber_grid()
    mdb = mock_mdbExomol()
    molmass = mdb.molmass
    MMR = 0.1
    cont_nu, index_nu, R, pmarray = init_modit(mdb.nu_lines, nus)

    def fT(T0, alpha):
        return T0[:, None] * (Parr[None, :])**alpha[:, None]

    dgm_ngammaL = set_ditgrid_matrix_exomol(mdb, fT, Parr, R, molmass, 0.2,
                                            np.array([T0_in]),
                                            np.array([alpha_in]))

    g = 2478.57
    SijM, ngammaLM, nsigmaDl = exomol(mdb, Tarr, Parr, R, molmass)
    xsm = xsmatrix(cont_nu, index_nu, R, pmarray, nsigmaDl, ngammaLM, SijM,
                   nus, dgm_ngammaL)
    dtau = dtauM(dParr, jnp.abs(xsm), MMR * np.ones_like(Parr), molmass, g)
    sourcef = piBarr(Tarr, nus)
    F0 = rtrun(dtau, sourcef)
    filename = pkg_resources.resource_filename(
        'exojax', 'data/testdata/' + TESTDATA_CO_EXOMOL_MODIT_EMISSION_REF)
    dat = pd.read_csv(filename, delimiter=",", names=("nus", "flux"))
    residual = np.abs(F0 / dat["flux"].values - 1.0)
    print(np.max(residual))
    assert np.all(residual < 0.01)

    return F0


if __name__ == "__main__":
#    test_xs_exomol()
    test_rt_exomol()
