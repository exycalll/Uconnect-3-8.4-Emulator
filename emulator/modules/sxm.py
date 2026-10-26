import hashlib, io, json, os, queue, re, sqlite3, threading, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime

import handlers as H
from handlers import on

VARIANT = {"VARIANT_DAB": "NO", "VARIANT_ECELL": "NO", "VARIANT_HWTYPE": "B", "VARIANT_MARKET": "NA",
           "VARIANT_MODEL": "VP4", "VARIANT_MODELYEAR": "15", "VARIANT_PRODUCT": "VP4",
           "VARIANT_REVISION": "1", "VARIANT_SDARS": "YES", "VARIANT_TMCPRO": "NO"}


@on("platform", "get_variantinfo")
def platform_variant(dest, args, conn):
    H.B.send("platform", {"get_variantinfo": VARIANT}, conn)


CATS = {"Pop": 1, "Rock": 2, "Hip-Hop/R&B": 3, "Dance/Electronic": 4, "Country": 5,
        "Jazz/Standards": 6, "Classical": 7, "Sports": 8, "Howard Stern": 9, "Comedy": 10,
        "News/Public Radio": 11, "Politics/Issues": 12, "Traffic/Weather": 13, "Ect": 14}

LINEUP = [
    (1, "SiriusXM Preview", "Pop", [("SiriusXM", "Channel Guide"), ("SiriusXM", "Free Preview Weekend")]),
    (2, "SiriusXM Hits 1", "Pop", [("Taylor Swift", "Blank Space"), ("Mark Ronson", "Uptown Funk"),
                                   ("Ed Sheeran", "Thinking Out Loud"), ("Maroon 5", "Sugar")]),
    (3, "Venus", "Pop", [("Jason Derulo", "Want To Want Me"), ("Rihanna", "FourFiveSeconds"), ("Ariana Grande", "One Last Time")]),
    (5, "'50s on 5", "Pop", [("Elvis Presley", "Jailhouse Rock"), ("Buddy Holly", "Peggy Sue"), ("Chuck Berry", "Johnny B. Goode")]),
    (6, "'60s on 6", "Pop", [("The Beatles", "Help!"), ("The Supremes", "Stop! In The Name Of Love"), ("The Beach Boys", "Good Vibrations")]),
    (7, "'70s on 7", "Pop", [("Fleetwood Mac", "Dreams"), ("ABBA", "Dancing Queen"), ("Elton John", "Tiny Dancer")]),
    (8, "'80s on 8", "Pop", [("Michael Jackson", "Billie Jean"), ("a-ha", "Take On Me"),
                             ("Madonna", "Like A Virgin"), ("Duran Duran", "Hungry Like The Wolf")]),
    (9, "'90s on 9", "Pop", [("Nirvana", "Smells Like Teen Spirit"), ("TLC", "Waterfalls"), ("Spice Girls", "Wannabe")]),
    (10, "Pop2K", "Pop", [("OutKast", "Hey Ya!"), ("Britney Spears", "Toxic"), ("Kelly Clarkson", "Since U Been Gone")]),
    (15, "The Pulse", "Pop", [("Coldplay", "Viva La Vida"), ("Adele", "Rolling In The Deep"), ("OneRepublic", "Counting Stars")]),
    (16, "The Blend", "Pop", [("Train", "Hey, Soul Sister"), ("Sara Bareilles", "Love Song"), ("Phil Collins", "Easy Lover")]),
    (20, "Elvis Radio", "Rock", [("Elvis Presley", "Suspicious Minds"), ("Elvis Presley", "Burning Love"), ("Elvis Presley", "Hound Dog")]),
    (24, "Radio Margaritaville", "Rock", [("Jimmy Buffett", "Margaritaville"), ("Kenny Chesney", "No Shoes, No Shirt, No Problems")]),
    (25, "Classic Rewind", "Rock", [("Bon Jovi", "Livin' On A Prayer"), ("Def Leppard", "Pour Some Sugar On Me"), ("Journey", "Separate Ways")]),
    (26, "Classic Vinyl", "Rock", [("Led Zeppelin", "Black Dog"), ("The Who", "Baba O'Riley"), ("Lynyrd Skynyrd", "Free Bird")]),
    (27, "Deep Tracks", "Rock", [("Pink Floyd", "Echoes"), ("The Allman Brothers Band", "Whipping Post"), ("Neil Young", "Cortez The Killer")]),
    (32, "The Bridge", "Rock", [("James Taylor", "Fire And Rain"), ("Eagles", "Peaceful Easy Feeling"), ("Jackson Browne", "Running On Empty")]),
    (34, "Lithium", "Rock", [("Pearl Jam", "Alive"), ("Soundgarden", "Black Hole Sun"), ("Stone Temple Pilots", "Plush")]),
    (36, "Alt Nation", "Rock", [("Imagine Dragons", "Shots"), ("Walk The Moon", "Shut Up And Dance"), ("Twenty One Pilots", "Tear In My Heart")]),
    (37, "Octane", "Rock", [("Shinedown", "Cut The Cord"), ("Disturbed", "The Vengeful One"), ("Breaking Benjamin", "Failure")]),
    (39, "Hair Nation", "Rock", [("Motley Crue", "Dr. Feelgood"), ("Poison", "Talk Dirty To Me"), ("Whitesnake", "Here I Go Again")]),
    (40, "Liquid Metal", "Rock", [("Metallica", "Master Of Puppets"), ("Slayer", "Raining Blood"), ("Pantera", "Walk")]),
    (44, "Hip-Hop Nation", "Hip-Hop/R&B", [("Drake", "Energy"), ("Kendrick Lamar", "King Kunta"), ("Big Sean", "Blessings")]),
    (45, "Shade 45", "Hip-Hop/R&B", [("Eminem", "Lose Yourself"), ("50 Cent", "In Da Club"), ("Dr. Dre", "Still D.R.E.")]),
    (46, "The Heat", "Hip-Hop/R&B", [("The Weeknd", "Earned It"), ("Chris Brown", "Ayo"), ("Usher", "I Don't Mind")]),
    (48, "Heart & Soul", "Hip-Hop/R&B", [("Alicia Keys", "No One"), ("John Legend", "All Of Me"), ("Mary J. Blige", "Be Without You")]),
    (51, "BPM", "Dance/Electronic", [("Calvin Harris", "Summer"), ("David Guetta", "Titanium"), ("Avicii", "Wake Me Up")]),
    (52, "Electric Area", "Dance/Electronic", [("Hardwell", "Spaceman"), ("Tiesto", "Red Lights"), ("Armin van Buuren", "Ping Pong")]),
    (56, "The Highway", "Country", [("Luke Bryan", "Kick The Dust Up"), ("Florida Georgia Line", "Sun Daze"),
                                    ("Carrie Underwood", "Smoke Break"), ("Sam Hunt", "Take Your Time")]),
    (58, "Prime Country", "Country", [("George Strait", "Check Yes Or No"), ("Alan Jackson", "Chattahoochee"), ("Brooks & Dunn", "Neon Moon")]),
    (59, "Willie's Roadhouse", "Country", [("Willie Nelson", "On The Road Again"), ("Patsy Cline", "Crazy"), ("Merle Haggard", "Mama Tried")]),
    (60, "Outlaw Country", "Country", [("Johnny Cash", "Folsom Prison Blues"), ("Waylon Jennings", "Luckenbach, Texas"), ("Steve Earle", "Copperhead Road")]),
    (67, "Real Jazz", "Jazz/Standards", [("Miles Davis", "So What"), ("John Coltrane", "Naima"), ("Dave Brubeck", "Take Five")]),
    (71, "Siriusly Sinatra", "Jazz/Standards", [("Frank Sinatra", "Fly Me To The Moon"), ("Tony Bennett", "The Way You Look Tonight"), ("Dean Martin", "That's Amore")]),
    (76, "Symphony Hall", "Classical", [("Beethoven", "Symphony No. 5"), ("Mozart", "Eine kleine Nachtmusik"), ("Dvorak", "New World Symphony")]),
    (80, "ESPN Radio", "Sports", [("Mike & Mike", "NFL Week 6 Preview"), ("SportsCenter", "Top Headlines")]),
    (83, "FOX Sports Radio", "Sports", [("The Herd", "Playoff Picture"), ("Fox Sports Update", "Scores And Highlights")]),
    (88, "SiriusXM NFL Radio", "Sports", [("Movin' The Chains", "Week 6 Breakdown"), ("Opening Drive", "Injury Report")]),
    (89, "MLB Network Radio", "Sports", [("Inside Pitch", "ALCS Game 3"), ("Power Alley", "Postseason Talk")]),
    (94, "Comedy Greats", "Comedy", [("George Carlin", "Stuff"), ("Richard Pryor", "Live On The Sunset Strip")]),
    (96, "Laugh USA", "Comedy", [("Jim Gaffigan", "Hot Pockets"), ("Brian Regan", "Stupid In School")]),
    (99, "Raw Dog Comedy", "Comedy", [("Louis C.K.", "Hilarious"), ("Bill Burr", "Why Do I Do This?")]),
    (100, "Howard 100", "Howard Stern", [("The Howard Stern Show", "Live"), ("Howard 100 News", "Wrap-Up")]),
    (101, "Howard 101", "Howard Stern", [("Howard Stern Show", "Replay"), ("Bad Boy Hour", "Special")]),
    (114, "FOX News Channel", "News/Public Radio", [("FOX News", "America's Newsroom"), ("FOX News", "The Five")]),
    (116, "CNN", "News/Public Radio", [("CNN", "Newsroom"), ("CNN", "The Situation Room")]),
    (124, "POTUS", "Politics/Issues", [("POTUS", "Morning Briefing"), ("POTUS", "Campaign 2016")]),
    (134, "Chicago Traffic/Weather", "Traffic/Weather", [("Traffic & Weather", "Chicago Area Report")]),
    (136, "Detroit Traffic/Weather", "Traffic/Weather", [("Traffic & Weather", "Detroit Area Report")]),
    (138, "New York Traffic/Weather", "Traffic/Weather", [("Traffic & Weather", "New York Area Report")]),
    (-1, "Discord", "Ect", [("Join the Community", "discord.gg/X66nKtjwpW")]),
]
CH = {c[0]: c for c in LINEUP}
NUMS = [c[0] for c in LINEUP]
STATIC_CAT = {c[0]: c[2] for c in LINEUP}
STATIC_SONGS = {c[0]: c[3] for c in LINEUP}
STATIC_NAME = {c[0]: c[1] for c in LINEUP}

