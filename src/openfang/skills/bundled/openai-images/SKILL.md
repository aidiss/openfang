---
name: openai-images
description: Generate images via OpenAI's DALL-E and GPT Image APIs.
homepage: https://platform.openai.com/docs/api-reference/images
metadata:
  {
    "openfang":
      {
        "emoji": "🎨",
        "requires": { "bins": ["curl", "jq"], "env": ["OPENAI_API_KEY"] },
        "primaryEnv": "OPENAI_API_KEY",
      },
  }
---

# OpenAI Image Generation

Generate images using DALL-E 3, DALL-E 2, or GPT Image models.

## Generate Image (DALL-E 3)

```bash
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A white siamese cat",
    "n": 1,
    "size": "1024x1024"
  }' | jq -r '.data[0].url'
```

Download the image:

```bash
URL=$(curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A futuristic cityscape at sunset",
    "n": 1,
    "size": "1792x1024",
    "quality": "hd"
  }' | jq -r '.data[0].url')

curl -s "$URL" -o image.png
```

## DALL-E 3 Options

| Parameter | Values | Default |
|-----------|--------|---------|
| size | `1024x1024`, `1792x1024`, `1024x1792` | `1024x1024` |
| quality | `standard`, `hd` | `standard` |
| style | `vivid`, `natural` | `vivid` |
| n | `1` only | `1` |

HD quality example:

```bash
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "Detailed oil painting of a mountain landscape",
    "size": "1792x1024",
    "quality": "hd",
    "style": "natural"
  }' | jq -r '.data[0].url'
```

## DALL-E 2

Supports multiple images per request:

```bash
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-2",
    "prompt": "A cute robot",
    "n": 4,
    "size": "512x512"
  }' | jq -r '.data[].url'
```

DALL-E 2 sizes: `256x256`, `512x512`, `1024x1024`

## Image Variations (DALL-E 2 only)

Create variations of an existing image:

```bash
curl -s https://api.openai.com/v1/images/variations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F image="@original.png" \
  -F n=2 \
  -F size="1024x1024" | jq -r '.data[].url'
```

## Image Edits (DALL-E 2 only)

Edit an image with a mask:

```bash
curl -s https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F image="@original.png" \
  -F mask="@mask.png" \
  -F prompt="A sunlit indoor lounge area with a pool" \
  -F n=1 \
  -F size="1024x1024" | jq -r '.data[0].url'
```

## Base64 Response

Get image as base64 instead of URL:

```bash
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A simple icon",
    "response_format": "b64_json"
  }' | jq -r '.data[0].b64_json' | base64 -d > image.png
```

## Tips

- DALL-E 3 revises prompts automatically; check `revised_prompt` in response
- URLs expire after 1 hour; download images immediately
- Use descriptive, detailed prompts for better results
