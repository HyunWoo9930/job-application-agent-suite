# Job Application Agent Suite

[한국어 README](./README.md)

A multi-agent toolkit for Korean job application writing. It covers company and role analysis, reusable experience mining, question matching, drafting, tone adjustment, AI-style review, and final packaging.

## Overview

The workflow is split into the following stages:

1. `agent-00` intake validation
2. `agent-01a` industry analysis
3. `agent-01b` company analysis
4. `agent-01c` role analysis
5. `agent-01` synthesis
6. `agent-02a` corpus scan and reusable experience recommendation
7. `agent-02` experience mining
8. `agent-03` question-to-experience matching
9. `agent-03b` refinement and tail questions
10. `agent-03c` metric evidence validation
11. `agent-04` drafting
12. `agent-05` tone adjustment
13. `agent-06` AI-style and QA review
14. `agent-07` final packaging

This repository is designed as a controllable writing pipeline rather than a single-shot generator.

## Use Cases

- Organizing repeated Korean job application writing workflows
- Reusing experience evidence from older essays and notes
- Matching each question to the strongest supporting experience
- Reviewing drafts for repetitive phrasing and formulaic tone
- Using the project as a Codex skill or as a standalone prompt/script set

<details>
<summary>Repository structure</summary>

```text
job-application-agent-suite/
├── README.md
├── README.en.md
├── CONTRIBUTING.md
├── LICENSE
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── templates/
```

- `references/`: agent prompt files
- `scripts/`: pipeline helper scripts
- `templates/`: sample JSON inputs
- `SKILL.md`: Codex skill operating rules

</details>

<details>
<summary>Requirements and platform support</summary>

- macOS or Linux
- Python 3.9+
- UTF-8 terminal environment

Supported corpus formats:

- `.txt`
- `.md`
- `.markdown`
- `.rst`
- `.docx`

Not directly supported by the current scanner:

- `.pdf`
- `.hwp`

Example:

```bash
brew install python ripgrep git
```

Windows is not completely unsupported. Most scripts are plain Python and use `pathlib`, so they are likely to work, but the documented default paths and install examples are written for macOS/Linux. On Windows, the practical approach is to adapt the paths and command names.

Example:

```powershell
py scripts\use_agent.py --list
py scripts\scan_experience_corpus.py --path "$HOME\Desktop\취업\자기소개서"
```

</details>

## Quick Start

```bash
git clone https://github.com/HyunWoo9930/job-application-agent-suite.git
cd job-application-agent-suite
python3 scripts/use_agent.py --list
```

Print a prompt:

```bash
python3 scripts/use_agent.py --agent agent-01
python3 scripts/use_agent.py --agent agent-04
python3 scripts/use_agent.py --agent feedback
```

Render a prompt with sample input:

```bash
python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json
python3 scripts/use_agent.py --agent agent-06 --input templates/agent-06-input-from-existing-draft.sample.json
```

These commands print prompt text and do not call an LLM API directly.

## Codex Skill Installation

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/job-application-agent-suite ~/.codex/skills/
python3 ~/.codex/skills/job-application-agent-suite/scripts/use_agent.py --list
```

<details>
<summary>Scripts</summary>

### `scripts/use_agent.py`

Prints an agent prompt and optionally interpolates `{{variables}}` from JSON.

```bash
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
```

### `scripts/scan_experience_corpus.py`

Scans an essay corpus and extracts reusable experience candidates.

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --write-output /tmp/corpus_candidates.json
```

### `scripts/orchestrate_pipeline.py`

Creates and manages a per-question run directory with `state.json`.

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

### `scripts/persist_analysis_cache.py`

Saves and reloads company-role analysis artifacts.

```bash
python3 scripts/persist_analysis_cache.py \
  --input templates/pipeline-state.sample.json \
  --mode save
```

### `scripts/char_window_check.py`

Checks whether a draft fits within `N-20 .. N`.

```bash
python3 scripts/char_window_check.py --file /tmp/draft.txt --char-limit 800
```

### `scripts/ai_style_checker.py`

Reviews repetitive phrasing, formulaic endings, long lines, and repeated sentence starters.

```bash
python3 scripts/ai_style_checker.py --file /tmp/draft.txt
```

</details>

<details>
<summary>End-to-end example</summary>

```bash
mkdir -p ~/job_runs/naver_backend/Q1
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

Scan a local corpus:

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --state-input ~/job_runs/naver_backend/Q1/state.json \
  --write-state ~/job_runs/naver_backend/Q1/state.json
```

Review a draft:

```bash
python3 scripts/char_window_check.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt \
  --char-limit 800
python3 scripts/ai_style_checker.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt
```

</details>

<details>
<summary>Included templates</summary>

- `templates/agent-00-input.sample.json`
- `templates/agent-02a-input.sample.json`
- `templates/agent-03b-input.sample.json`
- `templates/agent-03c-input.sample.json`
- `templates/agent-06-input-from-existing-draft.sample.json`
- `templates/agent-07-input.sample.json`
- `templates/pipeline-state.sample.json`

</details>

<details>
<summary>Workflow notes</summary>

- default approval mode: `manual_per_step`
- `agent-02a.ready_for_agent_02 = false` blocks the next stage
- `external_feedback_required = true` and empty `external_feedback_notes` blocks `agent-07`
- final length target: `char_limit - 20 <= length <= char_limit`

</details>

## FAQ

### Does this repository call an LLM API directly?

No. The repository centers on prompt files and helper scripts.

### Does it work on Windows?

It is not fully unsupported. The scripts are mostly portable, but the documented defaults assume macOS/Linux paths. In practice, Windows usage means replacing `python3` with `py` and adapting file paths.

### Why is `.pdf` not directly supported?

The current corpus scanner reads `.docx` by parsing document XML and does not include a PDF parser.

## License

MIT License. See [LICENSE](./LICENSE).
