# ████████████████████████████████████████████████████████████████████
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ██████╗ ██╗ ██████╗ ██╗██╗   ██╗ █████╗ ████████╗ █████╗ ██████╗
# ██╔══██╗██║██╔════╝ ██║██║   ██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
# ██║  ██║██║██║  ███╗██║██║   ██║███████║   ██║   ███████║██████╔╝
# ██║  ██║██║██║   ██║██║╚██╗ ██╔╝██╔══██║   ██║   ██╔══██║██╔══██╗
# ██████╔╝██║╚██████╔╝██║ ╚████╔╝ ██║  ██║   ██║   ██║  ██║██║  ██║
# ╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ████████████████████████████████████████████████████████████████████
#
#  ◈ Another master codex from Digivatar
#  ◈ Avant-garde digital visual world-building and music artist
#  ◈ github.com/Master-Zomon  |  digivatar.com
# ───────────────────────────────────────────────────────────────────

# ◈ DIGIVATAR — digivatar-pixel-assembly — encode.py

"""
digivatar-pixel-assembly — encode.py
=====================================
Converts a native pixel art PNG (transparent background) into a
self-contained WebGL HTML file with the 3D cube assembly effect.

Usage:
    python encode.py your_art.png
    python encode.py your_art.png --output my_output.html
    python encode.py your_art.png --blob-only   # prints B64 string only

Requirements:
    pip install Pillow
"""

import sys
import math
import struct
import base64
import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required — run: pip install Pillow")
    sys.exit(1)


# ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  P A R A M E T E R S  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
# Tune these to change the look and feel of the effect.
# No need to touch any other part of the file.

# ── scatter — how far pixels flee their grid positions when exploded ──
SCATTER_XY      = 8000          # XY world-space radius
SCATTER_Z       = 2800          # Z push toward camera — makes near cubes huge
SPIN_AMOUNT     = math.pi * 3   # max local rotation per cube during flight

# ── feel — the timing and responsiveness of the assembly animation ──
SCROLL_SPEED    = 0.0004        # progress per scroll tick (lower = more scroll needed)
LERP_SPEED      = 0.055         # animation smoothing — the soul of the motion
SNAP_THRESHOLD  = 0.001         # locks to final state when this close to target

# ── assembled — how the art looks and reads when fully converged ──
VIEWPORT_FILL   = 0.82          # fraction of viewport the image fills (1.0 = edge to edge)
CUBE_ASSEMBLED  = 0.505         # cube size at rest — slight gap between pixels
CUBE_EXPLODED   = 8.0           # cube size multiplier at full scatter
LABEL_ASSEMBLED = 'PIXEL PERFECT'  # ← change this to your artist name or title

# ── visual — perspective, background, labels ──
FOV             = 700           # perspective FOV in world units (lower = more dramatic)
BG_COLOR        = '0.031,0.031,0.094,1'  # WebGL clearColor RGBA (0–1 range)
BG_HEX          = '#080818'     # CSS background — keep in sync with BG_COLOR
LABEL_ASSEMBLE  = 'SCROLL TO ASSEMBLE'
LABEL_UI        = 'SCROLL TO ASSEMBLE · DRAG TO ROTATE'

# ── cube face shading — brightness multiplier per face ──
# Controls the 3D read of each cube. Front brightest, bottom darkest.
SHADE_FRONT     = 1.0
SHADE_BACK      = 0.9
SHADE_TOP       = 0.6
SHADE_BOTTOM    = 0.4
SHADE_RIGHT     = 0.75
SHADE_LEFT      = 0.65


# ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  U T I L I T Y  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
# Helper functions used during pixel encoding.

def seed(index, multiplier):
    """
    Deterministic pseudo-random float in [0, 1) from an index and multiplier.
    Uses sin-based hash — cheap, good enough distribution for scatter/spin.
    The magic constants (127.1, 311.7, 43758.5453) are standard GLSL hash values.
    """
    x = math.sin(index * multiplier + 311.7) * 43758.5453
    return x - int(x)


def clamp_int16(value):
    """Clamp to signed 16-bit integer range for binary packing."""
    return max(-32768, min(32767, value))


# ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  E N C O D E  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
# Read the PNG, skip transparent pixels, pack each active pixel into
# an 18-byte binary record: position, color, scatter offset, spin axis.

def encode_pixels(img_path):
    """
    Convert a PNG to a compact binary blob.

    Each pixel record is 18 bytes packed as <BBBBBBhhhhhh>:
        B  px       — pixel X position in source grid
        B  py       — pixel Y position in source grid
        B  r,g,b   — RGB color (0–255)
        B  pad      — reserved, always 0
        h  ox,oy,oz — explosion offset in world space (signed int16)
        h  sx,sy,sz — spin axis values × 1000 (signed int16)

    Returns: (b64_string, image_width, image_height, active_pixel_count)
    """
    # validate input
    if not img_path.exists():
        print(f"ERROR: File not found: {img_path}")
        sys.exit(1)

    suffix = img_path.suffix.lower()
    if suffix not in ('.png', '.PNG'):
        print(f"WARNING: Expected a PNG file, got {suffix}. Proceeding anyway.")

    img    = Image.open(img_path).convert('RGBA')
    pixels = img.load()
    w, h   = img.size

    # collect non-transparent pixels
    active = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0:
                active.append((x, y, r, g, b))

    if not active:
        print("ERROR: No non-transparent pixels found.")
        print("       Make sure your PNG has a transparent background, not a solid color.")
        sys.exit(1)

    print(f"Image:  {w}×{h}px")
    print(f"Active: {len(active)} pixels ({w * h - len(active)} transparent, skipped)")

    # pack each pixel into 18-byte binary record
    buf = bytearray()
    for i, (px, py, r, g, b) in enumerate(active):

        # scatter — deterministic random offset per pixel using different seeds
        ox = int((seed(i, 127.1 * 3.1)  - 0.5) *  SCATTER_XY)
        oy = int((seed(i, 127.1 * 7.3)  - 0.5) *  SCATTER_XY)
        oz = int( seed(i, 127.1 * 13.7)         * -SCATTER_Z)   # negative = toward camera

        # spin — random axis per pixel, zeroes out when cube arrives home
        sx = int((seed(i, 127.1 * 2.9)  - 0.5) * SPIN_AMOUNT * 1000)
        sy = int((seed(i, 127.1 * 5.1)  - 0.5) * SPIN_AMOUNT * 1000)
        sz = int((seed(i, 127.1 * 8.3)  - 0.5) * SPIN_AMOUNT * 1000)

        buf += struct.pack(
            '<BBBBBBhhhhhh',
            px, py, r, g, b, 0,                                   # position + color + pad
            clamp_int16(ox), clamp_int16(oy), clamp_int16(oz),    # explosion offsets
            clamp_int16(sx), clamp_int16(sy), clamp_int16(sz)     # spin axes
        )

    b64 = base64.b64encode(bytes(buf)).decode()
    return b64, w, h, len(active)


# ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  B U I L D  H T M L  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
# Assemble the final self-contained HTML file.
# The JS inside is kept readable — a veteran should be able to open this
# and understand exactly what it does without a decoder ring.

