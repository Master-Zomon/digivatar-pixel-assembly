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
#
# ◈ DIGIVATAR — digivatar-pixel-assembly — encode.py
#

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
    print("Pillow required: pip install Pillow")
    sys.exit(1)


# ─────────────────────────────────────────────
# PARAMETERS — tweak these to change the effect
# ─────────────────────────────────────────────

# Scatter / explosion
SCATTER_XY      = 8000      # World-space XY scatter radius when exploded
SCATTER_Z       = 2800      # Z push toward camera when exploded (positive = toward viewer)
SPIN_AMOUNT     = math.pi * 3  # Max local spin per cube during flight

# Assembly feel
SCROLL_SPEED    = 0.0004    # Progress per scroll tick (lower = more scroll needed)
LERP_SPEED      = 0.055     # Animation smoothing (higher = snappier)
SNAP_THRESHOLD  = 0.001     # Lock to final state when this close to target

# Assembled image
VIEWPORT_FILL   = 0.82      # Fraction of viewport the assembled image fills
CUBE_ASSEMBLED  = 0.505     # Cube size at assembled state (relative to grid cell)
CUBE_EXPLODED   = 8.0       # Cube size multiplier when exploded

# Visual
FOV             = 700       # Perspective FOV in world units
BG_COLOR        = '0.031,0.031,0.094,1'  # WebGL clearColor RGBA (0–1)
BG_HEX          = '#080818' # CSS background color

# Cube face shading (brightness multiplier per face, applied to pixel color)
SHADE_FRONT     = 1.0
SHADE_BACK      = 0.9
SHADE_TOP       = 0.6
SHADE_BOTTOM    = 0.4
SHADE_RIGHT     = 0.75
SHADE_LEFT      = 0.65

# Label text
LABEL_ASSEMBLE  = 'SCROLL TO ASSEMBLE'
LABEL_ASSEMBLED = 'PIXEL PERFECT'  # ← change this to your artist name or title          # shown at 100% — change to your name/title
LABEL_UI        = 'SCROLL ↑↓ TO ASSEMBLE'

# ─────────────────────────────────────────────


def seed(i, k):
    x = math.sin(i * k + 311.7) * 43758.5453
    return x - int(x)


def encode_pixels(img_path):
    img = Image.open(img_path).convert('RGBA')
    pixels = img.load()
    w, h = img.size

    active = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0:
                active.append((x, y, r, g, b))

    if not active:
        print("ERROR: No non-transparent pixels found. Check your PNG has transparency.")
        sys.exit(1)

    print(f"Image: {w}×{h}px — {len(active)} active pixels ({w*h - len(active)} transparent, skipped)")

    buf = bytearray()
    for i, (px, py, r, g, b) in enumerate(active):
        ox = int((seed(i, 127.1 * 3.1) - 0.5) * SCATTER_XY)
        oy = int((seed(i, 127.1 * 7.3) - 0.5) * SCATTER_XY)
        oz = int(seed(i, 127.1 * 13.7) * -SCATTER_Z)
        sx = int((seed(i, 127.1 * 2.9) - 0.5) * SPIN_AMOUNT * 1000)
        sy = int((seed(i, 127.1 * 5.1) - 0.5) * SPIN_AMOUNT * 1000)
        sz = int((seed(i, 127.1 * 8.3) - 0.5) * SPIN_AMOUNT * 1000)

        clamp = lambda v: max(-32768, min(32767, v))
        buf += struct.pack('<BBBBBBhhhhhh',
                           px, py, r, g, b, 0,
                           clamp(ox), clamp(oy), clamp(oz),
                           clamp(sx), clamp(sy), clamp(sz))

    b64 = base64.b64encode(bytes(buf)).decode()
    return b64, w, h, len(active)


