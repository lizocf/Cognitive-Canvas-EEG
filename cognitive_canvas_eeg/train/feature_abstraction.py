import pandas as pd

from pathlib import Path


import typer
from loguru import logger
from tqdm import tqdm
import os
import antropy as ant
import sklearn
from sklearn.decomposition import PCA
import numpy as np 
import mne

from cognitive_canvas_eeg.config import *
from preprocessing import EEG_COLUMNS, SFREQ

app = typer.Typer()

# TODO: make variable names consistent 

FEATURE_NAMES = ["hjorth_activity", "hjorth_mobility", "hjorth_complexity", "katz_FD" ]

class FeatureAbstraction():
    def __init__(self,n,input_path: Path, output_path: Path):
        self.principal=PCA(n_components=n)
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
        return subject_df[EEG_COLUMNS], subject_df['Label']

    def hjorth_params(self,df_eeg):
        activity = np.var(df_eeg.to_numpy().T,axis=-1)
        mobility, complexity = ant.hjorth_params(df_eeg.to_numpy().T)

        return activity,mobility,complexity

    def katz_fractals(self,df_eeg):
        return ant.katz_fd(df_eeg.to_numpy().T)

    def pca(self,x):
        self.principal.fit(x)
        return self.principal.transform(x)
    
    def get_ratios(self, band1, band2):
        return band1 / band2

    def get_mne_raw(self, denoised_eeg, fourchan=False):
        if fourchan:
            EEG_COLUMNS = ['EEG.F3','EEG.FC5','EEG.FC6','EEG.F4']
        if denoised_eeg.shape[1] == 2:
            info = mne.create_info(ch_names=['EEG.FC5', 'EEG.FC6'], sfreq=SFREQ, ch_types='eeg')
        else:
            info = mne.create_info(ch_names=EEG_COLUMNS, sfreq=SFREQ, ch_types='eeg')
        raw = mne.io.RawArray(denoised_eeg.transpose(), info)
        return raw
    
    def bandpower(self, psd, freqs, band):
        band_freqs = np.logical_and(freqs >= band[0], freqs <= band[1])
        band_power = np.mean(psd[:, :, band_freqs], axis=-1) # averaging across all epochs 
        # psd --> [number of epochs, n_channels, n_time_points]
        # breakpoint()
        return np.mean(band_power, axis=0) # averages across all epochs 
    
    def get_mew(self, denoised_eeg_df):
        raw = self.get_mne_raw(denoised_eeg_df[['EEG.FC5', 'EEG.FC6']])
        p = raw.compute_psd()
        freqs = p.freqs 
        psd_data = p.data 

        mew_power = self.bandpower(np.expand_dims(psd_data, axis=0), freqs, (8,12))
        mean_power = np.mean(mew_power)
        return {'Mu' : np.mean(mean_power)}
    
    
    def spectral_power(self, denoised_eeg_df, fourchan=False):

        if fourchan:
            denoised_eeg_df = denoised_eeg_df[['EEG.F3','EEG.FC5','EEG.FC6','EEG.F4']]

        raw = self.get_mne_raw(denoised_eeg_df, fourchan=fourchan)
        p = raw.compute_psd()
        freqs = p.freqs 
        psd_data = p.data 

        band_powers = {band: self.bandpower(np.expand_dims(psd_data, axis=0), freqs, self.bands[band]) for band in self.bands}
        bands_names = list(band_powers.keys())

        # breakpoint()

        mean_powers = [np.mean(band_powers[band]) for band in bands_names]

        return {band: np.mean(band_powers[band]) for band in bands_names}
    
    def batches(self, fourchan=False):
        feature_df = pd.DataFrame(columns=['hjorth_activity', 'hjorth_mobility', 'hjorth_complexity','katz_FD', 'Label'])
        big_out = []
        for csv in tqdm(os.listdir(self.input_path)):
            # print(csv)
            if csv.endswith(".csv") and csv.startswith("raw"):
                csv_path = os.path.join(self.input_path, csv)

                eeg_df, label = self.get_eeg_df(csv_path)
                components = self.pca(eeg_df)

                bands = self.spectral_power(eeg_df, fourchan=fourchan)
                mew = self.get_mew(eeg_df)

                band_ratio = self.get_ratios(bands['Beta'], mew['Mu'])

                activity, mobility, complexity = self.hjorth_params(eeg_df)
                fractals = self.katz_fractals(eeg_df)

                data = ([activity, mobility, complexity, fractals])

                out = []
                for i, d in enumerate(data):
                    list_name = [FEATURE_NAMES[i] + "_" + s for s in EEG_COLUMNS]
                    out.append(dict(zip(list_name, d)))

                big_out.append(out[0] | out[1] | out[2] | out[3] | {'BMu Ratio' : band_ratio} | bands | mew | {'Label': label[0]})

                # breakpoint()

                # temp_df = pd.DataFrame({'hjorth_activity': activity, 'hjorth_mobility': mobility, 
                #                         'hjorth_complexity' : complexity,'katz_FD' : fractals,
                #                         'Label' : label[:14]})
                # feature_df = pd.concat([feature_df, temp_df], ignore_index=True)

                # breakpoint()
        
        feature_df = pd.DataFrame(big_out)

        breakpoint()

        feature_df.to_csv(f"{self.output_path}/feature_df.csv", index=False)


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = LZL_INTERIM_DATA_DIR,
    output_path: Path = LZL_PROCESSED_DATA_DIR
    # ----------------------------------------------
):
    
    f = FeatureAbstraction(n=3, input_path=input_path, output_path=output_path)
    
    # f.batches()
    f.batches(fourchan=True)
    


if __name__ == "__main__":
    app()
