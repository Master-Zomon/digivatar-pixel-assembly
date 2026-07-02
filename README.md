# digivatar-pixel-assembly

A WebGL tool that explodes your native pixel art into 3D spinning cubes — then assembles them back into the full image as the viewer scrolls.

Built by [Digivatar](https://github.com/Master-Zomon) — avant-garde digital visual world-building and music artist.

Font by MEK.txt | @MEK.txt — thank you for the incredible type. MEKZANTINE (Alpha v1)

**<a href="https://master-zomon.github.io/digivatar-pixel-assembly/digivatar_webgl.html" target="_blank">→ Live Demo 1 — CyberPunk Digi</a>**

**<a href="https://master-zomon.github.io/digivatar-pixel-assembly/comrades_webgl.html" target="_blank">→ Live Demo 2 — Comrades</a>**

**<a href="https://master-zomon.github.io/digivatar-pixel-assembly/nakamingo_webgl.html" target="_blank">→ Live Demo 3 — Nakamingo</a>**

---

## What it does

Drop in any native-resolution pixel art PNG with a transparent background. The tool converts every visible pixel into a 3D cube with its exact color. On load, the cubes are scattered in world space — flying toward the camera, spinning freely. As the viewer scrolls, they converge and lock into the pixel art portrait.

When fully assembled, individual pixels can be grabbed and pulled off the portrait, then snapped back or reclaimed by scrolling out.

No libraries. No dependencies. One HTML file, one Python script to encode your art.

---

## How to use it

No coding experience needed. Follow every step exactly.

---

### Step 1 — Install Python (one time only)

> **Never used Python before?** That is totally fine. Python is not an app you open and click around in — it runs invisibly in the background when you type commands. Think of it like installing a plugin that your terminal uses. You will never actually "open" Python. [Watch this beginner Python install guide for Windows](https://www.youtube.com/watch?v=uge4A1LHsNk) if you want to see exactly what to expect before you start — it covers the whole thing in under 9 minutes.

Python is a free tool this script needs to run. You only install it once.

1. Go to **python.org/downloads**
2. Click the big yellow Download button and run the installer
3. **Windows users — critical:** on the very first installer screen, check the box that says **"Add Python to PATH"** before you click anything else. It is easy to miss and if you skip it Python will not work.
4. Click **Install Now** and let it finish — no need to change any other settings
5. When done, press the **Windows key**, type **cmd**, and open **Command Prompt**
6. Type this exactly and hit Enter:

```
pip install Pillow
```

When you see "Successfully installed Pillow" you are done. You will never have to do this again.

---

### Step 2 — Download this tool

1. Click the green **Code** button at the top of this GitHub page
2. Click **Download ZIP**
3. Go to your Downloads folder and find `digivatar-pixel-assembly-main.zip`
4. Right-click it and select **Extract All** then click **Extract**
5. Move the extracted folder `digivatar-pixel-assembly-main` to your Desktop so it is easy to find

---

### Step 3 — Prepare your pixel art

Your PNG needs two things:

**Transparent background** — no solid color behind the art. If your file has a background color, remove it in Aseprite, Photoshop, or any pixel editor and re-export as PNG with transparency. The tool skips transparent pixels — that is how it knows what to turn into cubes.

**Native pixel size** — do not upscale your art before running it. Use the original canvas size you drew it at. If you drew it at 64x64, run it at 64x64. Upscaling blurs the pixels and breaks the effect.

**File name tip** — avoid spaces in your file name. `my art.png` will cause an error. Use `my_art.png` or `MyArt.png` instead.

---

### Step 4 — Run the tool

1. Copy your PNG file into the `digivatar-pixel-assembly-main` folder on your Desktop
2. Press the **Windows key**, search **cmd**, open **Command Prompt**
3. Type this and hit Enter:

```
cd Desktop\digivatar-pixel-assembly-main
```

4. Now type this — replacing `YourFileName.png` with your actual file name — and hit Enter:

```
python encode.py YourFileName.png
```

Example: if your file is called `my_character.png` you would type:

```
python encode.py my_character.png
```

You should see something like this:

```
Encoding my_character.png...
Image: 64x64px — 2840 active pixels (1256 transparent, skipped)
Output: output.html (52 KB)
Cubes: 2840
Done — open output.html in Chrome or Firefox
```

If you see that — it worked.

---

### Step 5 — Open your result

1. Go to the `digivatar-pixel-assembly-main` folder on your Desktop
2. Find the file called `output.html`
3. Right-click it and select **Open with** then **Google Chrome** or **Firefox**

Scroll down — your pixel art assembles from 3D spinning cubes.
Scroll up — it explodes back out.

That is it. You can share the `output.html` file with anyone — it works in any browser with no internet connection needed.

---

## Interactions

| Input | What it does |
|---|---|
| **Scroll** | Assembles / explodes the pixel art |
| **Drag** | Rotates the scene while assembling |
| **Double-click** | Resets scene rotation |
| **Triple-click** | Full reset — explodes back to start |
| **Drag pixel** *(assembled)* | Pulls an individual pixel off the portrait |
| **Click pixel** *(assembled)* | Snaps a pulled pixel back home |
| **Scroll out** *(assembled)* | Returns all pulled pixels and explodes |

The controls panel in the bottom center shows all interactions. Click **CONTROLS** to open it — it animates open like a CRT monitor powering on and closes the same way.

---

## Troubleshooting

**"python is not recognized"** — Python was not added to PATH during install. Uninstall Python, run the installer again, and check the "Add Python to PATH" box on the very first screen.

**"No module named PIL"** — Run `pip install Pillow` in Command Prompt and try again.

**"Cannot find path"** — The folder is not where you told the terminal to look. Make sure you moved `digivatar-pixel-assembly-main` to your Desktop, or adjust the cd command to match where your folder actually is.

**"No non-transparent pixels found"** — Your PNG does not have a transparent background. Remove the background in your pixel editor and export again with transparency.

**UnicodeEncodeError** — Download the latest `encode.py` from this repo and replace yours. This was a known Windows bug that has been fixed.

**File name has spaces** — Rename your PNG to remove spaces. Use underscores instead: `my_art.png`

---

## Parameters

All tunable values are at the top of `encode.py` and commented. You do not need to touch the HTML or GLSL.

### Scatter / explosion

| Parameter | Default | What it does |
|---|---|---|
| `SCATTER_XY` | `8000` | World-space radius of XY scatter. Higher = cubes fly further off screen when exploded. |
| `SCATTER_Z` | `2800` | How far cubes push toward the camera when exploded. Higher = closer to lens, appear larger. |
| `SPIN_AMOUNT` | `pi x 3` | How much each cube rotates during flight. Higher = more chaotic spin. |

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
| `CUBE_ASSEMBLED` | `0.505` | Pixel cube size at assembled state. Below 0.5 adds gap between pixels. Above 0.5 = overlap. |
| `CUBE_EXPLODED` | `8.0` | Cube size multiplier when fully exploded. Higher = bigger cubes near camera. |
| `LABEL_ASSEMBLED` | `PIXEL PERFECT` | Text shown when fully assembled. Change this to your artwork name or artist name. |

### Visual

| Parameter | Default | What it does |
|---|---|---|
| `FOV` | `700` | Perspective field of view in world units. Lower = more dramatic. Higher = flatter. |
| `BG_HEX` | `#080818` | Canvas background color. Change to match your site. Keep `BG_COLOR` in sync. |

### Cube face shading

| Face | Default |
|---|---|
| Front | `1.0` |
| Back | `0.9` |
| Top | `0.6` |
| Right | `0.75` |
| Left | `0.65` |
| Bottom | `0.4` |

---

## Embedding in a webpage

Run the embed script:

```
python embed.py output.html
```

This outputs `embed_section.html` — paste it into your page HTML. Works with plain HTML, WordPress, Webflow, or React.

---

## Performance

| Hardware | Expected framerate |
|---|---|
| M1/M2/M3 Mac | 60fps |
| Modern discrete GPU (RTX, RX series) | 60fps |
| Integrated Intel/AMD (2016 and newer) | 45-60fps |
| Older integrated graphics | 30fps |
| Mobile | Supported, varies by device |

---

## Example art

Live demos use pixel art from three different communities — each a self-contained HTML file in this repo.

`digivatar_webgl.html` — original art by [Digivatar](https://github.com/Master-Zomon), 154x154 native resolution.
`comrades_webgl.html` — Comrades pixel art community demo.
`nakamingo_webgl.html` — Nakamingo pixel art community demo.

---

## License

MIT — free to use, modify, and distribute.
If this helped your project, a shoutout to [Digivatar](https://github.com/Master-Zomon) is always appreciated.

---

If this codex helped you — donate to starving artist **digivatar.eth**

---

*Built with WebGL + Python + too many late nights.*

---

*Another master codex from Digivatar.*
