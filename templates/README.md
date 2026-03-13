# Templates

## Included files

- `agent-00-input.sample.json`: intake validator 입력 샘플
- `agent-02a-input.sample.json`: 기존 자소서 코퍼스 기반 경험 추천 단계 입력 샘플
- `agent-03b-input.sample.json`: 매칭 약점 정제/꼬리질문 단계 입력 샘플
- `agent-03c-input.sample.json`: 성과 수치 근거 검증 단계 입력 샘플
- `agent-06-input-from-existing-draft.sample.json`: 이미 작성한 초안 기준 QA 입력 샘플
- `agent-07-input.sample.json`: final packager 입력 샘플
- `pipeline-state.sample.json`: 오케스트레이터 상태 샘플

## Quick usage

```bash
python3 scripts/use_agent.py --agent agent-00 --input templates/agent-00-input.sample.json
python3 scripts/use_agent.py --agent agent-01a
python3 scripts/use_agent.py --agent agent-01b
python3 scripts/use_agent.py --agent agent-01c
python3 scripts/use_agent.py --agent agent-02a --input templates/agent-02a-input.sample.json
python3 scripts/use_agent.py --agent agent-03b --input templates/agent-03b-input.sample.json
python3 scripts/use_agent.py --agent agent-03c --input templates/agent-03c-input.sample.json
python3 scripts/use_agent.py --agent agent-06 --input templates/agent-06-input-from-existing-draft.sample.json
python3 scripts/use_agent.py --agent agent-07 --input templates/agent-07-input.sample.json
python3 scripts/orchestrate_pipeline.py --run-dir ~/job_runs/naver_backend/Q1 --init-run-dir --input templates/pipeline-state.sample.json
python3 scripts/orchestrate_pipeline.py --run-dir ~/job_runs/naver_backend/Q1 --write-next-input /tmp/next_input.json
python3 scripts/persist_analysis_cache.py --input templates/pipeline-state.sample.json --mode save
python3 scripts/scan_experience_corpus.py --path ~/Desktop/취업/자기소개서 --write-output /tmp/corpus_candidates.json
python3 scripts/scan_experience_corpus.py --path ~/Desktop/취업/자기소개서 --state-input ~/job_runs/naver_backend/Q1/state.json --write-state ~/job_runs/naver_backend/Q1/state.json
```

지원 포맷: `.docx`, `.txt`, `.md`, `.markdown`, `.rst` (`.pdf`, `.hwp` 미지원)

스캔 결과에는 `scanned_experience_list`(무엇을 스캔했는지)와 `suggested_for_use_now`(무엇을 쓸지)가 포함됩니다.

분석 캐시는 `industry/company/role/combined` 단위로 JSON과 Markdown이 각각 저장됩니다.

## Manual approval and hard gates

- 기본 승인 모드: `manual_per_step`
- 각 단계 결과를 사용자와 확인한 뒤 `state.json`의 `step_approvals.<agent-id>=true`로 승인 처리
- `agent-02a.ready_for_agent_02=false`면 `agent-02`로 진행 불가
- `external_feedback_required=true`일 때 `external_feedback_notes`가 비어 있으면 `agent-07` 진행 불가

## Per-question run directory

문항별로 아래 파일 구조를 고정 사용합니다.

- `state.json`
- `02a_scan_report.md`
- `04_draft.txt`
- `05_tone.txt`
- `06_qa.json`
- `external_feedback.md`
- `07_package.md`
