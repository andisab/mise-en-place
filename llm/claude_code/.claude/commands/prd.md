# Claude Command: PRD
This command helps you create a detailed and consistently-structured Product or Project Requirements Document (PRD). This is a sensible place to begin when just starting out a project or feature development.

## Usage
To create a PRD from resources currently available in the project, just type:
```
/prd
```

Or with options:
```
/prd --prompt "Create a new user authentication system"
/prd --doc "temp/feature-notes.md"
/prd --directory "docs/"
```

## What This Command Does

1. **Initial Prompt Processing**: Receives a brief description or request for a new feature/functionality
2. **Clarification Phase**: Asks structured clarifying questions across four key areas (Business, UX, Technical, Scope)
3. **PRD Generation**: Creates a comprehensive requirements document using the standard PRD template
4. **File Management**: Saves the document with proper naming in the appropriate directory
5. **Workflow Management**: Guides between PLAN mode (requirements gathering) and CODE mode (implementation ready)

## Goal

Create detailed Product Requirements Documents (PRDs) that are clear, actionable, and suitable for junior developers to understand and implement. Focus on the "what" and "why" of features, not implementation details.

## Clarifying Questions Framework

The AI should ask structured clarifying questions across four key categories. Questions marked with ⭐ are required; others are optional based on feature complexity.

### Business Context (Required)
⭐ **Problem/Goal**: "What problem does this feature solve for users?"
   - A) User pain point or frustration
   - B) Business opportunity or efficiency gain  
   - C) Competitive requirement or market demand

⭐ **Target User**: "Who is the primary user of this feature?"
   - A) End users (customers/clients)
   - B) Internal users (employees/admins)
   - C) External partners or stakeholders

**Success Metrics**: "How will success be measured?" (Choose 1-2)
   - A) User engagement metrics (clicks, time spent, retention)
   - B) Business metrics (revenue, conversions, efficiency)
   - C) Technical metrics (performance, error rates)

### User Experience (Required)
⭐ **Core Functionality**: "What are the 3 most important actions users should be able to perform?"
   - List in priority order with expected frequency of use

⭐ **User Stories**: "Provide 2-3 user stories in this format:"
   - As a [user type], I want to [action] so that [benefit]

**Design/UI Requirements**: "Are there specific UI/UX considerations?"
   - A) Follow existing design system/patterns
   - B) Create new design patterns
   - C) Reference specific mockups or examples

### Technical Requirements (Optional)
**Data Requirements**: "What data does this feature need to handle?"
   - A) User-generated content
   - B) System/application data
   - C) External API or service data

**Integration Points**: "Does this feature need to integrate with existing systems?"
   - List any known dependencies or connections
   - List frameworks or technologies to be used, if they are known. 

**Performance Considerations**: "Are there specific performance requirements?"
   - A) Response time expectations
   - B) Scalability requirements
   - C) Offline/connectivity considerations

### Scope & Boundaries (Required)
⭐ **Acceptance Criteria**: "What are the key success criteria?" (List 3-5 specific, testable conditions)

⭐ **Non-Goals**: "What should this feature NOT include?" (Important for scope management)

**Edge Cases**: "Are there important edge cases or error conditions to consider?"
   - A) Invalid input handling
   - B) Network/connectivity issues
   - C) Permission/authorization scenarios

## Command Options

- `--prompt "description"`: Provide an initial feature description to start the PRD process
- `--doc "path/to/file.md"`: Reference an existing document with additional context or requirements
- `--directory "target/path"`: Specify resources in a directory to reference. This should also be the directory to save the PRD in (overrides default precedence). 

**Default Behavior:**
- Without options: Prompts for initial feature description interactively
- Directory precedence: `/docs` → `/temp` → `/tasks` → current directory
- File naming: `prd-[feature-name].md` (sanitized, lowercase, hyphenated)

## PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., "The system must allow users to upload a profile picture."). Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
7.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions (e.g., "Should integrate with the existing Auth module").
8.  **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", "Reduce support tickets related to X").
9.  **Open Questions:** List any remaining questions or areas needing further clarification.

## Sample PRD Output

Here's an example of what a completed PRD should look like:

