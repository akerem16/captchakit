# Renderers

`captchakit` ships three renderers out of the box. They all implement
the same `Renderer` protocol (`content_type` + `async def render`), so
you can swap them without touching the manager.

| Renderer         | Output        | Deps    | Use when                          |
| ---------------- | ------------- | ------- | --------------------------------- |
| `ImageRenderer`  | PNG bytes     | Pillow  | default, universal                |
| `SVGRenderer`    | SVG bytes     | stdlib  | HD screens, smaller payload       |
| `AudioRenderer`  | WAV bytes     | stdlib  | accessibility alternative         |

## `SVGRenderer`

```python
from captchakit import SVGRenderer, Theme

renderer = SVGRenderer(
    width=220,
    height=80,
    font_size=40,
    theme=Theme.DARK,
    font_family="sans-serif",
)
```

- Pure Python string templating — no Pillow dependency.
- Typical payload is ~1 kB (vs ~4–8 kB for the equivalent PNG).
- Scales losslessly on high-DPI screens.
- Reuses the same `Theme` palette / noise settings as `ImageRenderer`.

Serve as `Content-Type: image/svg+xml`. Browsers render it inline inside
an `<img>` tag just like a PNG.

## Picking the right renderer

- **Default** → `ImageRenderer`. Max compatibility; every email client,
  image widget and ancient browser can display it.
- **Mobile-first or HD webapps** → `SVGRenderer`. Smaller over-the-wire,
  crisp at any zoom level.
- **Accessibility** → always pair one of the visual renderers with
  `AudioRenderer` (see [Audio](audio.md)).

## Bring your own

Implement the `Renderer` protocol — a content type plus an async
`render(challenge) -> bytes`:

```python
class QRRenderer:
    content_type = "image/png"
    async def render(self, challenge):
        import qrcode, io
        buf = io.BytesIO()
        qrcode.make(challenge.prompt).save(buf, format="PNG")
        return buf.getvalue()
```
