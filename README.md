# Uconnect 8.4AN emulator

the **stock** Uconnect 8.4AN touchscreen software (RA4 17.43.01, MY15 NAFTA — Dodge/Chrysler/Jeep/Ram 2015-2017)
running on a windows PC, straight out of the official USB update files. No head unit needed.

### screenshots & previews

| | |
|---|---|
| ![](docs/screenshots/am.gif) ![](docs/screenshots/fm.gif) **radio** — uses dummy am/fm radio info, change it urself if u so please | ![](docs/screenshots/sxm.gif) **siriusxm** — FULLY working live* data streams ! |
| ![](docs/screenshots/media.gif) **media** — usb bt and aux all pull from same source, ur user music folder. working metadata other than album art | ![](docs/screenshots/trvllnk.gif) **travel link** — half-working travel data, will fix in later update |
| ![](docs/screenshots/phone.gif) **phone** — you can pair ur own phone ! | ![](docs/screenshots/book.gif) **phonebook** — contact list, recents, favorites |
| ![](docs/screenshots/climate.gif) **climate** — dual-zone temp controls, fan speed, auto, modes,ect shi | ![](docs/screenshots/controls.gif) **controls** — heated/vented seats, heated steering wheel |
| ![](docs/screenshots/set.gif) **settings** — config ur emulator however u want | ![](docs/screenshots/nav22.png) **navigation** — fully working using google maps ! |
| ![](docs/screenshots/drvmds.gif) **srt drive modes** — street, sport, track, and use custom for whatever you want | ![](docs/screenshots/drvinfo.gif) **drive mode info** — details on transmission, steering, suspesnion, ect... |
| ![](docs/screenshots/drvoverview.gif) **powertrain overview** — overview for the modes u have picked | ![](docs/screenshots/rpm.gif) **launch control** — launch rpm setup and activation |
| ![](docs/screenshots/perfpages.gif) **hellcat perf pages** — live gauges, timers, g-force, engine stats | ![](docs/screenshots/hellcatimages.gif) **hellcat visuals** — model-specific charger hellcat pics, fresh from the uconencts sw |
| ![](docs/screenshots/300.gif) **chrysler 300** — 300c srt performance pages and vehicle pics | ![](docs/screenshots/wk2drv.gif) **wk2 grand cherokee** — wk2 srt jeep selec-track drive modes |
| ![](docs/screenshots/wk2pics.gif) **wk2 visuals** — srt grand cherokee pics | |

also:
- **boot splash** — the car's own brand splash images, chosen exactly like the real vp4 `splash.lua` (brand + SRT/SiriusXM/Beats flags).
- **themes** — all brand themes (Dodge, Jeep, Chrysler, Ram, SRT, Viper, Fiat, Maserati…); switch from the panel or live in the head unit's own Settings.
- **sound** — Media plays real files through Windows (play/pause/skip/seek, volume knob, mute); incoming calls ring.
- **hardware panel** in the browser — volume & tune knobs, faceplate keys, climate knobs, gear shift, theme & splash pickers, restart, raw message injector.
- **CAN signal map** (`can/`) — 261 CAN message IDs / 1,511 signals (byte, bit, mask, PPS object) extracted from the firmware's `canservice`, for 9 vehicle CAN architectures.

### new in this update

- **srt drive modes** — fully working drive modes powered by `modules/drivemode.py`. handles hellcat red/black keys (500 / 700+ hp) plus wk2 srt screens and the selec-track dial.
- **performance control** — non-srt r/t and scat pack models get the stock dodge/chrysler performance control app.
- **performance pages** — since the original java apps can't run natively off the dump, everything is redrawn completely from scratch using the exact stock artwork, fonts, and layout inside the head-unit window. covers all stock versions (wk/la/lx/ld/zf/etc... r/t, scat, 300c, hellcat, wk2 srt, and viper with its options page) driven live by a simulated car (launch, cruise, brake, steer) right from the panel.
- **vehicle picker** — switch between 19 different cars (ld, la, lx, wk2, wd, zf, etc...). changes the car config, theme, and boot splash instantly—settings › theme updates to match that specific model's themes.
- **siriusxm channel logos** — loads the firmware's actual channel art (`emulator/sdars/channelart`) straight onto the siriusxm screen.
- **languages** — settings › display › language pulls the market's real language list (north america, europe, rest of world, japan, korea, china, etc.) and switches the whole ui live. you can also toggle markets and languages directly from the panel.
- **phone names** — change your connected phone name and the head unit's bluetooth broadcast name straight from the panel.
- **real bluetooth audio** — pair a real phone from phone › add device and stream audio right through media › bluetooth (calls and contacts stay simulated).

