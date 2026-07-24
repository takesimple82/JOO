# JOO Command Center Installation Guide

## 1. Clone Repository

```bash
git clone https://github.com/takesimple82/JOO.git
cd JOO
```

---

## 2. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 3. Install GitHub CLI

```bash
brew install gh
```

Authenticate GitHub:

```bash
gh auth login
```

---

## 4. Install GPT CLI

Install the GPT CLI according to your environment and ensure it is available from the terminal.

Example:

```bash
gpt --version
```

---

## 5. Verify Environment

```bash
git --version
gh --version
bash --version
gpt --version
```

---

## 6. Run JOO

```bash
./run.sh
```

If everything is configured correctly, JOO will generate:

```
Research/
Knowledge/
Reports/
```
