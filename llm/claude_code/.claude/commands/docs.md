# Claude Command: Docs
This command helps you analyze and update CLAUDE.md files to improve Claude Code's performance and maintain project documentation consistency.

## Usage
To analyze and update project documentation, just type:
```
/docs
```

Or to update only the Project Status Summary & To Do's section:
```
/docs --status-only
```

### Parameters
- `--status-only`: Limits the analysis and updates to only the "## Project Status Summary & To Do's" section. This is useful for quick status updates without reviewing the entire documentation structure.

## What This Command Does

### Full Documentation Analysis (default)
1. **Discovery**: Automatically locates CLAUDE.md in current directory, then .claude/CLAUDE.md
2. **Analysis**: Reviews git changes, chat history, and existing CLAUDE.md to identify:
   - **Inconsistencies**: Where documentation conflicts with actual project state
   - **Missing Context**: Where Claude Code needs more detailed guidance  
   - **Redundant Content**: Where documentation can be streamlined
   - **Structural Issues**: Sections that don't match the standard template
3. **Recommendations**: Presents specific improvement suggestions with explanations and expected benefits
4. **User Confirmation**: Waits for approval on which improvements to implement
5. **Documentation Update**: Updates existing CLAUDE.md or creates new one using the standard template
6. **Quality Check**: Ensures documentation follows project structure and maintains consistency

### Status-Only Mode (`--status-only`)
When using the `--status-only` parameter, the command focuses exclusively on the Project Status Summary & To Do's section:

1. **Targeted Discovery**: Locates CLAUDE.md and identifies the "## Project Status Summary & To Do's" section
2. **Status Analysis**: Reviews recent git changes, commits, and project progress to determine:
   - **Completed Items**: Tasks that should be marked as ✅ completed
   - **New Tasks**: Emerging priorities that should be added to the to-do list  
   - **Updated Priorities**: Changes in task importance or categorization (⚠️ Hardening, ♻️ Refactor, ✨ Features, 📋 Documentation)
   - **Current Status**: Overall project state description updates
3. **Status Recommendations**: Presents specific updates to status items with reasoning
4. **User Approval**: Confirms which status changes to implement
5. **Targeted Update**: Updates only the Project Status Summary & To Do's section while preserving all other documentation
6. **Date Stamp**: Updates the "Updated" timestamp to reflect the current date

## Output Format

The updated CLAUDE.md should follow this structured template:

```markdown
# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status Summary & To Do's
**Updated**: *[Current Date]*

**Current Status**: [Brief project state description] - [High-level status summary]
- ✅ [Major completed milestone or feature]
- ✅ [Another completed key component]
- ✅ [Third completed major feature]
- ✅ [Additional completed milestone]
- ✅ [Final completed achievement]

**To Do**: [Brief summary of remaining work priorities]
- ⚠️ **Hardening**: [Critical items requiring attention]
  - [Specific hardening task with technical details]
  - [Another critical improvement needed]
  - [Third priority item for system stability]
- ♻️ **Refactor**: [Code/structure improvements needed]
  - [Specific refactoring task with reasoning]
  - [Another area needing restructuring]
  - [Third refactoring priority]
- ✨ **Features**: [New features and enhancements]
  - [New feature to be added]
  - [Enhancement to existing functionality]
  - [Additional capability to implement]
  - [Future enhancement consideration]
- 📋 **Documentation**: [Documentation tasks and improvements]
  - [Documentation that needs updating]
  - [New documentation to be created]

## Repository Overview

[Brief description of what this repository/project does and its primary purpose]

## Core Architecture

### [System/Component Name]
- **[Key Component]**: [Description of role and responsibilities]
- **[Another Component]**: [Description and how it fits in the system]
- **[Configuration File]**: [Purpose and format explanation]
- **[Directory Structure]**: [Organization and purpose]

### Key Design Principles
- **[Principle 1]**: [Explanation and benefits]
- **[Principle 2]**: [How it's implemented and why]
- **[Principle 3]**: [Impact on development workflow]

### Repository Structure
```
├── [directory]/     # [Purpose and contents]
│   ├── [subdirectory]/  # [Specific use case]
│   └── [files]      # [File descriptions]
├── [other-dir]/     # [Another area of the project]
└── [config-files]   # [Configuration and setup files]
```

## Getting Started
```
# Install dependencies and set up environment
[dependency-install-command] && cp .env.example .env

