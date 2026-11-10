"""Run: python tools/build_guides.py. Builds the site's FPS guides (guides/*/index.html and guides/index.html) from the content below."""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://pulseoptimizerapp.github.io"
UPDATED = "November 2026"
UPDATED_ISO = "2026-11-10"

WINDOWS = [
    ("Run your monitor at its real refresh rate",
     "Many 144 Hz and 240 Hz monitors run at 60 Hz out of the box, so you never see the extra frames. Settings → System → Display → Advanced display → Choose a refresh rate, and pick the highest."),
    ("Plug the monitor into the graphics card",
     "A cable in the motherboard's port makes games run on the processor's weak built-in graphics, or routes every frame through it. Use the ports on the graphics card at the back of the PC."),
    ("Turn on XMP or EXPO in the BIOS",
     "Memory runs at a slow default speed until you turn on its profile (XMP on Intel boards, EXPO on AMD). It's one setting, and in CPU-heavy games it's often worth 10–20%. Two matching sticks in the right slots (dual channel) matter even more than speed."),
    ("Keep Game Mode on and background recording off",
     "Settings → Gaming → Game Mode: On. Then Settings → Gaming → Captures → Record what happened: Off, so Windows isn't recording in the background while you play."),
    ("Update your graphics driver",
     "New drivers fix stutters and add per-game optimizations. Get them from NVIDIA, AMD or Intel directly."),
    ("Laptops: plug in and use the real graphics card",
     "On battery, laptops cut power hard. Plug in, then Settings → System → Display → Graphics, pick the game, and set it to High performance so it runs on the graphics card, not the built-in chip."),
]

