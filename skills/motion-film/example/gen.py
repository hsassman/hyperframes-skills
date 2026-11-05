"""Demo film — "From seed to cup" for a fictional roaster, 20 s, 1920x1080 @ 30 fps, on a 120 BPM bar grid (bars every 2 s).
It exercises every part of the kit: grounds, titles, hand-drawn illustrations with edge boil, a sticker + arrow annotation,
a counter, Three.js particles, a band wipe, a shutter transition, a 3D map with routes and a burst into the end card.

    python3 gen.py [--audio assets/mix.wav]      -> index.html + events.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kit"))
from filmkit import Film, Theme  # noqa: E402

FONTS = [("Poppins", 600, "assets/fonts/poppins-latin-600-normal.woff2"), ("Poppins", 700, "assets/fonts/poppins-latin-700-normal.woff2"),
         ("Poppins", 800, "assets/fonts/poppins-latin-800-normal.woff2"), ("Inter", 400, "assets/fonts/inter-latin-400-normal.woff2"),
         ("Inter", 500, "assets/fonts/inter-latin-500-normal.woff2"), ("Caveat", 700, "assets/fonts/caveat-latin-700-normal.woff2")]
th = Theme(bg="#0F2A33", ink="#1F2A30", paper="#FAF6F0", accent="#E8743B", accent2="#2BA3B8", font_faces=FONTS)
TOTAL = 20.0
film = Film(TOTAL, th, scripts=["assets/gsap.min.js", "assets/MorphSVGPlugin.min.js", "assets/film3d.js", "assets/geo.js"])
ILL = json.load(open(os.path.join(HERE, "assets", "illos.json")))
C0, C1, C2, C3 = 0.0, 6.0, 12.0, 16.0          # chapter starts on bar lines

# ---------------------------------------------------------------- 00 Grown (0 - 6)
film.ground("g0", C0, C1 - C0 + 0.6, "gr0", word="GROWN", word_col="rgba(232,116,59,.18)")
film.title("f0", "t0", 130, 150, "01", "From seed", "Grown.", "Picked by hand when the cherries turn red.", C0 + 0.4, col=th.ink, chip_bg=th.accent)
end0 = film.illo("f0", ILL["sprout"], "il0", 1180, 260, 1.15, C0 + 0.8)
film.note("f0", "n0", 1230, 860, "hand-picked", end0 + 0.2, sticker=True, size=56, rot=-4)
film.arrow("f0", "a0", 1420, 870, 1470, 760, end0 + 0.55, bend=-0.3)
film.container("cf0", "f0", C0, C1 - C0 + 0.5, 40)
film.canvas3d("cv0", C0, C1 - C0, 30)
film.init3d(f"FILM3D.particles('cv0',{{start:{C0},end:{C1},count:500,size:22,color:'#FFF6E8',seed:3,beam:true,fadeIn:0.6,fadeOut:0.5}});")
film.band_wipe("w01", C1 - 0.47, color=th.bg)

# ---------------------------------------------------------------- 01 Roasted & packed (6 - 12)
film.ground("g1", C1, C2 - C1 + 0.4, "gr1", word="PACKED", word_col="rgba(31,42,48,.12)", z=2)
film.title("f1", "t1", 130, 150, "02", "Roasted", "Packed.", "Roasted in small batches, sealed the same day.", C1 + 0.5, col=th.ink, style="letters")
end1 = film.illo("f1", ILL["parcel"], "il1", 1100, 300, 1.05, C1 + 0.8)
film.counter("f1", "s1", 140, 640, 1200, "bags a week (demo figure)", C1 + 2.4, dur=1.4, col=th.ink, label_col=th.ink)
film.container("cf1", "f1", C1, C2 - C1 + 0.1, 40)
film.shutter("sh12", "shutter.jpg", C2 - 0.56)

# ---------------------------------------------------------------- 02 Shipped — 3D map (12 - 16)
film.raw_clip("labels", C2, C3 - C2 + 0.2, 60, "".join(f'<div class="city" id="lb{i}">{n}</div>' for i, n in enumerate(["Mombasa", "Kisumu", "Nakuru", "Eldoret"])))
film.canvas3d("cvm", C2, C3 - C2 + 0.3, 20)
cities = [([39.66, -4.04], "lb0"), ([34.76, -0.09], "lb1"), ([36.07, -0.30], "lb2"), ([35.27, 0.51], "lb3")]
fol = film.burst("bu", "burst.png", C3 - 0.6, follow=True, z=97)
film.init3d("FILM3D.map('cvm',{start:%s,end:%s,highStart:true,pull0:0.15,pull1:1.6,viewShift:-420,pushIn:0.9,home:{ll:[36.82,-1.29]},"
            "follow:{el:'%s',t0:%s,t1:%s},cities:[%s]});" % (C2, C3 + 0.3, fol, C3 - 0.6, C3 + 0.6,
            ",".join(f"{{ll:[{ll[0]},{ll[1]}],at:{1.5 + k * 0.2:.2f},label:'{lb}'}}" for k, (ll, lb) in enumerate(cities))))
film.title("f2", "t2", 130, 140, "03", "Shipped", "Everywhere.", "", C2 + 1.2, style="blur", size=130)
film.container("cf2", "f2", C2, C3 - C2 - 0.3, 61)

# ---------------------------------------------------------------- 03 End card (16 - 20)
film.ground("g3", C3 - 0.05, TOTAL - C3 + 0.05, "gr3", z=90)
film.L("f3").append('<div id="brand" style="position:absolute;left:0;width:1920px;top:360px;text-align:center;font-family:Poppins;font-weight:800;font-size:150px;letter-spacing:-5px;color:#1F2A30;opacity:0">Northwind</div>')
film.T(f"tl.fromTo('#brand',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.9,ease:'power3.out'}},{C3 + 0.2});")
film.note("f3", "tag", 760, 560, "from seed to cup", C3 + 0.9, col=th.accent, size=96, rot=-2)
film.container("cf3", "f3", C3, TOTAL - C3, 95)
film.fade_out(TOTAL - 1.0, 0.9)

audio = sys.argv[sys.argv.index("--audio") + 1] if "--audio" in sys.argv else None
n = film.write(os.path.join(HERE, "index.html"), audio=audio)
print("wrote index.html", n, "bytes,", len(film.events), "events")
