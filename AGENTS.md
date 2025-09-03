# Repository Guidelines

## Project Structure & Modules
- `content/posts/`: Markdown sources (`YYYY-MM-DD-title.md`, with YAML frontmatter).
- `templates/`: Jinja2 templates (`base.html`, `post.html`, `index.html`).
- `scripts/`: Build/deploy/validate tools (Python).
- `assets/` and `images/`: Source CSS and images (copied to `docs/`).
- `docs/`: Generated site for GitHub Pages (do not edit manually).

## Build, Test, and Dev
- `npm run build`: Generate site into `docs/`.
- `npm run serve`: Build and launch local preview server.
- `npm run dev`: Build then serve for development.
- `npm run validate`: Lint article frontmatter, image paths, basics.
- `npm run deploy` / `npm run publish` / `npm run ビルドして公開`: Full build + publish.
- Python direct (after `source venv/bin/activate`): `python scripts/build.py [--serve]`, `python scripts/deploy.py`.

## Coding Style & Naming
- Python: PEP 8, 4-space indent, `snake_case` for files/functions in `scripts/`.
- Templates: Use Jinja2 blocks consistently; keep shared layout in `base.html`.
- Posts: Filename `YYYY-MM-DD-title.md`; image paths like `../images/filename.jpg`.
- Content: YAML frontmatter requires `title`, `date` (YYYY-MM-DD), `category`, `description`; `tags` is a list.

## Testing Guidelines
- Run `npm run validate` before pushing; fix reported errors/warnings.
- Preview locally with `npm run serve` and spot-check links/images.
- Do not commit changes under `docs/` without running a fresh build.

## Commit & Pull Requests
- Commit style examples:
  - New post: `feat(post): add <title>`
  - Post update: `chore(post): update <title> - <change>`
  - System: `refactor(build): <scope>` / `fix(validator): <issue>`
- PRs should include: clear description, linked issues, steps to validate (commands), and screenshots for UI changes.

## Security & Configuration
- No secrets in repo or posts; GitHub Pages publishes from `docs/` only.
- Use `venv` + `pip install -r requirements.txt`; Node >= 14 for npm scripts.
- Large media: commit to `images/`; avoid external hotlinks when possible.

