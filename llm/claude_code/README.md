# Introduction to Claude Code (Round 1)

**Claude Code** is Anthropic’s agentic coding tool that operates directly in the terminal, providing AI-powered assistance for software development tasks.  Launched in February 2025 alongside Claude 3.7 Sonnet, it enables developers to delegate substantial engineering tasks directly from their command line interface. Code stays local - there is no indexing or waiting.  With enough configuration and refinement, Claude Code should be able to use and master all of your team's CLI tools (e.g., git, docker, bq) so you may focus on solutions, not syntax. 

Claude Code is a more advanced agentic system with a more capable ability to reason and think, compared to most IDE-based agentic tools. It is also more advanced in terms of its ability to use and master CLI tools, since it is "CLI-native." 

>**Boris Cherny**: "*Think of the Claude Code as a super-intelligent Unix utility that can be chained with other CLI tools (e.g. `jq`).*"

#### Things Claude Code Can Do
| 1. Discover | 2. Design | 3. Build | 4. Deploy | 5. Support & Scale |
|-------------|-----------|----------|-----------|-------------------|
| Explore codebase and history | Plan project | Implement code | Automate CI/CD | Debug errors |
| Search documentation | Develop tech specs | Write and execute tests | Configure environments | Large-scale refactor |
| Onboard & learn | Define architecture | Create commits and PRs | Manage deployments | Monitor usage & performance |

#### Tools Claude Code Comes With
*CC ships with approx 12 tools out of the box. Built-in: bash, file search, file listing, file read & write, web fetch, web search, TODO's, sub-agents.*


| Tool | Description | Permission Required |
|------|-------------|-------------------|
| AgentTool | Runs a sub-agent to handle complex, multi-step tasks | No |
| BashTool | Executes shell commands in your environment | Yes |
| GlobTool | Finds files based on pattern matching | No |
| GrepTool | Searches for patterns in file contents | No |
| LSTool | Lists files and directories | No |
| FileReadTool | Reads the contents of files | No |
| FileEditTool | Makes targeted edits to specific files | Yes |
| FileWriteTool | Creates or overwrites files | Yes |
| NotebookReadTool | Reads and displays Jupyter notebook contents | No |
| NotebookEditTool | Modifies Jupyter notebook cells | Yes |

&nbsp;
## Claude Code Commands
### Installation and Essential CLI commands
---
```bash
# Install
npm install -f @anthropic-ai/claude-code

# Interactive REPL mode
claude

# Update to latest version
claude update

# Health check configuration
claude doctor

# MCP server management
claude mcp list
claude mcp add <name> <command>
claude mcp add-json <name> '<json>'

# Resume previous conversation
claude --continue

# Single command execution (print mode)
claude -p "your prompt here"
```

### Interactive slash commands & setup
---
```bash
# Get Started
/login           # Switch authentication method
/logout          # Log out of current session
/model           # Switch between Claude models (Opus 4, Sonnet 4, Haiku 3.5)

# Set up
/mcp             # Manage Model Context Protocol servers
/mcp "add filesystem from claude desktop" # Add an MCP servers from Claude Desktop. Adding all CD MCP's is not recommended, because capabilities differ... 
/memory		 # Shows all of the different memory files that are getting pulled in.  
/config          # Access configuration settings & turn on notifications
/status          # Get a summary of current status
/permissions     # Manage tool permissions
/allowed-tools   # Configure allowed tools and customize permissions

# Working... 
/init            # Initialize project with CLAUDE.md file
/ide             # Connect to IDE when using external terminal
/clear           # Clear conversation context (recommended frequent use)
/compact	# Like clear but keep a summary of previous conversation
/help            # Documentation and assistance

# Other commands
/install-github-app	# Tag @claude on your issues & PR's
/bug             # Report issues directly to Anthropic
/vim             # Enable Vim keybindings
/theme		 # Enable light/dark mode
/terminal-setup  # Configure terminal settings. Enable shift+enter to insert newlines.

# Turn on MacOS dictation! Works well w/Claude Code. 
```

#### Keybindings
---
| Key | Key Function |
|-----|--------------|
| Shift+tab | Auto-accept edits |
| # | Create a memory |
| ctrl+r | See memory. Verbose output |
| ! | Enter bash mode |
| @ | Add a file/folder to context |
| Esc | Cancel anytime with attempt to rollback gracefully |
| Double-esc | Jump back in history, --resume to resume |
| /vibe | (Command function) |



