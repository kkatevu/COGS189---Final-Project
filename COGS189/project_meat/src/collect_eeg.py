import glob
import sys
import time
import serial
import os
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from serial import Serial
from threading import Thread, Event
from queue import Queue
from psychopy.hardware import keyboard

# CONFIGURATION
lsl_out = False
sampling_rate = 250
CYTON_BOARD_ID = 0  # 0 for no daisy, 2 for daisy, 6 for daisy + WiFi
BAUD_RATE = 115200
ANALOGUE_MODE = '/2'  # Reads from analog pins A5(D11), A6(D12), and A7(D13)

# USER INPUT FOR SUBJECT & SESSION
subject_id = input("Enter Subject ID: ").strip()
session_id = input("Enter Session Number: ").strip()
if not subject_id or not session_id.isdigit():
    print("Invalid input. Please enter a valid Subject ID and numeric Session ID.")
    sys.exit()

session_id = int(session_id)  # Convert session number to integer
save_dir = f'project_meat/data/subjects/subject_{subject_id}_session_{session_id}/'
os.makedirs(save_dir, exist_ok=True)  # Ensure subject/session folder exists

# FILENAMES
save_file_eeg = os.path.join(save_dir, f"eeg_run-{session_id}.npy")
save_file_aux = os.path.join(save_dir, f"aux_run-{session_id}.npy")
save_file_timestamps = os.path.join(save_dir, f"timestamps_run-{session_id}.npy")

# FIND OPENBCI PORT
def find_openbci_port():
    """Finds the port to which the Cyton Dongle is connected."""
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.usbserial*')
    else:
        raise EnvironmentError('Error finding ports on your operating system')

    for port in ports:
        try:
            s = Serial(port=port, baudrate=BAUD_RATE, timeout=None)
            s.write(b'v')
            time.sleep(2)
            if s.inWaiting():
                line = ''
                while '$$$' not in line:
                    line += s.read().decode('utf-8', errors='replace')
                if 'OpenBCI' in line:
                    s.close()
                    return port
            s.close()
        except (OSError, serial.SerialException):
            pass
    raise OSError('Cannot find OpenBCI port.')

# INITIALIZE BOARD
print(BoardShim.get_board_descr(CYTON_BOARD_ID))
params = BrainFlowInputParams()
params.serial_port = find_openbci_port() if CYTON_BOARD_ID != 6 else None
params.ip_port = 9000 if CYTON_BOARD_ID == 6 else None

board = BoardShim(CYTON_BOARD_ID, params)
board.prepare_session()
board.config_board('/0')
board.config_board('//')
board.config_board(ANALOGUE_MODE)
board.start_stream(45000)
stop_event = Event()

# FUNCTION TO COLLECT DATA
def get_data(queue_in):
    while not stop_event.is_set():
        data_in = board.get_board_data()
        timestamp_in = data_in[board.get_timestamp_channel(CYTON_BOARD_ID)]
        eeg_in = data_in[board.get_eeg_channels(CYTON_BOARD_ID)]
        aux_in = data_in[board.get_analog_channels(CYTON_BOARD_ID)]
        if len(timestamp_in) > 0:
            print('Data Queued: EEG:', eeg_in.shape, 'AUX:', aux_in.shape, 'Timestamps:', timestamp_in.shape)
            queue_in.put((eeg_in, aux_in, timestamp_in))
        time.sleep(0.1)

# THREAD FOR CONTINUOUS DATA COLLECTION
queue_in = Queue()
cyton_thread = Thread(target=get_data, args=(queue_in,))
cyton_thread.daemon = True
cyton_thread.start()

# RECORD EEG DATA
keyboard = keyboard.Keyboard()
eeg = np.zeros((8, 0))
aux = np.zeros((3, 0))
timestamps = np.zeros((0,))

while not stop_event.is_set():
    time.sleep(0.1)
    keys = keyboard.getKeys()
    if 'escape' in keys:
        stop_event.set()
        break
    while not queue_in.empty():
        eeg_in, aux_in, timestamp_in = queue_in.get()
        print('Processing: EEG:', eeg_in.shape, 'AUX:', aux_in.shape, 'Timestamps:', timestamp_in.shape)
        eeg = np.hstack((eeg, eeg_in))
        aux = np.hstack((aux, aux_in))
        timestamps = np.hstack((timestamps, timestamp_in))
        print('Total Collected:', eeg.shape, aux.shape, timestamps.shape)

# SAVE EEG, AUX, AND TIMESTAMPS
np.save(save_file_eeg, eeg)
np.save(save_file_aux, aux)
np.save(save_file_timestamps, timestamps)
print(f"Data saved: \n EEG: {save_file_eeg} \n AUX: {save_file_aux} \n Timestamps: {save_file_timestamps}")

# CLEANUP
board.stop_stream()
board.release_session()
print("Session closed.")
