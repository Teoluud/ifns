import yaml
from pathlib import Path
from typing import Any


class ConfigReader:
    """ Handles the parsing of the YAML configuration file.
    """

    def __init__(self, filepath: str | Path) -> None:
        """ Constructor.
        """
        self.filepath = Path(filepath)
        self._config: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        """ Loads and returns the YAML file content as a dictionary.
        """
        if not self.filepath.exists():
            raise FileNotFoundError(
                f'Configuration file not found: {self.filepath.resolve()}'
            )
        with open(self.filepath, 'r', encoding='utf-8') as file:
            try:
                # safe_load is crucial to prevent arbitrary code execution
                self._config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise RuntimeError(f'Error parsing YAML file: {exc}')
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """ Retrieves a specific configuration block by its top-level key.
        """
        if not self._config:
            self.load()
        return self._config.get(key, default)