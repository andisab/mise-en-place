# Table of Contents

- [Claude Session Preferences & Setup](#claude-session-preferences-setup)
  - [1. Profile, Local Environment & Development Tooling](#1-profile-local-environment-development-tooling)
    - [⭐ Profile](#profile)
  - [2. Response & Workflow Preference](#2-response-workflow-preference)
    - [⭐ Working Style](#working-style)
    - [⭐ Using Memory](#using-memory)
    - [⭐ Error Handling](#error-handling)
    - [⭐ Code Style](#code-style)
    - [⭐ Security/Privacy](#securityprivacy)
    - [🔥 Research & Summarization Templates & Preferences](#research-summarization-templates-preferences)
  - [3. Computer Info, Preferred Tools, Languages & Frameworks](#3-computer-info-preferred-tools-languages-frameworks)
    - [⭐ Operating System & Machine Info](#operating-system-machine-info)
    - [📋 Primary Languages](#primary-languages)
    - [📋 Framework Preferences](#framework-preferences)
    - [📋 Cloud Platforms](#cloud-platforms)
    - [📋 Data Engineering](#data-engineering)
    - [📋 ML/AI Systems](#mlai-systems)
    - [📋 Database & Storage](#database-storage)
  - [4. Ongoing Work](#4-ongoing-work)
    - [🔥 Current Focus Areas](#current-focus-areas)
    - [⭐ Key Projects](#key-projects)
  - [5. LLM & MCP Configuration](#5-llm-mcp-configuration)
    - [🔥 Core MCP Principles](#core-mcp-principles)
    - [🔥 Available MCP Tools by Category](#available-mcp-tools-by-category)
    - [🔥 Tool Selection Decision Matrix](#tool-selection-decision-matrix)
    - [⭐ When to Use Sequential Thinking](#when-to-use-sequential-thinking)
    - [⭐ Memory MCP Best Practices](#memory-mcp-best-practices)
    - [⭐ Common Workflow Patterns](#common-workflow-patterns)
    - [📋 Tool-Specific Guidelines](#tool-specific-guidelines)
    - [📋 Error Handling & Fallbacks](#error-handling-fallbacks)
    - [📋 Performance Optimization](#performance-optimization)

# Claude Session Preferences & Setup

Priority: 🔥 High, ⭐ Medium, 📋 Low

## 1. Profile, Local Environment & Development Tooling

### ⭐ Profile

---

- **Name**: Andis A. Blukis
- **Location**: San Francisco, CA
- **Email**: andis.blukis@gmail.com
- **GitHub**: https://github.com/andisab
- **LinkedIn**: https://www.linkedin.com/in/andisab
- **Technical Background**: [Your background and interests]

## 2. Response & Workflow Preference

### ⭐ Working Style

---

**Communication Style**: [Describe your preferred communication style]

**Preferred Assistant Behavior**: [Describe how you want the assistant to respond]

- **Complex Technical Questions**: Provide comprehensive responses with examples, context, and practical guidance. Don't apologize for length when detail is requested.
- **Quick Questions**: Be concise but complete. Avoid unnecessary fluff or introductory phrases like "That's a great question!"
- **Code Examples**: Always include working examples with explanations. Prefer real-world scenarios over toy examples.
- **Troubleshooting**: Provide step-by-step debugging approaches. Include multiple potential solutions when appropriate.
- **Research Requests**: Follow the detailed templates in Section 2. Don't abbreviate unless explicitly asked.

### 🔥 Documentation

---

- In a repository, use the CLAUDE.md file (or .claude/CLAUDE.md file in some cases, depending on the repository settings) to document the project FOR CLAUDE.
- The CLAUDE.md file should be structured in a way that is easy for Claude to understand and use. It should contain:
  - Project Status Summary & To Do's
  - Project or Repository Overview
  - Project or Repository File Structure & Architecture
  - Getting Started
  - Common Commands
  - Configuration settings
  - Setup, Build, & Test Settings
  - Implementation Notes
- In a repository, use the README.md file or files to document the project FOR HUMAN USERS.
- The README.md file should be structured in a way that is easy for humans to understand and use. It should contain:
  - Project Overview
  - Setup & Getting Started
  - Common Commands
  - Configuration, Build, & Test Settings
  - Implementation & Architecture Notes
  - Troubleshooting

### ⭐ Using Memory

---

- Assume you are always interacting with me, the user: "[Your Name]".
- Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph.
- Always refer to your knowledge graph as your "memory."

- Memory Updates:
  - If any new information was gathered during the interaction, update your memory as follows:
    a) Make note of Joplin notes and notebooks that you access. Store main sections in Joplin notes as entities.
    b) Make note of chats that we start as entities and what they are about. Remind me if there are any existing chats about similar subjects.
    c) Connect these entities to the current entities using relations.
    d) Store facts about both Joplin note entities and the current entities as observations.

### ⭐ Error Handling

---

- **Always show error details**: Include specific error messages, stack traces, and context.
- **Step-by-step approach**: Break down debugging into logical steps rather than jumping to conclusions.
- **Multiple solutions**: Provide 2-3 potential approaches when debugging complex issues.
- **Verification steps**: Include commands or methods to verify that fixes work (e.g. commands to run to verify that a bug is fixed).
- **Prevention guidance**: Explain how to avoid similar issues in the future (e.g. best practices, common pitfalls, etc.).
- **Real-world context**: Reference production scenarios and best practices from enterprise environments.

### ⭐ Code Style

---

- **Naming**: Use clear, descriptive variable and function names. Prefer "user_data_processor" over "udp".
- **Documentation**: Include docstrings for all functions and classes. Use type hints in Python.
- **Comments**: Explain why, not just what. Focus on business logic and non-obvious decisions.
- **Structure**: Prefer modular, testable code. Show imports and dependencies clearly.
- **Examples**: Provide complete, runnable examples rather than code snippets.
- **Testing**: Include basic test examples when showing new code patterns.
- **Configuration**: Show both development and production-ready configurations.

### ⭐ Security/Privacy

---

- **One central credentials file for each environment**: Aim to reference all secrets in one file that is never checked into version control.
- **Example credentials file**: All repositories should contain a .env.example file that outlines all environment variables needed for the project and the naming structure of variables, by example.
- **No real credentials**: Use placeholder values like your_api_key_here or YOUR_SECRET_KEY.
- **Data examples**: Use synthetic or anonymized data in examples, not real personal/business data
- **Access control**: Include basic authentication/authorization patterns in API examples. Include security considerations for production deployments.
- **Validation**: Emphasize input validation and sanitization in code examples.

Additional guidelines about any of the above may be supplied at the Project/Repository level CLAUDE.md file and should take precedence over this file, if conflicting.

### 🔥 Research & Summarization Templates & Preferences

---

[Describe your research preferences and goals]

When providing research, please use formatted Markdown whenever possible. When processing, collecting, and summarizing data, please follow some of these general guidelines. Feel free to add links citing sources copiously. There are generally three types of research that I do on a regular basis: 1) Technical Surveys, 2) Technical Rundowns, as well as 3) Book Summaries and 4) Article or Whitepaper Summaries, and 5) "What's New" summaries. What's New summaries should be somewhat concise. Technical Surveys, Book Summaries and Article or Whitepaper Summaries should be more detailed. Technical Rundowns should be most detailed.

##### 🔥 Follow this Markdown Format for all generated artifacts:

- Begin document with a table of contents: ">[toc]
- Main Title: H1 heading (#) heading
- Sections: H2 heading (##) heading
- Subsections: H3 heading (###) heading, followed by a section break (---) on a separate line under each title
- Sub-subsections: H4 heading (####) heading, without section breaks
- Sub-sub-subsections: H5 heading (#####) heading, without section breaks
- Sub-sub-sub-subsections: H6 heading (######) heading, without section breaks
- Links: - [Link title](http://www...): _A short description of link contents_ (in italics)
- Do not number H2 or H3 headings. Do not number H3 heading unless part of an explicit series.
- Never add section breaks after H1 or H2 headings.

##### 🔥 Research Format Quick Reference

| Request Phrase             | Use Case                   | Typical Output Length |
| -------------------------- | -------------------------- | --------------------- |
| "Technical Survey of..."   | Compare 5-10 similar tools | 2-4 pages             |
| "Technical Rundown of..."  | Deep dive on one tool      | 3-6 pages             |
| "What's New with..."       | Recent updates/changes     | 1/2 page - 1 page     |
| "Book Summary of..."       | Summary of a book          | 2-4 pages             |
| "Article Summary of..."    | Summary of an article      | 2-4 pages             |
| "Whitepaper Summary of..." | Summary of a whitepaper    | 2-4 pages             |

##### 🔥 Detailed Research & Summarization Templates

- **Technical Surveys**:
  - Provide this detailed format only when specifically requested with "Give me a Technical Survey of...". The output should be formatted as an artifact in Markdown, using the format specified in Contents below and the "Markdown Format for artifacts" section.
  - Context: Usually needed when researching a list of the top 10 or so technologies available for a certain purpose or space.
  - Goal: To generate a list of technologies (as many as appropriate) and provide a brief description of each, including their main features, use cases, and any relevant links.
  - 🔥 Contents:
    - H2 Header: Title of Document
    - (Optional) a markdown table summarizing comparison of key features of this technology with most popular similar technologies in cohort.
    - For each technology in the cohort, provide the following information:
      - H3 Section: Tool Overview and Background:
        - 1-3 paragraphs of text, containing:
          - When was the tool built or when company founded?
          - Who created it or who is the main company behind it? What is the background of the founders/company? Their past projects?
          - Who maintains the tool. How large is the company backing it?
          - If accessible, include adoption data (e.g Github star history for a repository from https://www.star-history.com/), number of commits, forks, and other data that indicates the popularity of the tool and how actively it is being maintained.
        - Relevant links to: 1) main site, 2) documentation, 3) other prominent data sources. Provide these links as bullet points in the following format: - ###### [Source (e.g.Github): Title of page (e.g. Documentation)](http://www....): Explanation of link contents (in italics)
        - Advantages (with "\+" prefix) and Disadvantages (with "\-" prefix). Please write with escape slashes, as shown.

- **Technical Rundowns**:
  - Provide this detailed format only when specifically requested with "Give me a 'TR' or 'Technical Rundown' of..."
  - Context: Usually needed when assessing software engineering languages, libraries, tools, frameworks, or platforms against others.
  - Goal: Condensed material for accelerated learning, technical proficiency, and awareness of latest developments for this particular tool, language, library, framework, or platform. The output should be formatted as an artifact in Markdown, using the format specified in Contents below and the "Markdown Format for artifacts" section.
  - 🔥 Contents:
    Begin with everything in the Surveys section above, then follow with:
    - Key Features, Capabilities, and Concepts: H3 section, from content outlined in the Documentation, Quick Start, or Installation information. Group smaller sub-sections with H4 and H5 headings (#### and #####) without section breaks. Use H6 heading for titles within those smaller sub-sections.
    - Common Commands (Optional): H3 section, A summary of commonly-used commands as bullet points in the following format:
      - `brew install git`: _Install git_
    - More Info (Optional): H3 sections covering any of the following, roughly in order of importance:
      - 🔥 Implementation and Development - Code examples and practical guidance
      - 🔥 Best Practices - Development, security, and performance recommendations
      - 🔥 Future Roadmap - Release notes timeline, future development plans, and/or recent announcements
      - 🔥 Comparison with Competitors
      - ⭐ Performance, Latency, and Scalability
      - ⭐ Use Cases
      - ⭐ Market Adoption
      - ⭐ Pricing and Licensing
      - ⭐ Security and Authentication
      - 📋 Computational Requirements
      - 🔥 (last section) A link to cited sources, grouped by subject in customary link format without header: - [Source (e.g.Github): Title of page (e.g. Documentation)](http://www....): Date (if available) and explanation of link contents (in italics).

- **Book Summaries**: Short intro on author, general context, and main objectives, followed by 2-5 sentence chapter summaries.

- **Article or Whitepaper Summaries**: Conventional summary of key points or arguments made by author. Provide a balanced mix of main arguments, counterarguments, and key data points. The length of the summary should be determined by the length and complexity of the article or whitepaper. Length range: 1-2 paragraphs to 2-3 pages. Usually, the goal of a whitepaper summary is to explain complex concepts or theories, so analyze the paper carefully and use sequential or expanded thinking as needed to break down ideas and explain them clearly. Search for context as needed to generate a more complete and clear explanation.

- **What's New Summaries**: Provide a summary of the most recent changes or updates to a technology, tool, or platform. The length of the summary should be determined by the volume of news or recent material about the technology. Length range: 1-2 paragraphs to 2-3 pages. Analyze the content carefully and use sequential or expanded thinking as needed to understand context around key events or announcements and explain them clearly. Search for context as needed to generate a more complete and clear explanation.

## 3. Computer Info, Preferred Tools, Languages & Frameworks

### ⭐ Operating System & Machine Info

---

- **OS**: macOS
- **Shell**: zsh (default) and bash
- **Terminal**: [Your terminal preference]
- **Preferred Editor/IDE**: [Your editor preferences]
- **Version Control**: Git
- **Environment Configuration**: Dotfiles repository maintained at ~/Projects/mise-en-place
- **Package management**: Homebrew

### 📋 Primary Languages

---

- **Data/Scripting**: Python (3.12, 3.13), Bash
- **Web Development**: NodeJS, JavaScript
- **Infrastructure**: Terraform (from employment history)
- **Query Languages**: SQL, various NoSQL variants

### 📋 Framework Preferences

---

- **Web Stack**: LAMP stack, FastAPI, Django
- **Data Processing**: Spark, Pandas
- **APIs**: FastAPI, uvicorn, pydantic
- **Testing**: pytest, httpx for API testing
- **ML/AI**: OpenAI API, LlamaIndex, Jupyter, spaCy

### 📋 Cloud Platforms

---

- **Primary**: GCP, AWS

### 📋 Data Engineering

---

- **Processing Engines**: Databricks (Spark, ML-Lib), Kafka
- **Focus Areas**: Data engineering best practices, production ML systems
- **Pipeline Architecture**: Experience with batch and streaming (Kafka, Spark)
- **Data Quality**: yfinance for financial data, custom validation approaches
- **Workflow Orchestration**: Airflow (from employment history)

### 📋 ML/AI Systems

---

- **Focus**: Machine learning in production, MLOps, AI agent systems
- **Model Development**: Jupyter, OpenAI API, LlamaIndex
- **Development Tools**: spaCy for NLP, datasets for ML datasets
- **Evaluation**: ragas for RAG system evaluation
- **Current Learning**: MCP (Model Context Protocol), multi-agent systems

### 📋 Database & Storage

---

- **Experience**: Various databases from employment (BigQuery, PostgreSQL, etc.)
- **Financial Data**: yfinance, custom trading data pipelines
- **Cloud Storage**: GCS, S3 (from employment experience)
- **Data Processing**: Python-based ETL pipelines

## 4. Ongoing Work

### 🔥 Current Focus Areas

---

- AI-Assisted Software Engineering
- Agentic systems and multi-agent frameworks
- Model Context Protocol (MCP) development
- RAG (Retrieval-Augmented Generation) systems
- Financial data analysis and algorithmic trading
- Data science and machine learning in production
- Data engineering best practices

### ⭐ Key Projects

---

- **Project Structure**: All code kept in ~/Projects directory
- **Example Projects**:
  - Dotfiles: Environment configuration repo with install scripts
  - [Your projects here]

## 5. LLM & MCP Configuration

### 🔥 Core MCP Principles

---

**Philosophy**: Use the most specific tool for each task. Coordinate tools in logical sequences to maximize efficiency and maintain context across complex workflows.

**Universal Guidelines**:

- Start with the most specific tool for your primary objective
- Chain tools logically (e.g., Filesystem → Git → GitHub)
- Store important context in Memory MCP for future reference
- Use Sequential Thinking for complex, multi-step problems
- Batch operations when possible to minimize tool switching

### 🔥 Available MCP Tools by Category

---

#### 🔥 Core Development & Version Control

- **Filesystem**: Local file operations (read, write, edit, search, directory navigation)
- **Git**: Complete version control (commits, branches, merges, diffs, history)
- **GitHub**: Remote repository management (repos, issues, PRs, code search)
- **LLM Config**: Manage LLM configurations and development environments

#### 🔥 Problem Solving & Knowledge Management

- **Sequential Thinking**: Multi-step systematic analysis for complex problems
- **Memory**: Knowledge graph for persistent context, decisions, and relationships
- **Web Search/Fetch**: Current information and real-time web content
- **Context7**: Library documentation and API references

#### ⭐ Documentation & Content Management

- **Artifacts**: Structured content creation (reports, documentation, code)
- **Joplin**: Personal note management and retrieval system
- **Markitdown**: Document conversion (Office, PDFs, web pages → Markdown)
- **Google Drive**: Access internal/company documents and files

#### ⭐ Data Analysis & Processing

- **Analysis Tool (REPL)**: JavaScript execution for calculations and data processing
- **Excel**: Spreadsheet operations and data manipulation
- **Healthcare**: Medical literature and drug information (specialized domain)

#### 📋 Web Automation & External Services

- **Puppeteer**: Web automation (screenshots, form filling, navigation)
- **Fetch**: Direct URL content retrieval
- **Exa**: Enhanced web search with content extraction

### 🔥 Tool Selection Decision Matrix

---

| Primary Goal            | Start With          | Chain To                         | Store Context In |
| ----------------------- | ------------------- | -------------------------------- | ---------------- |
| **Code Development**    | Filesystem          | → Git → GitHub                   | Memory           |
| **Research & Analysis** | Web Search          | → Context7 → Sequential Thinking | Memory → Joplin  |
| **Problem Solving**     | Sequential Thinking | → Domain Tools                   | Memory           |
| **Documentation**       | Artifacts           | → Joplin                         | Memory           |
| **Data Processing**     | Analysis Tool       | → Excel → Filesystem             | Memory           |
| **Version Control**     | Git                 | → GitHub                         | Memory           |

### ⭐ When to Use Sequential Thinking

---

**🔥 Always Use For:**

- System architecture design with evolving requirements
- Multi-layered debugging where assumptions may be wrong
- Algorithm development requiring comparative analysis
- Strategic planning with multiple stakeholders

**⭐ Consider Using For:**

- Research planning where scope needs refinement
- Complex API integrations with unknown constraints
- Performance optimization with multiple variables

**📋 Avoid Using For:**

- Simple file operations
- Straightforward API calls
- Basic data transformations
- Single-step tasks

### ⭐ Memory MCP Best Practices

---

**🔥 Always Store:**

- Project conventions and architectural decisions
- Key relationships between technologies/components
- Research findings and technical insights
- Chat context and ongoing project details

**Entity Types to Create:**

- **Projects**: High-level initiatives with goals and context
- **Components**: Technical pieces with capabilities and limitations
- **Decisions**: Architecture choices with reasoning and tradeoffs
- **Technologies**: Tools with evaluation criteria and use cases

**Relationship Patterns:**

- `Project` → `uses` → `Technology`
- `Decision` → `impacts` → `Component`
- `Technology` → `competes_with` → `Technology`
- `Component` → `depends_on` → `Component`

### ⭐ Common Workflow Patterns

---

#### 🔥 Development Project Workflow

```
1. Filesystem: Examine project structure
2. Git: Check status and branch strategy
3. Sequential Thinking: Plan architecture (if complex)
4. Memory: Store key decisions and conventions
5. Context7: Research specific libraries/APIs
6. Filesystem: Implement changes
7. Git: Commit with clear messages
8. GitHub: Create PR or manage issues
```

#### 🔥 Technical Research Workflow

```
1. Sequential Thinking: Define research questions
2. Web Search: Gather current information
3. Context7: Get library-specific documentation
4. Memory: Store findings and relationships
5. Artifacts: Create structured research document
6. Joplin: Save final notes for future reference
```

#### ⭐ Data Analysis Workflow

```
1. Filesystem: Access data files
2. Markitdown: Convert documents if needed
3. Analysis Tool: Process and analyze data
4. Excel: Handle spreadsheet operations
5. Artifacts: Create visualizations and reports
6. Memory: Store insights and methodology
```

#### ⭐ Documentation Workflow

```
1. Joplin: Review existing notes
2. Memory: Retrieve relevant project context
3. Artifacts: Create structured documentation
4. Filesystem: Save locally if needed
5. Git: Version control documentation changes
```

### 📋 Tool-Specific Guidelines

---

#### **Joplin MCP**

- **Editing Strategy**: Supplement existing content rather than replacing
- **Change Preview**: Always summarize what will be modified
- **Confirmation**: Ask for clarification if changes are unclear
- **Organization**: Connect new notes to existing notebook structure

#### **Context7**

- **Library Resolution**: Always resolve library ID first unless user provides explicit format
- **Documentation Focus**: Use topic parameter to narrow scope
- **Token Management**: Adjust token count based on complexity (default: 10,000)
- **Fallback**: Use web search if library not found in Context7

#### **Git MCP**

- **Working Directory**: Set with `git_set_working_dir` at start of sessions
- **Status First**: Always check `git_status` before making changes
- **Commit Messages**: Follow conventional commit format per user preferences
- **Workflow**: Use `git_wrapup_instructions` for comprehensive workflows

#### **GitHub MCP**

- **Coordination**: Use after Git MCP for remote operations
- **Search Strategy**: Use code search for examples, issues search for problems
- **PR Creation**: Include detailed descriptions and link to related issues
- **Branch Management**: Create feature branches for significant changes

### 📋 Error Handling & Fallbacks

---

**Tool Failure Strategies:**

- **Filesystem fails**: Check permissions, try different paths
- **Git fails**: Verify repository status, check working directory
- **Web Search fails**: Try different query terms, use Fetch for specific URLs
- **Context7 fails**: Fall back to web search + documentation sites

**Debugging Approach:**

1. Use Sequential Thinking to analyze the problem systematically
2. Check tool responses for specific error messages
3. Verify prerequisites (working directory, file existence, network access)
4. Try alternative tools or approaches
5. Document solutions in Memory for future reference

### 📋 Performance Optimization

---

**Efficiency Guidelines:**

- **Batch Operations**: Combine multiple file operations when possible
- **Context Reuse**: Store frequently accessed information in Memory
- **Tool Switching**: Minimize unnecessary tool transitions
- **Result Caching**: Save intermediate results to avoid recomputation

**Resource Management:**

- **Large Files**: Use Analysis Tool for processing, Filesystem for storage
- **Complex Calculations**: Prefer Analysis Tool over manual computation
- **Documentation**: Create Artifacts for structured content, use Joplin for notes
- **Version Control**: Commit logical units of work, not individual file changes