def build_html(b64, w, h):
    """Build a self-contained WebGL HTML file from the encoded pixel blob."""

    # build face shade array — 4 verts per face × 6 faces
    shades = ', '.join(
        str(s) for s in [
            SHADE_FRONT,  SHADE_FRONT,  SHADE_FRONT,  SHADE_FRONT,
            SHADE_BACK,   SHADE_BACK,   SHADE_BACK,   SHADE_BACK,
            SHADE_TOP,    SHADE_TOP,    SHADE_TOP,    SHADE_TOP,
            SHADE_BOTTOM, SHADE_BOTTOM, SHADE_BOTTOM, SHADE_BOTTOM,
            SHADE_RIGHT,  SHADE_RIGHT,  SHADE_RIGHT,  SHADE_RIGHT,
            SHADE_LEFT,   SHADE_LEFT,   SHADE_LEFT,   SHADE_LEFT,
        ]
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Pixel Assembly</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: {BG_HEX}; overflow: hidden; }}
    canvas {{ display: block; width: 100vw; height: 100vh; }}
    #lbl {{
      position: fixed; top: 18px; left: 50%; transform: translateX(-50%);
      color: rgba(180,140,255,0.9); font: 11px monospace; letter-spacing: .2em;
      pointer-events: none; background: rgba(8,8,24,0.65);
      padding: 6px 18px; border-radius: 20px; z-index: 10;
      backdrop-filter: blur(4px);
    }}
    #ui {{
      position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
      color: rgba(255,255,255,0.7); font: 11px monospace; letter-spacing: .15em;
      pointer-events: none; background: rgba(8,8,24,0.65);
      padding: 6px 24px; border-radius: 20px; z-index: 10;
      backdrop-filter: blur(4px); text-align: center; width: 420px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    @media (max-width: 768px) {{
      #lbl {{ font-size: 4vw; padding: 3vw 5vw; letter-spacing: .06em; }}
      #ui  {{ font-size: 3.5vw; padding: 3vw 5vw; width: 92vw; letter-spacing: .04em; }}
    }}
  </style>
</head>
<body>

<canvas id="c"></canvas>
<div id="lbl">{LABEL_ASSEMBLE}</div>
<div id="ui">{LABEL_UI}<br>DOUBLE-CLICK RESET ROTATION · TRIPLE-CLICK FULL RESET</div>

<script>
/*
 * ████████████████████████████████████████████████████████████████████
 * ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
 * ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 * ██████╗ ██╗ ██████╗ ██╗██╗   ██╗ █████╗ ████████╗ █████╗ ██████╗
 * ██╔══██╗██║██╔════╝ ██║██║   ██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
 * ██║  ██║██║██║  ███╗██║██║   ██║███████║   ██║   ███████║██████╔╝
 * ██║  ██║██║██║   ██║██║╚██╗ ██╔╝██╔══██║   ██║   ██╔══██║██╔══██╗
 * ██████╔╝██║╚██████╔╝██║ ╚████╔╝ ██║  ██║   ██║   ██║  ██║██║  ██║
 * ╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
 * ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 * ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
 * ████████████████████████████████████████████████████████████████████
 *
 *  ◈ Another master codex from Digivatar
 *  ◈ Avant-garde digital visual world-building and music artist
 *  ◈ github.com/Master-Zomon  |  digivatar.com
 * ─────────────────────────────────────────────────────────────────── */

// ◈ DIGIVATAR — digivatar-pixel-assembly — output.html

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  D E C O D E  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Unpack the binary blob — every pixel becomes a cube with color, position, spin.

const B64   = "{b64}";

const bin   = atob(B64);
const bytes = new Uint8Array(bin.length);
for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);

const dv = new DataView(bytes.buffer);
const ST = 18;         // bytes per pixel record
const W  = {w};        // source image width in pixels
const H  = {h};        // source image height in pixels
const N  = bytes.length / ST | 0;  // total active pixel count

const pxX = new Float32Array(N), pxY = new Float32Array(N);
const pxR = new Float32Array(N), pxG = new Float32Array(N), pxB = new Float32Array(N);
const oX  = new Float32Array(N), oY  = new Float32Array(N), oZ  = new Float32Array(N);
const sX  = new Float32Array(N), sY  = new Float32Array(N), sZ  = new Float32Array(N);

for (let i = 0; i < N; i++) {{
  const o  = i * ST;
  pxX[i]   = bytes[o];
  pxY[i]   = bytes[o + 1];
  pxR[i]   = bytes[o + 2] / 255;
  pxG[i]   = bytes[o + 3] / 255;
  pxB[i]   = bytes[o + 4] / 255;
  oX[i]    = dv.getInt16(o + 6,  true);
  oY[i]    = dv.getInt16(o + 8,  true);
  oZ[i]    = dv.getInt16(o + 10, true);
  sX[i]    = dv.getInt16(o + 12, true) / 1000;
  sY[i]    = dv.getInt16(o + 14, true) / 1000;
  sZ[i]    = dv.getInt16(o + 16, true) / 1000;
}}

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  W E B G L  S E T U P  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// GPU context. One draw call per frame handles all {w}x{h} cubes in parallel.

