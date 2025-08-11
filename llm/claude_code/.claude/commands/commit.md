# Claude Command: Commit
This command helps you create well-formatted commits with conventional commit messages and emoji.

## Usage
To create a commit, just type:
```
/commit
```

Or with options:
```
/commit --branch "feat/ui-improvements"
/commit --branch
/commit --no-attrib
/commit --branch "feat/ui-improvements" --no-attrib
```

## What This Command Does
1. **Branch Management**: When `--branch` parameter is used:
   - Validates branch name follows conventions (`feat/`, `fix/`, `docs/`, `refactor/`, `chore/`)
   - Checks if branch already exists and warns if it does
   - If not on main/master but already on a feature branch, asks if you want to use current branch
   - Creates new branch using `git checkout -b "branch-name"` (safely brings all changes with you)
   - Confirms branch creation with user before proceeding
2. **File Staging**: Checks which files are staged with `git status`
3. **Auto-staging**: If 0 files are staged, automatically adds all modified and new files with `git add`
4. **Change Analysis**: Performs a `git diff` to understand what changes are being committed
5. **Commit Splitting**: Analyzes the diff to determine if multiple distinct logical changes are present
6. **Multi-commit Logic**: If multiple distinct changes are detected, suggests breaking the commit into multiple smaller commits
7. **Message Generation**: For each commit (or the single commit if not split), creates a commit message using emoji conventional commit format
8. **Attribution**: Adds attribution message unless `--no-attrib` parameter is used
9. 🔥 **Safety Check**: You MUST always confirm with user in ALL CAPS if preparing to `git reset --hard` or any other operations that may result in data loss!

## Best Practices for Commits
- **Verify before committing**: Ensure code is linted, builds correctly, and documentation is updated
- **Atomic commits**: Each commit should contain related changes that serve a single purpose
- **Split large changes**: If changes touch multiple concerns, split them into separate commits
- **Conventional commit format**: Use the format `<type>: <description>` where type is one of:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, etc)
  - `refactor`: Code changes that neither fix bugs nor add features
  - `perf`: Performance improvements
  - `test`: Adding or fixing tests
  - `chore`: Changes to the build process, tools, etc.
- **Present tense, imperative mood**: Write commit messages as commands (e.g., "add feature" not "added feature")
- **Concise first line**: Keep the first line under 72 characters
- **Emoji**: Each commit type is paired with an appropriate emoji:
  - ✨ `feat`: New feature
  - 🐛 `fix`: Bug fix
  - 📝 `docs`: Documentation
  - 💄 `style`: Formatting/style
  - ♻️ `refactor`: Code refactoring
  - ⚡️ `perf`: Performance improvements
  - ✅ `test`: Tests
  - 🔧 `chore`: Tooling, configuration
  - 🚀 `ci`: CI/CD improvements
  - 🗑️ `revert`: Reverting changes
  - 🧪 `test`: Add a failing test
  - 🚨 `fix`: Fix compiler/linter warnings
  - 🔒️ `fix`: Fix security issues
  - 👥 `chore`: Add or update contributors
  - 🚚 `refactor`: Move or rename resources
  - 🏗️ `refactor`: Make architectural changes
  - 🔀 `chore`: Merge branches
  - 📦️ `chore`: Add or update compiled files or packages
  - ➕ `chore`: Add a dependency
  - ➖ `chore`: Remove a dependency
  - 🌱 `chore`: Add or update seed files
  - 🧑‍💻 `chore`: Improve developer experience
  - 🧵 `feat`: Add or update code related to multithreading or concurrency
  - 🔍️ `feat`: Improve SEO
  - 🏷️ `feat`: Add or update types
  - 💬 `feat`: Add or update text and literals
  - 🌐 `feat`: Internationalization and localization
  - 👔 `feat`: Add or update business logic
  - 📱 `feat`: Work on responsive design
  - 🚸 `feat`: Improve user experience / usability
  - 🩹 `fix`: Simple fix for a non-critical issue
  - 🥅 `fix`: Catch errors
  - 👽️ `fix`: Update code due to external API changes
  - 🔥 `fix`: Remove code or files
  - 🎨 `style`: Improve structure/format of the code
  - 🚑️ `fix`: Critical hotfix
  - 🎉 `chore`: Begin a project
  - 🔖 `chore`: Release/Version tags
  - 🚧 `wip`: Work in progress
  - 💚 `fix`: Fix CI build
  - 📌 `chore`: Pin dependencies to specific versions
  - 👷 `ci`: Add or update CI build system
  - 📈 `feat`: Add or update analytics or tracking code
  - ✏️ `fix`: Fix typos
  - ⏪️ `revert`: Revert changes
  - 📄 `chore`: Add or update license
  - 💥 `feat`: Introduce breaking changes
  - 🍱 `assets`: Add or update assets
  - ♿️ `feat`: Improve accessibility
  - 💡 `docs`: Add or update comments in source code
  - 🗃️ `db`: Perform database related changes
  - 🔊 `feat`: Add or update logs
  - 🔇 `fix`: Remove logs
  - 🤡 `test`: Mock things
  - 🥚 `feat`: Add or update an easter egg
  - 🙈 `chore`: Add or update .gitignore file
  - 📸 `test`: Add or update snapshots
  - ⚗️ `experiment`: Perform experiments
  - 🚩 `feat`: Add, update, or remove feature flags
  - 💫 `ui`: Add or update animations and transitions
  - ⚰️ `refactor`: Remove dead code
  - 🦺 `feat`: Add or update code related to validation
  - ✈️ `feat`: Improve offline support

