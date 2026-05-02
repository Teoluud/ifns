# ⚛️ Spectroscopic Data Analysis Pipeline

A modular, object-oriented Python framework for analyzing physics spectroscopic data using `pandas` and `PyROOT`. 

This repository was specifically built to analyze:
1. **Strontium-90 Calibrations:** Rebinning, calculating the Kurie plots, and extracting the endpoint energy via linear fit for two distinct geometric setups (**Centered** and **Equivalent** sources).
2. **Cosmic Muon Spectra:** Rebinning and fitting the minimum ionizing particle (MIP) Landau peak.
3. **Bethe-Bloch Energy Loss:** Computing the experimental energy loss of vertical cosmic muons using the equivalent source calibration factor.

## 🚀 Features

* **Data/Logic Separation:** Uses `pandas` for fast data manipulation (rebinning, error propagation) and `PyROOT` strictly for physics fitting and visualization.
* **Package Layout:** The core logic is structured as an importable Python package (`ifns/`), ensuring clean namespaces and excellent maintainability.
* **Pipeline Architecture:** Encapsulates entire workflows (`PeakAnalysisPipeline`, `KurieCalibrationPipeline`) allowing you to analyze multiple datasets with different fit ranges in a few lines of code without duplication.
* **Data-Driven Configuration:** Parameters and fit ranges can be managed externally via `config.yml`.
* **Reproducible Setup:** Managed via Mamba/Conda for guaranteed cross-platform PyROOT compatibility.

## ⚙️ Installation

This project requires [Mamba](https://github.com/mamba-org/mamba) (or Conda) to correctly install the underlying PyROOT C++ binaries without compiling them from source.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Teoluud/ifns.git](https://github.com/Teoluud/ifns.git)
   cd ifns
   ```

2. **Create the isolated environment:**
   ```bash
   mamba env create -f environment.yml
   ```

3. **Activate the environment:**
   ```bash
   mamba activate muon_analysis
   ```

## 📊 Usage

The entire analysis suite is orchestrated from the `main.py` file. All paths are resolved dynamically using `pathlib`, meaning you can execute the script from anywhere.

To run the full pipeline:
```bash
python main.py
```

### Expected Output
1. The script will execute the pipelines sequentially and output the fit parameters directly to the console:
   
```text
   --- Running Calibration Pipeline: Centered_Sr_Calibration ---
   Fit Converged! Chi2/NDF: 10.61
   Calibration Factor (k): (6.9e-02 ± 1e-03) keV/CHN

   --- Running Peak Analysis: muons ---
   Fit Converged! Chi2/NDF: 1.25
   Peak Value: (6150.0 ± 20.0) CHN
   ```
2. High-resolution ROOT plots will be saved to the `output/` directory:
   * `kurie_plot_center.png`
   * `muoni.png`
   * `kurie_plot_equivalent.png`

## 📁 Repository Structure
```text
.
├── dati/                   # (Not tracked) Directory for raw CSV data
├── output/                 # (Not tracked) Directory for generated plots
├── ifns/                   # 📦 Main Python Package
│   ├── __init__.py         
│   ├── data/               # Data ingestion, YAML parsing, and Pandas rebinning
│   ├── physics/            # ROOT Minuit wrapping and calibration math
│   ├── visualization/      # Pandas-to-ROOT adapters and canvas rendering
│   └── workflows/          # High-level Orchestrator classes (Pipelines)
├── main.py                 # Execution script
├── config.yml              # Dataset paths and fit parameters
└── environment.yml         # Conda environment definition
```
