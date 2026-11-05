"""Demo film for a fictional tree-planting organisation, 20 s, 1920x1080 @ 30 fps, on a 120 BPM bar grid (bars every 2 s).
It exercises every part of the kit: grounds, titles, hand-drawn illustrations with edge boil, a sticker + arrow annotation,
a counter, Three.js particles, a band wipe, a texture-cover transition, a 3D map with routes and labels, and a burst that
follows the map's origin into the end card. All names and figures are placeholders.

    python3 gen.py [--audio assets/mix.wav]      -> index.html + events.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kit"))
from filmkit import Film, Theme  # noqa: E402

FONTS = [("Archivo", 700, "assets/fonts/archivo-latin-700-normal.woff2"), ("Archivo", 800, "assets/fonts/archivo-latin-800-normal.woff2"),
         ("Inter", 400, "assets/fonts/inter-latin-400-normal.woff2"), ("Inter", 500, "assets/fonts/inter-latin-500-normal.woff2"),
         ("Kalam", 700, "assets/fonts/kalam-latin-700-normal.woff2")]
th = Theme(bg="#1F3326", ink="#1C2228", paper="#F7F5F0", accent="#E9A23B", accent2="#5FA36A",
           display="Archivo", body="Inter", hand="Kalam", font_faces=FONTS)
TOTAL = 20.0
film = Film(TOTAL, th, scripts=["assets/gsap.min.js", "assets/MorphSVGPlugin.min.js", "assets/film3d.js", "assets/geo.js"])
ILL = json.load(open(os.path.join(HERE, "assets", "illos.json")))
C0, C1, C2, C3 = 0.0, 6.0, 12.0, 16.0          # chapter starts on bar lines

# ---------------------------------------------------------------- 01 Plant (0 - 6)
film.ground("g0", C0, C1 - C0 + 0.6, "gr0", word="PLANT", word_col="rgba(95,163,106,.20)")
film.title("f0", "t0", 130, 150, "01", "Day one", "Plant.", "Every project starts with one seedling in the ground.", C0 + 0.4, col=th.ink, chip_bg=th.accent)
end0 = film.illo("f0", ILL["sprout"], "il0", 1180, 260, 1.15, C0 + 0.8)
film.note("f0", "n0", 1230, 860, "native species", end0 + 0.2, sticker=True, size=56, rot=-4)
film.arrow("f0", "a0", 1420, 870, 1470, 760, end0 + 0.55, bend=-0.3)
film.container("cf0", "f0", C0, C1 - C0 + 0.5, 40)
film.canvas3d("cv0", C0, C1 - C0, 30)
film.init3d(f"FILM3D.particles('cv0',{{start:{C0},end:{C1},count:500,size:22,color:'#FFF8E1',seed:3,beam:true,fadeIn:0.6,fadeOut:0.5}});")
film.band_wipe("w01", C1 - 0.47, color=th.bg)

# ---------------------------------------------------------------- 02 Grow (6 - 12)
film.ground("g1", C1, C2 - C1 + 0.4, "gr1", word="GROW", word_col="rgba(28,34,40,.10)", z=2)
film.title("f1", "t1", 130, 150, "02", "Year five", "Grow.", "Cared for until the canopy closes.", C1 + 0.5, col=th.ink, chip_bg=th.accent2, style="letters")
film.illo("f1", ILL["tree"], "il1", 1080, 230, 1.0, C1 + 0.8)
film.counter("f1", "s1", 140, 640, 48000, "trees planted (demo figure)", C1 + 2.4, dur=1.4, col=th.ink, label_col=th.ink)
film.container("cf1", "f1", C1, C2 - C1 + 0.2, 40)
film.texture_cover("tc12", "paper.jpg", C2 - 0.7, 1.5, fade_out=0.45)

# ---------------------------------------------------------------- 03 Spread — 3D map (12 - 16)
sites = [([36.95, -0.42], "Nyeri"), ([34.76, -0.09], "Kisumu"), ([36.07, -0.30], "Nakuru"), ([35.27, 0.51], "Eldoret")]
film.raw_clip("labels", C2, C3 - C2 + 0.2, 60, "".join(f'<div class="maplabel" id="lb{i}">{n}</div>' for i, (_, n) in enumerate(sites)))
film.canvas3d("cvm", C2, C3 - C2 + 0.3, 20)
fol = film.burst("bu", "burst.png", C3 - 0.6, follow=True, z=97)
colors = "{land:'#6FAE7E',side:'#2A4A34',neighbour:'#3E5E48',ground:'#22382A',bg:['#3F6B4C','#1F3326','#0E1A12'],fog:'#1F3326',route:'#F2C14E',routeStart:'#FFF1C9',pin:'#F2C14E'}"
film.init3d("FILM3D.map('cvm',{start:%s,end:%s,colors:%s,highStart:true,pull0:0.15,pull1:1.6,viewShift:-420,pushIn:0.9,home:{ll:[36.82,-1.29]},"
            "follow:{el:'%s',t0:%s,t1:%s},cities:[%s]});" % (C2, C3 + 0.3, colors, fol, C3 - 0.6, C3 + 0.6,
            ",".join(f"{{ll:[{ll[0]},{ll[1]}],at:{1.5 + k * 0.2:.2f},label:'lb{k}'}}" for k, (ll, _) in enumerate(sites))))
film.title("f2", "t2", 130, 140, "03", "Ten years on", "Spread.", "", C2 + 1.2, style="blur", size=130, chip_bg=th.accent)
film.container("cf2", "f2", C2, C3 - C2 - 0.3, 61)

# ---------------------------------------------------------------- 04 End card (16 - 20)
film.ground("g3", C3 - 0.05, TOTAL - C3 + 0.05, "gr3", z=90)
film.L("f3").append(f'<div id="brand" style="position:absolute;left:0;width:1920px;top:360px;text-align:center;font-family:{th.display};'
                    f'font-weight:800;font-size:150px;letter-spacing:-5px;color:{th.ink};opacity:0">Northwind</div>')
film.T(f"tl.fromTo('#brand',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.9,ease:'power3.out'}},{C3 + 0.2});")
film.note("f3", "tag", 770, 560, "plant the long game", C3 + 0.9, col=th.accent2, size=84, rot=-2)
film.container("cf3", "f3", C3, TOTAL - C3, 95)
film.fade_out(TOTAL - 1.0, 0.9)

audio = sys.argv[sys.argv.index("--audio") + 1] if "--audio" in sys.argv else None
n = film.write(os.path.join(HERE, "index.html"), audio=audio)
print("wrote index.html", n, "bytes,", len(film.events), "events")
