# Anam's Blog (Jekyll)

Migrated from Ghost 2.28 on 2026-09-28. Every URL the Ghost site served still resolves at the same path.

## Run locally

    bundle install
    npm install                         # image optimiser; also turns on the pre-commit hook
    bundle exec jekyll serve            # http://localhost:4000
    bundle exec jekyll serve --drafts   # include _drafts/

## Images

Images are shrunk automatically so pages stay fast. `scripts/optimize-images.mjs` (using sharp):

- scales anything wider than 2000px down to 2000px,
- re-encodes JPEG (mozjpeg, quality 80), PNG (palette, quality 90) and WebP (quality 80),
- applies EXIF rotation and strips metadata, including camera and GPS details,
- only rewrites a file if it gets at least 5% smaller, so optimised images are never recompressed.

It runs in two places:

1. **Pre-commit hook** (`.githooks/pre-commit`): new or changed images are optimised in place and
   re-staged before each commit. `npm install` switches the hook on (`core.hooksPath`), so do that
   once after every clone. HEIC files are refused; export them as JPEG.
2. **Deploy workflow**: `npm run optimize-images -- --all` runs before `jekyll build`, so the live site
   is optimised even if a commit skipped the hook (`--no-verify`, or a machine without `npm install`).

To check what it would do: `npm run optimize-images -- --all --check`.

## Deploy

`.github/workflows/deploy.yml` runs `jekyll build` and publishes `_site/` to GitHub Pages on every
push to `main`, once a day (so future-dated posts appear on their date), and on demand from the
Actions tab.

### Domain

**`anam.co` is the blog's domain.** Set it in GitHub under Settings → Pages → Custom domain;
with an Actions deploy, GitHub ignores the repo's `CNAME` file. DNS is on Cloudflare: `anam.co`
has A records for GitHub Pages (185.199.108–111.153), DNS-only until GitHub issues the certificate.

`blog.anam.co` is the old Ghost address, and every old post link points there. It redirects to
`anam.co` at Cloudflare; GitHub never sees it (a Pages site gets a certificate for only one domain,
which is why pointing `blog.anam.co` at GitHub gives an SSL error). Set up in Cloudflare:

1. DNS: `AAAA blog 100::`, **proxied** (orange cloud). `100::` is a placeholder for redirect-only hosts.
2. Redirect rule, first: hostname `blog.anam.co` and path `/rss/` → static `https://anam.co/feed.xml`, 301.
   This keeps existing RSS subscribers working.
3. Redirect rule: hostname `blog.anam.co` → dynamic `concat("https://anam.co", http.request.uri.path)`,
   301, preserve query string.

Check with `curl -sI https://blog.anam.co/docker-in-bangla/ | grep -i location`.

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