const canvas = document.getElementById('c');
canvas.width  = window.innerWidth;
canvas.height = window.innerHeight;

const gl = canvas.getContext('webgl', {{ antialias: false, alpha: false }});
if (!gl) {{
  document.body.innerHTML = '<p style="color:#ff44ff;font:16px monospace;padding:2rem">WebGL not supported in this browser.</p>';
  throw new Error('WebGL not supported');
}}

gl.getExtension('OES_element_index_uint');
gl.enable(gl.DEPTH_TEST);
// blend disabled — depth test handles occlusion cleanly, no transparency stacking
gl.clearColor({BG_COLOR});
gl.disable(gl.CULL_FACE);

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  S H A D E R S  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Vertex shader runs on GPU — position, spin, assembly, scene rotation, projection.
// ep drives everything: 0.0 = chaos, 1.0 = assembled.

const vs = `
  attribute vec3  aPos, aColor, aExp, aTgt, aSpin;
  attribute float aShd;
  uniform float   uP, uRX, uRY, uPS, uSRX, uSRY;
  uniform vec2    uScr;
  varying vec3    vC;
  varying float   vA;

  mat3 rX(float a) {{ float c=cos(a),s=sin(a); return mat3(1,0,0, 0,c,-s, 0,s,c); }}
  mat3 rY(float a) {{ float c=cos(a),s=sin(a); return mat3(c,0,s, 0,1,0, -s,0,c); }}
  mat3 rZ(float a) {{ float c=cos(a),s=sin(a); return mat3(c,-s,0, s,c,0, 0,0,1); }}

  void main() {{
    // easeInOut curve — slow start, fast middle, soft landing
    float ep = uP < 0.5
      ? 2.0 * uP * uP
      : -1.0 + (4.0 - 2.0 * uP) * uP;

    // spin factor — 1.0 at exploded, zeroes out as cube arrives home
    float sf = 1.0 - ep;
    float h  = mix(uPS * {CUBE_EXPLODED}, uPS * {CUBE_ASSEMBLED}, ep);
    vec3  p  = rZ(aSpin.z*sf) * rY(aSpin.y*sf) * rX(aSpin.x*sf) * (aPos * h);

    // lerp from exploded origin to assembled grid position
    vec3 wp = mix(aExp, aTgt, ep);

    // scene rotation — rigid body, fades to flat in last 10% of assembly
    float sceneF = clamp((1.0 - ep) / 0.1, 0.0, 1.0);
    float cSX = cos(uSRX * sceneF), sSX = sin(uSRX * sceneF);
    float cSY = cos(uSRY * sceneF), sSY = sin(uSRY * sceneF);
    float wpY  = wp.y * cSX - wp.z * sSX;
    float wpZ2 = wp.y * sSX + wp.z * cSX;
    float wpX2 = wp.x * cSY + wpZ2 * sSY;
    float wpZ3 = -wp.x * sSY + wpZ2 * cSY;
    wp = vec3(wpX2, wpY, wpZ3);

    // projection — perspective divide, clamp Z to avoid near-plane clipping
    vec3  rot = rX(uRX) * rY(uRY) * p;
    float d   = max(wp.z + rot.z + 800.0, 50.0);   // 800 = camera offset, 50 = near clip
    float ps2 = {FOV}.0 / d;                         // {FOV} = FOV in world units
    float s   = mix(ps2, 1.0, ep);
    vec2  sc  = (wp.xy + rot.xy) * s / uScr;
    float zn  = clamp((wp.z + rot.z) / 3000.0, -0.99, 0.99);  // 3000 = depth range

    gl_Position = vec4(sc.x, -sc.y, zn, 1.0);
    vC = aColor * aShd;
    vA = 1.0;    // fully opaque — no transparency stacking artifacts
  }}
`;

const fs = `
  precision mediump float;
  varying vec3  vC;
  varying float vA;
  void main() {{ gl_FragColor = vec4(vC, vA); }}
`;

