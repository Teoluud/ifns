import pandas as pd
import numpy as np


class HistogramRebinner:
    """ Handles the rebinning operations and the statistical error propagation.
    """
    
    def __init__(self, rebin_factor: int):
        """ Constructor.
        """
        if rebin_factor < 1:
            raise ValueError("The rebin factor must be >= 1.")
        self.k = rebin_factor

    def apply(self, df: pd.DataFrame, x_col: str, y_col: str, err_col: str = 'Error') -> pd.DataFrame:
        """
        Rebins grouping k adjacient rows.
        - Channel: takes the average of the grouped bins (center of the new bin).
        - Counts: sums the counts (N_J).
        - Error: calculates the square root of the sum (sqrt(N_J)).
        """
        if self.k == 1:
            df_rebin = df.copy()
            df_rebin['Error'] = np.sqrt(df_rebin[y_col])
            return df_rebin

        # Groups using integer division of the index
        df_rebin = df.groupby(df.index // self.k).agg({
            x_col: 'mean',
            y_col: 'sum'
        }).reset_index(drop=True)
        # Poisson error propagation
        df_rebin['Error'] = np.sqrt(df_rebin[y_col])
        return df_rebin