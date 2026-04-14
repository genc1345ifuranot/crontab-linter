# crontab-linter

> A CLI tool that validates and explains crontab expressions with timezone-aware scheduling checks.

---

## Installation

```bash
pip install crontab-linter
```

Or install from source:

```bash
git clone https://github.com/yourname/crontab-linter.git
cd crontab-linter
pip install .
```

---

## Usage

Validate and explain a crontab expression:

```bash
crontab-linter "*/5 * * * *"
```

**Output:**
```
✔ Valid expression
  Runs every 5 minutes
  Next 3 occurrences (UTC):
    - 2024-03-15 14:25:00
    - 2024-03-15 14:30:00
    - 2024-03-15 14:35:00
```

Check with a specific timezone:

```bash
crontab-linter "0 9 * * 1-5" --timezone "America/New_York"
```

Lint a full crontab file:

```bash
crontab-linter --file /etc/cron.d/myjobs
```

---

## Features

- Validates crontab syntax and catches common mistakes
- Explains expressions in plain English
- Previews upcoming scheduled run times
- Supports timezone-aware scheduling via `--timezone`
- Lints entire crontab files line by line

---

## License

This project is licensed under the [MIT License](LICENSE).