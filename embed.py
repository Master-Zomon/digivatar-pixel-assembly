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

"""
digivatar-pixel-assembly — embed.py
=====================================
Converts the standalone output.html into a page-embed version
that triggers as the user scrolls to that section of your site.

Usage:
    python embed.py output.html
    python embed.py output.html --output my_section.html

What it produces:
    embed_section.html  — paste this <section> block into your page
    digivatar-data.js   — external data file loaded async (keeps your page fast)

The scroll listener is rewritten to track the section's position
in the page rather than the mouse wheel. Works with plain HTML,
WordPress, Webflow, or React.
"""

import re
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Convert standalone pixel assembly HTML to page embed')
    parser.add_argument('input', help='Path to output.html from encode.py')
    parser.add_argument('--output', '-o', default='embed_section.html', help='Output filename (default: embed_section.html)')
    parser.add_argument('--data-file', default='digivatar-data.js', help='External data JS filename (default: digivatar-data.js)')
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: File not found: {in_path}")
        sys.exit(1)

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  R E A D  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # Load the standalone HTML and extract the pieces we need to rewrite.
    #
    content = in_path.read_text()

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  E X T R A C T  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # Pull the B64 blob, script, and styles out of the standalone file.
    #
    # Extract B64 blob
    b64_match = re.search(r'const B64="([^"]+)";', content)
    if not b64_match:
        print("ERROR: Could not find B64 data in HTML. Make sure this is output from encode.py")
        sys.exit(1)

    b64 = b64_match.group(1)

    # Write external data file
    data_path = Path(args.data_file)
    data_path.write_text(f'const B64="{b64}";')
    print(f"Data file: {data_path} ({len(b64)//1024} KB)")

    # Strip B64 from inline script
    content_no_b64 = content.replace(f'const B64="{b64}";', '/* B64 loaded externally */')

    # Extract just the script content
    script_match = re.search(r'<script>(.*?)</script>', content_no_b64, re.DOTALL)
    if not script_match:
        print("ERROR: Could not extract script block")
        sys.exit(1)

    script = script_match.group(1)

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  R E W R I T E  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # Swap fullscreen canvas for section-relative sizing.
    # Swap wheel listener for scroll-position listener.
    #
    # Rewrite canvas sizing — fullscreen → section-relative
    script = script.replace(
        'canvas.width=window.innerWidth;canvas.height=window.innerHeight;',
        'canvas.width=section.offsetWidth;canvas.height=section.offsetHeight;'
    )
    script = script.replace(
        "canvas.width=window.innerWidth;canvas.height=window.innerHeight;",
        "canvas.width=section.offsetWidth;canvas.height=section.offsetHeight;"
    )

    # Rewrite resize listener
    script = script.replace(
        "window.addEventListener('resize',()=>{canvas.width=window.innerWidth;canvas.height=window.innerHeight;});",
        "window.addEventListener('resize',()=>{canvas.width=section.offsetWidth;canvas.height=section.offsetHeight;});"
    )

    # Replace wheel listener with scroll listener
    wheel_pattern = r"window\.addEventListener\('wheel'.*?\}\),\s*\(\{passive:false\}\)\);"
    scroll_listener = """window.addEventListener('scroll',()=>{
  const rect=section.getBoundingClientRect();
  const scrolled=-rect.top/rect.height;
  tgt=Math.max(0,Math.min(1,scrolled));
});"""
    script = re.sub(wheel_pattern, scroll_listener, script, flags=re.DOTALL)

    # Add section reference at top of script
    script = "const section=document.getElementById('pixel-assembly-section');\n" + script

    # Extract styles
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    styles = style_match.group(1) if style_match else ''

    # Scope styles to section — replace body with section selector
    styles = styles.replace('body{', '#pixel-assembly-section{')
    styles = styles.replace('canvas{', '#pixel-assembly-section canvas{')
    styles = styles.replace('#ui{', '#pixel-assembly-ui{')
    styles = styles.replace('#lbl{', '#pixel-assembly-lbl{')

    # Extract label text
    lbl_match = re.search(r'<div id="lbl">(.*?)</div>', content)
    ui_match = re.search(r'<div id="ui">(.*?)</div>', content)
    lbl_text = lbl_match.group(1) if lbl_match else 'SCROLL TO ASSEMBLE'
    ui_text = ui_match.group(1) if ui_match else 'SCROLL ↑↓ TO ASSEMBLE'

    # Update label IDs in script
    script = script.replace("document.getElementById('lbl')", "document.getElementById('pixel-assembly-lbl')")

    embed = f"""<!--
  digivatar-pixel-assembly — embed block
  Paste this into your page where you want the effect to appear.
  Also include digivatar-data.js before this block:
  <script src="{data_path}" async></script>
-->

<style>
{styles}
#pixel-assembly-section {{
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}}
</style>

<section id="pixel-assembly-section">
  <canvas id="c"></canvas>
  <div id="pixel-assembly-lbl">{lbl_text}</div>
  <div id="pixel-assembly-ui">{ui_text}</div>
</section>

<script src="{data_path}"></script>
<script>
{script}
</script>
"""

    # ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  O U T P U T  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # Write the embed block and external data file.
    #
    out_path = Path(args.output)
    out_path.write_text(embed)
    print(f"Embed block: {out_path}")
    print(f"\nTo use:")
    print(f"  1. Copy {data_path} to your site")
    print(f"  2. Paste the contents of {out_path} into your page HTML")
    print(f"  3. The effect triggers as the user scrolls into the section")


if __name__ == '__main__':
    main()
