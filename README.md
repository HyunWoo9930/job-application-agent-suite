# Job Application Agent Suite

한국어 자소서/커버레터 작성을 단계별로 분리해서 처리하는 멀티 에이전트 세트입니다.  
회사/직무 분석부터 경험 발굴, 문항 매칭, 초안 작성, 톤 보정, AI스러운 문장 점검, 최종 패키징까지 한 흐름으로 재현할 수 있습니다.

이 저장소는 두 가지 방식으로 사용할 수 있습니다.

1. Codex skill 폴더에 넣어서 에이전트 프롬프트 묶음으로 사용
2. 일반 GitHub 저장소처럼 내려받아 스크립트와 템플릿만 독립적으로 사용

---

## 1. What This Repository Does

이 프로젝트는 자소서 작성 과정을 아래 단계로 쪼개서 다룹니다.

1. `agent-00` 입력 검증
2. `agent-01a` 산업 분석
3. `agent-01b` 회사 분석
4. `agent-01c` 직무 분석
5. `agent-01` 분석 종합
6. `agent-02a` 기존 자소서 코퍼스 스캔 및 재사용 경험 추천
7. `agent-02` 경험 카드화
8. `agent-03` 문항-경험 매칭
9. `agent-03b` 꼬리질문/정제
10. `agent-03c` 수치 근거 검증
11. `agent-04` 초안 작성
12. `agent-05` 톤 보정
13. `agent-06` AI톤/QA 점검
14. `agent-07` 최종 제출본 패키징

핵심 목표는 아래 4가지입니다.

- 한 번에 다 쓰지 않고 단계별로 품질을 통제할 수 있게 하기
- 기존 자소서/경험 문서를 재활용할 수 있게 하기
- 과장된 표현이나 근거 없는 수치를 줄이기
- 최종 글자 수와 문항 적합도를 기계적으로 다시 검사하기

---

## 2. Who This Is For

이 저장소는 특히 아래 사용자에게 잘 맞습니다.

- 한국 기업 자소서를 반복적으로 작성해야 하는 취업 준비생
- 여러 회사/직무 지원서를 구조적으로 관리하고 싶은 사람
- 기존 자소서 파일에서 재사용 가능한 경험을 자동으로 추리고 싶은 사람
- 초안 작성 후 AI 같은 문체나 선언형 문장을 줄이고 싶은 사람
- Codex/Claude 같은 도구에 넣어 단계별 에이전트 운영을 해보고 싶은 사람

---

## 3. Repository Structure

```text
job-application-agent-suite/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── agent-00-intake-validator.md
│   ├── agent-01-company-role-analyst.md
│   ├── agent-01a-industry-analyst.md
│   ├── agent-01b-company-analyst.md
│   ├── agent-01c-role-analyst.md
│   ├── agent-02a-corpus-experience-recommender.md
│   ├── agent-02-experience-miner.md
│   ├── agent-03-question-experience-matcher.md
│   ├── agent-03b-experience-refiner.md
│   ├── agent-03c-metric-evidence-tracker.md
│   ├── agent-04-drafting-assistant.md
│   ├── agent-05-tone-customizer.md
│   ├── agent-06-ai-style-and-qa-reviewer.md
│   └── agent-07-final-packager.md
├── scripts/
│   ├── use_agent.py
│   ├── scan_experience_corpus.py
│   ├── orchestrate_pipeline.py
│   ├── persist_analysis_cache.py
│   ├── char_window_check.py
│   └── ai_style_checker.py
└── templates/
    ├── agent-00-input.sample.json
    ├── agent-02a-input.sample.json
    ├── agent-03b-input.sample.json
    ├── agent-03c-input.sample.json
    ├── agent-06-input-from-existing-draft.sample.json
    ├── agent-07-input.sample.json
    └── pipeline-state.sample.json
```

각 폴더 역할은 아래와 같습니다.

- `references/`: 실제 에이전트 프롬프트 본문
- `scripts/`: 프롬프트 출력, 코퍼스 스캔, 파이프라인 상태 관리, QA용 유틸
- `templates/`: 바로 실행해볼 수 있는 샘플 입력 JSON
- `agents/openai.yaml`: UI/에이전트 메타 정보
- `SKILL.md`: Codex skill로 사용할 때의 운영 규칙

