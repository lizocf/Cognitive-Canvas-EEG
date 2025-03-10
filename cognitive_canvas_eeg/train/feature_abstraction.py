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

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, INTERIM_DATA_DIR
from preprocessing import EEG_COLUMNS

app = typer.Typer()

# TODO: make variable names consistent 

FEATURE_NAMES = ["hjorth_activity", "hjorth_mobility", "hjorth_complexity", "katz_FD" ]


class FeatureAbstraction():
    def __init__(self,n,input_path: Path, output_path: Path):
        self.principal=PCA(n_components=n)
        self.input_path = input_path
        self.output_path = output_path

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
    
    def batches(self):
        feature_df = pd.DataFrame(columns=['hjorth_activity', 'hjorth_mobility', 'hjorth_complexity','katz_FD', 'Label'])
        big_out = []
        for csv in tqdm(os.listdir(self.input_path)):
            # print(csv)
            if csv.endswith(".csv") and csv.startswith("raw"):
                csv_path = os.path.join(self.input_path, csv)

                eeg_df, label = self.get_eeg_df(csv_path)
                components = self.pca(eeg_df)
                activity, mobility, complexity = self.hjorth_params(eeg_df)
                fractals = self.katz_fractals(eeg_df)

                data = ([activity, mobility, complexity, fractals])

                out = []
                for i, d in enumerate(data):
                    list_name = [FEATURE_NAMES[i] + "_" + s for s in EEG_COLUMNS]
                    out.append(dict(zip(list_name, d)))

                big_out.append(out[0] | out[1] | out[2] | out[3] | {'Label': label[0]})








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
    input_path: Path = INTERIM_DATA_DIR,
    output_path: Path = PROCESSED_DATA_DIR
    # ----------------------------------------------
):
    
    f = FeatureAbstraction(n=3, input_path=input_path, output_path=output_path)
    
    f.batches()
    


if __name__ == "__main__":
    app()