GUIDES = [
    {
        "slug": "valorant-fps",
        "game": "VALORANT",
        "title": "How to get more FPS in VALORANT: the best settings for 2026",
        "h1": "More FPS in VALORANT",
        "desc": "The VALORANT settings that actually raise FPS and cut input lag in 2026, why each one matters, and the Windows fixes worth the most frames.",
        "lead": "VALORANT is light on the graphics card and heavy on the CPU and memory, so the settings that matter are different from most games. Here's what to change, in order of impact, and why.",
        "calc": "Valorant",
        "best": "Multithreaded Rendering: On. It spreads VALORANT's work over more CPU cores, and since VALORANT is limited by the CPU on most PCs, it's worth more than any graphics setting.",
        "intro_note": "Check your FPS in a real match or Deathmatch, not the Range: the Range runs much faster than a full lobby, so it hides the drops you feel in games.",
        "sections": [
            ("Video → General", [
                ("Display Mode", "Fullscreen", "Gives the game the screen directly, for the lowest delay."),
                ("Resolution", "Your monitor's native", "Lowering it barely helps in VALORANT, because the CPU, not the graphics card, usually sets the pace."),
                ("Limit FPS Always", "Off", "Or a cap just under what your PC holds steadily, if your FPS swings a lot. A steady cap feels smoother than a jumpy uncapped rate."),
                ("NVIDIA Reflex Low Latency", "On", "Cuts input lag when the graphics card is the limit. On + Boost keeps the card clocked up for a little less lag and more power use."),
            ]),
            ("Video → Graphics Quality", [
                ("Multithreaded Rendering", "On", "The biggest one: spreads the work over more CPU cores. Only turn it off on a 2- or 4-thread CPU, and test both."),
                ("Material Quality", "Low", "Fewer effects on surfaces, more frames."),
                ("Texture Quality", "Low", "Medium is fine with 4 GB of video memory or more; it costs very little."),
                ("Detail Quality", "Low", "Fewer small details on the map."),
                ("UI Quality", "Low", "Lighter menus and interface."),
                ("Vignette", "Off", "Darkened screen edges cost frames and visibility."),
                ("VSync", "Off", "VSync adds delay. Use a frame cap instead if you see tearing."),
                ("Anti-Aliasing", "None or MSAA 2x", "None for the most FPS, MSAA 2x for smoother edges at a small cost."),
                ("Anisotropic Filtering", "1x to 4x", "Sharper ground textures at angles; the cost is tiny either way."),
                ("Improve Clarity", "Off", "On makes edges crisper at a small cost: try both."),
                ("Experimental Sharpening", "Off", ""),
                ("Bloom", "Off", "Glow around bright things: no gameplay value."),
                ("Distortion", "Off", "Warping effects from abilities cost frames and clarity."),
                ("Cast Shadows", "Off", "A noticeable frame cost for shadows that don't help you spot players."),
            ]),
        ],
        "extra": [
            ("Why VALORANT is CPU-bound", "Even a mid-range graphics card can push VALORANT past 300 FPS, so the processor and memory decide where you land. That's why turning on XMP/EXPO and running two memory sticks matter so much more here than lowering graphics settings, and why X3D processors like the Ryzen 7 9800X3D lead every VALORANT benchmark."),
        ],
        "sources": [
            ("Best VALORANT settings 2026 (esports.net)", "https://www.esports.net/wiki/guides/best-valorant-settings/"),
            ("NVIDIA Reflex", "https://www.nvidia.com/en-us/geforce/technologies/reflex/"),
        ],
    },
    {
        "slug": "fortnite-fps",
        "game": "Fortnite",
        "title": "How to get more FPS in Fortnite: the best settings for 2026",
        "h1": "More FPS in Fortnite",
        "desc": "The Fortnite settings that raise FPS and cut input lag in 2026, including Performance mode, view distance and Reflex, plus the Windows fixes worth the most frames.",
        "lead": "Fortnite can look stunning or run very fast, and the biggest switch between the two is the rendering mode. Here's the setup competitive players use, and why each setting matters.",
        "calc": "Fortnite",
        "best": "Rendering Mode: Performance. It switches Fortnite to a lighter renderer built for frame rate, usually a big gain over DirectX 12 mode on mid-range and older PCs.",
        "intro_note": "Fortnite rebuilds its shaders after big updates and driver installs, so the first match afterwards stutters. Play one game before judging your settings.",
        "sections": [
            ("Display", [
                ("Window Mode", "Fullscreen", "The lowest delay, and Windows can't throttle the game."),
                ("Resolution", "Your monitor's native", "Lower 3D Resolution below instead if you need frames: the interface stays sharp."),
                ("Vsync", "Off", "Vsync adds delay."),
                ("Rendering Mode", "Performance", "The big one. A lighter renderer built for frame rate, using far less of the graphics card and video memory than DirectX 12 mode."),
                ("Frame Rate Limit", "Unlimited, or your refresh rate", "Cap at your monitor's refresh rate if you see tearing or your FPS swings a lot."),
            ]),
            ("Graphics quality (Performance mode)", [
                ("View Distance", "Near", "Far costs frames; Medium if you want to see buildings sooner."),
                ("3D Resolution", "100%", "Drop it 10% at a time only if you're still short of your refresh rate."),
                ("Textures", "Low", "Easy on video memory, which matters most on 4–6 GB cards."),
                ("Meshes", "Low", "Simpler objects in Performance mode."),
            ]),
            ("Advanced graphics", [
                ("NVIDIA Reflex Low Latency", "On + Boost", "Cuts input lag on NVIDIA cards. On AMD, turn on Anti-Lag 2 in the AMD software if your driver offers it for Fortnite."),
                ("Show FPS", "On", "So you can see what each change does."),
            ]),
        ],
        "extra": [
            ("Staying in DirectX 12 mode?", "If you'd rather keep DirectX 12 for the looks, turn Nanite, Lumen global illumination and reflections, and hardware ray tracing off, and use DLSS (NVIDIA), FSR (AMD) or TSR at a Quality or Balanced setting. That keeps most of the image for a fraction of the cost."),
        ],
        "sources": [
            ("Fortnite on PC: best settings for competitive play in 2026 (Epic Games)", "https://store.epicgames.com/news/fortnite-on-pc-best-settings-for-competitive-play-in-2026"),
        ],
    },
    {
        "slug": "cs2-fps",
        "game": "Counter-Strike 2",
        "title": "How to get more FPS in CS2: the best video settings for 2026",
        "h1": "More FPS in CS2",
        "desc": "The Counter-Strike 2 video settings that raise FPS and keep players easy to see in 2026, why each matters, and the Windows fixes worth the most frames.",
        "lead": "CS2 runs on Source 2 and leans on both the CPU and the graphics card, and its frame rate swings more than most games during smokes and molotovs. These settings raise your average and, just as important, your lows.",
        "calc": "Counter-Strike 2",
        "best": "Lowering Particle Detail and Shader Detail, with Ambient Occlusion off. They raise your lowest frame rates in smokes and molotovs, where CS2 drops the most.",
        "intro_note": "Judge settings in a real match, or with a community FPS benchmark map, not on an empty server: smokes, fire and full teams are where CS2's frame rate drops.",
        "sections": [
            ("Video → Display", [
                ("Display Mode", "Fullscreen", "The lowest delay."),
                ("Aspect Ratio and Resolution", "Your choice", "Native looks best. Many pros play 4:3 at 1280×960 stretched for bigger models; it also gives a few more frames."),
                ("Refresh Rate", "Your monitor's highest", "Make sure it isn't stuck at 60 Hz."),
            ]),
            ("Video → Advanced", [
                ("Boost Player Contrast", "Enabled", "Makes players stand out from the background. A small cost, worth it."),
                ("Wait for Vertical Sync", "Disabled", "VSync adds delay."),
                ("Multisampling Anti-Aliasing", "None or 2x MSAA", "None for the most FPS; 2x or 4x smooths edges if you have headroom."),
                ("Global Shadow Quality", "Low to High", "Low for frames. Many players keep it higher because shadows can give away positions."),
                ("Model / Texture Detail", "Low", "Little visual difference in matches."),
                ("Texture Filtering Mode", "Bilinear", "The cheapest filtering."),
                ("Shader Detail", "Low", ""),
                ("Particle Detail", "Low", "Helps your lows in smokes, molotovs and grenades."),
                ("Ambient Occlusion", "Disabled", "Soft contact shadows cost frames and don't help."),
                ("High Dynamic Range", "Performance", ""),
                ("FidelityFX Super Resolution", "Disabled", "Upscaling blurs distant players; only use it on a very weak graphics card."),
                ("NVIDIA Reflex Low Latency", "Enabled", "Cuts input lag on NVIDIA cards."),
            ]),
        ],
        "extra": [
            ("Uncap your frame rate", "Open the developer console (turn it on in Game settings) and type fps_max 0 to remove the frame cap, or set a cap a little under what your PC holds steadily if your frame rate swings a lot: steady frames feel smoother than a jumpy higher number."),
        ],
        "sources": [
            ("Best CS2 video settings 2026 (Hotspawn)", "https://www.hotspawn.com/counter-strike/guide/best-cs2-video-settings"),
            ("NVIDIA Reflex", "https://www.nvidia.com/en-us/geforce/technologies/reflex/"),
        ],
    },
]

