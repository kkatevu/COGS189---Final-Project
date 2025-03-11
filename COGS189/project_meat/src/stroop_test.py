import os
import pygame
import random
import time
import csv
import sys
from datetime import datetime  # NEW: for timestamps

def main():
    """
    Modified Stroop Test:
      - Prompts for user ID
      - Saves partial or full data to data/stroop_results_<USER_ID>.csv
      - 5 tests total, each with 20 trials
      - 'Exit Early' button allows partial saving
      - NOW includes a Timestamp column for each trial.
    """

    # -------------------------------------------------------------------------
    # 1) Ask for User ID and Build Save Path
    # -------------------------------------------------------------------------
    user_id = input("Enter user ID: ").strip()

    # Construct path: place CSV inside the ../data directory relative to this script
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    save_path = os.path.join(data_dir, f"stroop_results_{user_id}.csv")

    # -------------------------------------------------------------------------
    # 2) Initialize Pygame and Set Up
    # -------------------------------------------------------------------------
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stroop Test")

    # Darker yellow for better visibility
    COLORS = {
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "BLUE": (0, 0, 255),
        "YELLOW": (200, 200, 0)
    }
    COLOR_KEYS = list(COLORS.keys())

    # Fonts
    FONT = pygame.font.Font(None, 80)
    BUTTON_FONT = pygame.font.Font(None, 50)
    INSTRUCTION_FONT = pygame.font.Font(None, 40)

    # "Continue" button & "Exit" button side by side
    continue_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 40, 150, 60)
    exit_rect     = pygame.Rect(WIDTH // 2 +  10, HEIGHT // 2 + 40, 150, 60)

    # Master list of all results
    all_results = []

    # -------------------------------------------------------------------------
    # 3) Helper Functions
    # -------------------------------------------------------------------------
    def generate_trials():
        """Generate 20 trials: 10 correct (word == color) and 10 incorrect."""
        trials = []
        num_correct = 10
        num_incorrect = 10

        while num_correct > 0 or num_incorrect > 0:
            word = random.choice(COLOR_KEYS)
            # Decide if this trial will be correct or incorrect
            if num_correct > 0 and random.random() < 0.5:
                color = word  # Match
                num_correct -= 1
            else:
                possible_colors = [c for c in COLOR_KEYS if c != word]
                color = random.choice(possible_colors)  # Mismatch
                num_incorrect -= 1
            trials.append((word, COLORS[color], word == color))

        random.shuffle(trials)
        return trials

    def draw_menu(message):
        """
        Draws the screen with a message and two buttons:
          [Continue]  [Exit Early]
        """
        screen.fill((255, 255, 255))

        # Show message
        msg_surface = INSTRUCTION_FONT.render(message, True, (0, 0, 0))
        msg_rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(msg_surface, msg_rect)

        # Draw Continue button
        pygame.draw.rect(screen, (0, 128, 0), continue_rect, border_radius=8)
        c_text = BUTTON_FONT.render("Continue", True, (255, 255, 255))
        c_text_rect = c_text.get_rect(center=continue_rect.center)
        screen.blit(c_text, c_text_rect)

        # Draw Exit button
        pygame.draw.rect(screen, (128, 0, 0), exit_rect, border_radius=8)
        e_text = BUTTON_FONT.render("Exit Early", True, (255, 255, 255))
        e_text_rect = e_text.get_rect(center=exit_rect.center)
        screen.blit(e_text, e_text_rect)

        pygame.display.flip()

    def handle_menu():
        """
        Waits until the user clicks one of the two buttons:
          - 'Continue' => return "continue"
          - 'Exit Early' => return "exit"
        """
        while True:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    # User closed the window => exit early
                    return "exit"
                elif evt.type == pygame.MOUSEBUTTONDOWN:
                    if continue_rect.collidepoint(evt.pos):
                        return "continue"
                    elif exit_rect.collidepoint(evt.pos):
                        return "exit"

    def save_results(results_list):
        """
        Appends results to CSV at `save_path`.
        If file doesn't exist, write the header first.
        """
        file_exists = os.path.isfile(save_path)
        with open(save_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Test Number",
                    "Word",
                    "Match?",
                    "User Response",
                    "Reaction Time",
                    "Correct",
                    "Timestamp"  # <--- NEW COLUMN
                ])
            writer.writerows(results_list)
        print(f"Results saved to {save_path}")

    def run_one_test(test_number):
        """
        Runs exactly 20 trials for a given test_number.
        Returns a list of [test_number, word, is_match, response, rt, is_correct, timestamp].
        """
        results = []
        trials = generate_trials()

        for i in range(20):
            # Record the timestamp for this trial's start
            trial_timestamp = datetime.now().isoformat()

            screen.fill((255, 255, 255))
            word, color, is_match = trials[i]

            # Render the Stroop word
            text_surface = FONT.render(word, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)

            # Render instructions
            inst_surface = INSTRUCTION_FONT.render(
                "Press F for Correct | Press J for Incorrect",
                True, (0, 0, 0)
            )
            screen.blit(inst_surface, (WIDTH // 2 - 200, HEIGHT - 50))

            pygame.display.flip()

            start_time = time.time()
            response = None

            # Wait for user key press
            waiting_for_response = True
            while waiting_for_response:
                for evt in pygame.event.get():
                    if evt.type == pygame.QUIT:
                        # Exit early => save partial results
                        if results:
                            all_results.extend(results)
                        save_results(all_results)
                        pygame.quit()
                        sys.exit(0)

                    elif evt.type == pygame.KEYDOWN:
                        if evt.key == pygame.K_f:
                            response = True  # user thinks it's a match
                            waiting_for_response = False
                        elif evt.key == pygame.K_j:
                            response = False # user thinks it's NOT a match
                            waiting_for_response = False

            reaction_time = time.time() - start_time
            is_correct = (response == is_match)
            results.append([
                test_number, 
                word, 
                is_match, 
                response, 
                reaction_time, 
                is_correct, 
                trial_timestamp  # add timestamp
            ])

            # Short delay (100ms) between trials
            pygame.time.delay(100)

        return results

    # -------------------------------------------------------------------------
    # 4) Main Loop: 5 Tests
    # -------------------------------------------------------------------------
    current_test = 1
    while current_test <= 5:
        # Show menu: "Begin Test X" or "Test X Completed"
        if current_test == 1:
            draw_menu(f"Begin Test {current_test}")
        else:
            draw_menu(f"Test {current_test - 1} Completed. Begin Test {current_test}?")

        choice = handle_menu()
        if choice == "exit":
            # Save partial results and exit
            if all_results:
                save_results(all_results)
            pygame.quit()
            print("Exited early.")
            return

        # Run the test
        test_results = run_one_test(current_test)
        all_results.extend(test_results)

        current_test += 1

    # After finishing all 5 tests, show "All done"
    draw_menu("All 5 Tests Complete!")
    pygame.display.flip()

    choice = handle_menu()
    # Regardless of the choice, save final results
    if all_results:
        save_results(all_results)

    pygame.quit()
    print("All tests complete. Program finished.")

# -----------------------------------------------------------------------------
# Run the script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
