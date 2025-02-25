from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm

from cognitive_canvas_eeg.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30)
}

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
