import os
import pygame
import random
import time
import csv
import sys
from datetime import datetime

# -------------------------------------------------------------------
# USER INPUT FOR SUBJECT & SESSION
# -------------------------------------------------------------------
subject_id = input("Enter Subject ID: ").strip()
session_id = input("Enter Session Number: ").strip()
if not subject_id or not session_id.isdigit():
    print("Invalid input. Please enter a valid Subject ID and numeric Session ID.")
    sys.exit()

session_id = int(session_id)  # Convert session number to integer

save_dir = os.path.join(
    os.path.dirname(__file__),  
    "..",                       
    "data"
)
os.makedirs(save_dir, exist_ok=True)

# Construct a filename: "stroop_results_SUBJECTID_SESSIONID.csv"
save_filename = f"stroop_results_{subject_id}_session_{session_id}.csv"
save_path = os.path.join(save_dir, save_filename)

# -------------------------------------------------------------------
# PYGAME SETUP (Full Screen)
# -------------------------------------------------------------------
pygame.init()

# Grab the full screen resolution of the current display
info_object = pygame.display.Info()
WIDTH, HEIGHT = info_object.current_w, info_object.current_h

# Create a full screen display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Stroop Test")

# Define color dictionary
COLORS = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (200, 200, 0)
}
COLOR_KEYS = list(COLORS.keys())

# Fonts
FONT = pygame.font.Font(None, 80)
INSTRUCTION_FONT = pygame.font.Font(None, 40)

# -------------------------------------------------------------------
# EXPERIMENT VARIABLES
# -------------------------------------------------------------------
WAIT_DURATION = 10  # 300 seconds = 5 minutes. Adjust as needed.

# -------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------
def save_results(results_list):
    """
    Appends results to a CSV file. If the file does not exist,
    it creates it and writes the header row.
    """
    file_exists = os.path.isfile(save_path)
    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Test Number",
                "Round Number",
                "Word",
                "Match?",        # Indicates if this trial is a match trial.
                "User Response",
                "Reaction Time",
                "Correct",       # Indicates if the subject's response was correct.
                "Timestamp"
            ])
        writer.writerows(results_list)
    print(f"Results saved to {save_path}")

def generate_trials():
    """
    Creates 20 Stroop trials with a random ratio of matching vs. non-matching.
    
    A random number (between 0 and 20) is chosen for matching trials.
    The remaining trials are non-matching.
    """
    total_trials = 20
    num_match = random.randint(0, total_trials)
    num_mismatch = total_trials - num_match
    trials = []

    # Create match trials (word's text and color match)
    for _ in range(num_match):
        word = random.choice(COLOR_KEYS)
        trials.append((word, COLORS[word], True))
    
    # Create mismatch trials (word's text and color do NOT match)
    for _ in range(num_mismatch):
        word = random.choice(COLOR_KEYS)
        mismatch_choices = [c for c in COLOR_KEYS if c != word]
        color_choice = random.choice(mismatch_choices)
        trials.append((word, COLORS[color_choice], False))
    
    random.shuffle(trials)
    return trials

def show_message(message, duration=3):
    """
    Displays a simple message on screen for `duration` seconds.
    (Note: ESC won't interrupt these brief messages.)
    """
    screen.fill((255, 255, 255))
    msg_surface = INSTRUCTION_FONT.render(message, True, (0, 0, 0))
    msg_rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(msg_surface, msg_rect)
    pygame.display.flip()
    time.sleep(duration)

