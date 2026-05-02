import numpy as np
import pandas as pd
import ROOT


class PandasToRootAdapter:
    """
    Class that converts a Pandas DataFrame (already processed and rebinned)
    in a PyROOT TH1F histogram, keeping poissonian errors.
    """
    def __init__(self, df: pd.DataFrame, name: str = 'obj', title: str = 'Plot',
                 x_axis: str = 'X', y_axis: str = 'Y'):
        """ Constructor.
        """
        self.df = df
        self.name = name
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.hist = None
        self.graph = None

    def build_histogram(self, x_col: str, y_col: str, x_min: float, x_max: float, err_col: str = 'Error') -> ROOT.TH1F:
        """ Creates and populates the ROOT histogram from the DataFrame.
        """
        if self.df.empty:
            raise ValueError("The DataFrame is empty.")

        # Bin calculation
        n_bins = len(self.df)
        # Compute the bin width assuming they're uniform
        # (e.g. if the channels are 250, 750, 1250... the bin width is 500)
        bin_widths = self.df[x_col].diff().dropna()
        bin_width = bin_widths.iloc[0] if not bin_widths.empty else 1.0
        # Histogram boundaries
        min_center = self.df[x_col].min()
        max_center = self.df[x_col].max()
        low_edge = min_center - (bin_width / 2.0)
        high_edge = max_center + (bin_width / 2.0)
        # Create the histogram
        self.hist = ROOT.TH1F(self.name, f"{self.title};{self.x_axis};{self.y_axis}", 
                              n_bins, low_edge, high_edge)
        # Keeps track of the weights to keep the errorbars
        self.hist.Sumw2()
        # Manual filling (because we have pre-binned data)
        for _, row in self.df.iterrows():
            if row[x_col] < x_min:
                continue
            elif row[x_col] > x_max:
                break
            # Find which bin corresponds to the new CHN center.
            bin_idx = self.hist.FindBin(row[x_col])
            # Set Counts and Poisson error (sqrt(N))
            self.hist.SetBinContent(bin_idx, row[y_col])
            self.hist.SetBinError(bin_idx, row[err_col])
        return self.hist
    
    def build_graph(self, x_col: str, y_col: str, x_min: float, x_max:float,
                    err_x_col: str | None = None, err_y_col: str | None = None) -> ROOT.TGraphErrors:
        """ Extracts numpy arrays from the DataFrame and builds a TGraphErrors.
        """
        if self.df.empty:
            raise ValueError("The DataFrame is empty.")
        # Apply the range, using a mask
        mask = (self.df[x_col] >= x_min) & (self.df[x_col] <= x_max)
        df_filtered = self.df[mask]
        if df_filtered.empty:
            raise ValueError('The DataFrame is empty after applying the x_min - x_max filter.')
        # Extract 64-bit numpy arrays (ROOT requires C-contiguous double precision)
        x = df_filtered[x_col].to_numpy(dtype=np.float64)
        y = df_filtered[y_col].to_numpy(dtype=np.float64)
        n_points = len(x)
        # Error handling: extract columns if provided, otherwise fill with zeros
        ex = df_filtered[err_x_col].to_numpy(dtype=np.float64) if err_x_col and err_x_col in df_filtered else np.zeros(n_points, dtype=np.float64)
        ey = df_filtered[err_y_col].to_numpy(dtype=np.float64) if err_y_col and err_y_col in df_filtered else np.zeros(n_points, dtype=np.float64)
        # Initialize graph
        self.graph = ROOT.TGraphErrors(n_points, x, y, ex, ey)
        self.graph.SetName(self.name)
        self.graph.SetTitle(f"{self.title};{self.x_axis};{self.y_axis}")
        return self.graph