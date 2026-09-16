# Nback App

Run using command 
```python3 pygame_nback.py```

The default experimental block number is 9, but the number of experimental blocks can be set with the --blocks flag:
```python3 pygame_nback.py --blocks 3```

Debug mode can also be toggled with the --debug flag. This reduces the rest time during fixation and decreases the number of trials per experimental block. The default for this flag is False
```python3 pygame_nback.py --debug True```

## Stroop test

Install Pygame if needed: `python3 -m pip install pygame`.
Run from this folder: `python3 stroop-test.py`.

Select the **ink color**, ignoring the word itself. All words are incongruent.
Click the black-text answer buttons below the word. Press Space to start and
Escape to quit. The initial white fixation cross on black lasts 30 seconds,
matching the n-back app.

Customize the number of words, time between word onsets, and initial fixation:

```sh
python3 stroop-test.py --trials 60 --interval-ms 2500 --fixation-ms 30000
```

The interval is also the response deadline. Each word stays visible for that
interval, even after an answer; only the first answer counts. Edit the `COLORS`
list in the script to change the available words, ink colors, and answer buttons.
Each entry contains a unique name and an RGB tuple; at least two are required.

Results are saved in `results/stroop_<timestamp>.csv` beside the script. Use
`--output path/to/results.csv` to choose a new file (existing files are never
overwritten). Each presented word has one row with its trial number, response
time in milliseconds, ink color (`word_color`), word meaning (`word_text`),
user answer, correct answer (the ink color), correctness, and status.
Missed answers have blank answer/time fields, `is_correct=False`, and
`status=no_response`; an unanswered word on early exit has `status=interrupted`.
Answered trials are saved immediately, including when you exit early.
Use `--seed 123` for reproducible stimulus choices, or `--help` for all options.

### Requirements and installation

The Stroop program requires Python 3.8 or newer, Pygame 2.5 or newer (below
version 3), a graphical desktop, and a mouse. It opens a 1024 × 720 window.
It uses Python's standard library for CSV saving and does not require NumPy
or pandas. `environment.yml` describes the older n-back environment; use
`requirements-stroop.txt` for the Stroop program.

From the repository folder (`task_apps`), create an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-stroop.txt
.venv/bin/python stroop-test.py --trials 40 --interval-ms 2000
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.
If your terminal is in the parent `stroop-test` folder, first run `cd task_apps`.
If macOS reports `/opt/homebrew/bin/python3: No such file or directory`, use
`/usr/bin/python3` instead of `python3` to create the environment, provided
`/usr/bin/python3 --version` works and reports Python 3.8 or newer:

```sh
/usr/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-stroop.txt
.venv/bin/python stroop-test.py --trials 40 --interval-ms 2000
```

### Configuration reference

| Option | Default | Meaning |
| --- | --- | --- |
| `--trials` | `40` | Total number of words; a positive integer. |
| `--interval-ms` | `2000` | Word display duration and response deadline in milliseconds; a positive integer. |
| `--fixation-ms` | `30000` | Initial fixation duration in milliseconds; a nonnegative integer. Set to `0` to skip. |
| `--output` | Timestamped CSV in `results/` beside the script | Output path; parent folders are created and existing files are never overwritten. Relative paths use the terminal's current folder. |
| `--seed` | Random each run | Integer seed for reproducible word/ink pairs with the same color list. |
| `--help` | — | Show available options and exit. |

Default colors are red, blue, green, and yellow. For example, add
`("purple", (128, 0, 128))` to `COLORS` to include purple. Names and RGB values
must each be unique, RGB channels must be integers between 0 and 255, and
at least two colors are needed. Buttons are generated automatically in up
to four columns; excessive color counts or long labels are rejected if they
cannot fit the window. Answer labels always use black text.

Each trial samples two distinct entries: one supplies the word and the other
supplies its ink color. There are no congruent trials. Sampling is random;
color frequencies are not guaranteed to be balanced. The first valid left
click counts. A selected button is highlighted until the next word. There
is no correctness feedback during the test. The final screen shows the
number correct out of all recorded trials.

### CSV specification

| Column | Meaning |
| --- | --- |
| `trial` | Trial number, starting at 1. |
| `response_time_ms` | Milliseconds from display of the first word frame to processing the first valid click; blank for an unanswered trial. |
| `word_color` | Actual ink color name. |
| `word_text` | Color named by the displayed word. |
| `user_answer` | Selected color name; blank if unanswered. |
| `correct_answer` | Correct color name, equal to `word_color`. |
| `is_correct` | `True` for a correct answer, otherwise `False`. |
| `status` | `answered`, `no_response` (deadline reached), or `interrupted` (unanswered trial when Escape/window close ends the test). |

Example:

```csv
trial,response_time_ms,word_color,word_text,user_answer,correct_answer,is_correct,status
1,521.337,blue,red,blue,blue,True,answered
2,,green,yellow,,green,False,no_response
```

The header is written at launch and each trial row is flushed when recorded.
Trials that have not appeared are not recorded. Exiting before the first word
leaves a header-only CSV. Results and local virtual environments are excluded
from version control by `.gitignore`.

Timing uses a monotonic clock, with reaction time starting immediately after
the first stimulus frame is presented. The display loop runs at up to 60 frames
per second, so configured intervals and response times are subject to frame
scheduling and input-processing delay. These are software measurements, not
hardware-calibrated stimulus timings.
