from pathlib import Path

import pandas as pd


class ImportData:
    """ Class that handles data importing (from csv).
    """

    def __init__(self, filepath: str | Path) -> None:
        """ Constructor.
        """
        self.filepath = Path(filepath)

    def load_data(self) -> pd.DataFrame:
        """ Loads the CSV into a pandas dataframe.
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f'File not found: {self.filepath.resolve()}')
        df = pd.read_csv(self.filepath, comment='#')
        if 'Channel' not in df.columns or 'Counts' not in df.columns:
            raise ValueError(f'The CSV has to have columns "Channel" and "Counts".')
        return df