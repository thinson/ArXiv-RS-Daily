# Contributing

Thanks for your interest in improving this project.

## Quick rules

- Keep secrets out of code (use env vars only).
- Keep changes small and focused.
- Preserve output compatibility when possible.
- Add a short test/repro step in PR description.

## Development flow

1. Fork and create a feature branch.
2. Make your changes.
3. Run a local sanity check:
   - `python3 scripts/daily_arxiv_cross_filter.py --dry-run --days 1`
   - `python3 scripts/daily_digest_llm_upgrade.py --date YYYYMMDD`
4. Update docs if behavior changed.
5. Open a PR with:
   - What changed
   - Why it changed
   - How you tested

## Suggested areas

- Better filtering quality
- More robust LLM parsing/retries
- Digest quality checks
- Better observability/logging

## Security

If you find a security issue, please report privately before opening a public issue.
