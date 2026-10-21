# Скиллы агентов

Каталог `.agents/skills/` (скиллы [mattpocock/skills](https://github.com/mattpocock/skills) для OpenCode) **не хранится в git** — на каждой машине он свой. В репозитории лежит только `skills-lock.json`: манифест с источником и хешами, по которому скиллы восстанавливаются одной командой.

```powershell
# окружение: зависимости uv + локальные скиллы из skills-lock.json
./scripts/bootstrap.ps1

# обновить скиллы до последних версий (заодно перепишет skills-lock.json)
./scripts/bootstrap.ps1 -Update

# точечно, без скрипта
npx -y skills@latest update -p -y
npx -y skills@latest add mattpocock/skills -a opencode
```

Требуется Node.js (`npx`). Если его нет — окружение всё равно поднимается, скиллы просто не ставятся.
