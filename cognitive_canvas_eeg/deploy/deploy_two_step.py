from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream, cf_string

from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm
# import redis 
import torch

from cognitive_canvas_eeg.config import *
import socket
import time
import sys
import numpy as np 
import pandas as pd
import pywt
import torch
from eegnet import EEGNet
from cognitive_canvas_eeg.train.preprocessing import EEGPreprocessor, EEG_COLUMNS
from cognitive_canvas_eeg.train.feature_abstraction import FeatureAbstraction
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pickle
import os

T = 1 # Seconds
SAMP_RATE = 128 # Hz
CROPPED_COLS = ['EEG.F3','EEG.FC5','EEG.FC6','EEG.F4']
FEATURE_NAMES = ["hjorth_activity", "hjorth_mobility", "hjorth_complexity", "katz_FD" ]
# MODELS_DIR = "../../models"

app = typer.Typer()
preprocessor = EEGPreprocessor(LZL_RAW_DATA_DIR, LZL_INTERIM_DATA_DIR)
featabs = FeatureAbstraction(n=3, input_path=LZL_INTERIM_DATA_DIR, output_path=LZL_PROCESSED_DATA_DIR)

def save_model(model, filename=None):
    with open(filename, 'wb') as file:
        pickle.dump(model, file)

def load_model(filename):
    with open(filename, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

# fn = filename
def load_classification_models(model_1_fn='logreg_7_3CLASS_0.8462.pkl', LR_model_fn='rf_4_LR_0.6000.pkl', PP_model_fn='logreg_6_PP_0.6000.pkl'):
    model_1 = load_model(MODELS_DIR / model_1_fn)
    LR_model = load_model(MODELS_DIR / LR_model_fn)
    PP_model = load_model(MODELS_DIR / PP_model_fn)
    return model_1, LR_model, PP_model


def classify(input, model_1, LR_model, PP_model, pca1, pcaLR, pcaPP):
    
    m1_input = pca1.fit(input)
    three_output = model_1.predict(m1_input)

    if three_output == 0:       # resting
        return 0
    elif three_output == 1:     # left/right
        lr_input = pcaLR.fit(input)
        LR_output = LR_model.predict(lr_input)
        return LR_output
    
    elif three_output == 2:     # push/pull
        pp_input = pcaPP.fit(input)
        PP_output = PP_model.predict(pp_input)
        return PP_output
    else:                       # ERROR
        return 0
 
def get_trained_pca(num_components, scaled_data):
    pca = PCA(n_components = num_components) 
    pca.fit(scaled_data)

    # pca_data = pca.transform(scaled_data)
    # pca_data.shape
    return pca


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    model_path: Path = MODELS_DIR / "model.pt",
    # -----------------------------------------
):
    print("Loading deployment schema...")

    scaler = StandardScaler()
    training_df = pd.read_csv('../data/lzl_processed/feature_df.csv')
    scaled_data = scaler.fit_transform(np.array(training_df))

    pca7 = get_trained_pca(7, scaled_data)  # THREE-WAY MODEL
    pca6 = get_trained_pca(6, scaled_data)  # PP MODEL
    pca4 = get_trained_pca(4, scaled_data)  # LR MODEL

    model_1, LR_model, PP_model = load_classification_models()

    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_ip = '10.10.10.10' 

    inlet = StreamInlet(resolve_stream('type', 'EEG')[0]) 
       
    time.sleep(5)
    # client_socket.connect((server_ip, 12347))

    try:
        while True:
            chunk, timestamps = inlet.pull_chunk()  # Returns all samples in buffer
            if chunk:
                if len(chunk) == T*SAMP_RATE:
                    chunk_arr = np.array(chunk)
                    chunk_arr = chunk_arr[:, 3:-2]

                    # chunk_arr = chunk_arr[:,[2,3,10,11]]    # [['EEG.F3','EEG.FC5','EEG.FC6','EEG.F4']]
                    chunk_df = pd.DataFrame(chunk_arr, columns=EEG_COLUMNS)

                    denoised_eeg = preprocessor.get_denoised(chunk_df)                    
                    feature_df = featabs.apply_abstraction(denoised_eeg)
                    
                    scaled_in = scaler.fit_transform(np.array(feature_df))  # DOESNT WORK

                    # PCA7 DOESNT WORK ON ONE INPUT

                    breakpoint()
                    predicted = classify(scaled_in, model_1, LR_model, PP_model, pca7, pca4, pca6)

                    p = int(predicted)
                    print('SENDING: ', p)
                    # message = p.to_bytes(4, byteorder='big')
                    # client_socket.send(message)

                    time.sleep(T)
                else:      
                    time.sleep(T)

    except KeyboardInterrupt:
        print("\nShutdown signal received. Closing connection...")
        # client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    app()