function mkShader(type, src) {{
  const sh = gl.createShader(type);
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS))
    console.error('Shader compile error:', gl.getShaderInfoLog(sh));
  return sh;
}}

const prg = gl.createProgram();
gl.attachShader(prg, mkShader(gl.VERTEX_SHADER,   vs));
gl.attachShader(prg, mkShader(gl.FRAGMENT_SHADER, fs));
gl.linkProgram(prg);
if (!gl.getProgramParameter(prg, gl.LINK_STATUS))
  console.error('Shader link error:', gl.getProgramInfoLog(prg));
gl.useProgram(prg);

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  G E O M E T R Y  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Six faces, 24 vertices, 36 indices. Every pixel gets this same unit cube.
// Face shading: Front 1.0 · Back 0.9 · Top 0.6 · Bottom 0.4 · Right 0.75 · Left 0.65

const fv = [
  -1,-1, 1,  1,-1, 1,  1, 1, 1,  -1, 1, 1,   // front
  -1,-1,-1, -1, 1,-1,  1, 1,-1,   1,-1,-1,   // back
  -1, 1,-1, -1, 1, 1,  1, 1, 1,   1, 1,-1,   // top
  -1,-1,-1,  1,-1,-1,  1,-1, 1,  -1,-1, 1,   // bottom
   1,-1,-1,  1, 1,-1,  1, 1, 1,   1,-1, 1,   // right
  -1,-1,-1, -1,-1, 1, -1, 1, 1,  -1, 1,-1    // left
];

const fsh = [ {shades} ];

const fi = [
   0, 1, 2,  0, 2, 3,   // front
   4, 5, 6,  4, 6, 7,   // back
   8, 9,10,  8,10,11,   // top
  12,13,14, 12,14,15,   // bottom
  16,17,18, 16,18,19,   // right
  20,21,22, 20,22,23    // left
];

const NV  = 24;   // vertices per cube
const NI  = 36;   // indices per cube (6 faces × 2 triangles × 3 verts)

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  B U F F E R S  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Build per-vertex arrays — position, color, explosion origin, target, spin, shade.

const ps   = Math.min(canvas.width, canvas.height) / Math.max(W, H) * {VIEWPORT_FILL};
const ox2  = -(W * ps) / 2;   // center the grid horizontally
const oy2  = -(H * ps) / 2;   // center the grid vertically
const tot  = N * NV;

const posA = new Float32Array(tot * 3);
const colA = new Float32Array(tot * 3);
const expA = new Float32Array(tot * 3);
const tgtA = new Float32Array(tot * 3);
const spnA = new Float32Array(tot * 3);
const shdA = new Float32Array(tot);

for (let i = 0; i < N; i++) {{
  const tx = ox2 + pxX[i] * ps + ps / 2;   // assembled X world position
  const ty = oy2 + pxY[i] * ps + ps / 2;   // assembled Y world position
  for (let v = 0; v < NV; v++) {{
    const idx = i * NV + v;
    const v3  = v * 3;
    posA[idx*3]   = fv[v3];     posA[idx*3+1] = fv[v3+1]; posA[idx*3+2] = fv[v3+2];
    colA[idx*3]   = pxR[i];     colA[idx*3+1] = pxG[i];   colA[idx*3+2] = pxB[i];
    expA[idx*3]   = oX[i];      expA[idx*3+1] = oY[i];     expA[idx*3+2] = oZ[i];
    tgtA[idx*3]   = tx;         tgtA[idx*3+1] = ty;         tgtA[idx*3+2] = 0;
    spnA[idx*3]   = sX[i];      spnA[idx*3+1] = sY[i];     spnA[idx*3+2] = sZ[i];
    shdA[idx]     = fsh[v];
  }}
}}

const idxA = new Uint32Array(N * NI);
for (let i = 0; i < N; i++)
  for (let j = 0; j < NI; j++)
    idxA[i * NI + j] = i * NV + fi[j];

function mkBuf(data, type = gl.ARRAY_BUFFER) {{
  const b = gl.createBuffer();
  gl.bindBuffer(type, b);
  gl.bufferData(type, data, gl.STATIC_DRAW);
  return b;
}}