ICON = '<img src="{up}img/icon.svg" alt="" width="28" height="28">'
DL = "https://github.com/PulseOptimizerApp/Pulse/releases/latest/download/Pulse.exe"
GC = '<script data-goatcounter="https://pulseoptimizer.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'


def esc(s): return html.escape(s, quote=True)


def head(title, desc, url, up, extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/img/og.png">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Pulse">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0E0D0B">
<link rel="icon" type="image/png" sizes="32x32" href="{up}img/favicon-32.png">
<link rel="icon" type="image/svg+xml" href="{up}img/icon-small.svg">
<link rel="preload" href="{up}fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{up}css/site.css">
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="{up}" aria-label="Pulse home">{ICON.format(up=up)}Pulse</a>
    <nav class="links" aria-label="Site">
      <a href="{up}">App</a>
      <a href="{up}fps-calculator/">FPS calculator</a>
      <a href="{up}guides/" aria-current="page">FPS guides</a>
    </nav>
    <div class="right"><a class="btn go sm dl" href="{DL}" data-goatcounter-click="download-guide-nav">Download Pulse</a></div>
  </div>
</header>
"""


def foot(up):
    return f"""
<footer>
  <div class="wrap">
    <p>Pulse is free and open source. Not affiliated with Riot Games, Epic Games, Valve, NVIDIA, AMD or Intel.</p>
    <nav aria-label="Footer"><a href="{up}">Pulse</a><a href="{up}fps-calculator/">FPS calculator</a><a href="{up}guides/">FPS guides</a><a href="https://github.com/PulseOptimizerApp/Pulse">Source</a></nav>
  </div>
</footer>
{GC}
</body>
</html>
"""


def callout(up, where):
    return f"""<div class="callout">
  <div>
    <h3>Let Pulse check all of this for you</h3>
    <p>Pulse finds a monitor stuck at 60 Hz, RAM at its default speed, games on the built-in graphics and background recording, explains each fix, and measures your real FPS before and after. Free, no account.</p>
  </div>
  <a class="btn go dl" href="{DL}" data-goatcounter-click="download-{where}">Download Pulse</a>
</div>"""


def guide(g):
    up = "../../"
    url = f"{SITE}/guides/{g['slug']}/"
    toc = [("windows", "Fix your PC's setup first")] + [(f"s{i}", name) for i, (name, _) in enumerate(g["sections"])] + [(f"x{i}", t) for i, (t, _) in enumerate(g["extra"])]
    faq = [
        (f"What's the single best setting for FPS in {g['game']}?", g["best"]),
        (f"Why is my FPS still low in {g['game']}?", "Usually a setup problem rather than a setting: a monitor running at 60 Hz, memory at its slow default speed, one memory stick, or the monitor plugged into the motherboard. Fix those first; they're worth more than any in-game setting."),
    ]
    ld = {
        "@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
        "dateModified": UPDATED_ISO, "datePublished": UPDATED_ISO, "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "Pulse", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "Pulse", "logo": {"@type": "ImageObject", "url": SITE + "/img/icon-256.png"}},
    }
    ldfaq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    extra = f'<script type="application/ld+json">{json.dumps(ld)}</script>\n<script type="application/ld+json">{json.dumps(ldfaq)}</script>'
    out = [head(g["title"], g["desc"], url, up, extra)]
    out.append(f"""<main id="main" class="wrap narrow">
  <div class="page-head">
    <a class="tag" href="../">FPS guides</a>
    <h1>{esc(g['h1'])}</h1>
    <p class="lead">{esc(g['lead'])}</p>
    <p class="meta">Updated {UPDATED}</p>
  </div>
  <article class="prose">
    <nav class="toc" aria-label="In this guide"><b>In this guide</b><ol>{''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)}</ol></nav>
    <p class="note">{esc(g['intro_note'])}</p>
    <h2 id="windows">Fix your PC's setup first</h2>
    <p>These are worth more than any in-game setting, and they help every game. Most PCs have at least one of them wrong.</p>
    <ol>{''.join(f'<li><strong>{esc(t)}.</strong> {esc(d)}</li>' for t, d in WINDOWS)}</ol>
    {callout(up, 'guide-' + g['slug'])}
