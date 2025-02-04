from datetime import datetime

import numpy as np
from mne import Info, create_info
from mne.io.array import RawArray
from pylsl import StreamInlet, resolve_stream
import os 

# 1. enter ID of person and create new subfolder for each person, ex: 0_EEG
# 2. Prompt that a state is about to be recorded. Press enter to cont. make file name "raw_<ID>_<STATE>_EEG.fif"
# 3. After state is recorded vizualize the recording. Then prompt whether to continue or re record
# 4. repeat 2 and 3 until all states are done

SRATE = 256
TIME = 15 # seconds
STATES = ["RESTING", "LEFT", "RIGHT", "UP", "DOWN"]
CURRENT_STATE = 0
SUBJECT_ID = 0

def get_info() -> Info:
    ch_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7',
                'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

    info = create_info(
        sfreq=SRATE,
        ch_names=ch_names,
        ch_types=['eeg'] * len(ch_names)
    )

    return info

def record(state, id, cur_id, path):
        begin = input(f"Starting {state} recording. Press Enter to begin: ")
        if begin == "":
            streams = resolve_stream('type', 'EEG')

            # create a new inlet to read from the stream
            inlet = StreamInlet(streams[0])

            buffer = []
            while True:
                if len(buffer) == 128 * TIME:  # wait 5 seconds [HOW TO CONTROL TIME MEASUREMENT]
                    break

                sample, _ = inlet.pull_sample()
                sample = [el / 1000000 for el in sample]  # convert to microvolts

                buffer.append(sample)

            info = get_info()
            raw = RawArray(np.array(buffer).T, info)

            # raw.save("data_{}_raw.fif".format(datetime.now()))
            visualize(id, raw, cur_id, path)
            prompt(id, raw, cur_id, path)
        else:
            record(state, id, cur_id, path)

def visualize(id, raw, cur_id, path):
     psd = raw.plot_psd()
     psd.savefig(f"{path}/PSDs/{id}_{STATES[cur_id]}")

def prompt(id, raw,cur_id, path):
    
    answer = input(f"1: Continue. 2: Restart. 3: Exit. \n")
    if answer == "1":
        raw.save(f"{path}/EEGs/raw_{id}_{STATES[cur_id]}_eeg.fif")
        cur_id += 1
        print("Continuing to next state... \n")
        record(STATES[cur_id], id, cur_id, path)
    elif answer == "2":
        record(STATES[cur_id], id, cur_id, path)
    else:
         print("Bye! :3")


def main():
     SUBJECT_ID = input("Enter subject ID: ")
     path = f"data-collection/{SUBJECT_ID}_eeg"
     os.mkdir(path)
     record(STATES[CURRENT_STATE], int(SUBJECT_ID), CURRENT_STATE, path)

if __name__ == '__main__':
    main()
