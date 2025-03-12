import time
import numpy as np
import pandas as pd
import os
import sys
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter
from pynput import keyboard


# --------------------------
# USER INPUT FOR SUBJECT & SESSION
# --------------------------
subject_id = input("Enter Subject ID (e.g. subject001): ").strip()
session_id = input("Enter Session Number: ").strip()
if not subject_id or not session_id.isdigit():
    print("Invalid input. Please enter a valid Subject ID and numeric Session ID.")
    sys.exit()
session_id = int(session_id)

# --------------------------
# SET UP DIRECTORY STRUCTURE
# --------------------------
# Assume this script is in project_meat/src/
base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
subject_folder = os.path.join(base_data_dir, subject_id)
eeg_folder = os.path.join(subject_folder, "eeg")
os.makedirs(eeg_folder, exist_ok=True)

# Define the file path for saving data
save_file = os.path.join(eeg_folder, f"eeg_{subject_id}_session_{session_id}.csv")

# --------------------------
# BOARD CONFIGURATION
# --------------------------
running = True

def on_press(key, board):
    global running
    try:
        if key.char:
            board.insert_marker(1)
            # Get the most recent data (including timestamps)
            data = board.get_board_data(num_samples=1)
            # The last row in BrainFlow data is the timestamp row
            brainflow_timestamp = data[-1][0]
            print(f"Marker inserted at BrainFlow time {brainflow_timestamp}")
    except AttributeError:
        pass

    if key == keyboard.Key.esc:
        print("ESC pressed. Stopping data collection.")
        running = False
        return False

def main():
    BoardShim.enable_dev_board_logger()

    # Use synthetic board for demo; replace with your port if needed.
    params = BrainFlowInputParams()
    params.serial_port = "COM8"  # Adjust port as needed
    board = BoardShim(BoardIds.CYTON_BOARD, params)
    board.prepare_session()
    board.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'Start sleeping in the main thread')

    # Start keyboard listener for markers and stopping
    listener = keyboard.Listener(on_press=lambda key: on_press(key, board))
    listener.start()

    # Data collection loop
    while running:
        time.sleep(1)

    data = board.get_board_data()
    board.stop_stream()
    board.release_session()

    # Convert data to pandas DataFrame (transpose so that each column is a channel)
    df = pd.DataFrame(np.transpose(data))
    print(df.head(10))

    # Write the data to a CSV file in the correct directory.
    DataFilter.write_file(data, save_file, 'w')  # 'w' for write mode
    restored_data = DataFilter.read_file(save_file)
    restored_df = pd.DataFrame(np.transpose(restored_data))
    print('Data From the File')
    print(restored_df.head(10))

if __name__ == "__main__":
    main()
