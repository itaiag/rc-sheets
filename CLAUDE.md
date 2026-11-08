@AGENTS.md

## Claude Code specifics
- Use the Write/Edit tools for code; shell heredocs have mangled quotes and backslashes in this project.
- Long checks (Playwright, Pages build polling) can take minutes; give Bash a long timeout.