---

## 4. Requirements

최소 요구사항:

- macOS 또는 Linux
- `python3` 3.9 이상
- UTF-8 한글 파일을 다룰 수 있는 기본 터미널 환경

권장 도구:

- `rg` (`ripgrep`)
- Git

지원되는 코퍼스 스캔 확장자:

- `.txt`
- `.md`
- `.markdown`
- `.rst`
- `.docx`

현재 기본 스캐너는 아래 형식은 직접 읽지 않습니다.

- `.pdf`
- `.hwp`

macOS에서 준비 예시:

```bash
brew install python ripgrep git
```

버전 확인:

```bash
python3 --version
rg --version
git --version
```

---

## 5. Quick Start

가장 빠르게 동작 확인만 해보고 싶다면 아래 순서대로 하면 됩니다.

### 5-1. 저장소 받기

```bash
git clone https://github.com/YOUR_NAME/job-application-agent-suite.git
cd job-application-agent-suite
```

아직 GitHub에 올리기 전이라면 로컬 폴더를 그대로 써도 됩니다.

```bash
cd /path/to/job-application-agent-suite
```

### 5-2. 에이전트 목록 확인

```bash
python3 scripts/use_agent.py --list
```

### 5-3. 특정 에이전트 프롬프트 출력

```bash
python3 scripts/use_agent.py --agent agent-01
python3 scripts/use_agent.py --agent agent-04
python3 scripts/use_agent.py --agent feedback
```

`feedback`는 `agent-06`의 alias입니다.

### 5-4. 샘플 입력을 넣어서 프롬프트 확인

```bash
python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json
python3 scripts/use_agent.py --agent agent-06 --input templates/agent-06-input-from-existing-draft.sample.json
```

이 명령은 LLM을 직접 호출하지는 않고, 해당 단계에서 사용할 프롬프트 텍스트를 출력합니다.  
즉, "이 단계에서 모델에게 어떤 지시를 줄지"를 바로 확인할 수 있습니다.

---

## 6. Install As a Codex Skill

