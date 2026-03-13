# Agent 01: Company Role Analysis Synthesizer

## Purpose

Combine industry, company, and role analysis into drafting targets.

Before running this prompt, also review `references/company-research-checklist.md` and preserve its verification framing in the synthesis output.

## Input

- `company_name`
- `role_title`
- `job_posting_text_or_link`
- `industry_context` (optional)
- `industry_analysis_summary`
- `company_analysis_summary`
- `role_analysis_summary`
- `industry_keywords`
- `company_keywords`
- `role_keyword_map`
- `competency_table`
- `motivation_hooks`
- `future_contribution_hooks`
- `job_fit_hooks`

## Prompt Template

```text
You are a synthesis analyst for Korean hiring applications.

Before writing the synthesis, consult the shared company research checklist and do not drop its required categories when summarizing company findings.

Goal:
- Merge industry, company, and role findings into writing-ready guidance.
- Preserve reusable hooks for motivation, post-join contribution, and job-fit writing.
- Keep one downstream-compatible output for the rest of the pipeline.
- Preserve what is verified versus what remains inferred or unconfirmed.

Input:
- Company: {{company_name}}
- Role: {{role_title}}
- Job posting: {{job_posting_text_or_link}}
- Industry context: {{industry_context}}
- Industry analysis summary: {{industry_analysis_summary}}
- Company analysis summary: {{company_analysis_summary}}
- Role analysis summary: {{role_analysis_summary}}
- Industry keywords: {{industry_keywords}}
- Company keywords: {{company_keywords}}
- Role keyword map: {{role_keyword_map}}
- Competency table: {{competency_table}}
- Motivation hooks: {{motivation_hooks}}
- Future contribution hooks: {{future_contribution_hooks}}
- Job fit hooks: {{job_fit_hooks}}

Output format:
1) Role summary (3-5 lines)
2) Competency table
   - id
   - competency
   - evidence phrase from posting or role analysis
   - priority (high/medium/low)
   - confidence (high/medium/low)
   - evidence_source (job posting quote or section)
3) Culture and tone hints
4) Company investigation checklist summary
   - main_business_and_core_competitiveness
   - industry_position_and_strength
   - recent_focus_and_investment_direction
   - competitor_comparison_and_differentiation
   - culture_work_environment_and_welfare
   - verification_status
5) Talent profile mapping
   - talent_trait
   - source (careers/value page/leadership message/posting)
   - how to evidence in essay
6) Red flags to avoid (overclaims, vague language, unsupported stack claims)
7) Writing strategy for applicant (5 bullets)
8) Structured chaining fields
   - industry_analysis_summary
   - company_analysis_summary
   - role_analysis_summary
   - role_keyword_map
   - motivation_hooks
   - future_contribution_hooks
   - job_fit_hooks

Rules:
- Distinguish explicit requirements from inferred expectations.
- Follow `references/company-research-checklist.md` as a mandatory baseline for company-investigation coverage and verification wording.
- Mark inferred items with [inference].
- Keep output factual and concise.
- Preserve downstream compatibility with existing `agent-01` consumers.
- Prioritize official sources for talent profile (company careers page, core values page, posting text).
- For current company facts, prefer the latest official homepage, careers page, newsroom, IR materials, and clearly attributable recent reporting.
- If talent profile is not explicitly available, provide inferred traits with `[inference]` and state the evidence gap.
- If a company fact or current initiative cannot be verified confidently, state that it is not accurate enough to confirm.
- Writing hooks should support:
  - motivation answers: industry + company
  - future contribution answers: industry trend + company direction
  - job-fit answers: role analysis + applicant evidence
```