""")
    for i, (name, rows) in enumerate(g["sections"]):
        out.append(f'<h2 id="s{i}">{esc(name)}</h2>\n<table class="settings"><thead><tr><th>Setting</th><th>Set it to</th><th>Why</th></tr></thead><tbody>')
        for s, v, why in rows:
            out.append(f"<tr><td>{esc(s)}</td><td>{esc(v)}</td><td>{esc(why)}</td></tr>")
        out.append("</tbody></table>")
    for i, (t, d) in enumerate(g["extra"]):
        out.append(f'<h2 id="x{i}">{esc(t)}</h2>\n<p>{esc(d)}</p>')
    out.append(f"""<h2>What FPS should you expect?</h2>
<p>It depends on your CPU, graphics card and memory. The <a href="{up}fps-calculator/">free FPS calculator</a> shows the frame rate to expect in {esc(g['game'])} and 14 other games for any PC, and what holds it back.</p>
<h2>Questions</h2>
{''.join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in faq)}
<h2>Sources</h2>
<ul>{''.join(f'<li><a href="{u}" rel="noopener">{esc(t)}</a></li>' for t, u in g['sources'])}</ul>
  </article>
  {callout(up, 'guide-end-' + g['slug'])}
  <h2 style="margin-top:56px">More guides</h2>
  <div class="cards">{''.join(card(o, up + 'guides/') for o in GUIDES if o is not g)}</div>
</main>""")
    out.append(foot(up))
    os.makedirs(f"{ROOT}/guides/{g['slug']}", exist_ok=True)
    open(f"{ROOT}/guides/{g['slug']}/index.html", "w").write("".join(out))


def card(g, base):
    return f'<a class="card" href="{base}{g["slug"]}/"><h3>{esc(g["h1"])}</h3><p>{esc(g["desc"])}</p><span class="go-on">Read the guide</span></a>'


def index():
    up = "../"
    title = "FPS guides: the best settings for VALORANT, Fortnite and CS2 (2026)"
    desc = "Free, up-to-date guides to more FPS and less input lag in VALORANT, Fortnite and Counter-Strike 2: the settings that matter, why, and the Windows fixes worth the most frames."
    out = [head(title, desc, f"{SITE}/guides/", up)]
    out.append(f"""<main id="main" class="wrap">
  <div class="page-head">
    <a class="tag" href="./">FPS guides</a>
    <h1>More frames, less lag.</h1>
    <p class="lead">The settings that actually matter in each game, why they matter, and the PC setup fixes that are worth more than any of them. Updated {UPDATED}.</p>
  </div>
  <div class="cards" style="margin-top:0">{''.join(card(g, '') for g in GUIDES)}
    <a class="card" href="{up}fps-calculator/"><h3>FPS calculator</h3><p>Pick any CPU, graphics card and memory and see the FPS to expect in 15 popular games, and what holds the PC back.</p><span class="go-on">Open the calculator</span></a>
  </div>
  {callout(up, 'guides-index')}
</main>""")
    out.append(foot(up))
    open(f"{ROOT}/guides/index.html", "w").write("".join(out))


for g in GUIDES:
    guide(g)
index()
print("ok")
