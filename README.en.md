# Job Application Agent Suite

[한국어 README](./README.md)

A multi-agent toolkit for Korean job application writing. It breaks the workflow into smaller stages so you can analyze a target company and role, mine reusable experiences, draft answers, adjust tone, run AI-style checks, and package a final submission.

This repository can be used in two ways:

1. As a Codex skill under `~/.codex/skills`
2. As a normal GitHub repository with reusable prompts, scripts, and templates

---

## What It Does

The suite covers the full application-writing pipeline:

1. `agent-00` intake validation
2. `agent-01a` industry analysis
3. `agent-01b` company analysis
4. `agent-01c` role analysis
5. `agent-01` synthesis
6. `agent-02a` corpus scan and reusable experience recommendation
7. `agent-02` experience mining
8. `agent-03` question-to-experience matching
9. `agent-03b` refinement and tail questions
10. `agent-03c` metric and evidence validation
11. `agent-04` drafting
12. `agent-05` tone customization
13. `agent-06` AI-style and QA review
14. `agent-07` final packaging

The main goal is not "one-click generation," but a controllable, reviewable writing workflow.

---

## Repository Structure

```text
job-application-agent-suite/
├── README.md
├── README.en.md
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── templates/
```

- `references/`: prompt files for each agent
- `scripts/`: helper scripts for pipeline flow, validation, and corpus scan
- `templates/`: sample JSON inputs
- `SKILL.md`: Codex skill operating instructions

---

## Requirements

- macOS or Linux
- Python 3.9+
- UTF-8 terminal environment

Recommended:

- `ripgrep`
- Git

Supported corpus file formats:

- `.txt`
- `.md`
- `.markdown`
- `.rst`
- `.docx`

Not directly supported by the current scanner:

- `.pdf`
- `.hwp`

Install example on macOS:

```bash
brew install python ripgrep git
```

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/HyunWoo9930/job-application-agent-suite.git
cd job-application-agent-suite
```

List available agents:

```bash
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

These commands do not call an LLM directly. They print the prompt text you can feed into your model workflow.

---

## Install As a Codex Skill

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/job-application-agent-suite ~/.codex/skills/
```

Expected final path:

```text
~/.codex/skills/job-application-agent-suite
```

Verify installation:

```bash
python3 ~/.codex/skills/job-application-agent-suite/scripts/use_agent.py --list
```

---

## Script Overview

### `scripts/use_agent.py`

Prints a specific agent prompt and optionally interpolates `{{variables}}` from a JSON file.

```bash
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
```

### `scripts/scan_experience_corpus.py`

Scans a local essay/application corpus and extracts reusable experience candidates.

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --write-output /tmp/corpus_candidates.json
```

### `scripts/orchestrate_pipeline.py`

Creates and manages a per-question run directory and `state.json`.

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

### `scripts/persist_analysis_cache.py`

Saves or reloads company/role analysis artifacts for reuse.

```bash
python3 scripts/persist_analysis_cache.py \
  --input templates/pipeline-state.sample.json \
  --mode save
```

### `scripts/char_window_check.py`

Checks whether a draft is within `N-20 .. N`.

```bash
python3 scripts/char_window_check.py --file /tmp/draft.txt --char-limit 800
```

### `scripts/ai_style_checker.py`

Runs a heuristic AI-style review for repeated abstract phrases, formulaic endings, repetition, and readability issues.

```bash
python3 scripts/ai_style_checker.py --file /tmp/draft.txt
```

---

## First End-to-End Run

Create a run directory:

```bash
mkdir -p ~/job_runs/naver_backend/Q1
```

Initialize it with the sample pipeline state:

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

Scan an existing corpus:

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --state-input ~/job_runs/naver_backend/Q1/state.json \
  --write-state ~/job_runs/naver_backend/Q1/state.json
```

Check a draft:

```bash
python3 scripts/char_window_check.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt \
  --char-limit 800
```

```bash
python3 scripts/ai_style_checker.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt
```

---

## Smoke Test

```bash
python3 scripts/use_agent.py --list
printf 'Test sentence.\n' > /tmp/jaso_test.txt
python3 scripts/char_window_check.py --file /tmp/jaso_test.txt --char-limit 20
python3 scripts/ai_style_checker.py --file /tmp/jaso_test.txt
```

---

## Publishing Notes

Before publishing, make sure the repository does not include:

- private application drafts
- personal phone/email/address data
- confidential company details
- cached outputs from real applications

Recommended files for a clean public repo:

- `README.md`
- `README.en.md`
- `SKILL.md`
- `agents/`
- `references/`
- `scripts/`
- `templates/`
- `LICENSE`
- `.gitignore`

---

## License

This repository currently uses the MIT License. See `LICENSE` for details.