# Initialize project configuration
./setup.sh

# Verify setup is working correctly
[test-command]
```

## Common Commands
```
# Start development server
[dev-server-command]

# Build project for production
[build-command]

# Run test suite
[test-command]

# Deploy to staging/production
[deploy-command]

# Clean build artifacts and reset
[clean-command]
```

## Development Environment

### Tools & Technologies
- **[Primary Language/Framework]**: [Version and key details]
- **[Build Tool]**: [Purpose and configuration]
- **[Testing Framework]**: [How tests are structured and run]
- **[Package Management]**: [How dependencies are managed]
- **[Development Tools]**: [Editor, linting, formatting setup]
- **[Deployment/Infrastructure]**: [Container, cloud, or deployment details]

### Configuration
- **[Config Files]**: [Key configuration files and their purposes]
- **[Environment Variables]**: [Required and optional environment settings]
- **[Settings/Preferences]**: [Important project settings and how to modify them]

### Documentation Structure
- **[Main Documentation]**: [Primary documentation files and their purposes]
- **[Technical Docs]**: [Developer-focused documentation]
- **[User Guides]**: [End-user documentation and references]

## Implementation Notes

### [Architecture Pattern/Key Design]
- **[Primary Benefit]**: [Main advantage and how it's implemented]
- **[Secondary Benefit]**: [Additional advantage and implementation details]
- **[Impact]**: [Effect on development workflow and maintenance]

### [Technical Implementation]
- **[Core Technology/Approach]**: [How it works and why it was chosen]
- **[Integration Details]**: [How components connect and communicate]
- **[Configuration/Usage]**: [Key setup and usage considerations]

### Implementation History (Optional)
- **[Evolution]**: [How the implementation evolved and key decisions made]
- **[Current State]**: [Present approach and recent improvements]
- **[Lessons Learned]**: [Key insights and outcomes]
```

**File Details:**
- **Format:** Markdown (`.md`)
- **Location:** Project root (`./CLAUDE.md`) or `.claude/CLAUDE.md`
- **Status Indicators:** ✅ Completed, ⚠️ Needs Attention, ♻️ Refactor, ✨ Features, 📋 Documentation

## Workflow Instructions

### PLAN Mode (Analysis & Planning)
1. **Start in PLAN mode** for analysis and recommendation generation
2. **Discover documentation** - locate CLAUDE.md file (current directory, then .claude/CLAUDE.md)
3. **Review project context** - analyze git status, file changes, and chat history
4. **Identify improvement opportunities** - systematically review all sections or plan new structure
5. **Present recommendations** - provide clear explanations and expected benefits

### CODE Mode (Documentation Update)
1. **Switch to CODE mode** - only after user approves specific improvements
2. **Update documentation** - modify existing CLAUDE.md or create new one based on discovery results
3. **Follow template structure** - use established format for new files, maintain consistency for updates
4. **Preserve important context** - retain valuable information while removing redundancy

### Best Practices
- Focus on accuracy and consistency with actual project state
- Maintain clear, actionable guidance for Claude Code
- Use appropriate status indicators for tasks and features
- Keep documentation current with project evolution
- Preserve user-specific customizations and preferences

## Important Notes

### Integration with Other Commands
- If it has not already been run, use the `/prime` command first to understand full project context before analysis
- Consider running after significant project changes or feature additions
- Coordinate with `/commit` for version controlling documentation updates

### File Management
- Automatically discovers CLAUDE.md in current directory or .claude/CLAUDE.md
- Always backup existing CLAUDE.md before making changes
- Creates new CLAUDE.md in project root if none exists
- Ensures all placeholder content is replaced with actual project information

### Limitations
- Requires access to project files and git history for effective analysis
- Cannot automatically detect all project-specific requirements
- User review required for all suggested changes before implementation
- Will create CLAUDE.md in current directory if no existing file is found
