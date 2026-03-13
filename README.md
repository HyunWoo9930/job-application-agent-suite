# Job Application Agent Suite

[English README](./README.en.md)

한국어 자소서와 커버레터 작성을 위한 멀티 에이전트 툴킷입니다. 회사/직무 분석, 경험 발굴, 문항 매칭, 초안 작성, 톤 보정, AI스러운 문장 점검, 최종 패키징까지 하나의 흐름으로 다룰 수 있습니다.

## Overview

이 저장소는 자소서 작성 과정을 아래 단계로 분리합니다.

1. `agent-00` 입력 검증
2. `agent-01a` 산업 분석
3. `agent-01b` 회사 분석
4. `agent-01c` 직무 분석
5. `agent-01` 분석 종합
6. `agent-02a` 코퍼스 스캔 및 재사용 경험 추천
7. `agent-02` 경험 카드화
8. `agent-03` 문항-경험 매칭
9. `agent-03b` 정제 및 꼬리질문
10. `agent-03c` 수치 근거 검증
11. `agent-04` 초안 작성
12. `agent-05` 톤 보정
13. `agent-06` AI 스타일 및 QA 점검
14. `agent-07` 최종 패키징

핵심 방향은 빠른 자동 생성보다 단계별 검증과 재사용 가능한 작성 파이프라인에 가깝습니다.

## Use Cases

- 한국 기업 자소서를 반복적으로 작성하는 흐름 정리
- 기존 자소서 파일에서 재사용 가능한 경험 추출
- 문항별로 맞는 경험을 구조적으로 매칭
- 초안 이후 반복 표현, 선언형 문장, 과장된 톤 점검
- Codex skill 또는 독립형 프롬프트/스크립트 세트로 사용

## Repository Structure

```text
job-application-agent-suite/
├── README.md
├── README.en.md
├── CONTRIBUTING.md
├── LICENSE
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
├── scripts/
└── templates/
```

- `references/`: 단계별 에이전트 프롬프트
- `scripts/`: 파이프라인 보조 스크립트
- `templates/`: 샘플 입력 JSON
- `SKILL.md`: Codex skill 운영 규칙

## Requirements

- macOS 또는 Linux
- Python 3.9+
- UTF-8 터미널 환경

지원되는 코퍼스 스캔 형식:

- `.txt`
- `.md`
- `.markdown`
- `.rst`
- `.docx`

현재 직접 지원하지 않는 형식:

- `.pdf`
- `.hwp`

예시:

```bash
brew install python ripgrep git
```

## Quick Start

```bash
git clone https://github.com/HyunWoo9930/job-application-agent-suite.git
cd job-application-agent-suite
python3 scripts/use_agent.py --list
```

특정 프롬프트 출력:

```bash
python3 scripts/use_agent.py --agent agent-01
python3 scripts/use_agent.py --agent agent-04
python3 scripts/use_agent.py --agent feedback
```

샘플 입력과 함께 출력:

```bash
python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json
python3 scripts/use_agent.py --agent agent-06 --input templates/agent-06-input-from-existing-draft.sample.json
```

이 스크립트는 LLM API를 호출하지 않고, 각 단계에서 사용할 프롬프트를 출력합니다.

## Codex Skill Installation

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/job-application-agent-suite ~/.codex/skills/
python3 ~/.codex/skills/job-application-agent-suite/scripts/use_agent.py --list
```

## Scripts

### `scripts/use_agent.py`

에이전트 프롬프트 출력과 `{{variable}}` 치환을 담당합니다.

```bash
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
```

### `scripts/scan_experience_corpus.py`

기존 자소서/노트 폴더를 스캔해 재사용 가능한 경험 후보를 추출합니다.

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --write-output /tmp/corpus_candidates.json
```

출력에는 `scanned_experience_list`, `suggested_for_use_now`, `candidates`가 포함됩니다.

### `scripts/orchestrate_pipeline.py`

문항별 실행 디렉터리와 `state.json`을 관리합니다.

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

### `scripts/persist_analysis_cache.py`

회사/직무 분석 결과를 캐시에 저장하거나 다시 불러옵니다.

```bash
python3 scripts/persist_analysis_cache.py \
  --input templates/pipeline-state.sample.json \
  --mode save
```

### `scripts/char_window_check.py`

최종 글이 `N-20 .. N` 범위에 들어오는지 검사합니다.

```bash
python3 scripts/char_window_check.py --file /tmp/draft.txt --char-limit 800
```

### `scripts/ai_style_checker.py`

반복 표현, 선언형 어미, 긴 문장, 반복 시작 구문 등을 바탕으로 AI스러운 패턴을 점검합니다.

```bash
python3 scripts/ai_style_checker.py --file /tmp/draft.txt
```

## End-to-End Example

```bash
mkdir -p ~/job_runs/naver_backend/Q1
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

코퍼스 스캔:

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --state-input ~/job_runs/naver_backend/Q1/state.json \
  --write-state ~/job_runs/naver_backend/Q1/state.json
```

초안 점검:

```bash
python3 scripts/char_window_check.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt \
  --char-limit 800
python3 scripts/ai_style_checker.py \
  --file ~/job_runs/naver_backend/Q1/04_draft.txt
```

## Included Templates

- `templates/agent-00-input.sample.json`
- `templates/agent-02a-input.sample.json`
- `templates/agent-03b-input.sample.json`
- `templates/agent-03c-input.sample.json`
- `templates/agent-06-input-from-existing-draft.sample.json`
- `templates/agent-07-input.sample.json`
- `templates/pipeline-state.sample.json`

## Workflow Notes

- 기본 승인 모드는 `manual_per_step`
- `agent-02a.ready_for_agent_02 = false`이면 다음 단계로 넘어가지 않음
- `external_feedback_required = true`이고 `external_feedback_notes`가 비어 있으면 `agent-07`을 진행하지 않음
- 최종 길이 기준은 `char_limit - 20 <= length <= char_limit`

## FAQ

### LLM API를 직접 호출하나요?

아니요. 이 저장소의 중심은 프롬프트 파일과 파이프라인 보조 스크립트입니다.

### Windows에서도 사용할 수 있나요?

파이썬 스크립트는 대부분 이식 가능하지만, 기본 경로와 문서는 macOS/Linux 기준으로 작성되어 있습니다.

### 왜 `.pdf`는 직접 읽지 않나요?

현재 코퍼스 스캐너는 `.docx` 내부 XML을 직접 읽는 방식이며 PDF 파서는 포함하지 않습니다.

## License

MIT License. See [LICENSE](./LICENSE).
