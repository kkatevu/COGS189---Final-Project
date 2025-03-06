import numpy as np
import time
import os
from brainflow.board_shim import BoardShim, BrainFlowInputParams

# Initialize BrainFlow connection
def initialize_brainflow_board(board_id=0):
    """Initializes BrainFlow connection for EEG data collection."""
    params = BrainFlowInputParams()
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    return board

# Collect EEG data
def collect_eeg_data(board, duration=60):
    """
    Records EEG data for a given duration.

    Args:
        board: Initialized BrainFlow board object.
        duration: Duration of recording in seconds.

    Returns:
        EEG data as a NumPy array.
    """
    print(f"Collecting EEG data for {duration} seconds...")
    time.sleep(duration)  # Simulate experiment duration
    data = board.get_board_data()
    return data

# Save EEG data for each subject
def save_eeg_data(data, subject_id, session_id=1, folder="data/"):
    """
    Saves EEG data with a unique filename for each subject.

    Args:
        data: EEG data as a NumPy array.
        subject_id: Unique subject identifier.
        session_id: Session number (optional).
        folder: Directory where data will be saved.
    """
    # Ensure the data folder exists
    os.makedirs(folder, exist_ok=True)

    # Construct the filename
    filename = os.path.join(folder, f"subject_{subject_id}_session_{session_id}.npy")

    # Save the data
    np.save(filename, data)
    print(f"EEG data saved to {filename}")

   
