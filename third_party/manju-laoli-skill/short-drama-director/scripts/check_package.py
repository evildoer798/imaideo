from pathlib import Path
raise SystemExit(0 if (Path(__file__).parents[1]/"SKILL.md").exists() else 1)
