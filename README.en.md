# Job Application Agent Suite

[한국어 README](./README.md)

A multi-agent toolkit for Korean job application writing. It covers company and role analysis, reusable experience mining, question matching, drafting, tone adjustment, AI-style review, and final packaging.

> 1-minute usage
>
> 1. Clone the repository.
> 2. Run `python3 scripts/use_agent.py --list` to see available agents.
> 3. Run `python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json` to print one prompt.
> 4. Open the `examples/` folder to see sample draft and QA output formats.
> 5. If you want Codex to call it as a skill, first place this folder in `~/.codex/skills/job-application-agent-suite`.
> 6. Then ask Codex something like `Use job-application-agent-suite and help me draft one application answer`.

> Important
>
> The outputs from this repository should not be treated as final submission-ready essays by default.
> You should review them yourself, and ideally get additional feedback from another AI or a human reviewer before submitting anything.

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
├── examples/
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
- `examples/`: beginner-friendly sample outputs
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

Windows quick start:

```powershell
git clone https://github.com/HyunWoo9930/job-application-agent-suite.git
cd job-application-agent-suite
py scripts\use_agent.py --list
py scripts\use_agent.py --agent agent-00 --input templates\agent-00-input.sample.json
```

</details>

## Quick Start

```bash
git clone https://github.com/HyunWoo9930/job-application-agent-suite.git
cd job-application-agent-suite
python3 scripts/use_agent.py --list
```

If you are new to this repository, the walkthrough below is the fastest way to understand how it works.

<details open>
<summary>Beginner walkthrough</summary>

### 1. What do I need before I start?

You only need three things:

- a target company and role
- one application question with a character limit
- a few lines of experience notes

Example:

- company: `Naver`
- role: `Backend Engineer`
- question: `Why do you want to join us, and how will you contribute after joining?`
- limit: `800`
- notes: `payment API bottleneck fix`, `35% latency reduction`, `incident-response automation`

### 2. First command to run

This shows the available agents.

```bash
python3 scripts/use_agent.py --list
```

### 3. Print one prompt with sample input

```bash
python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json
```

The long text printed here is the actual prompt you would feed into your LLM workflow.

### 4. Create a run directory for one question

```bash
mkdir -p ~/job_runs/naver_backend/Q1
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

### 5. Check what was created

```bash
ls -la ~/job_runs/naver_backend/Q1
```

You should see files such as:

- `state.json`: current pipeline state
- `04_draft.txt`: draft output
- `05_tone.txt`: tone-adjusted version
- `06_qa.json`: QA results
- `07_package.md`: final packaged output

### 6. If you already have older essays, scan them for reusable experiences

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --write-output /tmp/corpus_candidates.json
```

This prints reusable experience candidates as JSON.

### 7. If you already have a draft, validate it immediately

```bash
python3 scripts/char_window_check.py --file /tmp/draft.txt --char-limit 800
python3 scripts/ai_style_checker.py --file /tmp/draft.txt
```

### 8. What is the normal usage pattern?

The simplest workflow is:

1. print a prompt with `use_agent.py`
2. send that prompt to Codex, Claude, OpenAI, or another model
3. save the result into `state.json` or the draft files
4. run the length and AI-style checks at the end

</details>

<details>
<summary>Recommended files for first-time users</summary>

1. `templates/agent-00-input.sample.json`
2. `templates/pipeline-state.sample.json`
3. `examples/naver-backend-q1/04_draft.sample.txt`
4. `examples/naver-backend-q1/06_ai_style_report.sample.txt`
5. `examples/naver-backend-q1/07_package.sample.md`

</details>

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

Important:

- A simple `git clone` is enough to run the local scripts and inspect the examples.
- But if you want Codex to recognize and invoke `job-application-agent-suite` as an installed skill, it should live at `~/.codex/skills/job-application-agent-suite`.

After installation, you can ask Codex to use the skill directly.

```text
Use job-application-agent-suite and start with company-role analysis for a Naver backend application.
```

```text
Use this skill and only do the company analysis step first.
```

```text
Load job-application-agent-suite and run only agent-06 for draft QA.
```

The important part is mentioning the skill name explicitly so Codex knows to use the prompts and workflow from this repository.

<details>
<summary>Example requests for Codex</summary>

- `Use job-application-agent-suite to analyze Samsung DS roles`
- `Use job-application-agent-suite to draft one application answer`
- `Load this skill and only run QA on my existing draft`
- `Use this skill starting from experience mining`

