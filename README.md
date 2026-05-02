# ⚛️ Spectroscopic Data Analysis Pipeline

A modular, object-oriented Python framework for analyzing physics spectroscopic data using `pandas` and `PyROOT`. 

This repository was specifically built to analyze:
1. **Cosmic Muon Spectra:** Rebinning and fitting the minimum ionizing particle (MIP) Landau peak.
2. **Strontium-90 Calibration:** Rebinning, calculating the Kurie plot, extracting the endpoint energy via linear fit, and computing the experimental calibration factor.

## 🚀 Features

* **Data/Logic Separation:** Uses `pandas` for fast data manipulation (rebinning, error propagation) and `PyROOT` strictly for physics fitting and visualization.
* **Modular Architecture (SOLID/PEP-8):**
  * `import_data.py`: Robust CSV loading using `pathlib`.
  * `analyzer.py`: Handles physically accurate histogram rebinning and Poisson error propagation.
  * `root_plotter.py`: Adapters to convert Pandas DataFrames into native ROOT `TH1F` and `TGraphErrors` objects, plus an aesthetic renderer.
  * `fitter.py`: A wrapper for ROOT's Minuit engine to apply arbitrary mathematical fits (Landau, Polynomial, etc.).
  * `physics_utils.py`: Isolates physical calculations (e.g., energy calibration factors, systematic error propagation) from the main orchestrator.
* **Reproducible Setup:** Managed via Mamba/Conda for guaranteed cross-platform PyROOT compatibility.

## ⚙️ Installation

This project requires [Mamba](https://github.com/mamba-org/mamba) (or Conda) to correctly install the underlying PyROOT C++ binaries without compiling them from source.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Teoluud/ifns.git](https://github.com/Teoluud/ifns.git)
   cd your-repo-name
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

The entire analysis pipeline is orchestrated from the `main.py` file. 

To run the full suite (Muon Spectrum + Kurie Plot + Calibration):
```bash
python main.py
```

### Expected Output
1. The script will output the fit parameters directly to the console:
   ```text
   Fit converged! Chi2/Ndf: 1.25
   Calibration factor: (3.1e-02 +/- 5e-04) keV/CHN
   Vertical muon energy loss (MPV): (1.85e+03 +/- 2e+01) keV
   ```
2. High-resolution (1920x1080) plots will be saved to the working directory:
   * `muoni_root_plot.png`
   * `kurie_plot.png`

## 📁 Repository Structure
```text
.
├── dati/                   # Directory for raw CSV data
├── main.py                 # Main orchestrator script
├── import_data.py          # I/O handling
├── analyzer.py             # Data manipulation and rebinning
├── fitter.py               # ROOT TF1 and MINUIT wrapping
├── root_plotter.py         # Rendering and Pandas->ROOT conversion
├── physics_utils.py        # Energy calibration physics calculations
├── environment.yml         # Conda environment definition
```

## 📝 Note on Data Formats
Input data must be in CSV format with lines starting with `#` treated as comments. The parser expects at least two columns explicitly named:
* `Channel` (The ADC/TDC bin number)
* `Counts` (The number of events recorded in that bin)