```markdown
# PRD: User Authentication System

## Introduction/Overview
This feature implements a secure user authentication system to allow users to create accounts, log in, and manage their profiles. The goal is to provide a reliable, secure foundation for user access control across the platform.

## Goals
1. Enable user account creation and management
2. Provide secure login/logout functionality
3. Implement password reset capabilities
4. Establish role-based access control foundation

## User Stories
- As a new user, I want to create an account so that I can access personalized features
- As a returning user, I want to log in quickly so that I can continue using the platform
- As a user who forgot my password, I want to reset it so that I can regain access to my account

## Functional Requirements
1. The system must allow users to register with email and password
2. The system must validate email addresses during registration
3. The system must enforce password strength requirements (8+ chars, mixed case, numbers)
4. The system must send email verification for new accounts
5. The system must provide secure login with rate limiting
6. The system must implement password reset via email
7. The system must maintain user sessions securely
8. The system must allow users to update their profile information

## Non-Goals (Out of Scope)
- Social media login integration (Phase 2)
- Two-factor authentication (Phase 2)
- Advanced role management UI (Phase 2)
- Account suspension/deactivation workflows

## Design Considerations
- Follow existing design system patterns for forms and buttons
- Implement responsive design for mobile compatibility
- Use consistent error messaging patterns
- Ensure accessibility compliance (WCAG 2.1 AA)

## Technical Considerations
- Integrate with existing user database schema
- Use bcrypt for password hashing
- Implement JWT tokens for session management
- Follow OWASP security guidelines for authentication

## Success Metrics
- 95% successful registration completion rate
- < 2 second login response time
- < 1% user support tickets related to authentication
- Zero security incidents in first 30 days

## Open Questions
- Should we implement "Remember Me" functionality in Phase 1?
- What should be the session timeout duration?
- Do we need admin approval for new user registrations?
```

## Example Clarification Flow

Here's how the clarification process should work:

**User Initial Prompt:** "I need a feature for users to save their favorite items"

**AI Response:**
```
I'll help you create a PRD for a favorites feature. Let me ask some clarifying questions to ensure we build the right solution.

**Business Context (Required)**
⭐ What problem does this feature solve for users?
   A) Users lose track of items they're interested in
   B) Users want to compare items later
   C) Users need to share interesting items with others

⭐ Who is the primary user of this feature?
   A) End users browsing your catalog
   B) Internal users managing content
   C) External partners or affiliates

**User Experience (Required)**
⭐ What are the 3 most important actions users should perform with favorites?
   Please list in priority order with expected frequency.

⭐ Please provide 2-3 user stories in this format:
   - As a [user type], I want to [action] so that [benefit]

Would you like me to continue with Technical Requirements and Scope questions after these, or do you have specific answers for these first?
```

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output Format

*   **Format:** Markdown (`.md`)
*   **Location:** Uses `--directory` option or default precedence (see Command Options above)
*   **Filename:** `prd-[feature-name].md`

## Workflow Instructions

### PLAN Mode (Requirements Gathering)
1. **Start in PLAN mode** until all required clarifying questions are answered
2. **Ask questions systematically** by category (Business → UX → Technical → Scope)
3. **Provide numbered/lettered options** for easier user responses
4. **Confirm understanding** before proceeding to PRD generation

### CODE Mode (PRD Generation)
1. **Switch to CODE mode** only when requirements are complete
2. **Generate comprehensive PRD** using the established template structure
3. **Save file** with proper naming in appropriate directory
4. **Do NOT implement the feature** - only create the requirements document

### Best Practices
- Focus on "what" and "why", not "how" (implementation details)
- Keep requirements testable and measurable
- Include acceptance criteria that can be validated
- Ask follow-up questions if any answers are unclear
- Prioritize user value and business impact in requirements

## Important Notes

### Integration with Other Commands
- If working in an existing project, consider running `/prime` first to understand project context and existing architecture
- Reference existing project patterns and conventions where applicable 

### File Management
- Always check if target directory exists before saving
- If a PRD with same/similar name already exists, ask user if they want to overwrite it

### Limitations
- This command creates requirements documents only - does not implement features
- Requires user interaction for clarifying questions - cannot auto-generate without input
