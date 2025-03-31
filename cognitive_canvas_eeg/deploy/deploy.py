from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream, cf_string

from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm
import redis 
import torch

from cognitive_canvas_eeg.config import MODELS_DIR
import socket
import time
import sys

def preprocess(data_chunck):
    print(data_chunck)

    # Steps 
    # 1) --> Any sort of filtering
    # 2) DWT 
    # 3) make it into a tensor 
    # return that tensor. 

    pass 

app = typer.Typer()

@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    model_path: Path = MODELS_DIR / "model.pt",
    # -----------------------------------------
):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '10.10.10.10' 
    model = torch.jit.load(MODELS_DIR)
    
    inlet = StreamInlet(resolve_stream('type', 'EEG')[0], 
                    max_buflen=1.0)  # 1-second buffer
    
    client_socket.connect((server_ip, 12345))

    try:
        while True:
            chunk, timestamps = inlet.pull_chunk()  # Returns all samples in buffer
            if chunk:
                command = model.predict(preprocess(chunk))
                message = command.to_bytes(4, byteorder='big')
                client_socket.send(message)
                print(f"Sent: {message}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown signal received. Closing connection...")
        client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    app()
