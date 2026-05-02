import numpy as np
import ROOT


class EnergyCalibrator:
    """ Handles the ADC Channels to Energy (keV) conversion, using a calibration fit.
    """

    def __init__(self, endpoint_energy_kev: float, err_endpoint_energy: float) -> None:
        """ Constructor.
        """
        self.t0 = endpoint_energy_kev
        self.err_t0 = err_endpoint_energy
        self.k: float | None = None
        self.err_k: float | None = None

    def compute_calibration_factor(self, fit_result: ROOT.TFitResultPtr) -> tuple[float | None, float | None]:
        """ Calculates k (keV/CHN) from the linear fit of the Kurie Plot.
        """
        p0, p1 = fit_result.Parameter(0), fit_result.Parameter(1)
        err_p0, err_p1 = fit_result.ParError(0), fit_result.ParError(1)
        # x axis intercept (endpoint CHN)
        chn_0 = -p0 / p1
        err_chn_0 = abs(p0/p1) * np.sqrt((err_p0/p0)**2 + (err_p1/p1)**2)
        # Calibration factor k = E/CHN
        self.k = self.t0 / chn_0
        self.err_k = abs(self.t0/chn_0) * np.sqrt((self.err_t0/self.t0)**2 + (err_chn_0/chn_0)**2)
        return self.k, self.err_k
    
    def compute_energy(self, channel: float, err_channel: float) -> tuple[float, float]:
        """ Convertes an arbitrary channel to energy, propagating the calibration error.
        """
        if self.k is None or self.err_k is None:
            raise RuntimeError('Calibration has not yet been performed.')
        # Calculate energy
        energy = channel * self.k
        err_energy = np.sqrt((self.k*err_channel)**2 + (energy*self.err_k)**2)
        return energy, err_energy