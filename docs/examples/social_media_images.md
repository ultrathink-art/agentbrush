# Social Media Images

Workflows for creating social media assets with AgentBrush.

## Open Graph Images (1200x630)

Link preview images for Twitter, Facebook, Slack, Discord, etc.

```bash
# Create OG image from existing artwork
agentbrush resize artwork.png og_image.png --width 1200 --height 630 --pad

# Validate
agentbrush validate check og_image.png --preset social-og
```

### With text overlay:

```python
from agentbrush import remove_background, paste_centered, add_text, validate_design

# Remove background from logo/artwork
result = remove_background("logo.png", "logo_clean.png", color="white")

# Center on OG canvas with dark background
result = paste_centered(
    1200, 630, "logo_clean.png", "og_base.png",
    fit=True, bg_color=(20, 20, 30, 255),
)

# Add title text
result = add_text(
    "og_base.png", "og_final.png",
    text="My Project Name",
    position=(600, 500),
    font_name="mono-bold", font_size=48,
    color=(255, 255, 255, 255),
)

# Validate dimensions
result = validate_design("og_final.png", preset="social-og")
assert result.success, result.summary()
```

## Square Posts (1080x1080)

Instagram, social media square format:

```bash
# Resize to square with padding
agentbrush resize photo.png square_post.png --width 1080 --height 1080 --pad

# Or fit within square (letterboxed)
agentbrush resize photo.png square_post.png --width 1080 --height 1080 --fit --pad

# Validate
agentbrush validate check square_post.png --preset social-square
```

## Stories / Vertical (1080x1920)

```bash
agentbrush resize artwork.png story.png --width 1080 --height 1920 --pad
agentbrush validate check story.png --preset social-story
```

## Favicons (32x32)

```bash
# Resize logo to favicon
agentbrush resize logo.png favicon.png --width 32 --height 32

# Validate
agentbrush validate check favicon.png --preset favicon
```

## App Icons

```bash
# iOS (1024x1024, no transparency)
agentbrush resize logo.png icon_ios.png --width 1024 --height 1024 --pad
agentbrush validate check icon_ios.png --preset icon-ios

# Android (512x512, transparency OK)
agentbrush resize logo.png icon_android.png --width 512 --height 512 --pad
agentbrush validate check icon_android.png --preset icon-android
```

## Profile Avatars (256x256)

```bash
# Create avatar from photo
agentbrush remove-bg headshot.png headshot_clean.png --color white
agentbrush resize headshot_clean.png avatar.png --width 256 --height 256 --pad
agentbrush validate check avatar.png --preset avatar
```

## Banners (1920x480)

```bash
agentbrush resize panorama.png banner.png --width 1920 --height 480 --fit --pad
agentbrush validate check banner.png --preset banner
```

## Batch Processing

Process multiple images against the same preset:

```python
from pathlib import Path
from agentbrush import resize_image, validate_design

source_dir = Path("raw_photos")
output_dir = Path("og_images")
output_dir.mkdir(exist_ok=True)

for src in source_dir.glob("*.png"):
    out = output_dir / src.name
    resize_image(str(src), str(out), width=1200, height=630, pad=True)
    result = validate_design(str(out), preset="social-og")
    status = "OK" if result.success else "FAIL"
    print(f"{status}: {src.name}")
```