const iB  = mkBuf(idxA, gl.ELEMENT_ARRAY_BUFFER);
const pB  = mkBuf(posA);
const cB  = mkBuf(colA);
const eB  = mkBuf(expA);
const tB  = mkBuf(tgtA);
const sB  = mkBuf(spnA);
const shB = mkBuf(shdA);

function bindAttr(name, buf, size) {{
  const loc = gl.getAttribLocation(prg, name);
  if (loc < 0) return;
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
}}

bindAttr('aPos',   pB,  3);
bindAttr('aColor', cB,  3);
bindAttr('aExp',   eB,  3);
bindAttr('aTgt',   tB,  3);
bindAttr('aSpin',  sB,  3);
bindAttr('aShd',   shB, 1);

const uP   = gl.getUniformLocation(prg, 'uP');
const uRX  = gl.getUniformLocation(prg, 'uRX');
const uRY  = gl.getUniformLocation(prg, 'uRY');
const uScr = gl.getUniformLocation(prg, 'uScr');
const uPS  = gl.getUniformLocation(prg, 'uPS');
const uSRX = gl.getUniformLocation(prg, 'uSRX');
const uSRY = gl.getUniformLocation(prg, 'uSRY');

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  S T A T E  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Animation progress, rotation, interaction flags.

let prog    = 0;     // current assembly progress (0 = exploded, 1 = assembled)
let tgt     = 0;     // target progress driven by scroll
let rotX    = 0;     // global X rotation (reserved)
let rotY    = 0;     // global Y rotation (reserved)
let sceneRX = 0;     // scene rotation X — whole grid tips up/down
let sceneRY = 0;     // scene rotation Y — whole grid turns left/right
let drag    = false;
let lx = 0, ly = 0;

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  R E N D E R  L O O P  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Runs 60 times per second. Lerps progress, uploads uniforms, draws everything.

function draw() {{
  // chase the target — smooth, never instant (0.055 = lerp speed)
  prog += (tgt - prog) * {LERP_SPEED};
  if (Math.abs(tgt - prog) < {SNAP_THRESHOLD}) prog = tgt;

  // assembled — lock drag off
  if (prog >= 1) drag = false;

  gl.viewport(0, 0, canvas.width, canvas.height);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  const p = Math.max(0, Math.min(1, prog));
  gl.uniform1f(uP,   p);
  gl.uniform1f(uRX,  rotX);
  gl.uniform1f(uRY,  rotY);
  gl.uniform2f(uScr, canvas.width / 2, canvas.height / 2);
  gl.uniform1f(uPS,  ps);
  gl.uniform1f(uSRX, sceneRX);
  gl.uniform1f(uSRY, sceneRY);

  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, iB);
  gl.drawElements(gl.TRIANGLES, N * NI, gl.UNSIGNED_INT, 0);

  // update top label
  const lbl = document.getElementById('lbl');
  if      (p < 0.03) lbl.textContent = '{LABEL_ASSEMBLE}';
  else if (p > 0.97) lbl.textContent = '{LABEL_ASSEMBLED}';
  else               lbl.textContent = `ASSEMBLING... ${{Math.round(p * 100)}}%`;

  requestAnimationFrame(draw);
}}

draw();

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  E V E N T S  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Scroll assembles. Drag rotates. Double-click resets. Triple-click full reset.

window.addEventListener('wheel', e => {{
  e.preventDefault();
  tgt = Math.max(0, Math.min(1, tgt + e.deltaY * {SCROLL_SPEED}));
}}, {{ passive: false }});

window.addEventListener('mousemove', e => {{
  if (drag && prog < 1) {{
    sceneRY += (e.clientX - lx) * 0.005;
    sceneRX += (e.clientY - ly) * 0.005;
    lx = e.clientX;
    ly = e.clientY;
  }}
}});

canvas.addEventListener('mousedown', e => {{
  if (prog < 1) {{ drag = true; lx = e.clientX; ly = e.clientY; }}
}});

window.addEventListener('mouseup', () => drag = false);

