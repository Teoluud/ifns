from pathlib import Path

from ifns import ConfigReader, KurieCalibrationPipeline, PeakAnalysisPipeline

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / 'config.yml'
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)     # Creates the folder if it doesn't exist

def main():
    # Load the configuration
    config = ConfigReader(CONFIG_FILE)
    # --------------------------------------------------
    # STRONTIUM SPECTRUM
    # --------------------------------------------------
    sr_spectrum_cfg = config.get('sr_spectrum')
    sr_spectrum_pipeline = PeakAnalysisPipeline(
        name='Sr_Spectrum',
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
    kurie_center_cfg = config.get('kurie_center')
    center_sr_pipeline = KurieCalibrationPipeline(
        name='Centered_Sr_Calibration',
        filepath=BASE_DIR / kurie_center_cfg['filepath'],
        rebin_factor=kurie_center_cfg['rebin_factor'],
        fit_xmin=kurie_center_cfg['fit_xmin'],
        fit_xmax=kurie_center_cfg['fit_xmax']
    )
    k_center, err_k_center = center_sr_pipeline.run()
    center_sr_pipeline.save_plot(OUTPUT_DIR / 'kurie_plot_center.png')

    # --------------------------------------------------
    # MUON SPECTRUM ANALYSIS
    # --------------------------------------------------
    muon_cfg = config.get('muons')
    muon_pipeline = PeakAnalysisPipeline(
        name='muons',
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
    kurie_eq_cfg = config.get('kurie_equivalent')
    eq_sr_pipeline = KurieCalibrationPipeline(
        name='Equivalent_Sr_Calibration',
        filepath=kurie_eq_cfg['filepath'],
        rebin_factor=kurie_eq_cfg['rebin_factor'],
        fit_xmin=kurie_eq_cfg['fit_xmin'],
        fit_xmax=kurie_eq_cfg['fit_xmax']
    )
    k_eq, err_k_eq = eq_sr_pipeline.run()
    eq_sr_pipeline.save_plot(OUTPUT_DIR / 'kurie_plot_equivalent.png')

    # --------------------------------------------------
    # MUON BETHE-BLOCH CALCULATION
    # --------------------------------------------------
    if mpv_chn is not None and k_eq is not None and err_mpv_chn is not None:
        print("\n==================================================")
        print(" MUON BETHE-BLOCH")
        print("==================================================")
        muon_energy, err_muon_energy = eq_sr_pipeline.calibrator.compute_energy(mpv_chn, err_mpv_chn)
        print(f'Vertical Muon Energy Loss (MPV): ({muon_energy:.2e} +/- {err_muon_energy:.0e}) keV')
        print("==================================================")


if __name__ == "__main__":
    main()