# Themes

The `ImageRenderer` accepts a `Theme` that bundles background colour,
glyph palette, noise density and optional font.

## Built-in presets

```python
from captchakit import ImageRenderer, Theme

ImageRenderer(theme=Theme.CLASSIC)       # default
ImageRenderer(theme=Theme.DARK)          # dark canvas, pastel glyphs
ImageRenderer(theme=Theme.PASTEL)        # warm, low-contrast
ImageRenderer(theme=Theme.HIGH_CONTRAST) # WCAG AA: black on white, no noise
```

- `HIGH_CONTRAST` is the accessibility-friendly default for users with
  low vision. It removes decorative noise lines entirely.
- `DARK` is suited for dark-mode UIs; it uses a near-black background
  and light-on-dark glyphs.

## Custom theme

`Theme` is a frozen dataclass:

```python
from captchakit import ImageRenderer, Theme

brand = Theme(
    bg_color=(250, 240, 220),
    palette=(
        (110, 70, 20),
        (170, 100, 30),
        (200, 130, 40),
    ),
    noise_lines=3,
    font_path="/fonts/MyBrand-Bold.ttf",
)

renderer = ImageRenderer(width=260, height=90, theme=brand)
```

| Field         | Default                           | Notes                         |
| ------------- | --------------------------------- | ----------------------------- |
| `bg_color`    | `(245, 245, 245)` light gray      | RGB tuple                     |
| `palette`     | 5 muted colours                   | At least one entry required   |
| `noise_lines` | `4`                               | `0` disables decorative noise |
| `font_path`   | `None` (Pillow default)           | TrueType file path            |

The renderer's own `font_path` argument still wins over the theme's —
use it to override the theme bundle without redefining the colours.
