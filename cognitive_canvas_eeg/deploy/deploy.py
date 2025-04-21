from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream, cf_string

from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm
# import redis 
import torch

from cognitive_canvas_eeg.config import MODELS_DIR
import socket
import time
import sys
import numpy as np 
import pywt
import torch
from eegnet import EEGNet

T = 1 # Seconds
SAMP_RATE = 128 # Hz

def maddest(d, axis=None):
    return np.mean(np.absolute(d - np.mean(d, axis)), axis)

def denoise(data_chunk, wavelet='coif17', level=1):
    temp = [0]*data_chunk

    for c in range(data_chunk.shape[0]):
        coeff = pywt.wavedec(data_chunk[c,:], wavelet, mode="per")
        sigma = (1/0.6745) * maddest(coeff[-level])
        # breakpoint()

        uthresh = sigma * np.sqrt(2*np.log(data_chunk.shape[1]))
        coeff[1:] = (pywt.threshold(i, value=uthresh, mode='hard') for i in coeff[1:])

        temp[c,:] = pywt.waverec(coeff, wavelet, mode='per')

    return np.expand_dims(temp, axis=0)


def preprocess(data_chunk):
    data_chunk = np.einsum('jkl->jlk', data_chunk).squeeze(0)
    denoised_chunk = denoise(data_chunk)
    denoised_tensor = torch.from_numpy(denoised_chunk)
    denoised_tensor = denoised_tensor.to(torch.float32)

    # Steps 
    # 1) --> Any sort of filtering
    # 2) DWT 
    # 3) make it into a tensor 
    # return that tensor. 

    return denoised_tensor 

app = typer.Typer()

@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    model_path: Path = MODELS_DIR / "model.pt",
    # -----------------------------------------
):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '10.10.10.10' 


    # torch.serialization.add_safe_globals([EEGNet])
    model = EEGNet()
    model.load_state_dict(torch.load(model_path))
    # inlet = StreamInlet(resolve_stream('type', 'EEG')[0], max_buflen=1.0)  # 1-second buffer
    inlet = StreamInlet(resolve_stream('type', 'EEG')[0]) 
    
    time.sleep(5)
    client_socket.connect((server_ip, 12347))

    try:
        while True:
            chunk, timestamps = inlet.pull_chunk()  # Returns all samples in buffer
            if chunk:
                if len(chunk) == T*SAMP_RATE:
                # command = model.predict(preprocess(chunk))
                # message = command.to_bytes(4, byteorder='big')
                # client_socket.send(message)
                # print(f"Sent: {message}")
                    # print(len(chunk))
                    chunk_arr = np.array(chunk)
                    chunk_arr = chunk_arr[:, 3:-2]
                    chunk_arr = np.expand_dims(chunk_arr,axis=0)
                    chunk_tensor = preprocess(chunk_arr)

                    outputs = model(chunk_tensor)
                    _, predicted = torch.max(outputs, 1)  # Get predicted class

                    p = int(predicted)
                    print('SENDING: ', p)
                    message = p.to_bytes(4, byteorder='big')
                    client_socket.send(message)

                    # breakpoint()
                    time.sleep(T)
                else:
                    # print("WRONG", len(chunk))                    
                    time.sleep(T)

    except KeyboardInterrupt:
        print("\nShutdown signal received. Closing connection...")
        client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    app()
