# Context Window Prime

Always call necessary tool calls in parallel

# Basic Analysis
RUN:
- claude mcp list
- If Memory MCP is available: You MUST search for and retrieve existing project context from memory before adding new records 
- git status --porcelain
- git branch --show-current
- git log --oneline -10
- git ls-files

# Project Detection & Environment
RUN:
- ls -la pyproject.toml package.json go.mod Cargo.toml requirements.txt poetry.lock yarn.lock package-lock.json Pipfile Gemfile composer.json Makefile 2>/dev/null || echo "No project files found"
- ls -la .env.example Dockerfile docker-compose.yml .eslintrc* ruff.toml .flake8 .pre-commit-config.yaml 2>/dev/null || echo "No environment/tooling files found"
- ls -la .github/workflows/ .gitlab-ci.yml tests/ test/ __tests__/ 2>/dev/null || echo "No CI/testing found"

# Documentation Discovery
RUN:
- find . -maxdepth 3 -name "*.md" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/.git/*" 2>/dev/null | head -15

# Core Loading
READ:
- CLAUDE.md
- README.md
- Any .claude/specs/*.md files (if they exist)

# Extended Loading  
READ (if they exist and are reasonable size):
- Main project config files (pyproject.toml, package.json, go.mod, Cargo.toml, etc.)
- All discovered .md files (excluding already loaded README.md, CLAUDE.md)
- Key environment files (.env.example, docker-compose.yml, Dockerfile)
- Build files (Makefile - first 100 lines if large)

# Memory & Analysis
After loading all context:
- UPDATE existing project entities in Memory MCP with new discoveries (do NOT create duplicates)
- If no existing project entities found, then create new entities for project type, main technologies, and key files
- If duplicates exist, remove them. 
- Extract available commands from project configs (npm scripts, etc.)
- Note development setup (Docker, environment files, testing tools)
- Provide brief summary of project structure and key findings

⭐ **Loading Guidelines:**
- Always follow referenced files in CLAUDE.md
- Skip large files (>100KB) or read first 200 lines only
- Prioritize: Core docs → Project configs → Other .md files → Environment files
- Store discoveries in Memory for future sessions