## what can't work

anything that is native qnx/arm code in a real unit—like the **navigation map engine** (naviserver), the **voice recognition** engine, and the java **apps** (xlets)—won't run natively. the menus open and work fine, but 
the map surface itself and speech recognition are dead. out of all the java apps, only performance pages is redrawn. also, real hands-free bluetooth calls need bluetooth profiles that windows just doesn't support.

## next upd

- **map SXM to an api** — mapping SXM data (no audio obv).
- **bt song info** — read title/artist straight from the phone (AVRCP)
- **album arts**, SXM,BT,USB,ect...
- **real splash animations** — decode the `splash_movies/*.bin` animations.
- **voice prompts** — play the stock VR beeps/prompts (`start.wav`, `recog_*.wav`).

## run it

needs Windows, Python 3, and the free Adobe AIR 32 SDK (the runtime the car's HMI is built on).

```powershell
git clone https://github.com/exycalll/Uconnect-3-8.4-Emulator
cd uconnect-emulator
mkdir tools\airsdk
curl.exe -L -o tools\AdobeAIRSDK.zip https://airdownload.adobe.com/air/win/download/32.0/AdobeAIRSDK.zip
tar -xf tools\AdobeAIRSDK.zip -C tools\airsdk
pip install mutagen pillow
pip install winrt-runtime winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Media.Audio winrt-Windows.Devices.Enumeration winrt-Windows.Devices.Bluetooth winrt-Windows.Media.Control
emulator\run.bat
```

### bluetooth audio (optional, may need an adapter depending if u have it built in)
- **pairing:** go to `phone > settings > paired phones > add device` to make your pc discoverable, pair up, and stream audio straight through to media > bluetooth (supports play/pause/skip). calls and contacts are simulated.
- **iphones:** since iphones don't normally list standard pcs as audio gear, run `emulator\bt_car_audio.ps1` as administrator once so windows announces itself as car audio (pass `-undo` if you ever want to revert it).
- **naming:** want it to show up as "uconnect" on your phone instead of your pc's hostname? just run `emulator\bt_name.ps1 -name Uconnect` as administrator.

### running it & sound
- **startup:** the boot splash pops up first, then the 1024x768 head-unit window opens (your mouse acts as touch input) alongside the hardware control panel running locally at `http://127.0.0.1:4401/`.
- **media & music:** points straight to your local music folder (`~/Music`, or whatever you set as `"musicDir"` in `emulator/config.json`) acting like a usb stick. media plays real files (`.mp3`, `.m4a`, `.wma`, `.wav`, `.flac`) with full tags, seek controls, volume knob, and mute. incoming calls use the actual car ringtone (radio and siriusxm stay quiet).
- **config:** pick your car model, theme, splash screen, market/language, and phone names right inside the web panel (`http://127.0.0.1:4401/`)—everything saves automatically to `emulator/config.json`, and deeper vehicle equipment configs live in `emulator/state.json` (`VehicleConfig`).

## how this even came to be
well one day i was dicking arround in dealerconnect and thought to myself, whats really in these update files ? and so i found out that its the entire firmware js in plain sight, and then the gears started turning in 
my head and eventually i ended up showing exycal and he worked with another guy who had acess to claude (yes its majoryly vibecoded but im here tofix that and  make it to where the creator actually knows whats going on;))

## what about newer Uconnects ?

issue at the moment with the 2018+ ones that ppl are begging for is that they are encrypted, and can only be decrypted by some kinda key in the radio iteslf (afaik)

## layout

- `emulator/` — the emulator (see `emulator/README.md`): `backend.py`, `handlers.py`, `modules/`, `state.json`, `hmi/` (stock HMI), `panel.html`, `dev/`
- `decomp/` — decompiled ActionScript of the HMI
- `can/` — extracted CAN signal tables (`can_signals.csv`, `can_ids.csv`) and the tools that produced them
- `docs/screenshots/`

*2-3 min delay with a free api

Uconnect,Dodge,Ram,Jeep,Chrysler,Harman,Harman/Kardon SiriusXM etc. are trademarks of their owners; the HMI and firmware are © Stellantis / Harman.
this is an unofficial research project, im js a tool at a pc
