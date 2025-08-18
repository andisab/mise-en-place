# Context Window Prime

Always call necessary tool calls in parallel

# Basic Analysis
RUN:
- claude mcp list
- git status --porcelain
- git branch --show-current
- git log --oneline -10
- git ls-files

# Project Detection & Environment
RUN:
- ls -la pyproject.toml package.json go.mod Cargo.toml requirements.txt poetry.lock yarn.lock package-lock.json Pipfile Gemfile composer.json Makefile 2>/dev/null || echo "No project files found"
- ls -la .env.example Dockerfile docker-compose.yml .eslintrc\* ruff.toml .flake8 .pre-commit-config.yaml 2>/dev/null || echo "No environment/tooling files found"
- ls -la .github/workflows/ .gitlab-ci.yml tests/ test/ **tests**/ 2>/dev/null || echo "No CI/testing found"

# Documentation Discovery
RUN:
- find . -maxdepth 3 -name "_.md" -not -path "_/node*modules/*" -not -path "_/venv/_" -not -path "\_/.git/\*" 2>/dev/null | head -15

# Core Loading
READ:
- CLAUDE.md
- README.md
- Any .claude/specs/\*.md files (if they exist)

# Extended Loading
READ (if they exist and are reasonable size):
- Main project config files (pyproject.toml, package.json, go.mod, Cargo.toml, etc.)
- All discovered .md files (excluding already loaded README.md, CLAUDE.md)
- Key environment files (.env.example, docker-compose.yml, Dockerfile)
- Build files (Makefile - first 100 lines if large)

# Analysis

⭐ **Loading Guidelines:**
- Always follow referenced files in CLAUDE.md
- Skip large files (>100KB) or read first 200 lines only
- Prioritize: Core docs → Project configs → Other .md files → Environment files

⭐ After loading all context:
- Extract available commands from project configs (npm scripts, etc.)
- Note development setup (Docker, environment files, testing tools)
- Provide brief summary of project structure and key findings

# Memory
- 🔥 When using memory while in a repository, always use the EXACT name of the repository as the entity name, without adding any additional keywords or terms. This will ensure we are not creating duplicate records and allow us to find existing records more easily.
- Search for a repository record by exact repository name.
- If a record already exists, either update the entity with new information or add an observation , as seems appropriate. If multiple entities about the repository are found, consolidate them.
- If no entities are found, add a new one.