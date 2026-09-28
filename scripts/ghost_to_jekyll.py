#!/usr/bin/env python3
"""Convert a Ghost 2.x JSON export into Jekyll posts, tag pages and data files.

Usage: python3 scripts/ghost_to_jekyll.py path/to/export.json

Only posts, tags and a few public settings are read. The export also holds
password hashes, private keys, API secrets and subscriber emails, so it is
never copied into the site.
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

PER_PAGE = 25  # Casper's posts_per_page, matches the live site
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def yaml_str(value):
    # JSON strings are valid YAML scalars and escape everything we need.
    return json.dumps(value, ensure_ascii=False)


def ghost_date(value):
    # Ghost stores timestamps in UTC as "YYYY-MM-DD HH:MM:SS".
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def excerpt(post):
    if post.get("custom_excerpt"):
        return post["custom_excerpt"].strip()
    # Ghost's default excerpt: the first 33 words of the post with tags stripped.
    # (The export's "plaintext" field keeps markdown noise like "> " from quotes.)
    text = html.unescape(re.sub(r"<[^>]+>", " ", post.get("html") or ""))
    return " ".join(text.split()[:33])


def main(export_path):
    with open(export_path, encoding="utf-8") as fh:
        data = json.load(fh)["db"][0]["data"]

    tags = {t["id"]: t for t in data["tags"]}
    post_tags = {}
    for pt in sorted(data["posts_tags"], key=lambda r: r["sort_order"]):
        post_tags.setdefault(pt["post_id"], []).append(tags[pt["tag_id"]]["slug"])

    for folder in ("_posts", "_drafts", "tag"):
        os.makedirs(os.path.join(ROOT, folder), exist_ok=True)

    tag_counts = {}
    site_title = next(r["value"] for r in data["settings"] if r["key"] == "title")
    report = []
    for post in data["posts"]:
        if post["type"] != "post":
            continue
        published = post["status"] == "published"
        slug = post["slug"]
        date = ghost_date(post["published_at"] or post["created_at"])
        slugs = post_tags.get(post["id"], [])
        if published:
            for t in slugs:
                tag_counts[t] = tag_counts.get(t, 0) + 1

        front = [
            "---",
            f"title: {yaml_str(post['title'])}",
            f"date: {date.strftime('%Y-%m-%d %H:%M:%S +0000')}",
            f"permalink: /{slug}/",
            f"slug: {yaml_str(slug)}",
            f"ghost_id: {yaml_str(post['id'])}",
            f"tags: {yaml_str(slugs)}",
            f"excerpt: {yaml_str(excerpt(post))}",
        ]
        if post.get("feature_image"):
            front.append(f"image: {yaml_str(post['feature_image'])}")
        if post.get("featured"):
            front.append("featured: true")
        if post.get("updated_at"):
            front.append(f"last_modified_at: {ghost_date(post['updated_at']).strftime('%Y-%m-%d %H:%M:%S +0000')}")
        # Ghost served AMP copies at /<slug>/amp/; send those visitors to the post.
        front.append(f"redirect_from:\n  - /{slug}/amp/")
        # Post bodies are Ghost's rendered HTML and may contain {{ or {% in code samples.
        front.append("render_with_liquid: false")
        front.append("---")

        body = post.get("html") or ""
        if published:
            path = os.path.join(ROOT, "_posts", f"{date.strftime('%Y-%m-%d')}-{slug}.html")
        else:
            path = os.path.join(ROOT, "_drafts", f"{slug}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(front) + "\n" + body + "\n")
        report.append((post["status"], slug, len(body)))

    # Tag data, plus a page for every tag. Ghost answers 200 even for tags with
    # no posts, and paginates tag archives at /tag/<slug>/page/<n>/.
    with open(os.path.join(ROOT, "_data", "tags.json"), "w", encoding="utf-8") as fh:
        json.dump({t["slug"]: {"name": t["name"], "description": t["description"]}
                   for t in data["tags"]}, fh, ensure_ascii=False, indent=2)
    for tag in data["tags"]:
        slug = tag["slug"]
        pages = max(1, -(-tag_counts.get(slug, 0) // PER_PAGE))
        for num in range(1, pages + 1):
            url = f"/tag/{slug}/" if num == 1 else f"/tag/{slug}/page/{num}/"
            folder = os.path.join(ROOT, url.strip("/"))
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as fh:
                title = f"{tag['name']} - {site_title}" + (f" (Page {num})" if num > 1 else "")
                fh.write(f"---\nlayout: tag\ntitle: {yaml_str(title)}\ntag: {yaml_str(slug)}\npermalink: {url}\n"
                         f"page_num: {num}\ntotal_pages: {pages}\n"
                         f"redirect_from:\n  - {url}amp/\n---\n")

    for status, slug, size in sorted(report):
        print(f"{status:10} {size:7} {slug}")
    print(f"{len(data['tags'])} tags")


if __name__ == "__main__":
    main(sys.argv[1])