&nbsp;
### Tips for effective usage
---
###### 1. Start w/**codebase Q&A** to familiarize with Claude Code. This is a good way to acclimate. 
Example questions: 
	- How is `@RoutingController.py` used? 
	- How do I make a new `@app/services/ValidationTemplateFactory`?
	- Why does `recoverFromException` take so many arguments? Look through git history to answer. 
	- Why did we fix issue #18363 by add the if/else in `@src/login.ts` API? 
	- In which version did we release the new `@api/ext/PreHooks.php` API? 
	- Look at PR #9383, then carefully verify which app versions were impacted? 
	- What did I ship last week? 
	
###### 2. **Editing Code**. Develop a sense for what Claude-Code *just knows*, and where it needs help. 
Example prompts & tips:
	- "Propose a few fixes for issue #8732, then implement the one I pick." 
	- "Identify edge cases that are not covered in `@app/tests/signupTest.ts`, then update the tests to cover these." + "Think hard" or "ultrathink"
	- "commit, push, pr"
	- "Use 3 parallel agents to brainstorm ideas for how to clean up `@services/aggregator/feed_service.cpp`"

###### 3. **Tell Claude about your bash tools or MCP servers**. Teach it to use your tools.  
1. `claude mcp add barley_server -- node myserver`
2. "Use the barley CLI to check for error logs in the last training run. Use barley -h to check for how to use it."
3. 	**Write code > screenshot result > iterate**: "Implement [mock.png], then screenshot it with Puppeteer and iterate until it looks like the mock."

###### 4. **Adopt the workflow and steps to the task.** 
"Thinking up front" pays off with Claude Code and "conversational programming" in general. 

