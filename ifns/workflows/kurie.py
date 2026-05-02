import logging
from pathlib import Path
import numpy as np
import ROOT

from ..data import ImportData, HistogramRebinner
from ..visualization import PandasToRootAdapter, RootRenderer
from ..physics import RootFitter, EnergyCalibrator


class KurieCalibrationPipeline:
    """ Handles the entire process for Kurie Plot endpoint calibration.
    """

    def __init__(self, name: str, filepath: str | Path, rebin_factor: int,
                 fit_xmin: float, fit_xmax: float,
                 endpoint_kev: float = 2.28e3, err_endpoint_kev: float = 0.04e3
                 ) -> None:
        """ Constructor.
        """
        self.name = name
        self.filepath = filepath
        self.rebin_factor = rebin_factor
        self.fit_xmin = fit_xmin
        self.fit_xmax = fit_xmax
        # Initialize the physics calculator
        self.calibrator = EnergyCalibrator(endpoint_kev, err_endpoint_kev)
        # State variables to hold results
        self.graph: ROOT.TGraphErrors | None        = None
        self.fit_result: ROOT.TFitResultPtr | None  = None
        self.k: float | None        = None
        self.err_k: float | None    = None

    def run(self) -> tuple[float | None, float | None]:
        """ Executes the whole calibration pipeline.
        """
        logging.info(f'--- Running Calibration Pipeline: {self.name} ---')
        # Load and Rebin
        df_raw = ImportData(self.filepath).load_data()
        df_rebinned = HistogramRebinner(self.rebin_factor).apply(df_raw, 'Channel', 'Counts')
        # Kurie Y and Errors
        df_rebinned['kurie_y'] = np.sqrt(df_rebinned['Counts']) / df_rebinned['Channel']
        err_chn = 65 * self.rebin_factor / 2.0
        df_rebinned['err_chn'] = err_chn    
        df_rebinned['err_kurie_y'] = np.sqrt(
            df_rebinned['Counts'] * (df_rebinned['err_chn'] / df_rebinned['Channel'])**2 + 0.25
            ) / df_rebinned['Channel']
        # Build ROOT TGraphErrors
        self.graph = PandasToRootAdapter(
            df_rebinned, name=f'g_kurie_{self.name}', title=f'Kurie Plot - {self.name}',
            x_axis='CHN', y_axis='#sqrt{conteggi} / CHN'
        ).build_graph('Channel', 'kurie_y', x_min=self.fit_xmin, x_max=self.fit_xmax, err_x_col='err_chn', err_y_col='err_kurie_y')
        # Perform Fit
        fitter = RootFitter(f'fit_{self.name}', 'pol1', x_min=self.fit_xmin, x_max=self.fit_xmax)
        fitter.set_initial_parameters(0.02, -1e-7)
        self.fit_result = fitter.apply_to_graph(self.graph)
        # Extract Calibration Factor
        if self.fit_result is not None and self.fit_result.IsValid():
            chi2, ndf = self.fit_result.Chi2(), self.fit_result.Ndf()
            logging.info(f'Fit converged! Chi2/NDF: {chi2/ndf:.2f}')
            self.k, self.err_k = self.calibrator.compute_calibration_factor(self.fit_result)
            logging.info(f'Calibration Factor (k): ({self.k:.2e} ± {self.err_k:.1e}) keV/CHN')
        else:
            logging.warning('Warning: Fit failed to converge!')
        return self.k, self.err_k
    
    def save_plot(self, output_filename: str | Path) -> None:
        """ Renders and saves the plot if the pipeline has been run.
        """
        if self.graph is None:
            raise RuntimeError('Cannot save plot: Pipeline has not been run yet.')
        RootRenderer.draw_and_save(self.graph, output_filename,
                                   x_min=self.fit_xmin-1000, x_max=self.fit_xmax+1000)