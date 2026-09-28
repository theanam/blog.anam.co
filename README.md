# Anam's Blog (Jekyll)

Migrated from Ghost 2.28 on 2026-09-28. Every URL the Ghost site served still resolves at the same path.

## Run locally

    bundle install
    bundle exec jekyll serve            # http://localhost:4000
    bundle exec jekyll serve --drafts   # include _drafts/

## Deploy

`.github/workflows/deploy.yml` runs `jekyll build` and publishes `_site/` to GitHub Pages on every
push to `main`, once a day (so future-dated posts appear on their date), and on demand from the
Actions tab. `CNAME` sets the custom domain to blog.anam.co.

## Theme

[jasper2](https://github.com/jekyllt/jasper2) (MIT), a Jekyll port of Ghost's Casper. Its markup is
adapted to this site, and `assets/built/screen.css` is the newer Casper 2.x stylesheet taken from
the live Ghost site (Casper is MIT, © Ghost Foundation), so pages look the same as they did on Ghost.
`assets/custom.css` adds Bangla font fallbacks (Noto Sans Bengali).

jasper2's own tag/author generator plugins are not used: they build `/tag/<name>/page2` URLs, while
Ghost used `/tag/<slug>/page/2/`. Tag and author archives come from `scripts/ghost_to_jekyll.py` instead.

The header cover image is off because the live site's cover (hosted on casper.ghost.org) is broken,
so its header is plain black. Uncomment `cover:` in `_config.yml` to bring back Casper's default cover.

## Layout

- `_posts/` — 45 published posts. Bodies are Ghost's rendered HTML, so they look exactly as they did. New posts can be Markdown (`YYYY-MM-DD-slug.md`).
- `_drafts/` — 8 unpublished Ghost drafts.
- `tag/` — one page per Ghost tag, paginated like Ghost (`/tag/<slug>/page/<n>/`).
- `content/images/` — images, kept at Ghost's original paths.
- `_data/tags.json` — tag slug → display name.
- `scripts/ghost_to_jekyll.py` — the converter. Re-running it overwrites `_posts/`, `_drafts/`, `tag/` and `_data/tags.json`.

## URL mapping

| Ghost | Jekyll |
| --- | --- |
| `/<slug>/` | same (explicit `permalink` in each post) |
| `/<slug>/amp/` | redirect to `/<slug>/` |
| `/page/<n>/` | same (jekyll-paginate, 25 per page) |
| `/tag/<slug>/`, `/tag/<slug>/page/<n>/` | same (every tag, including empty ones) |
| `/author/anam/`, `/author/anam/page/2/` | same |
| `/sitemap.xml` | same (jekyll-sitemap) |
| `/rss/` | HTML redirect to `/feed.xml` (see below) |

## Known gaps

- `/rss/` and `/<slug>/amp/` are meta-refresh redirects. Browsers follow them, but feed readers don't. Add a real 301 at your host (`/rss/ → /feed.xml`) to keep existing RSS subscribers.
- Ghost's split sitemaps (`/sitemap-posts.xml` etc.) are gone; there is a single `/sitemap.xml`. Resubmit it in Search Console.
- Seven images in "Learn CSS3 cubic-bezier…", "Develop for the browser…" and "Fix Google Webfont problem…" were already dead on the live Ghost site (`anam.co/assets/…`, `/sites/all/files/ani.png`).
- The Google Analytics UA tag from Ghost's code injection was not carried over (Universal Analytics has been shut down).
- Subscribers (4 emails) and Ghost members were not migrated.
- Never commit the Ghost export JSON: it contains password hashes, private keys, API secrets and subscriber emails. `.gitignore` excludes it.
