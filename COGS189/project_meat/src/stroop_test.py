import os
import sys
import time
import csv
import random
import numpy as np
import pygame
from datetime import datetime
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter

# ====================================
# USER INPUT & DIRECTORY SETUP
# ====================================
subject_id = input("Enter Subject ID (e.g. subject001): ").strip()
session_id = input("Enter Session Number: ").strip()
if not subject_id or not session_id.isdigit():
    print("Invalid input. Please enter a valid Subject ID and numeric Session ID.")
    sys.exit()
session_id = int(session_id)

# Base data folder (assumed relative to project_meat/src/)
base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
subject_folder = os.path.join(base_data_dir, subject_id)
os.makedirs(subject_folder, exist_ok=True)

# Create subfolders for EEG and Stroop data
eeg_folder = os.path.join(subject_folder, "eeg")
stroop_folder = os.path.join(subject_folder, "stroop")
os.makedirs(eeg_folder, exist_ok=True)
os.makedirs(stroop_folder, exist_ok=True)

# Define file paths for saving data
eeg_save_file = os.path.join(eeg_folder, f"eeg_{subject_id}_session_{session_id}.npy")
aux_save_file = os.path.join(eeg_folder, f"aux_{subject_id}_session_{session_id}.npy")
timestamps_save_file = os.path.join(eeg_folder, f"timestamps_{subject_id}_session_{session_id}.npy")
csv_stroop_file = os.path.join(stroop_folder, f"stroop_{subject_id}_session_{session_id}.csv")

# ====================================
# PYGAME SETUP FOR STROOP
# ====================================
pygame.init()
info_object = pygame.display.Info()
WIDTH, HEIGHT = info_object.current_w, info_object.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Stroop Test")

COLORS = {"RED": (255, 0, 0), "GREEN": (0, 255, 0), "BLUE": (0, 0, 255), "YELLOW": (200, 200, 0)}
COLOR_KEYS = list(COLORS.keys())
FONT = pygame.font.Font(None, 80)
INSTRUCTION_FONT = pygame.font.Font(None, 40)
# For testing, set wait duration to 1 second; change to 300 for actual 5-minute stages.
WAIT_DURATION = 300

# ====================================
# STROOP EXPERIMENT FUNCTIONS
# ====================================
def save_stroop_results(results_list):
    file_exists = os.path.isfile(csv_stroop_file)
    with open(csv_stroop_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Test Number",
                "Round Number",
                "Word",
                "Match?",        # True/False
                "User Response", # True/False
                "Reaction Time",
                "Correct",       # True/False
                "Timestamp"
            ])
        writer.writerows(results_list)
    print(f"Stroop results saved to {csv_stroop_file}")

def generate_trials():
    total_trials = 20
    num_match = random.randint(0, total_trials)
    num_mismatch = total_trials - num_match
    trials = []
    for _ in range(num_match):
        word = random.choice(COLOR_KEYS)
        trials.append((word, COLORS[word], True))
    for _ in range(num_mismatch):
        word = random.choice(COLOR_KEYS)
        mismatch_choices = [c for c in COLOR_KEYS if c != word]
        color_choice = random.choice(mismatch_choices)
        trials.append((word, COLORS[color_choice], False))
    random.shuffle(trials)
    return trials

def show_message(message, duration=3):
    screen.fill((255, 255, 255))
    msg_surface = INSTRUCTION_FONT.render(message, True, (0, 0, 0))
    msg_rect = msg_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(msg_surface, msg_rect)
    pygame.display.flip()
    time.sleep(duration)

def run_timer(duration, message):
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        remaining = int(duration - elapsed)
        if remaining < 0:
            remaining = 0
        screen.fill((255, 255, 255))
        msg_surface = INSTRUCTION_FONT.render(message, True, (0, 0, 0))
        msg_rect = msg_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(msg_surface, msg_rect)
        timer_surface = FONT.render(f"Time Remaining: {remaining}s", True, (0, 0, 0))
        timer_rect = timer_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        screen.blit(timer_surface, timer_rect)
        pygame.display.flip()
        if remaining <= 0:
            break
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        time.sleep(1)