def build_html(b64, w, h):
    shades = f'{SHADE_FRONT},{SHADE_FRONT},{SHADE_FRONT},{SHADE_FRONT},' \
             f'{SHADE_BACK},{SHADE_BACK},{SHADE_BACK},{SHADE_BACK},' \
             f'{SHADE_TOP},{SHADE_TOP},{SHADE_TOP},{SHADE_TOP},' \
             f'{SHADE_BOTTOM},{SHADE_BOTTOM},{SHADE_BOTTOM},{SHADE_BOTTOM},' \
             f'{SHADE_RIGHT},{SHADE_RIGHT},{SHADE_RIGHT},{SHADE_RIGHT},' \
             f'{SHADE_LEFT},{SHADE_LEFT},{SHADE_LEFT},{SHADE_LEFT}'

    js = f'''
const bin=atob(B64),bytes=new Uint8Array(bin.length);
for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
const dv=new DataView(bytes.buffer),ST=18,W={w},H={h},N=bytes.length/ST|0;
const pxX=new Float32Array(N),pxY=new Float32Array(N),pxR=new Float32Array(N),pxG=new Float32Array(N),pxB=new Float32Array(N);
const oX=new Float32Array(N),oY=new Float32Array(N),oZ=new Float32Array(N),sX=new Float32Array(N),sY=new Float32Array(N),sZ=new Float32Array(N);
for(let i=0;i<N;i++){{const o=i*ST;pxX[i]=bytes[o];pxY[i]=bytes[o+1];pxR[i]=bytes[o+2]/255;pxG[i]=bytes[o+3]/255;pxB[i]=bytes[o+4]/255;oX[i]=dv.getInt16(o+6,true);oY[i]=dv.getInt16(o+8,true);oZ[i]=dv.getInt16(o+10,true);sX[i]=dv.getInt16(o+12,true)/1000;sY[i]=dv.getInt16(o+14,true)/1000;sZ[i]=dv.getInt16(o+16,true)/1000;}}
const canvas=document.getElementById('c');
canvas.width=window.innerWidth;canvas.height=window.innerHeight;
const gl=canvas.getContext('webgl',{{antialias:false,alpha:false}});
gl.getExtension('OES_element_index_uint');
gl.enable(gl.DEPTH_TEST);// blend disabled — depth test handles occlusion cleanly
gl.clearColor({BG_COLOR});
gl.disable(gl.CULL_FACE);
const vs=`attribute vec3 aPos,aColor,aExp,aTgt,aSpin;attribute float aShd;uniform float uP,uRX,uRY,uPS;uniform vec2 uScr;varying vec3 vC;varying float vA;mat3 rX(float a){{float c=cos(a),s=sin(a);return mat3(1,0,0,0,c,-s,0,s,c);}}mat3 rY(float a){{float c=cos(a),s=sin(a);return mat3(c,0,s,0,1,0,-s,0,c);}}mat3 rZ(float a){{float c=cos(a),s=sin(a);return mat3(c,-s,0,s,c,0,0,0,1);}}void main(){{float ep=uP<0.5?2.0*uP*uP:-1.0+(4.0-2.0*uP)*uP;float sf=1.0-ep;float h=mix(uPS*{CUBE_EXPLODED},uPS*{CUBE_ASSEMBLED},ep);vec3 p=rZ(aSpin.z*sf)*rY(aSpin.y*sf)*rX(aSpin.x*sf)*(aPos*h);vec3 wp=mix(aExp,aTgt,ep);vec3 r=rX(uRX)*rY(uRY)*p;float d=max(wp.z+r.z+800.0,50.0);float ps={FOV}.0/d;float s=mix(ps,1.0,ep);vec2 sc=(wp.xy+r.xy)*s/uScr;float zn=clamp((wp.z+r.z)/3000.0,-0.99,0.99);gl_Position=vec4(sc.x,-sc.y,zn,1.0);vC=aColor*aShd;vA=1.0;}}`;
const fs=`precision mediump float;varying vec3 vC;varying float vA;void main(){{gl_FragColor=vec4(vC,vA);}}`;
function mkS(t,s){{const sh=gl.createShader(t);gl.shaderSource(sh,s);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(sh));return sh;}}
const prg=gl.createProgram();gl.attachShader(prg,mkS(gl.VERTEX_SHADER,vs));gl.attachShader(prg,mkS(gl.FRAGMENT_SHADER,fs));gl.linkProgram(prg);gl.useProgram(prg);
const fv=[-1,-1,1,1,-1,1,1,1,1,-1,1,1,-1,-1,-1,-1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,1,-1,1,-1,-1,1,-1,-1,-1,-1,1,-1,1,1,-1,1,1,1,-1,1,1,1,-1,-1,1,1,-1,1,1,1,1,-1,1,-1,-1,1,-1,1,1,-1,1,-1,-1,-1,-1];
const fsh=[{shades}];
const fi=[0,1,2,0,2,3,4,5,6,4,6,7,8,9,10,8,10,11,12,13,14,12,14,15,16,17,18,16,18,19,20,21,22,20,22,23];
const NV=24,NI=36;
const ps=Math.min(canvas.width,canvas.height)/Math.max(W,H)*{VIEWPORT_FILL};
const ox2=-(W*ps)/2,oy2=-(H*ps)/2,tot=N*NV;
const posA=new Float32Array(tot*3),colA=new Float32Array(tot*3),expA=new Float32Array(tot*3),tgtA=new Float32Array(tot*3),spnA=new Float32Array(tot*3),shdA=new Float32Array(tot);
for(let i=0;i<N;i++){{for(let v=0;v<NV;v++){{const idx=i*NV+v,v3=v*3;posA[idx*3]=fv[v3];posA[idx*3+1]=fv[v3+1];posA[idx*3+2]=fv[v3+2];colA[idx*3]=pxR[i];colA[idx*3+1]=pxG[i];colA[idx*3+2]=pxB[i];expA[idx*3]=oX[i];expA[idx*3+1]=oY[i];expA[idx*3+2]=oZ[i];tgtA[idx*3]=ox2+pxX[i]*ps+ps/2;tgtA[idx*3+1]=oy2+pxY[i]*ps+ps/2;tgtA[idx*3+2]=0;spnA[idx*3]=sX[i];spnA[idx*3+1]=sY[i];spnA[idx*3+2]=sZ[i];shdA[idx]=fsh[v];}}}}
const idxA=new Uint32Array(N*NI);
for(let i=0;i<N;i++)for(let j=0;j<NI;j++)idxA[i*NI+j]=i*NV+fi[j];
function mkB(d,t=gl.ARRAY_BUFFER){{const b=gl.createBuffer();gl.bindBuffer(t,b);gl.bufferData(t,d,gl.STATIC_DRAW);return b;}}
const iB=mkB(idxA,gl.ELEMENT_ARRAY_BUFFER),pB=mkB(posA),cB=mkB(colA),eB=mkB(expA),tB=mkB(tgtA),sB=mkB(spnA),shB=mkB(shdA);
function ba(n,b,sz){{const l=gl.getAttribLocation(prg,n);if(l<0)return;gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,sz,gl.FLOAT,false,0,0);}}
ba('aPos',pB,3);ba('aColor',cB,3);ba('aExp',eB,3);ba('aTgt',tB,3);ba('aSpin',sB,3);ba('aShd',shB,1);
const uP=gl.getUniformLocation(prg,'uP'),uRX=gl.getUniformLocation(prg,'uRX'),uRY=gl.getUniformLocation(prg,'uRY'),uScr=gl.getUniformLocation(prg,'uScr'),uPS=gl.getUniformLocation(prg,'uPS');
let prog=0,tgt=0,rotX=0.0,rotY=0.0;
function draw(){{prog+=(tgt-prog)*{LERP_SPEED};if(Math.abs(tgt-prog)<{SNAP_THRESHOLD})prog=tgt;gl.viewport(0,0,canvas.width,canvas.height);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);const p=Math.max(0,Math.min(1,prog));gl.uniform1f(uP,p);gl.uniform1f(uRX,rotX);gl.uniform1f(uRY,rotY);gl.uniform2f(uScr,canvas.width/2,canvas.height/2);gl.uniform1f(uPS,ps);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,iB);gl.drawElements(gl.TRIANGLES,N*NI,gl.UNSIGNED_INT,0);document.getElementById('lbl').textContent=p<.03?'{LABEL_ASSEMBLE}':p>.97?'{LABEL_ASSEMBLED}':`ASSEMBLING... ${{Math.round(p*100)}}%`;requestAnimationFrame(draw);}}
draw();
window.addEventListener('wheel',e=>{{e.preventDefault();tgt=Math.max(0,Math.min(1,tgt+e.deltaY*{SCROLL_SPEED}));}},({{passive:false}}));
window.addEventListener('resize',()=>{{canvas.width=window.innerWidth;canvas.height=window.innerHeight;}});
'''

    html = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Pixel Assembly</title>'
        f'<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:{BG_HEX};overflow:hidden}}'
        'canvas{display:block;width:100vw;height:100vh}'
        '#ui{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,0.7);font:11px monospace;letter-spacing:.15em;pointer-events:none;background:rgba(8,8,24,0.65);padding:6px 18px;border-radius:20px;z-index:10;backdrop-filter:blur(4px)}'
        '#lbl{position:fixed;top:18px;left:50%;transform:translateX(-50%);color:rgba(180,140,255,0.9);font:11px monospace;letter-spacing:.2em;pointer-events:none;background:rgba(8,8,24,0.65);padding:6px 18px;border-radius:20px;z-index:10;backdrop-filter:blur(4px)}'
        '</style></head><body>'
        f'<canvas id="c"></canvas>'
        f'<div id="lbl">{LABEL_ASSEMBLE}</div>'
        f'<div id="ui">{LABEL_UI}</div>'
        f'<script>const B64="{b64}";{js}</script>'
        '</body></html>'
    )
    return html


def main():
    parser = argparse.ArgumentParser(description='Convert pixel art PNG to WebGL cube assembly HTML')
    parser.add_argument('image', help='Path to PNG with transparent background')
    parser.add_argument('--output', '-o', default='output.html', help='Output HTML filename (default: output.html)')
    parser.add_argument('--blob-only', action='store_true', help='Print only the B64 data string and exit')
    args = parser.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"ERROR: File not found: {img_path}")
        sys.exit(1)

    print(f"Encoding {img_path.name}...")
    b64, w, h, n_active = encode_pixels(img_path)

    if args.blob_only:
        print(b64)
        return

    html = build_html(b64, w, h)
    out_path = Path(args.output)
    out_path.write_text(html, encoding='utf-8')

    print(f"Output:  {out_path} ({len(html)//1024} KB)")
    print(f"Cubes:   {n_active}")
    print(f"Done — open {out_path} in Chrome or Firefox")


if __name__ == '__main__':
    main()

# ◈ end of codex — Digivatar