_persisted_xm = H.B.PERSIST.get("XMFavorites", {})
_saved_favs = _persisted_xm.get("allFavorites", [])
_max_fav_id = max([f.get("id", 0) for f in _saved_favs], default=0)

XM = {"channel": -1, "previous": 8, "presets": [41, 37, 34, 27, 10, -1, 45, 50, 46, 49, 153, 6],
      "skipped": [], "favorites": _saved_favs, "fav_id": _max_fav_id, "market": 0, "jump_from": None}


def _save_persist_favorites():
    if "XMFavorites" not in H.B.PERSIST:
        H.B.PERSIST["XMFavorites"] = {}
    H.B.PERSIST["XMFavorites"]["allFavorites"] = XM["favorites"]
    try:
        with open(H.B.PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(H.B.PERSIST, f, indent=1)
    except Exception as e:
        _log(f"failed to save favs: {e}")


def favorites_publish():
    xm_set("XMFavorites", "allFavorites", XM["favorites"])
    active = []
    for n in NUMS:
        artist, title = now_playing(n)
        for f in XM["favorites"]:
            if (f["favoriteType"] == "song" and f["song"] == title) or (f["favoriteType"] == "artist" and f["artist"] == artist):
                active.append({"channel": n, "artist": artist, "song": title,
                               "isActiveArtist": f["favoriteType"] == "artist", "isActiveSong": f["favoriteType"] == "song"})
                break
    xm_set("XMFavorites", "activeFavorites", active)
    publish_current()
    _save_persist_favorites()


def _add_favorite(kind, args):
    num = int(args.get("newFavorite", XM["channel"]))
    artist, title = now_playing(num if num in CH else XM["channel"])
    if _xmp_fault() or not (title if kind == "song" else artist):
        return
    if not any(f["favoriteType"] == kind and f["song" if kind == "song" else "artist"] == (title if kind == "song" else artist)
               for f in XM["favorites"]):
        XM["fav_id"] += 1
        XM["favorites"].append({"id": XM["fav_id"], "favoriteType": kind, "artist": artist,
                                "song": title if kind == "song" else ""})
    favorites_publish()


@on("XMFavorites", "setFavoriteSong")
def fav_song(dest, args, conn):
    _add_favorite("song", args)


@on("XMFavorites", "setFavoriteArtist")
def fav_artist(dest, args, conn):
    _add_favorite("artist", args)


@on("XMFavorites", "getProperties")
def fav_get_properties(dest, args, conn):
    active = []
    for n in NUMS:
        artist, title = now_playing(n)
        for f in XM["favorites"]:
            if (f["favoriteType"] == "song" and f["song"] == title) or (f["favoriteType"] == "artist" and f["artist"] == artist):
                active.append({"channel": n, "artist": artist, "song": title,
                               "isActiveArtist": f["favoriteType"] == "artist", "isActiveSong": f["favoriteType"] == "song"})
                break
    H.B.send("XMFavorites", {
        "getProperties": {
            "allFavorites": XM["favorites"],
            "activeFavorites": active,
            "favAllowed": {"isArtistAllowed": True, "isSongAllowed": True}
        }
    }, conn)


@on("XMFavorites", "Subscribe")
def fav_subscribe(dest, args, conn):
    favorites_publish()


@on("XMFavorites", "removeFavorite")
def fav_remove(dest, args, conn):
    XM["favorites"] = [f for f in XM["favorites"] if f["id"] != int(args.get("id", -1))]
    favorites_publish()


@on("XMFavorites", "removeAllFavorites")
def fav_remove_all(dest, args, conn):
    XM["favorites"] = []
    favorites_publish()


ESN = "0R7X9C2KQ4"


XMP_ON = os.environ.get("XMPLAYLIST", "1") != "0"
XMP_DEBUG = os.environ.get("XMP_DEBUG") == "1"
XMP_BASE = "https://xmplaylist.com/api"
XMP_UA = "sxm-hmi-emulator/1.0"
XMP_FEED_EVERY = 90
XMP_FEED_PAGES = 1
XMP_STATION_REFRESH = 6 * 3600
XMP_MAX_AGE = 30 * 60
XMP_FAULT_AFTER = 5 * 60
XMP_FAULT = ("xmplaylist.com api fault", "contact olithebest12")
ART_AS_LOGO = True

LIVE = {}
STN_IMG = {}
_DEEPLINK = {}
_BY_DEEPLINK = {}
_LINEUP_LIVE = False
_XMP_INIT_OK = False
_XMP_STATE = {"ok_at": 0.0}
_XMP_WAKE = threading.Event()
_ART = {"ver": 0}
_ART_Q = queue.PriorityQueue()
_ART_SEEN = set()
_ART_N = [0]

_PAGE_HOSTS = ("open.spotify.com", "music.apple.com", "itunes.apple.com", "www.youtube.com", "youtube.com",
               "music.youtube.com", "www.deezer.com", "deezer.com", "tidal.com", "listen.tidal.com", "pandora.com",
               "www.pandora.com", "www.amazon.com", "music.amazon.com", "soundcloud.com", "www.qobuz.com")
_IMG_KEY = re.compile(r"image|img|artwork|album_?art|cover|thumb|icon|logo|pic|small|medium|large", re.I)


def _log(msg):
    try:
        H.B.log("xm", msg)
    except Exception:
        pass
    print(f"[xmplaylist] {msg}", flush=True)


def _xmp_get(path_or_url):
    url = path_or_url if path_or_url.startswith("http") else XMP_BASE + path_or_url
    if urllib.parse.urlparse(url).hostname not in ("xmplaylist.com", "www.xmplaylist.com"):
        raise ValueError(f"refusing foreign url {url}")
    req = urllib.request.Request(url, headers={"User-Agent": XMP_UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def _results(data):
    if isinstance(data, dict):
        r = data.get("results", [])
        return r if isinstance(r, list) else []
    return data if isinstance(data, list) else []


def _find_image(o, hit=False):
    if isinstance(o, str):
        if hit and o.startswith(("http://", "https://")) and urllib.parse.urlparse(o).hostname not in _PAGE_HOSTS:
            return o
        return None
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("links", "link", "channel"):
                continue
            r = _find_image(v, hit or bool(_IMG_KEY.search(str(k))))
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = _find_image(v, hit)
            if r:
                return r
    return None


GENRE_CAT = {"pop": "Pop", "rock": "Rock", "hiphop": "Hip-Hop/R&B", "dance": "Dance/Electronic",
             "country": "Country", "jazz": "Jazz/Standards", "comedy": "Comedy"}


def _cat(name):
    slug = name.strip().lower()
    if slug in GENRE_CAT:
        return GENRE_CAT[slug]
    new = " ".join(w.capitalize() for w in slug.replace("-", " ").split()) or "Other"
    if new not in CATS:
        CATS[new] = max(CATS.values()) + 1
    return new


def _station_category(s, n):
    for k in ("genre", "category", "categories", "genres"):
        v = s.get(k)
        if isinstance(v, list) and v:
            v = v[0]
        if isinstance(v, dict):
            v = v.get("name") or v.get("title")
        if isinstance(v, str) and v.strip():
            return _cat(v.strip())
    return _cat(STATIC_CAT.get(n) or "Other")


ART_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sdars", "channelart")
XMP_ART_DIR = os.path.join(ART_DIR, "xmp")


def _cached_image(url, prio=1):
    if not url or not XMP_ON:
        return None
    h = hashlib.sha1(url.encode()).hexdigest()[:16]
    for ext in (".png", ".jpg"):
        p = os.path.join(XMP_ART_DIR, h + ext)
        if os.path.exists(p):
            return p
    if url not in _ART_SEEN and len(_ART_SEEN) < 20000:
        _ART_SEEN.add(url)
        _ART_N[0] += 1
        _ART_Q.put((prio, _ART_N[0], url))
    return None


def _art_worker():
    os.makedirs(XMP_ART_DIR, exist_ok=True)
    try:
        import PIL.Image
        have_pil = True
    except ImportError:
        have_pil = False
        _log("pillow missing, webp skipped")
    while True:
        _, _, url = _ART_Q.get()
        if not have_pil and urllib.parse.urlparse(url).path.lower().endswith(".webp"):
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": XMP_UA})
            with urllib.request.urlopen(req, timeout=10) as r:
                ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                data = r.read(8_000_000)
            if not ctype.startswith("image/"):
                raise ValueError(f"not an image ({ctype})")
            h = hashlib.sha1(url.encode()).hexdigest()[:16]
            if ctype in ("image/jpeg", "image/jpg"):
                path = os.path.join(XMP_ART_DIR, h + ".jpg")
            else:
                path = os.path.join(XMP_ART_DIR, h + ".png")
                if ctype != "image/png":
                    from PIL import Image
                    buf = io.BytesIO()
                    Image.open(io.BytesIO(data)).convert("RGBA").save(buf, "PNG")
                    data = buf.getvalue()
            tmp = path + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            _ART["ver"] += 1
        except Exception as e:
            _log(f"art error {e!r}")
        time.sleep(0.05)


def _local_url(path):
    return "file:///" + path.replace("\\", "/")


def _set_lineup(ch, deeplinks, imgs):
    global CH, NUMS, _LINEUP_LIVE, _DEEPLINK, _BY_DEEPLINK
    CH, NUMS = ch, sorted(ch)
    _DEEPLINK = deeplinks
    _BY_DEEPLINK = {d.lower(): n for n, d in deeplinks.items()}
    STN_IMG.clear()
    STN_IMG.update(imgs)
    _LINEUP_LIVE = True
    XM["skipped"] = [n for n in XM["skipped"] if n in CH]
    XM["presets"] = [n if n in CH else 0 for n in XM["presets"]]
    if XM["channel"] not in CH:
        XM["channel"] = 2 if 2 in CH else NUMS[0]
    if XM["previous"] not in CH:
        XM["previous"] = XM["channel"]


def _apply_lineup(ch, deeplinks, imgs):
    _set_lineup(ch, deeplinks, imgs)
    xm_set("XMApp", "availableChannelList", NUMS)
    xm_set("XMApp", "skippedChannelList", XM["skipped"])
    xm_set("XMPresets", "localXMPresetList", presets_payload())
    publish_lineup()
    publish_current()


def _xmp_refresh_stations(publish=True):
    data = _xmp_get("/station")
    items = list(_results(data))
    for _ in range(4):
        nxt = data.get("next") if isinstance(data, dict) else None
        if not nxt:
            break
        data = _xmp_get(nxt)
        items += _results(data)
    if XMP_DEBUG and items:
        _log(f"station keys: {sorted(items[0])}")
    ch, deeplinks, imgs = {}, {}, {}
    for s in items:
        if not isinstance(s, dict):
            continue
        try:
            n = int(s.get("number"))
        except (TypeError, ValueError):
            continue
        if n in ch:
            continue
        name = str(s.get("name") or "").strip() or f"Channel {n}"
        ch[n] = (n, name, _station_category(s, n), STATIC_SONGS.get(n, []))
        dl = str(s.get("deeplink") or "").strip()
        if dl:
            deeplinks[n] = dl
        img = s.get("imageUrl") or _find_image(s)
        if img:
            imgs[n] = img

    ch[-1] = (-1, "Discord", "Ect", [("Join the Community", "discord.gg/X66nKtjwpW")])
    SHORT[-1] = "Disco."

    if not ch:
        raise ValueError("empty station list")
    (_apply_lineup if publish else _set_lineup)(ch, deeplinks, imgs)
    _log(f"lineup synced: {len(ch)} chans")


def _track_art(item):
    sp = item.get("spotify")
    if isinstance(sp, dict):
        for k in ("albumImageMedium", "albumImageLarge", "albumImageSmall"):
            if isinstance(sp.get(k), str) and sp[k].startswith("http"):
                return sp[k]
    return _find_image(item.get("track"))


def _parse_item(item):
    t = item.get("track")
    if not isinstance(t, dict):
        return None
    title = str(t.get("title") or "").strip()
    if not title:
        return None
    a = t.get("artists")
    if isinstance(a, list):
        artist = ", ".join(str(x.get("name") if isinstance(x, dict) else x) for x in a)
    elif isinstance(a, str):
        artist = a
    else:
        artist = str(t.get("artist") or "")
    art = _track_art(item)
    try:
        played = datetime.fromisoformat(str(item.get("timestamp")).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        played = time.time()
    return artist.strip(), title, art, played


def _item_channel(item):
    c = item.get("channel")
    n = dl = None
    if isinstance(c, dict):
        n, dl = c.get("number"), c.get("deeplink")
    elif isinstance(c, str):
        dl = c
    dl = dl or item.get("channelId") or item.get("channel_id")
    try:
        return int(n)
    except (TypeError, ValueError):
        return _BY_DEEPLINK.get(str(dl).lower()) if dl else None


def _store(num, parsed):
    artist, title, art, played = parsed
    old = LIVE.get(num)
    if old and old[3] > played:
        return
    LIVE[num] = (artist, title, art, played, time.time())
    if art:
        _cached_image(art, prio=0)


def _xmp_refresh_feed():
    url, seen = "/feed", 0
    for _ in range(XMP_FEED_PAGES):
        data = _xmp_get(url)
        items = [i for i in _results(data) if isinstance(i, dict)]
        for item in sorted(items, key=lambda i: str(i.get("timestamp") or ""), reverse=True):
            n, p = _item_channel(item), _parse_item(item)
            if n in CH and p:
                _store(n, p)
                seen += 1
        url = data.get("next") if isinstance(data, dict) else None
        if not url:
            break
    if not seen:
        raise ValueError("empty feed")
    _XMP_STATE["ok_at"] = time.time()


def _xmp_fault():
    return XMP_ON and (not _LINEUP_LIVE or time.time() - _XMP_STATE["ok_at"] > XMP_FAULT_AFTER)


def _xmp_refresh_station(num):
    dl = _DEEPLINK.get(num)
    if not dl:
        return
    data = _xmp_get("/station/" + urllib.parse.quote(dl))
    items = sorted((i for i in _results(data) if isinstance(i, dict)),
                   key=lambda i: str(i.get("timestamp") or ""), reverse=True)
    for item in items:
        p = _parse_item(item)
        if p:
            _store(num, p)
            return


def _xmp_poller():
    next_feed = next_stations = backoff = 0
    if _XMP_INIT_OK:
        next_stations, next_feed = time.time() + XMP_STATION_REFRESH, time.time() + XMP_FEED_EVERY
    last_station_poll = {}
    while True:
        _XMP_WAKE.wait(5)
        _XMP_WAKE.clear()
        now = time.time()
        if now < backoff:
            continue
        try:
            if now >= next_stations:
                _xmp_refresh_stations()
                next_stations = now + XMP_STATION_REFRESH
            if now >= next_feed:
                _xmp_refresh_feed()
                next_feed = now + XMP_FEED_EVERY
            cur = XM["channel"]
            e = LIVE.get(cur)
            if (cur in _DEEPLINK and (not e or now - e[4] > XMP_FEED_EVERY)
                    and now - last_station_poll.get(cur, 0) > XMP_FEED_EVERY):
                last_station_poll[cur] = now
                _xmp_refresh_station(cur)
        except urllib.error.HTTPError as e:
            backoff = now + (180 if e.code == 429 else 60)
        except Exception:
            backoff = now + 60


def now_playing(num):
    if num == -1:
        return "Join the Community", "discord.gg/X66nKtjwpW"
    if _xmp_fault():
        return XMP_FAULT
    e = LIVE.get(num)
    if e and time.time() - e[3] < XMP_MAX_AGE:
        return e[0], e[1]
    songs = CH[num][3] if num in CH else []
    if songs and not _LINEUP_LIVE:
        length = 170 + (num * 37) % 100
        return songs[(int(time.time()) + num * 53) // length % len(songs)]
    return "", ""


def album_art(num):
    if num == -1:
        discord_art_path = os.path.join(ART_DIR, "discord.png")
        if os.path.exists(discord_art_path):
            return discord_art_path
    if _xmp_fault():
        return None
    e = LIVE.get(num)
    if e and e[2] and time.time() - e[3] < XMP_MAX_AGE:
        return _cached_image(e[2], prio=0)
    return None


SHORT = {1: "Preview", 2: "Hits 1", 3: "Venus", 5: "50s on 5", 6: "60s on 6", 7: "70s on 7", 8: "80s on 8",
         9: "90s on 9", 10: "Pop2K", 15: "Pulse", 16: "Blend", 20: "Elvis", 24: "Margvlle", 25: "Rewind",
         26: "Vinyl", 27: "DeepTrks", 32: "Bridge", 34: "Lithium", 36: "AltNation", 37: "Octane", 39: "HairNatn",
         40: "LiqMetal", 44: "HipHopNtn", 45: "Shade 45", 46: "The Heat", 48: "HrtSoul", 51: "BPM", 52: "Electric",
         56: "Highway", 58: "PrimeCtry", 59: "Willie's", 60: "Outlaw", 67: "RealJazz", 71: "Sinatra",
         76: "Symphony", 80: "ESPN", 83: "FOXSports", 88: "NFL", 89: "MLB", 94: "ComedyGr", 96: "LaughUSA",
         99: "Raw Dog", 100: "Howard100", 101: "Howard101", 114: "FOX News", 116: "CNN", 124: "POTUS",
         134: "CHI T/W", 136: "DET T/W", 138: "NYC T/W", -1: "Disco."}


LOGO_SID = {1: 1, 2: 13, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 30, 15: 26, 16: 155, 20: 18, 24: 91, 25: 49, 26: 46,
            27: 40, 32: 25, 34: 54, 36: 34, 37: 48, 39: 41, 40: 42, 44: 65, 45: 66, 46: 67, 48: 62, 51: 81, 52: 80,
            56: 16, 58: 17, 59: 10, 60: 12, 67: 70, 71: 73, 76: 110, 80: 140, 83: 142, 88: 55, 89: 175, 96: 151,
            99: 150, 100: 33, 101: 36, 114: 122, 116: 134, 124: 130, 134: 148, 136: 148, 138: 148}


def _logo_files():
    try:
        db = sqlite3.connect(os.path.join(ART_DIR, "channelart.db"))
        rows = db.execute("select source, imageId from image_assoc where srcType=0 and imageType=0").fetchall()
        db.close()
    except sqlite3.Error:
        return {}
    files = {sid: os.path.join(ART_DIR, f"I{img:05d}T00.png") for sid, img in rows}
    return {sid: f for sid, f in files.items() if os.path.exists(f)}


LOGOS = _logo_files()


def logo_url(num):
    if num == -1:
        discord_logo_path = os.path.join(ART_DIR, "discord.png")
        if os.path.exists(discord_logo_path):
            return _local_url(discord_logo_path)
    stock = LOGOS.get(LOGO_SID.get(num)) if (not _LINEUP_LIVE or CH[num][1] == STATIC_NAME.get(num)) else None
    f = _cached_image(STN_IMG.get(num)) or stock
    return _local_url(f) if f else "channelart/none.png"


def _short(num):
    name = CH[num][1]
    if not _LINEUP_LIVE or name == STATIC_NAME.get(num):
        s = SHORT.get(num)
        if s:
            return s
    return name.replace("SiriusXM ", "")[:9]


def station(num, full=False):
    n, name, cat, _ = CH[num]
    artist, title = now_playing(n)
    favs = XM["favorites"]
    art = album_art(n)
    st = {"channelID": n, "sid": 1000 + n, "channelName": name, "shortName": _short(n), "catName": cat,
          "catNum": CATS[cat], "artist": artist, "program": title, "isSubscribed": True,
          "isSongFavorite": bool(title) and any(f["favoriteType"] == "song" and f["song"] == title for f in favs),
          "isArtistFavorite": bool(artist) and any(f["favoriteType"] == "artist" and f["artist"] == artist for f in favs),
          "logoLocation": _local_url(art) if (art and ART_AS_LOGO and n == XM["channel"]) else logo_url(n),
          "albumArt": _local_url(art) if art else ""}
    if full:
        st["info"] = ""
        st["presetNum"] = XM["presets"].index(n) if n in XM["presets"] else 255
    return st


def xm_set(module, key, value, conn=None):
    H.B.mod(module)[key] = value
    H.B.send(module, {key: value}, conn)


def publish_current():
    xm_set("XMApp", "currentStationInfo", station(XM["channel"], True))


def publish_lineup():
    xm_set("XMApp", "stationInfoList", [station(n) for n in NUMS])


def presets_payload():
    return [{"channelID": n or 65535, "text": _short(n) if n in CH else ""} for n in XM["presets"]]


def tune(num):
    if num not in CH or num == XM["channel"]:
        return publish_current()
    XM["previous"], XM["channel"] = XM["channel"], num
    IR.update(fill=0, behind=0, paused=False)
    publish_current()
    ir_publish()
    _XMP_WAKE.set()


def _step(up):
    order = [n for n in NUMS if n not in XM["skipped"] and n != 1]
    if not order:
        return XM["channel"]
    i = order.index(XM["channel"]) if XM["channel"] in order else 0
    return order[(i + (1 if up else -1)) % len(order)]


@on("XMApp", "channelSelect")
def xm_select(dest, args, conn):
    tune(int(args.get("station", XM["channel"])))


@on("XMApp", "tunePreviousChannel")
def xm_prev(dest, args, conn):
    tune(XM["previous"])


@on("XMApp", "seekUpPress")
def xm_seek_up(dest, args, conn):
    tune(_step(True))


@on("XMApp", "seekDownPress")
def xm_seek_down(dest, args, conn):
    tune(_step(False))


@on("XMApp", "presetRecall")
def xm_preset_recall(dest, args, conn):
    p = int(args.get("presetNum", -1))
    if 0 <= p < 12 and XM["presets"][p]:
        tune(XM["presets"][p])


def _preset_step(up):
    filled = [n for n in XM["presets"] if n in CH]
    if filled:
        i = filled.index(XM["channel"]) if XM["channel"] in filled else -1
        tune(filled[(i + (1 if up else -1)) % len(filled)])


@on("XMApp", "presetSeekUp")
def xm_preset_up(dest, args, conn):
    _preset_step(True)


@on("XMApp", "presetSeekDown")
def xm_preset_down(dest, args, conn):
    _preset_step(False)


@on("XMPresets", "presetStore")
def xm_preset_store(dest, args, conn):
    p, ch = int(args.get("presetNum", -1)), int(args.get("channelNum", 65535))
    if 0 <= p < 12:
        XM["presets"][p] = ch if ch in CH else 0
        xm_set("XMPresets", "localXMPresetList", presets_payload())
        publish_current()


def _channel_list(args):
    v = args.get("channelList", [])
    return [int(x) for x in (v if isinstance(v, list) else str(v).strip("[]").split(",") if str(v).strip("[]") else [])]


@on("XMApp", "skipChannel")
def xm_skip(dest, args, conn):
    XM["skipped"] = sorted(set(XM["skipped"]) | set(_channel_list(args)))
    xm_set("XMApp", "skippedChannelList", XM["skipped"])


@on("XMApp", "clearSkipChannel")
def xm_unskip(dest, args, conn):
    XM["skipped"] = [n for n in XM["skipped"] if n not in _channel_list(args)]
    xm_set("XMApp", "skippedChannelList", XM["skipped"])


@on("XMApp", "getFeaturedFavoritesList")
def xm_featured_list(dest, args, conn):
    H.B.emit("XMApp", "featuredFavoritesList", conn)


FEATURED = {1: [2, 8, 26, 56], 2: [80, 88, 89, 83]}


@on("XMApp", "getFeaturedFav")
def xm_featured(dest, args, conn):
    chans = [n for n in FEATURED.get(int(args.get("bandID", 0)), []) if n in CH]
    H.B.send("XMApp", {"featureFavorite": {"list": [{"channelID": n, "name": CH[n][1]} for n in chans]}}, conn)


for _cmd in ("seekRelease", "scanUp", "scanDown", "scanCancel", "setCategoryFilter", "setTimeZoneOffset",
             "requestEnableICSTuning", "requestDisableICSTuning", "enableSmartFavs", "disableSmartFavs",
             "lockChannel", "clearLockChannel"):
    H._pending.append(("XMApp", _cmd, lambda dest, args, conn: None))


MARKETS = [{"uniqueID": 1, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 2, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 3, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 4, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 5, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 6, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 7, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 8, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2},
           {"uniqueID": 9, "marketID": "N/A", "marketName": "Depricated Service", "channel": -2}]


@on("XMTrafficJump", "selectTrafficMarket")
def tj_select(dest, args, conn):
    XM["market"] = int(args.get("marketID", 0))
    xm_set("XMTrafficJump", "selectedMarket", XM["market"])
    xm_set("XMTrafficJump", "jumpStatus", "JUMP_IDLE")


@on("XMTrafficJump", "clearTrafficMarkets")
def tj_clear(dest, args, conn):
    XM["market"] = 0
    xm_set("XMTrafficJump", "selectedMarket", 0)
    xm_set("XMTrafficJump", "jumpStatus", "JUMP_MARKET_NOT_SELECTED")


@on("XMTrafficJump", "trafficJumpPress")
def tj_press(dest, args, conn):
    m = next((m for m in MARKETS if m["uniqueID"] == XM["market"]), None)
    if not m:
        return H.B.send("XMTrafficJump", {"trafficJumpPress": {"CmdResponse": {"errCode": "eNoMarketSelected"}}}, conn)
    H.B.send("XMTrafficJump", {"trafficJumpPress": {"CmdResponse": {"errCode": "eSuccess"}}}, conn)
    if XM["jump_from"] is None:
        XM["jump_from"] = XM["channel"]
        xm_set("XMTrafficJump", "jumpStatus", "JUMP_IN_PROGRESS")
        tune(m["channel"])
    else:
        tj_cancel(dest, args, conn)


@on("XMTrafficJump", "cancelJump")
def tj_cancel(dest, args, conn):
    H.B.send("XMTrafficJump", {"cancelJump": {"CmdResponse": {"errCode": "eSuccess"}}}, conn)
    if XM["jump_from"] is not None:
        back, XM["jump_from"] = XM["jump_from"], None
        tune(back)
        xm_set("XMTrafficJump", "jumpStatus", "JUMP_COMPLETED")
    xm_set("XMTrafficJump", "jumpStatus", "JUMP_IDLE" if XM["market"] else "JUMP_MARKET_NOT_SELECTED")


LEAGUES = [{"abbrev": "MLB", "name": "Major League Baseball", "contentDescriptor": 1},
           {"abbrev": "NBA", "name": "National Basketball Association", "contentDescriptor": 2},
           {"abbrev": "NFL", "name": "National Football League", "contentDescriptor": 3},
           {"abbrev": "NHL", "name": "National Hockey League", "contentDescriptor": 4}]
TEAMS = {1: [("Detroit", "Tigers"), ("Chicago", "Cubs"), ("New York", "Yankees"), ("Kansas City", "Royals")],
         2: [("Detroit", "Pistons"), ("Chicago", "Bulls"), ("Golden State", "Warriors"), ("Cleveland", "Cavaliers")],
         3: [("Detroit", "Lions"), ("Chicago", "Bears"), ("Green Bay", "Packers"), ("New England", "Patriots")],
         4: [("Detroit", "Red Wings"), ("Chicago", "Blackhawks"), ("New York", "Rangers"), ("Boston", "Bruins")]}
GZ = {"favorites": []}


def gz_favorites_payload():
    out = [{"leagueDescriptor": lg, "teamDescriptor": tid, "alertType": at, "teamName": TEAMS[lg][tid][0],
            "teamNick": TEAMS[lg][tid][1]} for lg, tid, at in GZ["favorites"]]
    return {"currentTeamFavorites": out}


@on("XMGameZone", "requestLeagueList")
def gz_leagues(dest, args, conn):
    H.B.send("XMGameZone", {"leagueList": LEAGUES}, conn)


@on("XMGameZone", "requestTeamList")
def gz_teams(dest, args, conn):
    lg = int(args.get("contentDescriptor", 1))
    favs = {(l, t): a for l, t, a in GZ["favorites"]}
    teams = [{"league": lg, "teamID": i, "teamName": c, "teamNick": n, "alertType": favs.get((lg, i), "NONE")}
             for i, (c, n) in enumerate(TEAMS.get(lg, []))]
    H.B.send("XMGameZone", {"teamList": teams}, conn)


GZ_CHANNEL = {1: 89, 2: 80, 3: 88, 4: 83}


def gz_scores():
    out = []
    for lg, tid, _ in GZ["favorites"]:
        home, away = TEAMS[lg][tid], TEAMS[lg][(tid + 1) % len(TEAMS[lg])]
        out.append({"channel": GZ_CHANNEL[lg], "teams": f"{away[1]} at {home[1]}",
                    "scores": f"{(tid * 3 + lg) % 6} - {(tid + 2 * lg) % 5}"})
    return out


def _gz_publish():
    xm_set("XMGameZone", "currentTeamFavorites", gz_favorites_payload())
    xm_set("XMGameZone", "activeScores", gz_scores())


@on("XMGameZone", "setFavoriteTeam")
def gz_add(dest, args, conn):
    key = (int(args["leagueDescriptor"]), int(args["teamDescriptor"]))
    if key[0] in TEAMS and key[1] < len(TEAMS[key[0]]) and key not in [(l, t) for l, t, _ in GZ["favorites"]]:
        GZ["favorites"].append(key + (args.get("alertType", "GAME_SCORE"),))
    _gz_publish()


@on("XMGameZone", "removeFavTeam")
def gz_remove(dest, args, conn):
    key = (int(args["leagueDescriptor"]), int(args["teamDescriptor"]))
    GZ["favorites"] = [f for f in GZ["favorites"] if f[:2] != key]
    _gz_publish()


@on("XMGameZone", "removeAllTeams")
def gz_remove_all(dest, args, conn):
    GZ["favorites"] = []
    _gz_publish()


@on("XMGameZone", "enableGlobalGameAlert")
def gz_game_alert(dest, args, conn):
    xm_set("XMGameZone", "globalGameAlertStatus", {"Status": args.get("Status") in (True, "true")})


@on("XMGameZone", "enableGlobalScoreAlert")
def gz_score_alert(dest, args, conn):
    xm_set("XMGameZone", "globalScoreAlertStatus", {"Status": args.get("Status") in (True, "true")})


FUEL_DATA = [
    {"stationID": 1, "name": "Shell", "address": "123 Main St", "distance": "1.2 mi", "regular": "3.49", "midGrade": "3.79", "premium": "4.09", "diesel": "3.89"},
    {"stationID": 2, "name": "Exxon", "address": "456 Oak Ave", "distance": "2.5 mi", "regular": "3.45", "midGrade": "3.75", "premium": "4.05", "diesel": "3.85"},
    {"stationID": 3, "name": "Chevron", "address": "789 Pine Rd", "distance": "3.1 mi", "regular": "3.55", "midGrade": "3.85", "premium": "4.15", "diesel": "3.95"}
]

WEATHER_CURRENT = {"temperature": "67°F", "condition": "Sunny", "humidity": "45%", "wind": "NE 8 mph"}
WEATHER_3_6HR = [
    {"time": "12:00 PM", "temp": "68°F", "condition": "Partly Cloudy"},
    {"time": "3:00 PM", "temp": "71°F", "condition": "Sunny"},
    {"time": "6:00 PM", "temp": "65°F", "condition": "Clear"}
]
WEATHER_5_DAY = [
    {"day": "Today", "high": "72°F", "low": "52°F", "condition": "Sunny"},
    {"day": "Monday", "high": "75°F", "low": "54°F", "condition": "Partly Cloudy"},
    {"day": "Tuesday", "high": "68°F", "low": "49°F", "condition": "Rain"}
]
SKI_INFO = [{"resort": "Summit Alpine", "openStatus": "Open", "newSnow": "2 in", "baseDepth": "48 in"}]

SPORTS_SCORES = [
    {"league": "NFL", "matchup": "Chiefs vs 49ers", "score": "24 - 21", "status": "Final"},
    {"league": "NBA", "matchup": "Lakers vs Celtics", "score": "102 - 98", "status": "4th Qtr"}
]

MOVIE_LISTINGS = [
    {"title": "Dune: Part Two", "theater": "AMC Metro 12", "distance": "1.8 mi", "times": ["1:00 PM", "4:30 PM", "8:00 PM"]},
    {"title": "Civil War", "theater": "Regal Cinemas", "distance": "3.4 mi", "times": ["2:15 PM", "5:45 PM", "9:15 PM"]}
]

TRAFFIC_EVENTS = [
    {"eventID": 1, "road": "I-95 South", "description": "Construction work near Exit 42", "delay": "5 mins", "severity": "Moderate"}
]


@on("XMFuel", "requestFuelPrices")
def fuel_request(dest, args, conn):
    H.B.send("XMFuel", {"fuelList": FUEL_DATA}, conn)


@on("XMLandWeather", "requestWeather")
def weather_request(dest, args, conn):
    H.B.send("XMLandWeather", {"currentWeather": WEATHER_CURRENT, "hourlyForecast": WEATHER_3_6HR, "forecast5Day": WEATHER_5_DAY, "skiInfo": SKI_INFO}, conn)


@on("XMSports", "requestSportsScores")
def sports_request(dest, args, conn):
    H.B.send("XMSports", {"sportsScores": SPORTS_SCORES}, conn)


@on("XMMovies", "requestMovieListings")
def movies_request(dest, args, conn):
    H.B.send("XMMovies", {"movieListings": MOVIE_LISTINGS}, conn)


@on("XMTraffic", "requestTrafficEvents")
def traffic_request(dest, args, conn):
    H.B.send("XMTraffic", {"trafficEvents": TRAFFIC_EVENTS}, conn)


BUFFER = 44 * 60
IR = {"fill": 0, "behind": 0, "paused": False, "ff": 0}


def ir_publish():
    fill_pct = min(100, IR["fill"] * 100 // BUFFER)
    play_pct = max(0, 100 - IR["behind"] * 100 // BUFFER)
    b = IR["behind"]
    xm_set("XMInstantReplay", "replayBufferStatus", {"fillPct": fill_pct, "playbackPct": play_pct,
                                                     "hours": b // 3600, "minutes": b // 60 % 60, "seconds": b % 60})
    xm_set("XMInstantReplay", "replayPlayStatus", {"pauseStatus": "PAUSE" if IR["paused"] else "PLAY",
                                                   "isLive": b == 0 and not IR["paused"], "fastForwardActive": IR["ff"] > 0,
                                                   "rewindActive": IR["ff"] < 0, "scanActive": False})


def _ir_move(delta):
    IR["behind"] = max(0, min(IR["fill"], IR["behind"] - delta))
    ir_publish()


for _cmd, _fn in {
    "live": lambda a: IR.update(behind=0, paused=False, ff=0),
    "pausePlayRelease": lambda a: IR.update(paused=not IR["paused"]),
    "seekPrevious": lambda a: IR.update(behind=min(IR["fill"], IR["behind"] + 30)),
    "seekForward": lambda a: IR.update(behind=max(0, IR["behind"] - 30)),
    "rewindPress": lambda a: IR.update(ff=-1),
    "fastForwardPress": lambda a: IR.update(ff=1),
    "rewindRelease": lambda a: IR.update(ff=0),
    "fastForwardRelease": lambda a: IR.update(ff=0),
    "seekToPosition": lambda a: IR.update(behind=min(IR["fill"], max(0, (100 - int(a.get("percent", 100))) * BUFFER // 100))),
}.items():
    H._pending.append(("XMInstantReplay", _cmd, (lambda f: lambda d, a, c: (f(a), ir_publish()))(_fn)))
for _cmd in ("pausePlayPress", "scanPressed", "setIRMode", "requestPlaylist", "playFromPlaylist"):
    H._pending.append(("XMInstantReplay", _cmd, lambda dest, args, conn: None))


def _sxm_ticker():
    last_songs = {}
    last_lineup = last_cur = 0
    last_ver = _ART["ver"]
    lineup_dirty = False
    while True:
        time.sleep(1)
        try:
            songs = {n: now_playing(n) for n in NUMS}
            ver = _ART["ver"]
            if last_songs:
                cur, t = XM["channel"], time.time()
                song_changed = songs.get(cur) != last_songs.get(cur)
                if song_changed or (ver != last_ver and t - last_cur > 3):
                    last_cur = t
                    publish_current()
                if songs != last_songs or ver != last_ver:
                    lineup_dirty = True
                if lineup_dirty and t - last_lineup > 60:
                    last_lineup, lineup_dirty = t, False
                    publish_lineup()
                    if XM["favorites"]:
                        favorites_publish()
            last_songs, last_ver = songs, ver
            if H.B.mod("Audio").get("audioSource", {}).get("source") == "sat":
                IR["fill"] = min(BUFFER, IR["fill"] + 1)
                if IR["paused"]:
                    IR["behind"] = min(IR["fill"], IR["behind"] + 1)
                elif IR["ff"]:
                    _ir_move(IR["ff"] * 10)
                    continue
                elif IR["behind"] == 0 and IR["fill"] % 5:
                    continue
                ir_publish()
        except Exception as e:
            H.B.log("!!", f"sxm ticker {e!r}")


def init(B):
    B.prop_store("VehicleConfig")["destination"] = "2"
    global _XMP_INIT_OK
    if XMP_ON:
        try:
            _xmp_refresh_stations(publish=False)
            _xmp_refresh_feed()
            _XMP_INIT_OK = True
            _log(f"startup ok: {len(NUMS)} chans")
        except Exception as e:
            _log(f"startup failed: {e!r}")
    x = B.mod("XMApp")
    x.update({
        "appStatus": {"appStatus": "READY"},
        "advisoryMsg": {"advisoryMsg": "NO ERROR"},
        "signalStrength": {"signalStrength": 3},
        "ESN": {"ESN": ESN},
        "xmAppVersion": "SXV300 07.01.15",
        "audioSubscriptionStatus": {"subStatus": 1},
        "dataServicesSubscriptionStatus": {s: 1 for s in (
            "channelArtSubStatus", "fuelSubStatus", "graphicalWeatherSubStatus", "landWeatherSubStatus",
            "moviesSubStatus", "securityAlertsSubStatus", "sportsSubStatus", "trafficSubStatus")},
        "dataServicesState": [{"service": s, "state": "READY"} for s in ("fuel", "movies", "sports", "weather")],
        "availableChannelList": NUMS,
        "skippedChannelList": [],
        "lockedChannelList": [],
        "smartFavoritesStatus": {"smartFavoritesStatus": 1},
        "featuredFavoritesList": {"list": [
            {"bandID": 1, "name": "SXM Picks", "longName": "SiriusXM Picks", "verboseName": "SiriusXM Picks",
             "description": "Channels picked for you"},
            {"bandID": 2, "name": "Sports", "longName": "Sports Talk", "verboseName": "Sports Talk & Play-by-Play",
             "description": "Live sports talk"}]},
        "stationInfoList": [station(n) for n in NUMS],
        "currentStationInfo": station(XM["channel"], True),
    })
    B.mod("XMPresets")["localXMPresetList"] = presets_payload()
    
    active_favs_init = []
    for n in NUMS:
        artist, title = now_playing(n)
        for f in XM["favorites"]:
            if (f["favoriteType"] == "song" and f["song"] == title) or (f["favoriteType"] == "artist" and f["artist"] == artist):
                active_favs_init.append({"channel": n, "artist": artist, "song": title,
                                         "isActiveArtist": f["favoriteType"] == "artist", "isActiveSong": f["favoriteType"] == "song"})
                break

    B.mod("XMFavorites").update({"allFavorites": XM["favorites"], "activeFavorites": active_favs_init,
                                 "favAllowed": {"isArtistAllowed": True, "isSongAllowed": True}})
                                 
    B.mod("XMGameZone").update({"globalGameAlertStatus": {"Status": True}, "globalScoreAlertStatus": {"Status": True},
                                "currentTeamFavorites": gz_favorites_payload(), "leagueList": LEAGUES,
                                "activeScores": []})
    B.mod("XMTrafficJump").update({"trafficList": MARKETS, "jumpStatus": "JUMP_MARKET_NOT_SELECTED", "selectedMarket": 0})
    B.mod("XMInstantReplay").update({"replayBufferStatus": {"fillPct": 0, "playbackPct": 100, "hours": 0, "minutes": 0, "seconds": 0},
                                     "replayPlayStatus": {"pauseStatus": "PLAY", "isLive": True, "fastForwardActive": False,
                                                          "rewindActive": False, "scanActive": False},
                                     "numPlaylistItems": 0, "currentOffset": 0})
    
    B.mod("XMFuel").update({"fuelList": FUEL_DATA})
    B.mod("XMLandWeather").update({"currentWeather": WEATHER_CURRENT, "hourlyForecast": WEATHER_3_6HR, "forecast5Day": WEATHER_5_DAY, "skiInfo": SKI_INFO})
    B.mod("XMSports").update({"sportsScores": SPORTS_SCORES})
    B.mod("XMMovies").update({"movieListings": MOVIE_LISTINGS})
    B.mod("XMTraffic").update({"trafficEvents": TRAFFIC_EVENTS})

    threading.Thread(target=_sxm_ticker, daemon=True).start()
    if XMP_ON:
        threading.Thread(target=_art_worker, daemon=True).start()
        threading.Thread(target=_xmp_poller, daemon=True).start()
        _log("poller started")
    else:
        _log("static data only")