def run_timer(duration, message):
    """
    Displays a countdown timer for `duration` seconds with `message`.
    ESC can be used to exit at any time.
    """
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        remaining = int(duration - elapsed)
        if remaining < 0:
            remaining = 0

        screen.fill((255, 255, 255))

        # Display the message
        msg_surface = INSTRUCTION_FONT.render(message, True, (0, 0, 0))
        msg_rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(msg_surface, msg_rect)

        # Display the timer
        timer_surface = FONT.render(f"Time Remaining: {remaining}s", True, (0, 0, 0))
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
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
    """
    Runs 20 trials of the Stroop Test and returns a list of results.
    Each trial result includes:
        [test_number, round_number, word, is_match, user_response, reaction_time, is_correct, timestamp]
    """
    results = []
    trials = generate_trials()

    for i in range(20):
        trial_timestamp = datetime.now().isoformat()
        screen.fill((255, 255, 255))
        word, color, is_match = trials[i]

        # Render the Stroop word
        text_surface = FONT.render(word, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, text_rect)

        # Render instructions (only F and J keys are valid)
        inst_surface = INSTRUCTION_FONT.render("Press F for Correct | Press J for Incorrect", True, (0, 0, 0))
        screen.blit(inst_surface, (WIDTH // 2 - 200, HEIGHT - 50))
        pygame.display.flip()

        start_time = time.time()
        response = None
        waiting_for_response = True

        # Wait for valid key press (F or J) or ESC to quit
        while waiting_for_response:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    save_results(results)
                    pygame.quit()
                    sys.exit(0)
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_ESCAPE:
                        save_results(results)
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

# -------------------------------------------------------------------
# FULL EXPERIMENT
# -------------------------------------------------------------------
def run_experiment():
    """
    Runs the entire experiment:
      1) Control Recording (EEG Baseline) - WAIT_DURATION
      2) Break - WAIT_DURATION
      3) Attention Test (Initial Stroop) - 5 rounds
      4) Doom Scroll - WAIT_DURATION
      5) Attention Task (Post-exposure Stroop) - 5 rounds

    After each Stroop test, overall accuracy and total time are computed.
    Summary rows for each test are appended to the CSV.
    """
    all_results = []

    # 1) Control Recording
    show_message("Control Recording Phase (EEG Baseline) - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Control Recording Phase (EEG Baseline)")

    # 2) Break
    show_message("Break Phase - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Break Phase")

    # 3) Attention Test (Initial Stroop)
    show_message("Attention Test - Stroop Test Begins", duration=2)
    test1_start_time = time.time()
    for round_number in range(1, 6):
        show_message(f"Starting Stroop Round {round_number} / 5", duration=2)
        test_results = run_stroop_test(test_number=1, round_number=round_number)
        all_results.extend(test_results)
    test1_total_time = time.time() - test1_start_time

    # 4) Doom Scroll
    show_message("Doom Scroll Phase - Get Ready", duration=2)
    run_timer(WAIT_DURATION, "Doom Scroll Phase - Watch Short Videos")

    # 5) Attention Task (Post-exposure Stroop)
    show_message("Post-exposure Attention Task - Stroop Test Begins", duration=2)
    test2_start_time = time.time()
    for round_number in range(1, 6):
        show_message(f"Starting Stroop Round {round_number} / 5", duration=2)
        test_results = run_stroop_test(test_number=2, round_number=round_number)
        all_results.extend(test_results)
    test2_total_time = time.time() - test2_start_time

    # Save trial results to CSV
    if all_results:
        save_results(all_results)

    # Compute accuracy for each Stroop test (Test 1 and Test 2)
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

    # Append summary rows for each test's accuracy and total time to the CSV
    with open(save_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SUMMARY", "Test 1", f"Accuracy: {accuracy1:.2f}% ({correct1}/{total1})", "", "", "", "", ""])
        writer.writerow(["SUMMARY", "Test 1", f"Total Time: {test1_total_time:.2f} seconds", "", "", "", "", ""])
        writer.writerow(["SUMMARY", "Test 2", f"Accuracy: {accuracy2:.2f}% ({correct2}/{total2})", "", "", "", "", ""])
        writer.writerow(["SUMMARY", "Test 2", f"Total Time: {test2_total_time:.2f} seconds", "", "", "", "", ""])

    print(f"Overall Accuracy Test 1: {correct1}/{total1} ({accuracy1:.2f}%)")
    print(f"Total Time Test 1: {test1_total_time:.2f} seconds")
    print(f"Overall Accuracy Test 2: {correct2}/{total2} ({accuracy2:.2f}%)")
    print(f"Total Time Test 2: {test2_total_time:.2f} seconds")

    show_message("Experiment Complete! Thank you.", duration=5)
    pygame.quit()
    print("Experiment finished.")

# If this file is run directly, execute run_experiment()
if __name__ == "__main__":
    run_experiment()