</details>

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
<summary>What output should I expect?</summary>

- `use_agent.py`: prints prompt text in the terminal
- `orchestrate_pipeline.py --init-run-dir`: creates a run directory and starter files
- `scan_experience_corpus.py`: prints JSON candidates and can save them to a file
- `char_window_check.py`: prints `PASS` or `FAIL`
- `ai_style_checker.py`: prints repeated patterns, flagged lines, and a `LOW/MEDIUM/HIGH` risk level

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
<summary>Example outputs</summary>

- `examples/naver-backend-q1/04_draft.sample.txt`
- `examples/naver-backend-q1/06_ai_style_report.sample.txt`
- `examples/naver-backend-q1/06_char_window_report.sample.txt`
- `examples/naver-backend-q1/07_package.sample.md`

</details>

<details>
<summary>Workflow notes</summary>

- default approval mode: `manual_per_step`
- `agent-02a.ready_for_agent_02 = false` blocks the next stage
- `external_feedback_required = true` and empty `external_feedback_notes` blocks `agent-07`
- final length target: `char_limit - 20 <= length <= char_limit`
- company analysis prioritizes main business, core competitiveness, industry position, recent focus and investment direction, competitor comparison, culture/welfare, and latest official-source verification.
- `agent-06` now reviews both detector-sensitive signals and weak human-texture points, with line-level reasoning and rewrite guidance rather than binary detection.

</details>

## FAQ

### Does this repository call an LLM API directly?

No. The repository centers on prompt files and helper scripts.

### Can I use it with just `git clone`?

Yes. A plain `git clone` is enough to run the scripts, inspect the templates, and open the examples. If you want Codex to invoke it like an installed skill, place it under `~/.codex/skills/job-application-agent-suite`.

Example:

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/job-application-agent-suite ~/.codex/skills/
```

If you already have the folder locally:

```bash
cp -R /absolute/path/job-application-agent-suite ~/.codex/skills/
```

### How do I call this skill from Codex?

Mention the skill name directly. For example: `Use job-application-agent-suite and start with company analysis` or `Use job-application-agent-suite and only review my draft`.

### Does this only work with Codex?

No. The `references/`, `scripts/`, and `templates/` in this repository can also be used in other environments such as Claude or Gemini CLI.

The difference is mostly in how you invoke it:

- The installed-skill workflow through `SKILL.md` is most directly tailored to Codex.
- In Claude or Gemini CLI, the practical pattern is usually to print a prompt with `scripts/use_agent.py` and then paste or adapt that prompt into the other tool.

### Can I submit the output as-is?

Not recommended. The outputs are better treated as drafts, analysis notes, or revision candidates rather than final submission-ready essays. You should review them yourself and ideally get extra feedback from another AI or a human reviewer.

### Are outputs saved automatically?

Yes. Unless you explicitly ask not to save files, the workflow is set up to save analysis artifacts under `~/job_runs/...` by default.

### What language are saved artifacts written in?

Korean by default. Since this workflow is designed for Korean job applications, saved analysis artifacts are normally written in Korean unless you explicitly ask for English output.

### Does it work on Windows?

It is not fully unsupported. The scripts are mostly portable, but the documented defaults assume macOS/Linux paths. In practice, Windows usage means replacing `python3` with `py` and adapting file paths.

### Why is `.pdf` not directly supported?

The current corpus scanner reads `.docx` by parsing document XML and does not include a PDF parser.

### What does `agent-06` actually do?

`agent-06` is not just a binary AI detector. It reviews detector-sensitive phrasing, overly polished structure, and weak human texture together, then gives line-level rewrite guidance.

### What if my draft is too short or too long?

The default target is `char_limit - 20 <= chars <= char_limit`. If it is too short, add more context, reasoning, or specific evidence. If it is too long, trim weak transitions and safe, generic closing phrases first.

### How much should I trust the company analysis?

The company-analysis flow prioritizes official homepage, careers, newsroom, and IR sources, but interpretation and recency issues are still possible. It is safer to verify important details yourself before using them in a final submission.

### Can I use this together with another AI tool?

Yes, and that is often a good idea. A practical workflow is to generate analysis or drafts here, then get a second round of feedback from another AI or a human reviewer before submitting.

## Contributing

Issues, suggestions, and PRs are all welcome if this repository helped you or if you have ideas to make the workflow more practical.

If you found this project useful, consider giving it a GitHub `Star`.

## License

MIT License. See [LICENSE](./LICENSE).
