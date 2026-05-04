import logging
from pathlib import Path
import ROOT

from ifns import ConfigReader, KurieCalibrationPipeline, PeakAnalysisPipeline, EnergyCalibrator

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / 'config.yml'
OUTPUT_DIR = BASE_DIR / 'output'

logging.basicConfig(
    level=logging.INFO, # Shows messages INFO, WARNING, ERROR and CRITICAL
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(), # Prints on the console
        # Uncomment below if you want to save in a file too.
        logging.FileHandler(BASE_DIR / 'analisi_run.log', mode='w') 
    ]
)


def main():
    # Suppress routine ROOT messages (Info, Warnings). 
    # It will now only print Errors or Fatal crashes.
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.gROOT.SetBatch(True)
    # Create the output folder if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Load the configuration
    config = ConfigReader(CONFIG_FILE)
    # --------------------------------------------------
    # STRONTIUM SPECTRUM
    # --------------------------------------------------
    logging.info("=" * 100)
    sr_spectrum_cfg = config.get('sr_spectrum')
    sr_spectrum_pipeline = PeakAnalysisPipeline(
        name='Stronzio',
        filepath=BASE_DIR / sr_spectrum_cfg['filepath'],
        fit_function='gaus',
        peak_param_idx=1,
        rebin_factor=sr_spectrum_cfg['rebin_factor'],
        fit_xmin=sr_spectrum_cfg['fit_xmin'],
        fit_xmax=sr_spectrum_cfg['fit_xmax']
    )
    tmax_chn, err_tmax_chn = sr_spectrum_pipeline.run()
    sr_spectrum_pipeline.save_plot(OUTPUT_DIR / 'sr_spectrum.png')

    # --------------------------------------------------
    # CENTERED SOURCE CALIBRATION
    # --------------------------------------------------
    logging.info("=" * 100)
    kurie_center_cfg = config.get('kurie_center')
    center_sr_pipeline = KurieCalibrationPipeline(
        name='Stronzio Centrato',
        filepath=BASE_DIR / kurie_center_cfg['filepath'],
        rebin_factor=kurie_center_cfg['rebin_factor'],
        fit_xmin=kurie_center_cfg['fit_xmin'],
        fit_xmax=kurie_center_cfg['fit_xmax'],
        p0_guess=kurie_center_cfg['p0_guess'],
        p1_guess=kurie_center_cfg['p1_guess']
    )
    k_center, err_k_center = center_sr_pipeline.run()
    center_sr_pipeline.save_plot(OUTPUT_DIR / 'kurie_plot_center.png')

    # --------------------------------------------------
    # MUON SPECTRUM ANALYSIS
    # --------------------------------------------------
    logging.info("=" * 100)
    muon_cfg = config.get('muons')
    muon_pipeline = PeakAnalysisPipeline(
        name='Muoni',
        filepath=BASE_DIR / muon_cfg['filepath'],
        fit_function='landau',
        peak_param_idx=1,
        rebin_factor=muon_cfg['rebin_factor'],
        fit_xmin=muon_cfg['fit_xmin'],
        fit_xmax=muon_cfg['fit_xmax']
    )
    mpv_chn, err_mpv_chn = muon_pipeline.run()
    muon_pipeline.save_plot(OUTPUT_DIR / 'muoni.png')

    # --------------------------------------------------
    # EQUIVALENT SOURCE CALIBRATION
    # --------------------------------------------------
    logging.info("=" * 100)
    kurie_eq_cfg = config.get('kurie_equivalent')
    eq_sr_pipeline = KurieCalibrationPipeline(
        name='Stronzio Decentrato',
        filepath=kurie_eq_cfg['filepath'],
        rebin_factor=kurie_eq_cfg['rebin_factor'],
        fit_xmin=kurie_eq_cfg['fit_xmin'],
        fit_xmax=kurie_eq_cfg['fit_xmax'],
        p0_guess=kurie_eq_cfg['p0_guess'],
        p1_guess=kurie_eq_cfg['p1_guess']
    )
    k_eq, err_k_eq = eq_sr_pipeline.run()
    eq_sr_pipeline.save_plot(OUTPUT_DIR / 'kurie_plot_equivalent.png')

    # --------------------------------------------------
    # MUON BETHE-BLOCH CALCULATION
    # --------------------------------------------------
    if mpv_chn is not None and k_eq is not None and err_mpv_chn is not None:
        # Compute the energy (calibrator returns keV)
        muon_energy_kev, err_muon_energy_kev = eq_sr_pipeline.calibrator.compute_energy(mpv_chn, err_mpv_chn)
        # Convert in MeV
        muon_energy_mev = muon_energy_kev / 1000.0
        err_muon_energy_mev = err_muon_energy_kev / 1000.0
        # Print output
        logging.info("=" * 50)
        logging.info(" MUON BETHE-BLOCH")
        logging.info("=" * 50)
        logging.info(f"Vertical Muon Energy Loss (MPV): ({muon_energy_mev:.2f} ± {err_muon_energy_mev:.2f}) MeV")
        logging.info("Theoretical Value (Polystyrene): ~2.06 MeV")
        logging.info("=" * 50)


if __name__ == "__main__":
    main()