Codex skill로 붙여서 쓰려면 보통 아래 구조를 맞추면 됩니다.

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/job-application-agent-suite ~/.codex/skills/
```

최종 경로:

```text
~/.codex/skills/job-application-agent-suite
```

설치 후 확인:

```bash
ls -la ~/.codex/skills/job-application-agent-suite
python3 ~/.codex/skills/job-application-agent-suite/scripts/use_agent.py --list
```

Codex에서 이 스킬을 사용할 때 핵심 파일은 아래 2개입니다.

- `SKILL.md`
- `references/*.md`

즉, 스킬 운영 규칙은 `SKILL.md`에 있고, 실제 단계별 에이전트 프롬프트는 `references/`에 들어 있습니다.

---

## 7. How the Pipeline Works

전체 흐름은 아래처럼 이해하면 가장 쉽습니다.

### Step A. 입력 정리

먼저 아래 정보를 준비합니다.

- 회사명
- 직무명
- 공고 링크 또는 공고 본문
- 자소서 문항과 글자 수 제한
- 지원자 경험 메모
- 금지 표현 또는 금지 주장

### Step B. 분석 베이스라인 생성

`agent-01a`, `agent-01b`, `agent-01c`, `agent-01`을 거치면서:

- 산업 맥락
- 회사 방향성
- 직무 핵심 역량
- 지원동기/기여 포인트

를 구조화합니다.

### Step C. 경험 찾기

`agent-02a`와 `agent-02`에서:

- 기존 자소서 폴더를 스캔하고
- 재사용 가능한 경험 후보를 추리고
- 각 경험을 카드 단위로 정리합니다

### Step D. 문항 연결

`agent-03`, `agent-03b`, `agent-03c`에서:

- 어떤 문항에 어떤 경험이 맞는지 매칭하고
- 증거가 약한 부분은 꼬리질문으로 보강하고
- 수치/성과가 실제 근거를 갖는지 검증합니다

### Step E. 문장화 및 QA

`agent-04`부터 `agent-07`까지:

- 초안 작성
- 톤 보정
- AI스러운 표현/중복 표현/문항 이탈 체크
- 최종 제출용 패키징

을 수행합니다.

---

## 8. Script Guide

### `scripts/use_agent.py`

가장 기본적인 진입점입니다.  
특정 에이전트 프롬프트를 출력하거나, 샘플 JSON 값을 `{{var}}` 자리에 치환해서 보여줍니다.

예시:

```bash
python3 scripts/use_agent.py --list
python3 scripts/use_agent.py --agent agent-01
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
```

이럴 때 사용합니다.

- "회사 분석 프롬프트만 보고 싶다"
- "초안 작성 프롬프트만 복사해서 다른 LLM에 넣고 싶다"
- "샘플 JSON이 실제로 어떻게 치환되는지 보고 싶다"

### `scripts/scan_experience_corpus.py`

기존 자소서/노트 폴더를 훑어서 재사용 가치가 높은 경험 문장을 뽑아냅니다.

기본 경로:

```text
~/Desktop/취업/자기소개서
```

예시:

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --write-output /tmp/corpus_candidates.json
```

출력에는 아래 정보가 포함됩니다.

- `scanned_experience_list`: 무엇을 스캔했는지
- `suggested_for_use_now`: 지금 우선 쓸 후보
- `candidates`: 상세 후보 목록

### `scripts/orchestrate_pipeline.py`

문항별 실행 폴더와 상태 파일을 관리합니다.  
실행 순서, 승인 상태, 다음 단계 입력을 기계적으로 정리할 때 사용합니다.

예시:

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

다음 입력 생성:

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --write-next-input /tmp/next_input.json
```

### `scripts/persist_analysis_cache.py`

회사/직무 분석 결과를 캐시로 저장하거나 다시 불러옵니다.  
같은 회사/직무 조합을 여러 문항에서 재사용할 때 유용합니다.

기본 캐시 경로:

```text
~/Desktop/회사 직무 분석
```

예시:

```bash
python3 scripts/persist_analysis_cache.py \
  --input templates/pipeline-state.sample.json \
  --mode save
```

### `scripts/char_window_check.py`

자소서가 글자 수 조건 `N-20 .. N`을 만족하는지 검사합니다.

예시:

```bash
python3 scripts/char_window_check.py \
  --file /tmp/draft.txt \
  --char-limit 800
```

공백 제외 모드:

```bash
python3 scripts/char_window_check.py \
  --file /tmp/draft.txt \
  --char-limit 800 \
  --count-mode no-space
```

### `scripts/ai_style_checker.py`

과하게 AI 같은 자소서 문체를 휴리스틱으로 잡아냅니다.

검사 포인트:

- 추상 표현 반복
- 선언형 어미 반복
- 반복되는 문장 시작
- 반복되는 3-gram
- 과도하게 긴 문장

예시:

```bash
python3 scripts/ai_style_checker.py --file /tmp/draft.txt
```

---

## 9. Example: First End-to-End Run

처음 써보는 사람이 가장 따라가기 쉬운 예시입니다.

### 9-1. 실행 폴더 만들기

```bash
mkdir -p ~/job_runs/naver_backend/Q1
```

### 9-2. 샘플 상태 파일로 초기화

```bash
python3 scripts/orchestrate_pipeline.py \
  --run-dir ~/job_runs/naver_backend/Q1 \
  --init-run-dir \
  --input templates/pipeline-state.sample.json
```

### 9-3. 생성된 폴더 확인

정상이라면 아래 파일들이 생깁니다.

```text
~/job_runs/naver_backend/Q1/
├── state.json
├── 02a_scan_report.md
├── 04_draft.txt
├── 05_tone.txt
├── 06_qa.json
├── external_feedback.md
└── 07_package.md
```

### 9-4. 코퍼스 스캔

```bash
python3 scripts/scan_experience_corpus.py \
  --path ~/Desktop/취업/자기소개서 \
  --state-input ~/job_runs/naver_backend/Q1/state.json \
  --write-state ~/job_runs/naver_backend/Q1/state.json
```

### 9-5. 필요한 에이전트 프롬프트 출력

```bash
python3 scripts/use_agent.py --agent agent-01a
python3 scripts/use_agent.py --agent agent-01b
python3 scripts/use_agent.py --agent agent-01c
python3 scripts/use_agent.py --agent agent-01
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
```

이 단계에서 보통은 출력된 프롬프트를 LLM에 넣고, 그 결과를 `state.json` 또는 각 단계 산출물에 반영합니다.

### 9-6. 초안 파일 검사

초안이 생겼다면 길이와 문체를 바로 점검합니다.

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

## 10. Sample Inputs Included

바로 써볼 수 있도록 샘플 JSON을 같이 넣어두었습니다.

### `templates/agent-00-input.sample.json`

전체 입력 검증용 샘플입니다.

- 회사명
- 직무명
- 공고 링크
- 문항 목록
- 지원자 프로필
- 경험 메모
- 금지 조건

### `templates/agent-02a-input.sample.json`

기존 자소서 코퍼스 추천 단계 샘플입니다.

- 문항
- 직무 키워드 맵
- 지원자 프로필
- 새 경험 메모
- 코퍼스 경로
- 기존 코퍼스 후보 예시

### `templates/agent-03b-input.sample.json`

매칭이 약할 때 꼬리질문을 유도하는 정제 단계 샘플입니다.

### `templates/agent-03c-input.sample.json`

수치와 증거가 실제로 연결되는지 확인하는 단계 샘플입니다.

### `templates/agent-06-input-from-existing-draft.sample.json`

이미 써둔 초안이 있을 때 QA만 따로 돌리는 샘플입니다.

### `templates/agent-07-input.sample.json`

최종 패키징 직전 입력 예시입니다.

### `templates/pipeline-state.sample.json`

문항별 런 디렉터리 초기화에 사용하는 통합 상태 샘플입니다.

---

## 11. Operating Rules

이 저장소는 "한 번에 자동 생성"보다 "단계별 검증"을 중시합니다.

중요 운영 규칙:

- 기본 승인 모드는 `manual_per_step`
- 각 단계 결과를 보고 다음 단계로 넘어가는 방식 권장
- `agent-02a.ready_for_agent_02 = false`면 `agent-02`로 바로 진행하지 않기
- `external_feedback_required = true`인데 `external_feedback_notes`가 비어 있으면 `agent-07`로 진행하지 않기
- 자소서 최종 길이는 `char_limit - 20 <= length <= char_limit`를 맞추기

이 규칙 때문에, 실제 사용 시에는 "초안만 빨리 뽑는" 용도보다 "제출 전 품질 관리" 용도로 더 강합니다.

---

## 12. Smoke Test

GitHub에 올리기 전이나 다른 컴퓨터로 옮긴 뒤에는 아래 테스트를 꼭 해보세요.

### 12-1. 에이전트 목록 출력

```bash
python3 scripts/use_agent.py --list
```

### 12-2. 프롬프트 출력 테스트

```bash
python3 scripts/use_agent.py --agent agent-01 | head -n 20
python3 scripts/use_agent.py --agent agent-06 --input templates/agent-06-input-from-existing-draft.sample.json | head -n 40
```

### 12-3. 글자 수 검사 테스트

```bash
printf '테스트 문장입니다.\n' > /tmp/jaso_test.txt
python3 scripts/char_window_check.py --file /tmp/jaso_test.txt --char-limit 20
```

### 12-4. AI 스타일 검사 테스트

```bash
python3 scripts/ai_style_checker.py --file /tmp/jaso_test.txt
```

### 12-5. 코퍼스 스캔 테스트

테스트용 폴더를 만들어서 실행해보면 가장 안전합니다.

```bash
mkdir -p /tmp/jaso_corpus
printf '결제 API 병목을 분석해 응답시간을 35%% 단축했습니다.\n' > /tmp/jaso_corpus/sample.txt
python3 scripts/scan_experience_corpus.py --path /tmp/jaso_corpus --write-output /tmp/corpus.json
```

정상이라면 JSON이 출력되고, `suggested_for_use_now` 목록이 포함됩니다.

---

## 13. How to Publish This to GitHub

아직 GitHub 업로드를 안 했다면 아래 순서대로 하면 됩니다.

### 13-1. 공개용 폴더 정리

GitHub에는 보통 아래만 올리면 충분합니다.

- `README.md`
- `SKILL.md`
- `agents/`
- `references/`
- `scripts/`
- `templates/`

가능하면 아래는 빼는 것이 좋습니다.

- 개인 자소서 원본
- 회사 실명/민감 정보가 들어간 산출물
- 실제 지원서 초안
- 캐시 폴더
- 실행 중 생성된 `job_runs/`
- 개인 데스크톱 경로가 박힌 민감한 테스트 결과

### 13-2. `.gitignore` 추천

최소한 아래 항목은 무시하는 것을 권장합니다.

```gitignore
__pycache__/
*.pyc
.DS_Store
.env
.env.*
job_runs/
tmp/
*.log
```

### 13-3. Git 초기화

```bash
cd /path/to/job-application-agent-suite
git init
git add .
git commit -m "Initial commit: job application agent suite"
```

### 13-4. GitHub 저장소 생성 후 연결

GitHub에서 빈 저장소를 만든 뒤:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_NAME/job-application-agent-suite.git
git push -u origin main
```

### 13-5. 공개 전에 꼭 다시 확인할 것

- 개인 이름, 전화번호, 이메일이 샘플에 남아 있지 않은지
- 실제 기업 지원 데이터가 들어 있지 않은지
- 내부 회사 정보, 비공개 수치, 고객 데이터가 섞이지 않았는지
- README의 경로 예시가 너무 개인 환경에 묶여 있지 않은지

---

## 14. Recommended GitHub Repository Description

GitHub 저장소 설명은 아래처럼 짧게 적으면 무난합니다.

```text
Multi-agent toolkit for Korean job applications: company/role analysis, experience mining, essay drafting, tone adjustment, AI-style review, and final packaging.
```

토픽 예시:

```text
job-application, cover-letter, prompt-engineering, ai-agents, codex-skill, career-tools, korean
```

---

## 15. FAQ

### Q. 이 저장소는 LLM API를 직접 호출하나요?

아니요. 현재 저장소의 핵심은 "프롬프트와 파이프라인 보조 스크립트"입니다.  
즉, 어떤 프롬프트를 어떤 순서로 쓸지 정리하고, 코퍼스 스캔/상태 관리/QA를 도와주는 구조입니다.

### Q. Windows에서도 되나요?

파이썬 스크립트 자체는 대부분 동작할 가능성이 높지만, 현재 문서와 기본 경로는 macOS/Linux 기준으로 적혀 있습니다.  
처음 공개할 때는 macOS/Linux 지원이라고 명시하는 편이 안전합니다.

### Q. `.docx`는 읽히는데 `.pdf`는 왜 안 읽히나요?

현재 `scan_experience_corpus.py`는 `.docx` 내부 XML을 직접 읽는 방식이고, `.pdf` 파서는 포함하지 않았기 때문입니다.

### Q. 바로 완전 자동화할 수 있나요?

가능은 하지만 이 저장소는 기본적으로 `manual_per_step` 운영을 권장합니다.  
자소서는 작은 사실 오류나 톤 이탈이 치명적일 수 있어서, 단계별 확인이 더 안전합니다.

---

## 16. Suggested Next Improvements

이 저장소를 더 완성도 있게 공개하고 싶다면 다음 순서를 추천합니다.

1. `LICENSE` 추가
2. `.gitignore` 추가
3. 민감 정보 제거된 데모 입력/출력 추가
4. 실제 예시 실행 결과 스크린샷 또는 샘플 산출물 추가
5. GitHub Release 태그(`v0.1.0`) 생성

---

## 17. License

원하는 라이선스를 아직 정하지 않았다면, 공개 전 `LICENSE` 파일을 추가하세요.  
보통은 `MIT` 또는 `Apache-2.0`를 많이 사용합니다.

라이선스가 없으면 다른 사람이 이 저장소를 참고하더라도 법적으로 재사용 범위가 불명확해질 수 있습니다.
