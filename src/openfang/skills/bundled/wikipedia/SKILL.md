---
name: wikipedia
description: Search and retrieve Wikipedia articles via the free API.
homepage: https://en.wikipedia.org/api/rest_v1/
metadata:
  { "openfang": { "emoji": "📚", "requires": { "bins": ["curl", "jq"] } } }
---

# Wikipedia

Query Wikipedia's free API for summaries, full articles, and search.

## Quick Summary

Get a brief summary of any topic:

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/page/summary/Python_(programming_language)" | jq '{title, extract}'
```

## Search Articles

Find articles matching a query:

```bash
curl -s "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=artificial+intelligence&format=json" | jq '.query.search[] | {title, snippet}'
```

## Full Article Content

Get full article as HTML:

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/page/html/Linux" | head -100
```

Get as mobile-friendly HTML:

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/page/mobile-html/Linux"
```

## Random Article

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/page/random/summary" | jq '{title, extract}'
```

## Article Sections

Get table of contents:

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/page/mobile-sections/Python_(programming_language)" | jq '.lead.sections[] | {id, line}'
```

## Other Languages

Replace `en.wikipedia.org` with language code:

```bash
# French
curl -s "https://fr.wikipedia.org/api/rest_v1/page/summary/Paris" | jq '{title, extract}'

# German
curl -s "https://de.wikipedia.org/api/rest_v1/page/summary/Berlin" | jq '{title, extract}'

# Japanese
curl -s "https://ja.wikipedia.org/api/rest_v1/page/summary/東京" | jq '{title, extract}'
```

## Related Pages

Get pages that link to an article:

```bash
curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=Python_(programming_language)&prop=links&pllimit=20&format=json" | jq '.query.pages[].links[].title'
```

## Tips

- URL-encode spaces as `_` or `%20`
- Article titles are case-sensitive (first letter capitalized)
- No API key required
- Rate limit: be reasonable (no explicit limit for read operations)