canvas.addEventListener('dblclick', () => {{ sceneRX = 0; sceneRY = 0; }});

let clickCount = 0, clickTimer = null;
canvas.addEventListener('click', () => {{
  clickCount++;
  clearTimeout(clickTimer);
  clickTimer = setTimeout(() => clickCount = 0, 400);
  if (clickCount >= 3) {{
    clickCount = 0;
    tgt = 0; prog = 0; sceneRX = 0; sceneRY = 0; drag = false;
  }}
}});

window.addEventListener('resize', () => {{
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
}});

// ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  T O U C H  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
// Mobile — single finger scroll, two finger rotate, double/triple tap reset.

let lastTouchY = 0, lastTouchX = 0;
let lastTap = 0, tapCount = 0, tapTimer = null;

canvas.addEventListener('touchstart', e => {{
  e.preventDefault();
  const t = e.touches;
  if (t.length === 1) {{
    lastTouchY = t[0].clientY;
    lastTouchX = t[0].clientX;
    const now = Date.now();
    if (now - lastTap < 400) tapCount++; else tapCount = 1;
    lastTap = now;
    clearTimeout(tapTimer);
    tapTimer = setTimeout(() => {{
      if (tapCount === 2) {{ sceneRX = 0; sceneRY = 0; }}
      if (tapCount >= 3)  {{ tgt = 0; prog = 0; sceneRX = 0; sceneRY = 0; drag = false; }}
      tapCount = 0;
    }}, 400);
  }}
  if (t.length === 2) {{
    lastTouchX = (t[0].clientX + t[1].clientX) / 2;
    lastTouchY = (t[0].clientY + t[1].clientY) / 2;
  }}
}}, {{ passive: false }});

canvas.addEventListener('touchmove', e => {{
  e.preventDefault();
  const t = e.touches;
  if (t.length === 1) {{
    const dy = t[0].clientY - lastTouchY;
    tgt = Math.max(0, Math.min(1, tgt - dy * 0.003));
    if (prog >= 0.98) {{
      sceneRY += (t[0].clientX - lastTouchX) * 0.005;
      sceneRX += (t[0].clientY - lastTouchY) * 0.005;
    }}
    lastTouchX = t[0].clientX;
    lastTouchY = t[0].clientY;
  }}
  if (t.length === 2) {{
    const cx = (t[0].clientX + t[1].clientX) / 2;
    const cy = (t[0].clientY + t[1].clientY) / 2;
    const dy = cy - lastTouchY;
    tgt = Math.max(0, Math.min(1, tgt - dy * 0.003));
    sceneRY += (cx - lastTouchX) * 0.004;
    lastTouchX = cx;
    lastTouchY = cy;
  }}
}}, {{ passive: false }});

canvas.addEventListener('touchend', () => {{ if (prog >= 1) drag = false; }}, {{ passive: false }});

// ◈ end of codex — Digivatar
</script>

</body>
</html>'''

    return html


# ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  E N T R Y  P O I N T  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
# Parse args, run encode, write output.

def main():
    parser = argparse.ArgumentParser(
        description='Convert native pixel art PNG to self-contained WebGL HTML.'
    )
    parser.add_argument(
        'image',
        help='Path to PNG with transparent background (native pixel size, no upscaling)'
    )
    parser.add_argument(
        '--output', '-o',
        default='output.html',
        help='Output HTML filename (default: output.html)'
    )
    parser.add_argument(
        '--blob-only',
        action='store_true',
        help='Print only the base64 data string and exit (useful for embed.py)'
    )
    args = parser.parse_args()

    img_path = Path(args.image)

    print(f"Encoding {img_path.name}...")
    b64, w, h, n_active = encode_pixels(img_path)

    if args.blob_only:
        print(b64)
        return

    html     = build_html(b64, w, h)
    out_path = Path(args.output)
    out_path.write_text(html, encoding='utf-8')

    print(f"Output: {out_path} ({len(html) // 1024} KB)")
    print(f"Cubes:  {n_active}")
    print(f"Done — open {out_path} in Chrome or Firefox")


if __name__ == '__main__':
    main()

# ◈ end of codex — Digivatar
