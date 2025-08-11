# Security Review Command

Perform a comprehensive security review of the codebase using available MCP tools. This command helps identify potential vulnerabilities, exposed credentials, and security best practice violations.

## What This Command Does

1. **Credential Scanning**
   - Search for hardcoded API keys, passwords, tokens, and secrets
   - Check for exposed environment variables
   - Identify potential credential patterns in:
     - Configuration files (.env, .config, *.json, *.yaml, *.yml)
     - Source code files
     - Shell scripts and batch files
     - Documentation and comments

2. **Common Vulnerability Patterns**
   - SQL injection risks (string concatenation in queries)
   - Command injection vulnerabilities (shell command execution)
   - Path traversal risks (unchecked file paths)
   - Cross-site scripting (XSS) vulnerabilities
   - Insecure deserialization
   - Hardcoded cryptographic keys

3. **Configuration Security**
   - Review file permissions (when accessible)
   - Check for overly permissive CORS settings
   - Identify debug modes left enabled
   - Find exposed admin interfaces
   - Review authentication configurations

4. **Dependency Analysis**
   - Check for known vulnerabilities in package.json, requirements.txt, etc.
   - Identify outdated dependencies
   - Review license compliance

5. **Best Practice Violations**
   - Missing input validation
   - Lack of output encoding
   - Insecure random number generation
   - Use of deprecated or unsafe functions
   - Missing security headers

## Search Patterns

### Credentials and Secrets
- API keys: `api_key`, `apikey`, `api-key`, `API_KEY`
- Passwords: `password`, `passwd`, `pwd`, `pass`
- Tokens: `token`, `auth_token`, `access_token`, `bearer`
- Secrets: `secret`, `private_key`, `priv_key`
- Database: `db_password`, `database_url`, `connection_string`
- AWS: `aws_access_key_id`, `aws_secret_access_key`
- Common patterns: Base64 encoded strings, JWT tokens, OAuth credentials

### Vulnerability Indicators
- SQL: `"SELECT * FROM" +`, `execute(query +`, `raw(`
- Command injection: `exec(`, `system(`, `eval(`, `subprocess`
- Path traversal: `../`, `..\\`, unchecked file operations
- Unsafe functions: `eval()`, `exec()`, `innerHTML`, `dangerouslySetInnerHTML`

## How to Use

1. Run `/security-review` to perform a full security scan
2. Review the findings organized by severity (Critical, High, Medium, Low)
3. Use Memory MCP to track security issues and remediation progress
4. For each finding, the review will provide:
   - Location (file and line number if available)
   - Description of the vulnerability
   - Potential impact
   - Recommended fix

## Example Output Format

```
🔒 SECURITY REVIEW RESULTS
========================

🚨 CRITICAL (2 issues)
---------------------
1. Hardcoded API Key
   File: config/api.js:15
   Pattern: `const API_KEY = "sk-1234567890abcdef"`
   Impact: Exposed credentials could lead to unauthorized API access
   Fix: Move to environment variables or secure credential storage

2. SQL Injection Risk
   File: routes/users.js:42
   Pattern: `db.query("SELECT * FROM users WHERE id = " + userId)`
   Impact: Potential database compromise
   Fix: Use parameterized queries

⚠️ HIGH (3 issues)
------------------
[Additional findings...]

📊 SUMMARY
----------
- Files scanned: 142
- Critical issues: 2
- High severity: 3
- Medium severity: 7
- Low severity: 12
- Recommended actions: Fix critical issues immediately
```

## Important Notes

- This tool uses pattern matching and may produce false positives
- Always verify findings in context before making changes
- Some security issues require manual code review to identify
- Consider using additional specialized security tools for production systems
- Store security review results in Memory for tracking remediation progress