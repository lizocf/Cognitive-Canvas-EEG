import time
from bsl import StreamPlayer

sp = StreamPlayer(stream_name='StreamPlayer', fif_file=r'data-collection/4_eeg/EEGs/raw_4_DOWN_eeg.fif')
sp.start()
time.sleep(10)
sp.stop()