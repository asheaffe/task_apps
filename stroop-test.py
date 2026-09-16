"""Pygame Stroop task. Run with --help for timing and color options."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import random
import time

# Add or remove entries here; names are both stimulus words and answer labels.
COLORS = [
    ("red", (255, 0, 0)),
    ("blue", (0, 0, 255)),
    ("green", (0, 160, 0)),
    ("yellow", (255, 215, 0)),
]
FIELDS = ["trial", "response_time_ms", "word_color", "word_text",
          "user_answer", "correct_answer", "is_correct", "status"]


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or a positive integer")
    return number


def pick_stimulus(colors, rng=random):
    """Sample two distinct colors, guaranteeing incongruence."""
    word, ink = rng.sample(colors, 2)
    return word[0], ink[0], ink[1]


def result_row(trial, word, ink, answer, response_time, status):
    return dict(zip(FIELDS, [trial, response_time, ink, word, answer or "",
                             ink, bool(answer == ink), status]))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=positive_int, default=40,
                        help="number of words (default: 40)")
    parser.add_argument("--interval-ms", type=positive_int, default=2000,
                        help="time between word onsets, also the response deadline (default: 2000)")
    parser.add_argument("--fixation-ms", type=nonnegative_int, default=30000,
                        help="initial fixation duration (default: 30000, matching n-back)")
    parser.add_argument("--output", type=Path,
                        help="CSV path; default: a timestamped file in results beside this script")
    parser.add_argument("--seed", type=int, help="optional random seed")
    return parser.parse_args()


def run(args):
    import pygame

    names = [name for name, rgb in COLORS]
    if len(COLORS) < 2 or len(set(names)) != len(names):
        raise ValueError("COLORS must contain at least two uniquely named colors")
    for name, rgb in COLORS:
        if not name or len(rgb) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in rgb):
            raise ValueError("Each color needs a nonempty name and three RGB integers from 0 to 255")
    if len(set(rgb for name, rgb in COLORS)) != len(COLORS):
        raise ValueError("Each color must have a distinct RGB value")

    output = args.output or Path(__file__).resolve().parent / "results" / (
        "stroop_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv")
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    # Exclusive creation prevents accidentally overwriting a previous session.
    with output.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        handle.flush()
        pygame.display.init()
        pygame.font.init()
        try:
            screen = pygame.display.set_mode((1024, 720))
            pygame.display.set_caption("Stroop test")
            clock = pygame.time.Clock()
            font = pygame.font.SysFont("Arial", 30)
            word_font = pygame.font.SysFont("Arial", 72)
            black, white = (0, 0, 0), (255, 255, 255)
            columns = min(4, len(COLORS))
            rows = (len(COLORS) + columns - 1) // columns
            button_height = min(64, 220 // rows)
            if button_height < 30:
                raise ValueError("Too many colors to fit the answer buttons in this window")
            buttons = []
            label_font = pygame.font.SysFont("Arial", min(30, button_height - 8))
            for index, name in enumerate(names):
                rect = pygame.Rect(40 + (index % columns) * (944 // columns),
                                   440 + (index // columns) * (button_height + 8),
                                   944 // columns - 12, button_height)
                label = label_font.render(name, True, black)
                if label.get_width() > rect.width - 12:
                    raise ValueError("Color name is too long for its answer button: " + name)
                buttons.append((rect, name, label))

            def centered(text, y, color=black, text_font=font):
                rendered = text_font.render(text, True, color)
                screen.blit(rendered, rendered.get_rect(center=(512, y)))

            state = "instructions"
            fixation_start = None
            onset = None
            trial = 0
            word = ink = None
            ink_rgb = None
            answered = False
            selected = None
            correct = 0
            recorded = 0
            running = True

            def save(answer, response_time, status):
                nonlocal recorded, correct
                writer.writerow(result_row(trial, word, ink, answer, response_time, status))
                handle.flush()
                recorded += 1
                correct += int(answer == ink)

            while running:
                events = pygame.event.get()
                now = time.perf_counter()
                if any(event.type == pygame.QUIT or
                       (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                       for event in events):
                    if state == "trial" and not answered:
                        save(None, "", "interrupted")
                    break

                if state == "instructions":
                    if any(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE for event in events):
                        state = "fixation"
                        fixation_start = now
                elif state == "trial":
                    # Process the deadline before input so late clicks cannot count.
                    if (now - onset) * 1000 >= args.interval_ms:
                        if not answered:
                            save(None, "", "no_response")
                        state = "done" if trial >= args.trials else "next"
                    elif not answered:
                        for event in events:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                selected = next((name for rect, name, label in buttons
                                                 if rect.collidepoint(event.pos)), None)
                                if selected is not None:
                                    save(selected, round((time.perf_counter() - onset) * 1000, 3), "answered")
                                    answered = True
                                    break
                elif state == "done":
                    if any(event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE for event in events):
                        running = False

                if state == "fixation" and (now - fixation_start) * 1000 >= args.fixation_ms:
                    state = "next"
                starting_trial = state == "next"
                if starting_trial:
                    trial += 1
                    word, ink, ink_rgb = pick_stimulus(COLORS, rng)
                    answered = False
                    selected = None
                    state = "trial"

                screen.fill(black if state == "fixation" else white)
                if state == "instructions":
                    centered("Stroop test", 180)
                    centered("Select the INK COLOR of each word.", 260)
                    centered("Ignore what the word says. Click an answer below it.", 310)
                    centered(f"{args.trials} words; {args.interval_ms / 1000:g} seconds per word.", 360)
                    centered(f"First, stare at the + for {args.fixation_ms / 1000:g} seconds.", 410)
                    centered("Press SPACE to begin. ESC exits and keeps your results.", 490)
                elif state == "fixation":
                    centered("+", 360, white)
                elif state == "trial":
                    centered(f"Word {trial} of {args.trials}", 100)
                    centered(word.upper(), 280, ink_rgb, word_font)
                    for rect, name, label in buttons:
                        pygame.draw.rect(screen, (220, 220, 220) if name == selected else white, rect)
                        pygame.draw.rect(screen, black, rect, 2)
                        screen.blit(label, label.get_rect(center=rect.center))
                elif state == "done":
                    centered("Test complete", 270)
                    centered(f"Correct: {correct} / {recorded}", 340)
                    centered("Results saved. Press SPACE to close.", 410)
                pygame.display.flip()
                if starting_trial:
                    # Reaction times start when the first stimulus frame is displayed.
                    onset = time.perf_counter()
                clock.tick(60)
        finally:
            pygame.quit()
    print(f"Results saved to: {output}")


if __name__ == "__main__":
    arguments = parse_args()
    try:
        run(arguments)
    except ModuleNotFoundError as exc:
        if exc.name != "pygame":
            raise
        raise SystemExit("Pygame is required. Install it with: python3 -m pip install pygame")
