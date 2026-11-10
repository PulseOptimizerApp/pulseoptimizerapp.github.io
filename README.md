# Pulse website

The website for [Pulse](https://github.com/PulseOptimizerApp/Pulse), served by GitHub Pages at https://pulseoptimizerapp.github.io/.

- `index.html`: the home page (self-contained: inline CSS and JS, self-hosted font). Download buttons point at the newest release that has the exe.
- `fps-calculator/`: the FPS calculator. It reads Pulse's own `hardware.json` from the app repo (falls back to `data/hardware.json`).
- `guides/`: FPS guides, built by `python tools/build_guides.py` (edit the content there, then run it).
- `stats.html`: live download counts and stars from GitHub, and a link to the GoatCounter visits dashboard.
- `guide/guide.json`: live data for the app's PC guide, refreshed nightly by `.github/workflows/refresh-guide.yml`.
- `img/shots/`: app screenshots, rendered from the real app by a test in the Pulse repo (`SiteShots`).
