# digivatar-pixel-assembly

A WebGL tool that explodes your native pixel art into 3D spinning cubes — then assembles them back into the full image as the viewer scrolls.

Built by [Digivatar](https://github.com/Master-Zomon) — avant-garde digital visual world-building and music artist.

**[→ Live Demo](https://master-zomon.github.io/digivatar-pixel-assembly/digivatar_webgl.html)**

---

## What it does

Drop in any native-resolution pixel art PNG with a transparent background. The tool converts every visible pixel into a 3D cube with its exact color. On load, the cubes are scattered in world space — flying toward the camera, spinning freely. As the viewer scrolls, they converge and lock into the pixel art portrait.

No libraries. No dependencies. One HTML file, one Python script to encode your art.

---

## Requirements

- Python 3
- Pillow: `pip install Pillow`
- A browser with WebGL support (all modern browsers)

---

## How to use it

### 1. Prepare your pixel art

Export your pixel art as a **PNG with transparent background** at its **native pixel resolution** — do not upscale it. The tool reads each pixel at 1:1 and maps it to a cube. Upscaling adds interpolated pixels that blur the effect.

If your art has a background color rather than transparency, remove it in Photoshop, Aseprite, or any pixel editor before exporting.

### 2. Encode your art

Run `encode.py` with your PNG:

```bash
python encode.py your_art.png
```

This reads every non-transparent pixel, packs position, color, and randomized explosion offsets into a compact binary blob, and outputs a new `output.html` ready to open in any browser.

That's it. No manual editing required.

### 3. Open in browser

Open `output.html` directly in Chrome or Firefox. Scroll down to assemble, scroll up to explode.

---

## Parameters

All tunable values are at the top of the script and commented. You do not need to touch the HTML or GLSL.

### Scatter / explosion

| Parameter | Default | What it does |
|---|---|---|
| `SCATTER_XY` | `8000` | World-space radius of XY scatter. Higher = cubes fly further off screen when exploded. |
| `SCATTER_Z` | `2800` | How far cubes push toward the camera when exploded. Higher = closer to lens, appear larger. |
| `SPIN_AMOUNT` | `π × 3` | How much each cube rotates during flight. Higher = more chaotic spin. |

### Assembly feel

| Parameter | Default | What it does |
|---|---|---|
| `SCROLL_SPEED` | `0.0004` | How much scroll progress per scroll tick. Lower = more scroll needed to complete assembly. |
| `LERP_SPEED` | `0.055` | How fast the animation chases scroll position. Lower = more fluid/laggy feel. Higher = snappier. |
| `SNAP_THRESHOLD` | `0.001` | How close to target before locking to final state. Prevents endless micro-animation. |

### Assembled image

| Parameter | Default | What it does |
|---|---|---|
| `VIEWPORT_FILL` | `0.82` | How much of the viewport the assembled image fills. 1.0 = edge to edge. |
| `CUBE_SIZE_ASSEMBLED` | `0.505` | Pixel cube size at assembled state relative to grid cell. Below 0.5 adds gap between pixels. Above 0.5 = overlap. |
| `CUBE_SIZE_EXPLODED` | `8.0` | Cube size multiplier when fully exploded. Higher = bigger cubes near camera. |

### Visual

| Parameter | Default | What it does |
|---|---|---|
| `FOV` | `700` | Perspective field of view in world units. Lower = more dramatic perspective. Higher = flatter. |
| `BACKGROUND_COLOR` | `#080818` | Canvas background. Change to match your site. |

### Cube face shading

Six faces, each with an independent brightness multiplier applied to the pixel color:

| Face | Default |
|---|---|
| Front | `1.0` |
| Back | `0.9` |
| Top | `0.6` |
| Right | `0.75` |
| Left | `0.65` |
| Bottom | `0.4` |

Raise all values closer to `1.0` for a flatter look. Increase contrast between them for a more dramatic 3D read.

---

## Embedding in a webpage

Instead of running as a standalone fullscreen page, you can drop it into any site so the effect triggers as the user scrolls to that section.

Run the embed script:

```bash
python embed.py output.html
```

This outputs `embed.html` — a self-contained `<section>` + `<canvas>` + `<script>` block you paste directly into your page HTML. The scroll listener is automatically rewritten to track the section's position in the page rather than the wheel event.

Works with plain HTML, WordPress, Webflow, or React.

**Performance note:** the B64 data blob is ~280KB. For production use, move it to an external file so it loads async and does not block page render. The embed script handles this automatically — it outputs a `digivatar-data.js` alongside `embed.html`.

---

## Performance

| Hardware | Expected framerate |
|---|---|
| M1/M2/M3 Mac | 60fps |
| Modern discrete GPU (RTX, RX series) | 60fps |
| Integrated Intel/AMD (2016 and newer) | 45–60fps |
| Older integrated graphics | 30fps |
| Mobile | Supported, varies by device |

The renderer uses a single `gl.drawElements()` call per frame. All vertex math runs in GLSL on the GPU. CPU cost per frame is minimal.

---

## Swapping art

The only thing that changes between artworks is the encoded data blob. If you want to swap your art manually without the script:

1. Run `encode.py your_new_art.png --blob-only` — prints just the B64 string
2. In `output.html`, find `const B64="..."` and replace the string between the quotes
3. If your new art is a different canvas size than 154×154, also update `W=154,H=154` to match

---

## Example art

The included demo uses original pixel art by [Digivatar](https://github.com/Master-Zomon).  
`example/CyberPunkDigi_NOBG_Native.png` — 154×154 native resolution, transparent background.

---

## License

MIT — free to use, modify, and distribute.  
If this helped your project, a shoutout to [Digivatar](https://github.com/Master-Zomon) is always appreciated.

---

*Built with WebGL + Python + too many late nights.*
