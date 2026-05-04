import logging
import ROOT


class RootFitter:
    """ Handles the definition of functions and fit execution.
    """

    def __init__(self, name: str, formula: str, x_min: float, x_max: float) -> None:
        """ 
        Constructor.
        param 'formula': ROOT expression (e.g. 'pol1', 'gaus', 'landau')
        """
        self.name = name
        self.x_min = x_min
        self.x_max = x_max
        self.func = ROOT.TF1(self.name, formula, self.x_min, self.x_max)
        self.fit_result: ROOT.TFitResultPtr | None = None

    def set_initial_parameters(self, *params: float) -> None:
        """ Initializes fit parameters. Necessary for fit convergence.
        """
        for i, p in enumerate(params):
            self.func.SetParameter(i, p)

    def set_parameter_limits(self, id: int, min: float, max: float) -> None:
        self.func.SetParLimits(id, min, max)
        
    def set_par_names(self, *names: str) -> None:
        """ Assigns a name to fit parameters.
        """
        for i, name in enumerate(names):
            self.func.SetParName(i, name)
    
    def set_line_color(self, color: int = ROOT.kRed) -> None:
        """ Sets line color for when it will be drawn.
        """
        self.func.SetLineColor(color)

    def apply_to_histogram(self, hist: ROOT.TH1F, options: str = 'RSQ') -> ROOT.TFitResultPtr:
        """
        Executes the fit on the histogram.
        'R' forces the fit to use the range (x_min, x_max) defined earlier.
        'S' tells ROOT to return the FitResultPtr containing the covariance matrix.
        """
        logging.info(f'Executing fit "{self.name}" on the histogram "{hist.GetName()}"...')
        self.fit_result = hist.Fit(self.func, options)
        return self.fit_result
    
    def apply_to_graph(self, graph: ROOT.TGraphErrors, options: str = 'RSQ') -> ROOT.TFitResultPtr:
        """ Executes the fit on a TGraphErrors. (Should work on TGraph too)
        """
        logging.info(f'Executing fit "{self.name}" on the graph "{graph.GetName()}"...')
        self.fit_result = graph.Fit(self.func, options)
        return self.fit_result