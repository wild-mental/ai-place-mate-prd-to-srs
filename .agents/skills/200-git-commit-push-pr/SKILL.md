---
name: 200-git-commit-push-pr
description: Git commit, push, and Pull Request best practices for team collaboration and AI agent safety
---
# Git Commit, Push, and PR Rules

## Atomic Commits
- One logical change per commit (single purpose, fully functional)
- Ensure each commit compiles and passes tests
- Use `git add -p` for selective staging, avoid mixing unrelated changes
- Write descriptive commit messages explaining WHY, not just WHAT

## Commit Message Format
- Use Conventional Commits: `<type>(<scope>): <subject>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`, `perf`
- Subject: imperative mood, lowercase, no period, max 50 chars
- Body (optional): detailed explanation, wrap at 72 chars
- Footer (optional): reference issues with `Closes #123` or `Refs #456`

## Branch Strategy
- ALWAYS create issue-specific branch before starting work
- Branch naming: `<type>/<issue-number>-<short-description>`
  - Examples: `feat/123-user-auth`, `fix/456-payment-bug`, `docs/789-api-guide`
- Push branch to remote immediately: `git push -u origin <branch-name>`
- Never commit directly to `main`, `master`, or `dev` branches

## AI Agent Safety Rules
- Run `git status` and `git diff` before any commit
- Verify correct branch with `git branch --show-current`
- Use `--no-verify` ONLY when explicitly requested by user
- NEVER force push (`--force`, `-f`) without explicit user confirmation
- Check remote connection before push: `git ls-remote`
- Confirm credentials are valid before attempting push operations

## Team Collaboration
- Pull latest changes before starting: `git pull origin <branch>`
- Rebase feature branches on main regularly to avoid conflicts
- Create draft PR immediately after first push: `gh pr create --draft`
- **PR Description must include:**
  - Summary of changes: **Analyze the full git diff between branches** and summarize the *semantic meaning* of all changes.
  - Ensure the summary covers all key modifications but remains concise (avoid verbose file listings).
  - Link to related issues
- Request reviews before merging; never self-merge without approval

## This Project

- **브랜치 이름에 이슈 번호를 넣는다** — `feat/12-tec-001-app-scaffold`.
  GitHub Project #25가 이슈 단위로 돌기 때문에 번호가 없으면 추적이 끊긴다.
  태스크 ID ↔ 이슈 번호는 `tools/issue_map.json`에 있다.
- **커밋 메시지는 한국어로 쓴다.** 이 저장소의 문서가 한국어다.
  제목은 Conventional Commits 형식을 유지한다 — `feat: 압축 수행 일정 문서 추가`
- **본문에 왜를 쓴다.** 무엇을 바꿨는지는 diff가 말한다.
  판단이 갈릴 수 있었던 지점, 대안을 버린 이유, 놓치면 조용히 깨지는 것을 적는다.
- **PR은 draft로 먼저 연다.** 본문에 `Closes #<번호>`를 넣어야 머지 시 이슈가 닫힌다.
- **생성물을 직접 편집한 커밋을 만들지 않는다.**
  `docs/plan-docs/[TaskList]...`·`[Plan]...`은 `tools/`의 생성기 산출물이다.
  원천(`tools/tasks_data.py`)을 고치고 생성기를 다시 돌린 결과를 커밋한다.
- **문서를 옮기거나 이름을 바꿨으면** `python3 tools/verify_links.py`를 돌린다.
  링크는 조용히 깨지고 렌더링은 멀쩡해 보인다.

## Examples
<example>
# Good: Atomic commit with clear message
git add src/auth/login.ts src/auth/login.test.ts
git commit -m "feat(auth): implement JWT token validation

- Add token expiry checking logic
- Include refresh token rotation
- Add unit tests for edge cases

Closes #234"
</example>

<bad-example>
# Bad: Mixed changes, vague message
git add .
git commit -m "updates"
git push origin main  # ❌ Pushing to main directly
</bad-example>