"""Ticket 02: onboarding, model setup and receiving screens in design/khonnai.figcraft.

Usage: python -I design/build_screens_02.py
Run after build_design_system.py. Adds a page "02 Onboarding and Receiving" (rebuilt from scratch on each run),
plus Chip / App Bar components and a few icons on the Components page.
Previews go to design/preview/02/.
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_design_system as ds  # noqa: E402
from build_design_system import run, frame, hl, vl, text_into, surface, icon_into, bind
from normalize_figcraft_names import SCREEN_NAMES, normalize
from refine_figcraft_flows import refine

PAGE_NAME = "02 Onboarding and Receiving"
PREVIEW = os.path.join(ds.ROOT, "preview", "02")
W = 375

# ids of existing components, looked up by name at start
C = {}
EXTRA_ICONS = {
    "chevron-left": '<path d="M15 6l-6 6 6 6"/>',
    "calendar": '<path d="M4 6h16v14H4z"/><path d="M4 10h16M8 3v4M16 3v4"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
    "eye-off": '<path d="M3 3l18 18"/><path d="M10.6 6.1A9.8 9.8 0 0 1 12 6c5 0 9 6 9 6a15 15 0 0 1-3 3.6M6.6 7.6C4.3 9.2 3 12 3 12s4 6 9 6a8.6 8.6 0 0 0 3.4-.7"/>',
}


def lookup():
    comps, pages = run([{"command": "component.list", "params": {}}, {"command": "page.list", "params": {}}])
    sets = {}
    for c in comps:
        if c["type"] == "COMPONENT_SET":
            sets[c["name"]] = c["id"]
    by_name = {c["name"]: c["id"] for c in comps if c["type"] == "COMPONENT"}
    return comps, pages, sets, by_name


def variant(set_id, name):
    kids = ds.node(set_id)["children"]
    return [k["id"] for k in kids if k["name"] == name][0]


def inst(parent, comp, props=None, fill=False, name=None):
    iid = run([{"command": "instance.create", "params": {"component": comp, "parent": parent}}])[0]["id"]
    cmds = []
    if props:
        cmds.append({"command": "instance.setProperties", "params": {"ids": [iid], "properties": props}})
    p = {"ids": [iid]}
    if fill:
        p["sizingH"] = "fill"
    if name:
        p["name"] = name
    if len(p) > 1:
        cmds.append({"command": "node.set", "params": p})
    if cmds:
        run(cmds)
    return iid


def box(parent, name, props, w=None, h=None):
    return run([frame(name, parent, props, w=w, h=h)])[0]["id"]


def txt(parent, text, style="Body/Default", color="color/text/primary", name=None, fill=True):
    return text_into(parent, text, style, color, name or text[:24], fill)


# ---------------------------------------------------------------- new components
def extra_components(page):
    existing = {c["name"] for c in run([{"command": "component.list", "params": {}}])[0]}
    cmds = [{"command": "page.select", "params": {"id": page}}]
    new_icons = [n for n in EXTRA_ICONS if f"Icon/{n}" not in existing]
    for i, name in enumerate(new_icons):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
               f'stroke="#5B6474" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{EXTRA_ICONS[name]}</svg>')
        cmds.append({"command": "file.import", "params": {"data": base64.b64encode(svg.encode()).decode(),
                                                          "name": f"{name}.svg", "x": (13 + i) * 48, "y": 0}})
    res = run(cmds)[1:]
    for fid, name in zip(ds.ids_of(res), new_icons):
        run([{"command": "component.create", "params": {"ids": [fid]}},
             {"command": "object.rename", "params": {"ids": [fid], "name": f"Icon/{name}"}}])
        vec = [d["id"] for d in ds.descendants(ds.full(fid)) if d["type"] not in ("FRAME", "GROUP")]
        run([bind(vec, "stroke", "color/icon/default")])

    if "Selected=True" not in existing:
        specs = [(f"Selected={s}", {"frame": hl(mainAlign="center", padding=[10, 16, 10, 16], sizingH="hug", sizingV="hug",
                                                minHeight=48, fill="#FFFFFF"), "sel": s == "True"}) for s in ("True", "False")]

        def build_chip(fid, d):
            txt(fid, "3 ตัว", "Body/Strong" if d["sel"] else "Body/Default",
                "color/text/brand" if d["sel"] else "color/text/primary", "Label", fill=False)
            surface(fid, fill="color/bg/brand-subtle" if d["sel"] else "color/bg/surface",
                    stroke="color/border/focus" if d["sel"] else "color/border/strong", weight=2 if d["sel"] else 1,
                    radius="radius/full")

        sid, fids = ds.variant_set(page, specs, build_chip, "Chip", 2, 120, 0, 0, 1560,
                                   "ตัวเลือกแบบแตะ ใช้แทน dropdown เมื่อมีตัวเลือกน้อย เช่น แพ็กละกี่ตัว ไซซ์ สี สูงขั้นต่ำ 48px")
        ds.add_props(sid, fids, [("Label", "text", "Label", "characters", None)])

    if "App Bar" not in existing:
        lookup_ids = {c["name"]: c["id"] for c in run([{"command": "component.list", "params": {}}])[0]}
        ab = box(page, "App Bar", hl(gap=4, padding=[8, 16, 8, 4], sizingV="hug", fill="#FFFFFF", minHeight=64), w=W)
        run([{"command": "node.set", "params": {"ids": [ab], "x": 400, "y": 1560}}])
        surface(ab, fill="color/bg/surface", stroke="color/border/default")
        run([{"command": "node.set", "params": {"ids": [ab], "strokeSides": [0, 0, 1, 0]}}])
        back = box(ab, "Back", hl(mainAlign="center", fill="none"), w=48, h=48)
        icon_into(back, lookup_ids["Icon/chevron-left"], "color/icon/default")
        col = box(ab, "Titles", vl(gap=0, sizingH="fill", sizingV="hug", fill="none"))
        txt(col, "เพิ่มรุ่น", "Heading/H3", "color/text/primary", "Title")
        txt(col, "ขั้นที่ 1 จาก 3", "Label/Default", "color/text/secondary", "Subtitle")
        run([{"command": "component.create", "params": {"ids": [ab]}},
             {"command": "node.set", "params": {"ids": [ab], "description": "แถบหัวหน้าจอ: ปุ่มย้อนกลับ 48px + ชื่อหน้า + คำอธิบายรอง"}}])
        ds.add_props(ab, [ab], [("Title", "text", "Title", "characters", None),
                                ("Subtitle", "text", "Subtitle", "characters", None),
                                ("Show subtitle", "boolean", "Subtitle", "visible", True),
                                ("Show back", "boolean", "Back", "visible", True)])
    # keep the title off the screen edge when the back button is hidden
    ab = {c["name"]: c["id"] for c in run([{"command": "component.list", "params": {}}])[0]}["App Bar"]
    back = [c["id"] for c in ds.node(ab)["children"] if c["name"] == "Back"][0]
    run([{"command": "node.set", "params": {"ids": [ab], "padding": [8, 16, 8, 16]}},
         {"command": "node.set", "params": {"ids": [back], "width": 40}}])


# ---------------------------------------------------------------- screen scaffolding
SCREENS = {}


def screen(page, key, title_text, col, row=0):
    x, y = col * (W + 80), row * 1100
    s = box(page, SCREEN_NAMES.get(title_text, title_text), vl(gap=0, sizingV="hug", minHeight=812, fill="#FFFFFF"), w=W)
    run([{"command": "node.set", "params": {"ids": [s], "x": x, "y": y, "clip": True}}])
    surface(s, fill="color/bg/canvas")
    SCREENS[key] = s
    return s


def app_bar(s, title, subtitle=None, back=True):
    props = {"Title": title, "Show subtitle": bool(subtitle), "Show back": back}
    if subtitle:
        props["Subtitle"] = subtitle
    return inst(s, C["App Bar"], props, fill=True, name="App Bar")


def body(s, gap=20):
    return box(s, "Body", vl(gap=gap, padding=[20, 16, 24, 16], sizingH="fill", sizingV="hug", fill="none"))


def footer(s):
    f = box(s, "Footer", vl(gap=8, padding=[16, 16, 24, 16], sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(f, fill="color/bg/surface", stroke="color/border/default")
    run([{"command": "node.set", "params": {"ids": [f], "strokeSides": [1, 0, 0, 0]}}])
    return f


def spacer(s):
    return box(s, "Spacer", vl(sizingH="fill", fill="none"), h=1)


def grow(nid):
    run([{"command": "node.set", "params": {"ids": [nid], "sizingV": "fill"}}])


def button(parent, label, style="Primary", size="Large", icon=None, fill=True):
    comp = C["btn"][f"Style={style}, Size={size}, State=Default"]
    props = {"Label": label, "Show icon": bool(icon)}
    if icon:
        props["Icon"] = C["icons"][icon]
    return inst(parent, comp, props, fill=fill, name=f"Button {label}")


def field(parent, label, value, helper=None, state="Default"):
    props = {"Label": label, "Value": value, "Show helper": bool(helper)}
    if helper:
        props["Helper"] = helper
    return inst(parent, C["input"][state], props, fill=True, name=f"Input {label}")


def chips(parent, labels, selected, name="Chips"):
    row = box(parent, name, hl(gap=8, sizingH="fill", sizingV="hug", fill="none", wrap=True, crossGap=8))
    ids = []
    for lab in labels:
        ids.append(inst(row, C["chip"]["True" if lab in selected else "False"], {"Label": lab}))
    return row, ids


def section_label(parent, text, hint=None):
    col = box(parent, "Label " + text[:16], vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
    txt(col, text, "Body/Strong")
    if hint:
        txt(col, hint, "Label/Default", "color/text/secondary")
    return col


def card(parent, name, gap=12):
    c = box(parent, name, vl(gap=gap, padding=16, sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(c, fill="color/bg/surface", stroke="color/border/default", radius="radius/lg")
    return c


def link(parent, text):
    t = txt(parent, text, "Body/Strong", "color/text/brand", "Link " + text[:16])
    run([{"command": "node.set", "params": {"ids": [t], "textAlign": "center"}}])
    return t


# ---------------------------------------------------------------- screens
def build(page):
    links = []  # (source id, dest key or "back")

    # 1 สมัครใช้งาน
    s = screen(page, "signup", "01 สมัครใช้งาน", 0)
    b = body(s, 24)
    run([{"command": "node.set", "params": {"ids": [b], "padding": [48, 24, 24, 24]}}])
    inst(b, C["logo_word"])
    head = box(b, "Heading", vl(gap=8, sizingH="fill", sizingV="hug", fill="none"))
    txt(head, "เริ่มใช้ khonnai ฟรี", "Heading/H1")
    txt(head, "ดูสต็อก ออกบิล และจองของให้ลูกค้า ได้จากมือถือเครื่องเดียว", "Body/Default", "color/text/secondary")
    field(b, "เบอร์มือถือหรืออีเมล", "081-234-5678")
    field(b, "ตั้งรหัสผ่าน", "••••••••", "อย่างน้อย 8 ตัว")
    links.append((button(b, "สมัครใช้งาน"), "create_shop"))
    links.append((link(b, "มีบัญชีอยู่แล้ว? เข้าสู่ระบบ"), "login"))

    # 2 เข้าสู่ระบบ
    s = screen(page, "login", "02 เข้าสู่ระบบ", 1)
    b = body(s, 24)
    run([{"command": "node.set", "params": {"ids": [b], "padding": [48, 24, 24, 24]}}])
    inst(b, C["logo_word"])
    txt(b, "เข้าสู่ระบบ", "Heading/H1")
    field(b, "เบอร์มือถือหรืออีเมล", "081-234-5678")
    field(b, "รหัสผ่าน", "••••••••")
    links.append((button(b, "เข้าสู่ระบบ"), "home"))
    txt(b, "ระบบจะจำการเข้าสู่ระบบไว้ ไม่ต้องล็อกอินใหม่ทุกครั้ง", "Label/Default", "color/text/secondary")
    links.append((link(b, "ยังไม่มีบัญชี? สมัครใช้งาน"), "signup"))

    # 3 สร้างร้าน
    s = screen(page, "create_shop", "03 สร้างร้าน", 2)
    app_bar(s, "สร้างร้าน", back=False)
    b = body(s, 24)
    txt(b, "ร้านของคุณชื่ออะไร?", "Heading/H2")
    field(b, "ชื่อร้าน", "ร้านเจ๊หน่อยชุดชั้นใน", "ลูกค้าจะเห็นชื่อนี้ในแคตตาล็อกและบนบิล")
    field(b, "ลิงก์ LINE ของร้าน (ไม่บังคับ)", "https://line.me/ti/p/~jaynoi",
          "ลูกค้ากดจากแคตตาล็อกเพื่อทักแชตร้าน ใส่ทีหลังได้")
    grow(spacer(s))
    f = footer(s)
    links.append((button(f, "สร้างร้าน"), "home"))

    # 4 หน้าแรก
    s = screen(page, "home", "04 หน้าแรก", 3)
    app_bar(s, "ร้านเจ๊หน่อยชุดชั้นใน", "ยินดีต้อนรับ", back=False)
    b = body(s, 16)
    empty = card(b, "Empty state", 12)
    txt(empty, "ยังไม่มีรุ่นในร้าน", "Heading/H3")
    txt(empty, "เพิ่มรุ่นแรกพร้อมไซซ์ สี ราคา และสต็อกที่จดไว้ในกระดาษ ใช้เวลาประมาณ 3 นาทีต่อรุ่น", "Body/Default", "color/text/secondary")
    links.append((button(empty, "เพิ่มรุ่นแรก", icon="plus"), "model_info"))
    txt(b, "ทางลัด", "Heading/H3")
    grid = box(b, "Shortcuts", hl(gap=12, sizingH="fill", sizingV="hug", fill="none", wrap=True, crossGap=12))
    for lab, icn, dest in (("ดูสต็อก", "package", "model_list"), ("ออกบิล", "receipt", None),
                           ("จอง", "bookmark", None), ("รับของเข้า", "truck", "receive")):
        t = box(grid, "Tile " + lab, vl(gap=12, padding=16, fill="#FFFFFF"), w=163, h=120)
        surface(t, fill="color/bg/surface", stroke="color/border/default", radius="radius/lg")
        circ = box(t, "Icon bg", hl(mainAlign="center", fill="none"), w=48, h=48)
        surface(circ, fill="color/bg/brand-subtle", radius="radius/full")
        icon_into(circ, C["icons"][icn], "color/icon/brand")
        txt(t, lab, "Heading/H3", fill=False)
        if dest:
            links.append((t, dest))
    share = card(b, "Share catalogue", 4)
    run([{"command": "node.set", "params": {"ids": [share], "layout": "horizontal", "crossAlign": "center", "gap": 12}}])
    circ = box(share, "Icon bg", hl(mainAlign="center", fill="none"), w=48, h=48)
    surface(circ, fill="color/bg/brand-subtle", radius="radius/full")
    icon_into(circ, C["icons"]["search"], "color/icon/brand")
    col = box(share, "Text", vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
    txt(col, "แชร์แคตตาล็อก", "Heading/H3")
    txt(col, "ส่งลิงก์ให้ลูกค้าประจำในกลุ่ม LINE", "Label/Default", "color/text/secondary")
    icon_into(share, C["icons"]["chevron-right"], "color/icon/default", name="Chevron")
    inst(s, C["bottom_nav"], fill=True)

    # 5 รายการรุ่น
    s = screen(page, "model_list", "05 รายการรุ่น", 4)
    app_bar(s, "รุ่นทั้งหมด", "14 รุ่น", back=False)
    b = body(s, 16)
    field(b, "ค้นหารุ่น", "พิมพ์ชื่อหรือรหัส เช่น A-102")
    chips(b, ["กำลังขาย (12)", "ซ่อนไว้ (2)"], ["กำลังขาย (12)"], "Filter")
    for name, meta, price in (("เสื้อใน A-102 ลูกไม้", "แพ็กละ 3 ตัว · คละสี", "฿180 / แพ็ก"),
                              ("เสื้อใน A-215 ไร้โครง", "แพ็กละ 6 ตัว · สีเดียว", "฿320 / แพ็ก"),
                              ("กางเกงใน P-310 เอวสูง", "แพ็กละ 12 ตัว · คละสี", "฿240 / แพ็ก"),
                              ("กางเกงใน P-118 เด็ก", "แพ็กละ 10 ตัว · คละสี", "฿150 / แพ็ก")):
        inst(b, C["model_card"], {"Name": name, "Meta": meta, "Price": price}, fill=True)
    f = footer(s)
    links.append((button(f, "เพิ่มรุ่น", icon="plus"), "model_info"))
    nav = inst(s, C["bottom_nav"], fill=True)
    items = [c["id"] for c in ds.node(nav)["children"]]
    run([{"command": "instance.setProperties", "params": {"ids": [items[0]], "properties": {"Active": "False"}}},
         {"command": "instance.setProperties", "params": {"ids": [items[1]], "properties": {"Active": "True"}}}])

    # 6 เพิ่มรุ่น ขั้น 1
    s = screen(page, "model_info", "06 เพิ่มรุ่น · ข้อมูลรุ่น", 0, 1)
    links.append((app_bar(s, "เพิ่มรุ่น", "ขั้นที่ 1 จาก 3 · ข้อมูลรุ่น"), "back"))
    b = body(s, 24)
    photo = box(b, "Photo", vl(gap=8, mainAlign="center", crossAlign="center", fill="#FFFFFF"), w=120, h=120)
    surface(photo, fill="color/bg/surface", stroke="color/border/strong", radius="radius/lg")
    run([{"command": "node.set", "params": {"ids": [photo], "dashes": [6, 4]}}])
    icon_into(photo, C["icons"]["camera"], "color/icon/brand")
    txt(photo, "ถ่ายรูปรุ่น", "Label/Default", "color/text/brand", fill=False)
    field(b, "ชื่อหรือรหัสรุ่น", "A-102 เสื้อในลูกไม้", "ใช้ชื่อเดียวกับที่ร้านเรียก")
    sec = box(b, "Pack size", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "แพ็กละกี่ตัว")
    chips(sec, ["3 ตัว", "6 ตัว", "10 ตัว", "12 ตัว", "อื่น ๆ"], ["3 ตัว"])
    sec = box(b, "Pack colour", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "สีในแพ็ก", "คละสี: ลูกค้าเลือกสีไม่ได้ ระบบนับสต็อกตามไซซ์อย่างเดียว")
    chips(sec, ["สีเดียวทั้งแพ็ก", "คละสี"], ["คละสี"])
    field(b, "ราคาแพ็ก (บาท)", "180", "ราคาต่อ 1 แพ็ก ตั้งราคาแยกไซซ์ได้ในขั้นถัดไป")
    sec = box(b, "Min stock", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "สต็อกขั้นต่ำ", "เหลือเท่านี้หรือน้อยกว่า จะขึ้นในรายการใกล้หมด")
    inst(sec, C["stepper"], {"Count": "5"})
    f = footer(s)
    links.append((button(f, "ถัดไป: ไซซ์"), "model_sizes"))

    # 7 เพิ่มรุ่น ขั้น 2
    s = screen(page, "model_sizes", "07 เพิ่มรุ่น · ไซซ์และราคา", 1, 1)
    links.append((app_bar(s, "เพิ่มรุ่น", "ขั้นที่ 2 จาก 3 · ไซซ์และราคา"), "back"))
    b = body(s, 24)
    sec = box(b, "Sizes", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "ไซซ์ที่มี", "แตะเพื่อเลือก รุ่นคละสีไม่ต้องเลือกสี")
    chips(sec, ["32", "34", "36", "38", "40", "+ เพิ่มไซซ์"], ["32", "34", "36"])
    sec = box(b, "Price", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "ราคาแพ็ก")
    chips(sec, ["เท่ากันทุกไซซ์", "บางไซซ์ราคาต่าง"], ["บางไซซ์ราคาต่าง"])
    c = card(sec, "Size prices", 12)
    for size, price, helper in (("32", "180", None), ("34", "180", None), ("36", "200", "ต่างจากราคาปกติ")):
        field(c, f"ไซซ์ {size}", price, helper)
    txt(b, "ถ้าเป็นรุ่นแพ็กสีเดียว จะมีขั้นเลือกสีของแต่ละไซซ์เพิ่ม (หน้าจอ 07b)", "Label/Default", "color/text/secondary")
    f = footer(s)
    links.append((button(f, "ถัดไป: สต็อกตั้งต้น"), "model_stock"))

    # 7b เพิ่มรุ่น สีของแต่ละไซซ์ (รุ่นแพ็กสีเดียว)
    s = screen(page, "model_colours", "07b เพิ่มรุ่น · สีของแต่ละไซซ์", 2, 1)
    links.append((app_bar(s, "เพิ่มรุ่น", "ขั้นที่ 2 จาก 3 · สีของแต่ละไซซ์"), "back"))
    b = body(s, 24)
    txt(b, "เลือกเฉพาะสีที่มีจริงในแต่ละไซซ์ ระบบจะไม่สร้างคู่ไซซ์/สีที่ร้านไม่มี", "Body/Default", "color/text/secondary")
    for size, sel in (("32", ["ดำ", "ขาว"]), ("34", ["ดำ", "ขาว", "เนื้อ"]), ("36", ["ดำ", "เนื้อ"])):
        sec = box(b, "Size " + size, vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
        section_label(sec, f"ไซซ์ {size}")
        chips(sec, ["ดำ", "ขาว", "เนื้อ", "+ สี"], sel)
    grow(spacer(s))
    f = footer(s)
    links.append((button(f, "ถัดไป: สต็อกตั้งต้น"), "model_stock"))

    # 8 เพิ่มรุ่น ขั้น 3
    s = screen(page, "model_stock", "08 เพิ่มรุ่น · สต็อกตั้งต้น", 3, 1)
    links.append((app_bar(s, "เพิ่มรุ่น", "ขั้นที่ 3 จาก 3 · สต็อกตั้งต้น"), "back"))
    b = body(s, 24)
    txt(b, "มีของกี่แพ็กตอนนี้?", "Heading/H2")
    txt(b, "กรอกจากกระดาษที่จดไว้ได้เลย แตะช่องแล้วพิมพ์จำนวนแพ็ก ช่องขีด — คือไซซ์/สีที่รุ่นนี้ไม่มี", "Body/Default", "color/text/secondary")
    inst(b, C["size_grid"])
    inst(b, C["alert"]["Type=Warning"], {"Title": "ยังไม่แน่ใจจำนวน?", "Message": "กดข้ามไปก่อนได้ รุ่นนี้จะยังไม่ขึ้นในแคตตาล็อกจนกว่าจะกรอกสต็อก"}, fill=True)
    f = footer(s)
    links.append((button(f, "บันทึกรุ่น", icon="check"), "model_list"))
    links.append((button(f, "ข้ามไปก่อน กรอกทีหลัง", "Secondary"), "model_list"))

    # 9 รับของเข้า
    s = screen(page, "receive", "09 รับของเข้า", 4, 1)
    links.append((app_bar(s, "รับของเข้า", "กรอกจากบิลของยี่ปั๊ว"), "back"))
    b = body(s, 16)
    field(b, "ยี่ปั๊ว", "ยี่ปั๊วสำเพ็ง ซอย 3")
    field(b, "วันที่รับของ", "26 ต.ค. 2569")
    for name, meta in (("เสื้อใน A-102 ลูกไม้", "แพ็กละ 3 ตัว"), ("เสื้อใน A-215 ไร้โครง", "แพ็กละ 6 ตัว")):
        c = card(b, "Lot " + name, 12)
        h = box(c, "Header", hl(gap=8, sizingH="fill", sizingV="hug", fill="none"))
        col = box(h, "Name", vl(gap=0, sizingH="fill", sizingV="hug", fill="none"))
        txt(col, name, "Body/Strong")
        txt(col, meta, "Label/Default", "color/text/secondary")
        rm = box(h, "Remove", hl(mainAlign="center", fill="none"), w=48, h=48)
        icon_into(rm, C["icons"]["close"], "color/icon/default")
        inst(c, C["size_grid"])
    button(b, "เพิ่มรุ่นในรอบนี้", "Secondary", icon="plus")
    f = footer(s)
    sm = box(f, "Summary", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
    txt(sm, "รวม 2 รุ่น", "Body/Default", "color/text/secondary", fill=False)
    txt(sm, "68 แพ็ก", "Body/Strong", fill=False)
    links.append((button(f, "บันทึกรับของเข้า", icon="check"), "receive_detail"))

    # 10 รายละเอียดรับของเข้า
    s = screen(page, "receive_detail", "10 รายละเอียดรับของเข้า", 5, 1)
    links.append((app_bar(s, "รับของเข้า 26 ต.ค.", "บันทึกแล้ว"), "back"))
    b = body(s, 16)
    inst(b, C["alert"]["Type=Success"], {"Title": "บันทึกแล้ว", "Message": "สต็อกเพิ่มขึ้น 68 แพ็ก"}, fill=True)
    c = card(b, "Info", 8)
    for k, v in (("ยี่ปั๊ว", "ยี่ปั๊วสำเพ็ง ซอย 3"), ("วันที่", "26 ต.ค. 2569"), ("บันทึกโดย", "มิ้น (ผู้ช่วยร้าน)")):
        r = box(c, "Row " + k, hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
        txt(r, k, "Body/Default", "color/text/secondary", fill=False)
        txt(r, v, "Body/Strong", fill=False)
    c = card(b, "Lines", 8)
    txt(c, "รายการที่รับเข้า", "Heading/H3")
    for line, qty in (("A-102 · ไซซ์ 32 ดำ", "12 แพ็ก"), ("A-102 · ไซซ์ 34 ดำ", "8 แพ็ก"), ("A-102 · ไซซ์ 34 ขาว", "5 แพ็ก"),
                      ("A-215 · ไซซ์ 36 เนื้อ", "3 แพ็ก"), ("…อีก 6 รายการ", "40 แพ็ก")):
        r = box(c, "Line " + line, hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween", minHeight=40))
        txt(r, line, "Body/Default", fill=False)
        txt(r, qty, "Body/Strong", fill=False)
    f = footer(s)
    button(f, "แก้ไขการรับของเข้า", "Secondary", icon="edit")
    links.append((button(f, "ยกเลิกการรับของเข้า", "Danger", icon="close"), "overlay:cancel_dialog"))

    # 11 dialog ยืนยันยกเลิก (overlay)
    d = run([frame("11 ยืนยันยกเลิกรับของเข้า (overlay)", page, vl(fill="none", sizingH="hug", sizingV="hug"))])[0]["id"]
    run([{"command": "node.set", "params": {"ids": [d], "x": 6 * (W + 80), "y": 1100}}])
    di = inst(d, C["dialog"], {"Title": "ยกเลิกการรับของเข้านี้?",
                               "Message": "สต็อกจะลดลง 68 แพ็ก ถ้าของบางรายการขายไปแล้วจนสต็อกไม่พอ ระบบจะไม่ให้ยกเลิก"})
    SCREENS["cancel_dialog"] = d
    acts = [x for x in ds.descendants(ds.full(di)) if x["type"] == "INSTANCE" and x["name"] == "Button"]
    for a, label in zip(acts, ("ยกเลิกการรับของเข้า", "ไม่ยกเลิก")):
        run([{"command": "instance.setProperties", "params": {"ids": [a["id"]], "properties": {"Label": label}}}])
        links.append((a["id"], "close"))
    return links


def wire(links, flows):
    cmds = []
    for src, dest in links:
        if dest == "back":
            action = {"type": "back"}
        elif dest == "close":
            action = {"type": "closeOverlay"}
        elif dest.startswith("url:"):
            action = {"type": "openUrl", "url": dest[4:]}
        elif dest.startswith("overlay:"):
            action = {"type": "openOverlay", "dest": SCREENS[dest.split(":")[1]], "position": "center"}
        else:
            action = {"type": "navigate", "dest": SCREENS[dest]}
        p ={"id": src, "trigger": {"type": "onClick"}, "action": action}
        if action["type"] == "navigate":
            p["transition"] = {"type": "dissolve"}
            p["durationMs"] = 200
        cmds.append({"command": "proto.interaction.add", "params": p})
    cmds += [{"command": "proto.flow.add", "params": {"start": SCREENS[key], "name": name}} for key, name in flows]
    cmds.append({"command": "proto.settings", "params": {"device": "Custom size", "width": W, "height": 812}})
    run(cmds)


def setup():
    """Fill C with the component ids the screens use. Returns the page list."""
    comps, pages, sets, by_name = lookup()
    comp_page = [p for p in pages if p["name"] == "Components"][0]["id"]
    extra_components(comp_page)
    comps, pages, sets, by_name = lookup()
    C.clear()
    C.update({
        "btn": {k: v for k, v in by_name.items() if k.startswith("Style=")},
        "input": {n.split("=")[1]: variant(sets["Input"], n) for n in ("State=Default", "State=Focus", "State=Error", "State=Disabled")},
        "chip": {s: variant(sets["Chip"], f"Selected={s}") for s in ("True", "False")},
        "alert": {n: variant(sets["Alert"], n) for n in ("Type=Error", "Type=Warning", "Type=Success")},
        "badge": {thai: variant(sets["Status Badge"], f"Status={english}") for thai, english in
                  (("มีของ", "In Stock"), ("ใกล้หมด", "Low Stock"), ("หมด", "Out of Stock"))},
        "stepper": sets["Pack Stepper"], "model_card": by_name["Model Card"], "size_grid": by_name["Size Grid"],
        "bottom_nav": by_name["Bottom Nav"], "dialog": by_name["Confirm Dialog"], "logo_word": by_name["Logo/Wordmark"],
        "App Bar": by_name["App Bar"],
        "icons": {k.split("/", 1)[1]: v for k, v in by_name.items() if k.startswith("Icon/")},
    })
    return pages


def publish(page_name, build_fn, flows, preview_dir):
    """Rebuild one screens page from scratch, wire its prototype and export previews."""
    pages = setup()
    SCREENS.clear()
    old = [p["id"] for p in pages if p["name"] == page_name]
    if old:
        run([{"command": "page.delete", "params": {"id": old[0]}}])
    page = run([{"command": "page.add", "params": {"name": page_name}}])[0]["id"]
    # keep screen pages in ticket order after Foundations / Components / Decisions
    names = [p["name"] for p in pages if p["name"] != page_name] + [page_name]
    fixed = [n for n in names if not n[:2].isdigit()]
    index = len(fixed) + sorted(n for n in names if n[:2].isdigit()).index(page_name)
    run([{"command": "page.move", "params": {"id": page, "index": index}},
         {"command": "page.select", "params": {"id": page}}])
    links = build_fn(page)
    wire(links, flows)
    os.makedirs(preview_dir, exist_ok=True)
    targets = list(SCREENS.values())
    res = run([{"command": "export.add", "params": {"ids": targets, "setting": {"size": "1x", "format": "png"}}},
               {"command": "file.exportLayers", "params": {"ids": targets, "dir": preview_dir}}])[-1]
    normalize(ds.OUT)
    refine(ds.OUT)
    print(json.dumps({"page": page, "screens": SCREENS, "links": len(links),
                      "preview": [f["path"] for f in res["files"]]}, ensure_ascii=False, indent=1))


def main():
    publish(PAGE_NAME, build, [("signup", "Sign Up and Shop Setup"), ("home", "Receive Goods")], PREVIEW)


if __name__ == "__main__":
    main()