def run_stroop_test(test_number, round_number):
    results = []
    trials = generate_trials()
    for i in range(20):
        trial_timestamp = datetime.now().isoformat()
        screen.fill((255, 255, 255))
        word, color, is_match = trials[i]
        text_surface = FONT.render(word, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surface, text_rect)
        inst_surface = INSTRUCTION_FONT.render("Press F for Correct | Press J for Incorrect", True, (0, 0, 0))
        screen.blit(inst_surface, (WIDTH//2 - 200, HEIGHT - 50))
        pygame.display.flip()
        start_time = time.time()
        response = None
        waiting_for_response = True
        while waiting_for_response:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    save_stroop_results(results)
                    pygame.quit()
                    sys.exit(0)
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_ESCAPE:
                        save_stroop_results(results)
                        pygame.quit()
                        sys.exit(0)
                    elif evt.key == pygame.K_f:
                        response = True
                        waiting_for_response = False
                    elif evt.key == pygame.K_j:
                        response = False
                        waiting_for_response = False
        reaction_time = time.time() - start_time
        is_correct = (response == is_match)
        results.append([
            test_number,
            round_number,
            word,
            is_match,
            response,
            reaction_time,
            is_correct,
            trial_timestamp
        ])
        pygame.time.delay(100)
    return results

# ====================================
# INTEGRATED EXPERIMENT FUNCTION
# ====================================
def run_experiment(board):
    all_results = []
    
    # Stage 1: Control Recording (EEG Baseline)
    board.insert_marker(10)
    show_message("Control Recording Phase (EEG Baseline) - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Control Recording Phase (EEG Baseline)")
    
    # Stage 2: Break Phase
    board.insert_marker(20)
    show_message("Break Phase - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Break Phase")
    
    # Stage 3: Attention Test (Initial Stroop) - Test #1
    board.insert_marker(30)
    show_message("Attention Test - Stroop Test Begins", duration=2)
    start_test1 = time.time()
    for round_number in range(1, 6):
        board.insert_marker(31)  # Optional marker for each round
        show_message(f"Starting Stroop Round {round_number} / 5", duration=2)
        test_results = run_stroop_test(test_number=1, round_number=round_number)
        all_results.extend(test_results)
    end_test1 = time.time()
    duration_test1 = end_test1 - start_test1
    
    # Stage 4: Doom Scroll Phase
    board.insert_marker(40)
    show_message("Doom Scroll Phase - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Doom Scroll Phase - Watch Short Videos")
    
    # Stage 5: Attention Task (Post-exposure Stroop) - Test #2
    board.insert_marker(50)
    show_message("Post-exposure Attention Task - Stroop Test Begins", duration=2)
    start_test2 = time.time()
    for round_number in range(1, 6):
        board.insert_marker(51)  # Optional marker for each round
        show_message(f"Starting Stroop Round {round_number} / 5", duration=2)
        test_results = run_stroop_test(test_number=2, round_number=round_number)
        all_results.extend(test_results)
    end_test2 = time.time()
    duration_test2 = end_test2 - start_test2

    # Save Stroop behavioral results to CSV
    if all_results:
        save_stroop_results(all_results)
    
    # Compute accuracy for each test
    test1_trials = [r for r in all_results if r[0] == 1]
    test2_trials = [r for r in all_results if r[0] == 2]
    
    if test1_trials:
        total1 = len(test1_trials)
        correct1 = sum(1 for r in test1_trials if r[6])
        accuracy1 = (correct1 / total1) * 100
    else:
        total1 = correct1 = accuracy1 = 0

    if test2_trials:
        total2 = len(test2_trials)
        correct2 = sum(1 for r in test2_trials if r[6])
        accuracy2 = (correct2 / total2) * 100
    else:
        total2 = correct2 = accuracy2 = 0

    with open(csv_stroop_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SUMMARY", "Test 1", f"Accuracy: {accuracy1:.2f}% ({correct1}/{total1})", f"Duration: {duration_test1:.2f}s"])
        writer.writerow(["SUMMARY", "Test 2", f"Accuracy: {accuracy2:.2f}% ({correct2}/{total2})", f"Duration: {duration_test2:.2f}s"])
    
    print(f"Test 1 - Accuracy: {correct1}/{total1} ({accuracy1:.2f}%), Duration: {duration_test1:.2f}s")
    print(f"Test 2 - Accuracy: {correct2}/{total2} ({accuracy2:.2f}%), Duration: {duration_test2:.2f}s")
    
    show_message("Experiment Complete! Thank you.", duration=5)
    pygame.quit()
    print("Stroop Experiment finished.")

# ====================================
# MAIN FUNCTION: EEG COLLECTION & EXPERIMENT
# ====================================
def main():
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = "COM8"  # Adjust port as needed
    board = BoardShim(BoardIds.CYTON_BOARD, params)
    board.prepare_session()
    board.start_stream(45000)
    
    # Run the integrated experiment (markers inserted programmatically)
    run_experiment(board)
    
    # Retrieve EEG data after experiment
    data = board.get_board_data()
    # Save EEG data (all channels except the last timestamp row)
    np.save(eeg_save_file, data[:-1, :])
    # Save auxiliary channels (using board.get_analog_channels)
    aux_channels = board.get_analog_channels(BoardIds.CYTON_BOARD)
    np.save(aux_save_file, data[aux_channels, :])
    # Save timestamps (last row)
    np.save(timestamps_save_file, data[-1, :])
    
    print(f"EEG Data saved:\n EEG: {eeg_save_file}\n AUX: {aux_save_file}\n Timestamps: {timestamps_save_file}")
    
    board.stop_stream()
    board.release_session()
    print("EEG session closed.")

if __name__ == "__main__":
    main()