###### 5. **Context Engineering & custom tools = better performance.** 
 [**Anthropic: Claude Memory**](https://docs.anthropic.com/en/docs/claude-code/memory): 
Taking time to set memory and context files (see above) is well worth the effort for a full-featured experience. 

###### 6. **Give Claude more context on-the-fly:**
**Shortcut**: type '#' to add something to memory. 

| File/Directory | Command to Type |
|----------------|-------------------------|
| `~/.claude/commands/foo.md`| `/user:foo` |
| `project-root/` | |
| • `.claude/commands/foo.md` | `/project:foo` |
| • `a/` | `@a` |
| • `commands/foo.md` | `/project:a:foo` |
| • `CLAUDE.md` | Pulled in on demand |
| • `foo.py` | `@a/foo.py` |

###### 7. **Take time to tune context.** 
Is it for you or your team? Do you want to add it automatically or lazily? 

###### 8. **Take time to tune tooling.**
Configure CLAUDE.md, MCP servers, permissions, and slash commands for your team, and check them into git. 

###### 9. **Other Hi-level Techniques:**

**Recommended development patterns**
- **Planning phase**: Ask Claude to create detailed implementation plans before coding
- **Research-first approach**: Have Claude read and understand codebase before making changes
- **Test-driven development**: Enhanced TDD workflows with automated test generation 
- **Extended thinking**: Use “think harder” or “ultrathink” prompts for complex problems
- **Context management**: Utilize CLAUDE.md files for project-specific context 
- **Session resumption**: Leverage `--continue` for long-running development tasks 

**Usage optimization techniques**
- **Strategic prompting**: Group multiple related questions in single prompts to reduce back-and-forth
- **File selection**: Be strategic about which files to include when using “Configure files” 
- **Context clearing**: Use `/clear` regularly to manage conversation context 
- **Custom commands**: Create project-specific slash commands for repetitive tasks 
- **MCP integration**: Connect to external tools and databases for enhanced capabilities 

**Cost and resource management**
- **Monitor usage**: Use verbose logging to track API consumption
- **Model selection**: Choose appropriate models for different tasks (Sonnet 4 for daily work, Opus 4 for complex problems) 
- **Batch operations**: Combine multiple small tasks into single prompts
- **Session limits**: Be aware of the 5-hour session windows and 50 sessions per month guideline



&nbsp;
### Intro to Claude Code (Round 2!) 
---
##### Reading
- [Main: Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Main: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code: Settings](https://docs.anthropic.com/en/docs/claude-code/settings)
- [SDK Docs](https://docs.anthropic.com/en/docs/claude-code/sdk)

##### Watching
- **YouTube**: [Mastering Claude in 30min](https://www.youtube.com/watch?v=6eBSHbLKuN0&ab_channel=Anthropic)
- **YouTube**: [1/4: Building Blocks for Tomorrow’s AI Agents](https://www.youtube.com/watch?v=oDks2gVHu4k&list=PLf2m23nhTg1P5BsOHUOXyQz5RhfUSSVUi)
- **YouTube**: [2/4: Mastering Claude Code in 30 Minutes](https://www.youtube.com/live/6eBSHbLKuN0?si=u0J-fv8tU6Yru0Rm)
- **YouTube**: [3/4: Taking Claude ot the Next Level](https://www.youtube.com/live/nZCy8E5jlok?si=o6tBjIoU24Mzmwhd)
- **YouTube**: [4/4: Code w/Claude - Opening Keynote](https://www.youtube.com/live/EvtPBaaykdo?si=H52d6VBvxGGvSpCg)

##### Resources & More Advanced
- [Github: Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code): *This is a great source for custom hooks, slash commands, and other advanced features.*
- [ClaudeLog](https://claudelog.com/): Experiments, insights & mechanics about Claude Code
- [Github: Context Engineering](https://github.com/coleam00/context-engineering-intro/tree/main): A template for getting started with Context Engineering. 
- **YouTube**: [Matt Maher: 13 Tricks w/CC]( https://www.youtube.com/watch?v=T_IYHx-9VGU)
- **YouTube**: [Greg Bagues: 47 CC Tips in 9min](https://www.youtube.com/watch?v=TiNpzxoBPz0)


&nbsp;
### Claude Context & Memory
---
Read more about [Claude Code: Settings here](https://docs.anthropic.com/en/docs/claude-code/settings). Claude Code uses a robust & layered configuration system:
| Feature | Enterprise policy (shared) | Global (just me) | Project (checked in) | Project (no version ctrl) |
|---------|---------------------------|------------------|------------------|-------------------|
| **Memory** | /Library/Application Support/ClaudeCode/CLAUDE.md | ~/.claude/CLAUDE.md | repo/CLAUDE.md | repo/CLAUDE.local.md |
|   | \**shared across all projects* | \**shared across all projects* | \**shared & checked into version control* | \**just for user, not checked into version control* |
| **Slash commands** | - | ~/.claude/commands/ | - | - |
| **Permissions** | /Library/Application Support/ClaudeCode/ policies.json | ~/.claude/settings.json | .claude/settings.json | .claude/settings.local.json |
| **MCP servers** | - | `claude mcp` | .mcp.json | `claude mcp` |

\* ***Try to keep the all project CLAUDE.md files as short as possible to manage token usage / consumption.*** 

##### **NOTE:** 
Configurations generally follow a clear precedence hierarchy. When servers with the same name exist at multiple scopes, the system resolves conflicts by prioritizing local-scoped servers first, followed by project-scoped servers, and finally user-scoped servers. This design ensures that personal configurations can override shared ones when needed. Select your scope based on:
**Local scope**: Personal servers, experimental configurations, or sensitive credentials specific to one project
**Project scope**: Team-shared servers, project-specific tools, or services required for collaboration
**User scope**: Personal utilities needed across multiple projects, development tools, or frequently-used services


### MCP Server Setup
---
```bash
# Add a local-scoped server (default)
claude mcp add my-private-server /path/to/server

# Explicitly specify local scope
claude mcp add my-private-server -s local /path/to/server
```

### Custom slash commands
---
Create reusable [custom slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) by placing Markdown files in specific directories correlated to scope:
- **Project commands**: `.claude/commands/` (shared with team)
- **Personal commands**: `~/.claude/commands/` (personal use)  

`<command-name>`: Name derived from the Markdown filename (without .md extension)

Commands support dynamic arguments using the optional `$ARGUMENTS` placeholder. For example:
```bash 
# Command definition
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# Usage
> /fix-issue 123
```


### Git integration workflow
---
Claude Code provides comprehensive Git operations:
- **Commit creation**: Automatically generate descriptive commit messages
- **PR generation**: Create pull requests with detailed descriptions
- **Git history searching**: Analyze commit history and code evolution
- **Merge conflict resolution**: Intelligent conflict resolution assistance
- **Branch management**: Create, switch, and manage branches  
- **Git worktree support**: Enable parallel development workflows 

### GitHub Actions integration
---
More info about [Github Actions in Claude Code here](https://docs.anthropic.com/en/docs/claude-code/github-actions). 

Enable background task execution:  
```yaml
# Example GitHub Action workflow
- uses: anthropics/claude-code-action@v1
  with:
    anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Review this PR and suggest improvements"
    allowed-tools: "read_file,write_file,run_command"
```

### Hooks
---
[Claude Code hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) are JavaScript functions that run at specific points in the conversation lifecycle, allowing you to customize behavior and add functionality. [Get started docs here](https://docs.anthropic.com/en/docs/claude-code/hooks-guide). Hooks are defined in your project's `.claude/` directory as JavaScript or Python modules and are automatically loaded when Claude Code starts in that project. This gives you powerful customization capabilities while keeping the core Claude Code experience clean and focused. The general convention appears to be to declare hooks in the `.claude/settings.json` file and then store implementation files in the `.claude/hooks` directory. 

###### **Key Hook Types**: 
Claude Code provides several hook events that run at different points in the workflow:
- **PreToolUse**: Runs before tool calls (can block them)
- **PostToolUse**: Runs after tool calls complete
- **Notification**: Runs when Claude Code sends notifications
- **Stop**: Runs when Claude Code finishes responding
- **SubagentStop**: Runs when subagent tasks complete

- **Conversation Hooks**: Run at the start/end of conversations
	- `onConversationStart()` - Initialize project context, set up environment
	- `onConversationEnd()` - Cleanup, save state, log metrics
- **Message Hooks**: Run before/after each message exchange
	- `onBeforeMessage()` - Pre-process user input, add context
	- `onAfterMessage()` - Post-process responses, trigger actions
- **Tool Hooks**: Run around MCP tool usage	
	- `onBeforeTool()` - Validate tool calls, add safety checks
	- `onAfterTool()` - Process tool results, log usage

###### A Few Common Use Cases
- **Auto-context**: Automatically pull in relevant project files
- **Linting**: Lint a file after making changes. 
- **Logging**: Track conversation metrics and tool usage
- **Safety**: Add validation layers for destructive operations
- **Integration**: Connect to external systems (Slack, JIRA, etc.)
- **Personalization**: Inject user preferences and project conventions

###### Github Repositories
- [**Github**: IndyDevDan: claude-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery): *A good video course w/code. Good YT account to follow, in general.* 
- [**Github**: wedevtodayjson/claude-hooks](https://github.com/webdevtodayjason/claude-hooks/tree/main/hooks): *A decent python hook collection.* 
- [**Github**: decider: claude-hooks](https://github.com/decider/claude-hooks/tree/main/hooks): *A decent bash script hook collection.* 
- [**Github**: codeinbox](https://github.com/codeinbox/codeinbox): *A Claude Code hooks into Slack implementation.* 
- [**Github**: IndyDevDan: multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability/blob/main/README.md): Advanced usage of hooks to follow spun-up agents in real time. 


## IDE integrations and development workflows

#### Cursor & Windsurf integration
- **Installation**: Simply type `ide` into a terminal window within the app. 
- IDE integrations work with Claude Code’s configuration system:
	- Run `claude`
	- Enter the `/config` command
	- Adjust your preferences. Setting the diff tool to auto will enable automatic IDE detection

#### Visual Studio Code integration
- **Installation**: Beta extension available via VS Code marketplace
- **Auto-installation**: Automatically installs when running `claude` in VS Code terminal 
- **Keyboard shortcuts**: Cmd+Esc (Mac) / Ctrl+Esc (Windows/Linux)
- **Features**: Diff viewing directly in IDE, file reference shortcuts (Cmd+Option+K / Alt+Ctrl+K) 

#### JetBrains IDEs support
Compatible with PyCharm, WebStorm, IntelliJ IDEA, GoLand: 
- **Plugin installation**: Required with full IDE restart
- **Remote Development**: Support with host-side plugin installation
- **CLI integration**: Requires `code`/`idea` command availability 