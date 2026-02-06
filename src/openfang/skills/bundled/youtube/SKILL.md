---
name: youtube
description: Get YouTube video info, transcripts, and download audio/video via yt-dlp.
homepage: https://github.com/yt-dlp/yt-dlp
metadata:
  {
    "openfang":
      {
        "emoji": "▶️",
        "requires": { "bins": ["yt-dlp"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "yt-dlp",
              "bins": ["yt-dlp"],
              "label": "Install yt-dlp (brew)",
            },
            {
              "id": "pip",
              "kind": "pip",
              "package": "yt-dlp",
              "bins": ["yt-dlp"],
              "label": "Install yt-dlp (pip)",
            },
          ],
      },
  }
---

# YouTube

Use `yt-dlp` to get video info, transcripts, and download media.

## Video Information

Get video metadata as JSON:

```bash
yt-dlp --dump-json "https://youtube.com/watch?v=VIDEO_ID" | jq '{title, duration, view_count, upload_date, description}'
```

Quick info (no download):

```bash
yt-dlp --print "%(title)s [%(duration_string)s]" "URL"
```

## Transcripts / Subtitles

List available subtitles:

```bash
yt-dlp --list-subs "URL"
```

Download auto-generated subtitles:

```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download -o "%(title)s" "URL"
```

Download manual subtitles:

```bash
yt-dlp --write-sub --sub-lang en --skip-download -o "%(title)s" "URL"
```

Convert to plain text (SRT to TXT):

```bash
yt-dlp --write-auto-sub --sub-lang en --convert-subs srt --skip-download "URL"
# Then: sed 's/<[^>]*>//g' file.en.srt | grep -v '^[0-9]' | grep -v '^$' | tr '\n' ' '
```

## Download Audio

Best audio only (for podcasts, music):

```bash
yt-dlp -x --audio-format mp3 "URL"
```

With metadata:

```bash
yt-dlp -x --audio-format mp3 --embed-thumbnail --add-metadata "URL"
```

## Download Video

Best quality:

```bash
yt-dlp "URL"
```

Specific quality:

```bash
# 1080p max
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" "URL"

# 720p
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" "URL"
```

List available formats:

```bash
yt-dlp -F "URL"
```

## Playlists

Download entire playlist:

```bash
yt-dlp -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

Just list videos (no download):

```bash
yt-dlp --flat-playlist --print "%(title)s | %(url)s" "PLAYLIST_URL"
```

## Channels

Download recent videos:

```bash
yt-dlp --playlist-end 10 "CHANNEL_URL"
```

## Search

Search YouTube and get first result:

```bash
yt-dlp --default-search "ytsearch" --print "%(title)s | %(webpage_url)s" "search query"
```

Search multiple results:

```bash
yt-dlp --default-search "ytsearch5" --print "%(title)s | %(webpage_url)s" "search query"
```

## Output Templates

Custom filename:

```bash
yt-dlp -o "%(upload_date)s - %(title)s.%(ext)s" "URL"
```

Available fields: `title`, `id`, `upload_date`, `duration`, `view_count`, `channel`, `playlist_title`, `playlist_index`

## Tips

- Works with YouTube, Vimeo, Twitter, TikTok, and 1000+ sites
- Use `--cookies-from-browser chrome` for age-restricted content
- Add `--no-warnings` for cleaner output
- Use `--simulate` or `-s` to test without downloading
