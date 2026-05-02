from pathlib import Path

import numpy as np
import ROOT

from ..data import ImportData, HistogramRebinner
from ..visualization import PandasToRootAdapter, RootRenderer
from ..physics import RootFitter, EnergyCalibrator


class PeakAnalysisPipeline:
    """ Pipeline to find the peak of a spectroscopic distribution.
    """

    def __init__(self, name: str, filepath: str | Path, fit_function: str, peak_param_idx: int = 1,
                 rebin_factor: int = 4, fit_xmin: float = 0, fit_xmax: float = 70000) -> None:
        """ Constructor.
        """
        self.name = name
        self.filepath = filepath
        self.fit_function = fit_function        # 'landau', 'gaus', etc.
        self.peak_param_idx = peak_param_idx    # Which parameter is the peak center? (1 for landau/gaus)
        self.rebin_factor = rebin_factor
        self.fit_xmin = fit_xmin
        self.fit_xmax = fit_xmax
        # State variables to hold results
        self.hist: ROOT.TH1F | None                 = None
        self.fit_result: ROOT.TFitResultPtr | None  = None
        self.peak_chn: float | None        = None
        self.err_peak_chn: float | None    = None

    def run(self) -> tuple[float | None, float | None]:
        """ Executes the whole peak analysis pipeline.
        """
        print(f'\n--- Running Peak Analysis: {self.name}')
        # Load and Rebin
        df_raw = ImportData(self.filepath).load_data()
        df_rebinned = HistogramRebinner(self.rebin_factor).apply(df_raw, 'Channel', 'Counts')
        # Build ROOT Histogram
        self.hist = PandasToRootAdapter(
            df_rebinned, name=f'h_{self.name}', title=f'Spectrum - {self.name}',
            x_axis='CHN', y_axis='Conteggi'
            ).build_histogram('Channel', 'Counts', x_min=0, x_max=70000, err_col='Error')
        # Perform Landau Fit
        fitter = RootFitter(f'fit_{self.name}', self.fit_function, x_min=self.fit_xmin, x_max=self.fit_xmax)
        self.fit_result = fitter.apply_to_histogram(self.hist)
        # Extract Peak
        if self.fit_result is not None and self.fit_result.IsValid():
            chi2, ndf = self.fit_result.Chi2(), self.fit_result.Ndf()
            print(f'Fit converged! Chi2/NDF: {chi2/ndf:.2f}')
            # Parameter 1 is the MPV of the Landau distribution
            self.peak_chn = self.fit_result.Parameter(self.peak_param_idx)
            self.err_peak_chn = self.fit_result.ParError(self.peak_param_idx)
            print(f'Peak Value: ({self.peak_chn:.2e} ± {self.err_peak_chn:.1e}) CHN')
        else:
            print(f'WARNING: Fit for {self.name} failed to converge!')
        return self.peak_chn, self.err_peak_chn
    
    def save_plot(self, output_filename: str | Path):
        """ Renders and saves the plot if the pipeline has been run.
        """
        if self.hist is None:
            raise RuntimeError('Cannot save plot: Pipeline has not been run yet.')
        RootRenderer.draw_and_save(self.hist, output_filename, x_min=0, x_max=70000)