from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

import pywt
import numpy as np
import mne
import pandas as pd

app = typer.Typer()

EEG_COLUMNS = [ 'EEG.AF3','EEG.F7','EEG.F3','EEG.FC5','EEG.T7','EEG.P7','EEG.O1',
                'EEG.O2','EEG.P8','EEG.T8', 'EEG.FC6','EEG.F4','EEG.F8','EEG.AF4']

SFREQ = 128

class EEGPreprocessor:
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        self.bands = {
        'Delta': (0.5, 4),
        'Theta': (4, 8),
        'Alpha': (8, 13),
        'Beta': (13, 30)
    }
        

    def get_eeg_df(self, csv_path):
        subject_df = pd.read_csv(csv_path)
        return subject_df[EEG_COLUMNS]

    def get_denoised(self, eeg_csv):
        raw_eeg = mne.io.read_raw_fif(eeg_csv)
        eeg_df = pd.DataFrame(raw_eeg.get_data().T)
        denoised_eeg = self.denoise(eeg_df, wavelet="coif17")
        return denoised_eeg

    def get_mne_raw(self, denoised_eeg):
        info = mne.create_info(ch_names=EEG_COLUMNS, sfreq=SFREQ, ch_types='eeg')
        raw = mne.io.RawArray(denoised_eeg.transpose(), info)
        return raw

    def maddest(self, d, axis=None):
        return np.mean(np.absolute(d - np.mean(d, axis)), axis)

    def denoise(self, x, wavelet='haar', level=1):
        ret = {key:[] for key in x.columns}
        
        for pos in x.columns:
            coeff = pywt.wavedec(x[pos], wavelet, mode="per")
            sigma = (1/0.6745) * self.maddest(coeff[-level])

            uthresh = sigma * np.sqrt(2*np.log(len(x)))
            coeff[1:] = (pywt.threshold(i, value=uthresh, mode='hard') for i in coeff[1:])

            ret[pos]=pywt.waverec(coeff, wavelet, mode='per')
        
        return pd.DataFrame(ret)

    def filter(self, raw, start, stop):
        raw_copy = raw.copy()
        filtered_eeg = raw_copy.filter(start,stop, picks='eeg')
        return filtered_eeg

    def bandpower(self,psd, freqs, band):
        band_freqs = np.logical_and(freqs >= band[0], freqs <= band[1])
        band_power = np.mean(psd[:, :, band_freqs], axis=-1) # averaging across all epochs 
        # psd --> [number of epochs, n_channels, n_time_points]
        return np.mean(band_power, axis=0) # averages across all epochs 

    def spectral_power(self, raw):
        p = raw.compute_psd()
        freqs = p.freqs 
        psd_data = p.data 

        band_powers = {band: self.bandpower(np.expand_dims(psd_data, axis=0), freqs, self.bands[band]) for band in self.bands}
        bands_names = list(band_powers.keys())
        mean_powers = [np.mean(band_powers[band]) for band in bands_names]

        return {band: np.mean(band_powers[band]) for band in bands_names}

@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    # ----------------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")
    logger.success("Processing dataset complete.")
    # -----------------------------------------


if __name__ == "__main__":
    app()
