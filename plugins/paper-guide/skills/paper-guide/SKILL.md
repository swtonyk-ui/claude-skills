---
name: paper-guide
description: 논문 PDF(1편 이상)를 받아 원문 순서를 따라가는 "문단별 한글 해설본" PDF를 만든다. 쉬운 한국어, 해부학·의학 용어는 영어 유지, 논문 figure 포함, 선택적으로 환자 케이스와 연결. Use when the user uploads paper PDFs and asks for "논문 해설본", "논문 쉽게 풀어서 PDF로", "paper commentary", or a Korean study guide of a paper.
---

# paper-guide — 논문 문단별 해설본 (portable: claude.ai / Claude Code)

Input: uploaded paper PDF(s) + optional case text (판독문/소견).
Output: `논문해설_<첫저자연도…>.pdf` (fallback: `.html` if no PDF renderer works).

`SK` = this skill's folder (where this SKILL.md lives). `W` = a fresh work dir (e.g. `/tmp/paper-guide`, or the scratchpad).
Uploaded files on claude.ai are usually under `/mnt/user-data/uploads/`; write deliverables to `/mnt/user-data/outputs/` when that folder exists, otherwise next to the input.

## Hard rules

- **해설이지 번역이 아니다.** Never translate sentence by sentence and never quote long passages. Explain what each part *means* in your own plain Korean, condensed. Figure captions: rewrite as "무엇을 보면 되는지" in 1–3 short lines, never translate the legend.
- Korean prose, **anatomy/medical terms stay in English**.
- Follow the paper's **own section order and headings**: `<h2>한글 소제목 <span class="en">Original Heading</span></h2>`.
- Short sentences, bullets over paragraphs, one idea per bullet.
- Each `h2` section: explanation → optional `<div class="easy">` one-line takeaway where the idea is hard.
- If a case was given: `<div class="case">` only where a section directly explains a case finding, plus a final "논문을 우리 케이스에 겹쳐 보기" section (finding → space/structure → which paper says so). No case → no case boxes.
- Every claim must come from the paper; mark added general knowledge as "일반 원칙".
- Use the paper's own figures (`Fig N`). Skip near-duplicates. Footer note: 그림 © 원 출판사, 개인 학습용.

## 의학 논문 모드 (Medical papers)

- **유형 판별 먼저**, 표지 논문 표에 표시: Original research / Diagnostic accuracy / Review·Pictorial essay / Case report / Systematic review·Meta-analysis / Guideline.
- 각 논문 paper-head 바로 아래 `<div class="key">` **핵심 3줄**: 무엇을 말하는가 / 근거는 무엇인가 / 판독·진료에서 무엇이 바뀌나.
- **약어표**: 논문 약어를 첫 등장 순서로 `<table>` (약어 | full term | 한 줄 뜻).
- 유형별 추가:
  - Original / Diagnostic accuracy: **연구 요약 표** (Design · 대상 N/기관/기간 · index test vs reference standard · primary outcome · 핵심 결과). 통계 용어(sensitivity, AUC, OR/HR, I² 등)는 처음 나올 때 한 줄 풀이(일반 원칙). `<div class="appraise">` **비판적 읽기**: 논문이 밝힌 limitation + 설계상 bias(retrospective, single center, selection/spectrum/verification bias) — 논문 근거와 일반 원칙을 구분 표기.
  - Review / Pictorial essay: **소견 표** (질환·구조 | 영상 소견 | 의미·감별). 이름 붙은 sign은 영어 그대로 + 무엇을 보면 되는지. `<div class="pearl">` 판독 팁·pitfall·mimic (논문에 나온 것만).
  - Case report: 증례 흐름 표 (증상 → 영상 → 진단 → 치료) + 왜 보고됐는지(새로운 점).
  - Meta-analysis: 포함 연구 수, pooled estimate + 95% CI, heterogeneity, 근거 수준.
  - Guideline: 권고 + 권고 등급 표, 이전 버전 대비 바뀐 점.
- 영상의학: modality·protocol(phase, window, sequence)이 나오면 정리. 판독문 영어 표현 예시 1–2줄은 "예시" 표시.
- **수치는 원문 그대로** (단위, 95% CI, P 값 포함). 반올림·재계산·추정 금지. 용량, cutoff, 분류 기준(grade/stage)도 원문과 정확히 일치. 텍스트 추출이 깨져 확신이 없으면 "(원문 확인)" 표시.
- 논문 결론 범위를 넘어 일반화하거나 진료 지시처럼 쓰지 않는다.
- 각 논문 마지막에 `<div class="takehome">` **Take-home message** 3–5개 bullet (판독·진료에서 기억할 것, 논문 근거만). 퀴즈·문제 만들지 않음.

## Steps

0. **Setup** (once per session):
   `python3 -c "import pymupdf, PIL" 2>/dev/null || pip install -q pymupdf pillow`
1. **Extract**: `python3 $SK/tool.py extract $W <pdf> [<pdf> ...]`
   → `$W/A.txt`, `$W/B.txt`… (page-marked text per paper), `$W/img/*`, `$W/sheet_*.jpg` (labelled contact sheets).
2. **Read every `X.txt` in full.** Note headings in order, figure/table captions.
3. **View every `sheet_*.jpg`** and map image files → figure numbers by page + caption order. Crop multi-content images with PIL into `$W/img/`.
4. **Write** `$W/guide.html` from `$SK/template.html`: replace `{{TITLE}}`, put content at `{{BODY}}`.
   Cover (`<h1>`, one line "원문 번역이 아니라 내용 설명", table of papers) → one `<section class="paper">` per paper → optional case section. Image paths relative: `img/<file>`.
5. **Render to PDF** — try in order, stop at the first that works:
   - Chrome/Chromium: `for b in chromium chromium-browser google-chrome "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do command -v "$b" >/dev/null 2>&1 || [ -x "$b" ] && break; done` then
     `"$b" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=<out.pdf> file://$W/guide.html`
   - WeasyPrint: `pip install -q weasyprint` then `python3 -c "import weasyprint; weasyprint.HTML('$W/guide.html').write_pdf('<out.pdf>')"`
     (needs a Korean font; if text renders as boxes, `fc-list :lang=ko` → set `font-family` in the CSS to an installed Korean font, or install `fonts-noto-cjk`.)
   - Neither works → `python3 $SK/tool.py bundle $W/guide.html <out.html>` (images inlined, one file) and tell the user: 브라우저에서 열고 인쇄 → PDF로 저장.
6. **Check** (PDF only): `python3 $SK/tool.py preview <out.pdf> $W/preview.png`, view it. Fix oversized figures (`figure.s` ≈ 210px, `figure.m` ≈ 290px), near-empty pages, broken SVG (`<b>` is invalid inside `<svg><text>`; use `<tspan font-weight="700">`). Re-render until clean.
7. Deliver the file and reply with page count + section list (one line each). Say what was skipped.

## Optional diagrams

Inline SVG only when a concept is spatial and no paper figure shows it. Short labels, 2–3 colors.
