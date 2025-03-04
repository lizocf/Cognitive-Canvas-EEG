import pandas as pd

from pathlib import Path


import typer
from loguru import logger
from tqdm import tqdm
import os
import antropy as ant
import sklearn
from sklearn.decomposition import PCA

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

class FeatureAbstraction():
    def __init__(self,n,df_eeg):
        self.num_of_components = n 
        self.principal=PCA(n_components=3)
        self.df_eeg = df_eeg

    def katz_fractals(self):
        return ant.katz_fd(self.df_eeg.to_numpy().T)

    def hjort_params(self):
        return ant.hjorth_params(self.df_eeg.to_numpy().T)

    def pca(self,x):
        self.principal.fit(x)
        return self.principal.transform(x)
    
    def batches(self):
        pass 

@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = PROCESSED_DATA_DIR
    # ----------------------------------------------
):
    
    pass 
    


if __name__ == "__main__":
    app()
