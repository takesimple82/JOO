# JOO Command Center

> AI-powered Chief Investment Officer (CIO) System for Evidence-Based Capital Allocation

JOO Command Center는 AI를 활용하여
매일 시장을 분석하고,
투자 아이디어를 평가하며,
Expected Value(EV)를 기반으로
최적의 자본 배분 결정을 지원하는 개인 투자 운영 시스템입니다.

JOO는 단순한 뉴스 요약기가 아니라,
Research → Knowledge → CIO Dashboard의 3단계 의사결정 파이프라인을 통해
투자 결정을 구조화합니다.
---
## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/takesimple82/JOO.git
cd JOO
```

### 2. Run JOO

```bash
./run.sh
```

JOO는 아래 순서로 자동 실행됩니다.

```
Research
    ↓
Knowledge
    ↓
CIO Dashboard
```

# Philosophy

JOO는 애널리스트가 아닙니다.

JOO는 CIO(Chief Investment Officer)입니다.

핵심 원칙

- Capital is the Product.
- Expected Value > Prediction.
- Capital Velocity > Holding Period.
- Evidence > Opinion.
- Process > Emotion.

---

# Project Structure

```
JOO/

├── Portfolio/
│   ├── portfolio.yaml
│   └── database.md
│
├── PromptLibrary/
│   ├── P001_Research.md
│   ├── P002_Knowledge.md
│   ├── P003_CIO.md
│   └── P003_Daily_CIO.md
│
├── Scripts/
│   ├── research_gpt.sh
│   ├── knowledge_gpt.sh
│   ├── cio_gpt.sh
│   ├── common.sh
│   └── run.sh
│
├── Research/
├── Knowledge/
├── Reports/
└── run.sh
```

---

# Workflow

run.sh

↓

Research

↓

Knowledge

↓

CIO Dashboard

↓

Daily Report

---

# Output

Research/

AI가 수집한 시장 데이터

Knowledge/

Research를 기반으로 추론한 결과

Reports/

최종 CIO Dashboard

---

# Run

프로젝트 루트에서 실행

```bash
./run.sh
```

---

# Git

최신 변경사항 저장

```bash
git add .
git commit -m "Update"
git push
```

---

# Requirements

- macOS
- Git
- GitHub CLI
- Bash
- GPT CLI

---

# Version

Current Version

v1.0
