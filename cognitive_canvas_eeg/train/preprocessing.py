from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

class EEGPreprocessor:
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path

    def process_csv(self):
        pass
    
    def write_csv(self):
        pass

    def dwt(self, eeg_df):
        pass

    def filter(self, raw, start, stop):
        raw_copy = raw.copy()
        filtered_eeg = raw_copy.filter(start,stop, picks='eeg')
        return filtered_eeg

    def bandpower(self, raw, start, stop):
        pass

    def spectral_power(self, raw):
        pass



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