## Branch Management

### Branch Creation Safety
This command uses `git checkout -b "branch-name"` to create new branches, which is the safest approach because:
- **All your changes follow you**: Both staged and unstaged changes move to the new branch automatically
- **No risk of losing work**: Your changes are never left behind or lost
- **Simple and reliable**: One command, predictable outcome
- **Easy recovery**: If something goes wrong, your changes are still there

### Branch Naming Conventions
Branch names must follow these patterns:
- `feat/feature-description` - For new features
- `fix/bug-description` - For bug fixes  
- `docs/documentation-area` - For documentation changes
- `refactor/component-name` - For code refactoring
- `chore/task-description` - For maintenance tasks

### Branch Name Inference
When using `--branch` without specifying a name, the command will analyze your changes and suggest a branch name based on:
- **File types changed**: docs/, tests/, src/, etc.
- **Change patterns**: New files (feat/), bug fixes (fix/), etc.
- **Commit message analysis**: Keywords that indicate the type of change

### Workflow Examples
```bash
# Create specific branch
/commit --branch "feat/user-authentication"

# Let command infer branch name from changes
/commit --branch

# Use current branch if already on feature branch
# (command will ask for confirmation)
```

### Troubleshooting
- **Branch already exists**: Command will warn you and ask if you want to switch to existing branch
- **Invalid branch name**: Command will suggest corrections following naming conventions
- **Already on feature branch**: Command asks if you want to use current branch or create new one

## Guidelines for Splitting Commits
When analyzing the diff, consider splitting commits based on these criteria:

1. **Different concerns**: Changes to unrelated parts of the codebase
2. **Different types of changes**: Mixing features, fixes, refactoring, etc.
3. **File patterns**: Changes to different types of files (e.g., source code vs documentation)
4. **Logical grouping**: Changes that would be easier to understand or review separately
5. **Size**: Very large changes that would be clearer if broken down

## Examples
Good commit messages:
- ✨ feat: add user authentication system
- 🐛 fix: resolve memory leak in rendering process
- 📝 docs: update API documentation with new endpoints
- ♻️ refactor: simplify error handling logic in parser
- 🚨 fix: resolve linter warnings in component files
- 🧑‍💻 chore: improve developer tooling setup process
- 👔 feat: implement business logic for transaction validation
- 🩹 fix: address minor styling inconsistency in header
- 🚑️ fix: patch critical security vulnerability in auth flow
- 🎨 style: reorganize component structure for better readability
- 🔥 fix: remove deprecated legacy code
- 🦺 feat: add input validation for user registration form
- 💚 fix: resolve failing CI pipeline tests
- 📈 feat: implement analytics tracking for user engagement
- 🔒️ fix: strengthen authentication password requirements
- ♿️ feat: improve form accessibility for screen readers

Example of splitting commits:
- First commit: ✨ feat: add new solc version type definitions
- Second commit: 📝 docs: update documentation for new solc versions
- Third commit: 🔧 chore: update package.json dependencies
- Fourth commit: 🏷️ feat: add type definitions for new API endpoints
- Fifth commit: 🧵 feat: improve concurrency handling in worker threads
- Sixth commit: 🚨 fix: resolve linting issues in new code
- Seventh commit: ✅ test: add unit tests for new solc version features
- Eighth commit: 🔒️ fix: update dependencies with security vulnerabilities

## Command Options
- `--branch "branch-name"`: Create or switch to specified branch before committing
- `--branch`: Create a new branch with name inferred from the changes being committed
- `--no-attrib`: Omit the "Generated with Claude Code" and "Co-Authored by Claude"attribution messages from commit notes

## Important Notes

### Branch Management
- **Safe branch creation**: Uses `git checkout -b` which automatically brings all your changes to the new branch
- **Branch validation**: Enforces naming conventions (`feat/`, `fix/`, `docs/`, `refactor/`, `chore/`)
- **Existing branch check**: Warns if branch name already exists
- **Current branch detection**: If already on feature branch, asks for confirmation before creating new branch
- **Change preservation**: Your staged and unstaged changes are never lost during branch operations

### Commit Workflow
- **Smart staging**: If specific files are staged, commits only those; otherwise stages all modified files
- **Change analysis**: Reviews diff to determine if multiple commits would be more appropriate
- **Commit splitting**: Helps stage and commit changes separately when multiple logical changes detected
- **Message validation**: Always reviews commit diff to ensure message matches the changes

### Attribution
- **Default behavior**: Includes "🤖 Generated with [Claude Code](https://claude.ai/code)" in commit messages
- **Opt-out available**: Use `--no-attrib` to omit attribution when needed

## Claude Code Limitations
**Note**: Claude Code cannot directly execute git commands by default, unless granted permission to do so. This command provides guidance and commit message templates that you'll need to execute manually in your terminal. Claude Code can:
- Help analyze changes using the Filesystem MCP tool
- Suggest appropriate commit messages and emoji
- Guide you through best practices for atomic commits
- Store commit conventions in Memory for consistency