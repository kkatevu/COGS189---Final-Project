import numpy as np
import time
import os
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BrainFlowError

# Initialize BrainFlow connection
def initialize_brainflow_board(board_id=0):
    """Initializes BrainFlow connection for EEG data collection."""
    params = BrainFlowInputParams()
    
    try:
        board = BoardShim(board_id, params)
        board.prepare_session()
        board.start_stream()
        print("BrainFlow board initialized successfully.")
        return board
    except BrainFlowError as e:
        print(f"Error initializing BrainFlow: {e}")
        return None

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
    if board is None:
        print("No board initialized. Exiting data collection.")
        return None
    
    print(f"Collecting EEG data for {duration} seconds...")
    time.sleep(duration)  # Simulate experiment duration
    data = board.get_board_data()
    print("EEG data collection complete.")
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
    if data is None:
        print("No EEG data to save.")
        return
    
    # Ensure the data folder exists
    os.makedirs(folder, exist_ok=True)

    # Construct the filename
    filename = os.path.join(folder, f"subject_{subject_id}_session_{session_id}.npy")

    # Save the data
    np.save(filename, data)
    print(f"EEG data saved to {filename}")

# Main function to run EEG data collection
def main():
    subject_id = input("Enter Subject ID: ").strip()
    session_id = input("Enter Session Number: ").strip()
    
    if not subject_id or not session_id.isdigit():
        print("Invalid input. Please enter a valid Subject ID and numeric Session ID.")
        return

    session_id = int(session_id)  # Convert session number to integer

    board = initialize_brainflow_board()
    if board:
        eeg_data = collect_eeg_data(board, duration=60)
        save_eeg_data(eeg_data, subject_id, session_id)
        
        # Properly stop and release the BrainFlow session
        board.stop_stream()
        board.release_session()
        print("BrainFlow session closed.")

if __name__ == "__main__":
    main()
