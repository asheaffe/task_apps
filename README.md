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


Customize the number of words, time between word onsets, and initial fixation:

```sh
python3 stroop-test.py --trials 60 --interval-ms 2500 --fixation-ms 30000
```

### Requirements


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
at least two colors are needed. 


### CSV spec

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

