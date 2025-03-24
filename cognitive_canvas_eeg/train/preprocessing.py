from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm
import os

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, INTERIM_DATA_DIR

import pywt
import numpy as np
import mne
import pandas as pd
import matplotlib.pyplot as plt

app = typer.Typer()

EEG_COLUMNS = ['EEG.AF3','EEG.F7','EEG.F3','EEG.FC5','EEG.T7','EEG.P7','EEG.O1',
               'EEG.O2','EEG.P8','EEG.T8', 'EEG.FC6','EEG.F4','EEG.F8','EEG.AF4']

SFREQ = 128

class EEGPreprocessor:
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        

    def get_eeg_df(self, csv_path):
        subject_df = pd.read_csv(csv_path, header=1)
        return subject_df[EEG_COLUMNS]

    def get_denoised(self, eeg_df):
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
    
    def batches(self):
        # TODO: RENAME OUTPUT FILES

        for csv in os.listdir(self.input_path):

            if csv.endswith(".csv") and csv.startswith("raw"):
                csv_path = os.path.join(self.input_path, csv)
                
                try:
                    eeg_df = self.get_eeg_df(csv_path)
                    denoised_eeg = self.get_denoised(eeg_df)

                    breakpoint()
                    bands = self.spectral_power(denoised_eeg)

                    words = csv_path.split('_')
                    words = [word.upper() for word in words]
                    
                    if "RESTING" in words or "REST" in words:
                        denoised_eeg['Label'] = 0
                    elif "LEFT" in words:
                        denoised_eeg['Label'] = 1
                    elif "RIGHT" in words:
                        denoised_eeg['Label'] = 2
                    elif "PULL" in words:
                        denoised_eeg['Label'] = 3
                    elif "PUSH" in words: 
                        denoised_eeg['Label'] = 4
                    else:
                        pass
                        
                    denoised_eeg.to_csv(f"{self.output_path}/{csv}", index=False)

                except:
                    pass


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR, 
    # output_path: Path = PROCESSED_DATA_DIR
    output_path: Path = INTERIM_DATA_DIR
    # ----------------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    # logger.info("Processing dataset...")
    # for i in tqdm(range(10), total=10):
    #     if i == 5:
    #         logger.info("Something happened for iteration 5.")
    # logger.success("Processing dataset complete.")
    # -----------------------------------------

    preprocessor = EEGPreprocessor(input_path, output_path)
    # eeg_df = preprocessor.get_eeg_df(input_path)
    # denoised_eeg = preprocessor.get_denoised(eeg_df)

    # raw = preprocessor.get_mne_raw(denoised_eeg)
    # delta_waves = preprocessor.filter(raw, 1, 4)
    # # delta_waves.plot(scalings="auto")
    # # plt.show()

    # band_dict = preprocessor.spectral_power(raw)
    # print(band_dict)

    preprocessor.batches()

if __name__ == "__main__":
    app()
