"""Ticket 05: public catalogue and the owner's share-link screens in design/khonnai.figcraft.

Usage: python -I design/build_screens_05.py
Adds (or rebuilds) the page "05 Public Catalogue". Previews go to design/preview/05/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_design_system as ds  # noqa: E402
import build_screens_02 as s2  # noqa: E402
from build_screens_02 import (C, app_bar, body, box, button, card, chips, field, footer, frame, grow, hl,  # noqa: E402
                              icon_into, inst, run, screen, spacer, surface, txt, vl, W, SCREENS)

PAGE_NAME = "05 Public Catalogue"
PREVIEW = os.path.join(ds.ROOT, "preview", "05")
SHOP = "ร้านเจ๊หน่อยชุดชั้นใน"
LINK = "khonnai.app/c/9fK2xQ7m"
SHOP_LINE = "https://line.me/ti/p/~jaynoi"  # sample ลิงก์ LINE ร้าน, set by the owner when creating the shop

# name, meta, price line, [(variant, status)]
MODELS = [
    ("เสื้อใน A-215 ไร้โครง", "แพ็กละ 6 ตัว · เลือกสีได้", "฿320 / แพ็ก",
     [("32 ดำ", "มีของ"), ("32 ขาว", "ใกล้หมด"), ("34 ดำ", "มีของ"), ("34 ขาว", "มีของ"), ("34 เนื้อ", "หมด"),
      ("36 ดำ", "หมด"), ("36 เนื้อ", "มีของ")]),
    ("เสื้อใน A-102 ลูกไม้", "แพ็กละ 3 ตัว · คละสี", "฿180 / แพ็ก · ไซซ์ 36 ฿200",
     [("32", "มีของ"), ("34", "มีของ"), ("36", "ใกล้หมด")]),
    ("กางเกงใน P-310 เอวสูง", "แพ็กละ 12 ตัว · คละสี", "฿240 / แพ็ก",
     [("M", "มีของ"), ("L", "ใกล้หมด"), ("XL", "มีของ")]),
]


def variant_pill(parent, label, status):
    """One ตัวเลือกสินค้า with its stock status, as the customer sees it (never the real count)."""
    p = box(parent, "Variant " + label, hl(gap=6, padding=[6, 10, 6, 10], sizingH="hug", sizingV="hug", fill="#FFFFFF"))
    style = {"มีของ": ("color/bg/success-subtle", "color/text/success", "color/icon/success", "check"),
             "ใกล้หมด": ("color/bg/warning-subtle", "color/text/warning", "color/icon/warning", "alert"),
             "หมด": ("color/bg/subtle", "color/text/secondary", "color/icon/default", "close")}[status]
    surface(p, fill=style[0], radius="radius/sm")
    icon_into(p, C["icons"][style[3]], style[2])
    txt(p, f"{label} · {status}", "Label/Default", style[1], fill=False)


def catalogue_card(parent, name, meta, price, variants, big=False):
    c = card(parent, "Model " + name, 12)
    top = box(c, "Top", hl(gap=12, sizingH="fill", sizingV="hug", fill="none", crossAlign="min"))
    img = box(top, "Image", hl(mainAlign="center", fill="none"), w=96 if not big else 120, h=96 if not big else 120)
    surface(img, fill="color/bg/subtle", radius="radius/md")
    icon_into(img, C["icons"]["camera"], "color/icon/default")
    info = box(top, "Info", vl(gap=4, sizingH="fill", sizingV="hug", fill="none"))
    txt(info, name, "Heading/H3")
    txt(info, meta, "Label/Default", "color/text/secondary")
    txt(info, price, "Body/Strong", "color/text/brand")
    wrap = box(c, "Variants", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", wrap=True, crossGap=8))
    for v, st in variants:
        variant_pill(wrap, v, st)
    return c


def catalogue_header(s):
    h = box(s, "Shop header", vl(gap=4, padding=[20, 16, 16, 16], sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(h, fill="color/bg/brand")
    txt(h, SHOP, "Heading/H2", "color/text/on-brand")
    txt(h, "แคตตาล็อกสินค้า · อัปเดตตามสต็อกจริง 15:20", "Label/Default", "color/text/on-brand")
    return h


def order_bar(s):
    f = footer(s)
    txt(f, "สนใจรุ่นไหน ทักแชต LINE ของร้านเพื่อสั่งซื้อ", "Body/Default", "color/text/secondary")
    return button(f, "ทักแชต LINE ของร้าน", "Primary")


def build(page):
    links = []

    # 27 แคตตาล็อก (ลูกค้า)
    s = screen(page, "catalogue", "27 แคตตาล็อก (ลูกค้าเห็น)", 0)
    catalogue_header(s)
    b = body(s, 16)
    field(b, "ค้นหารุ่น", "พิมพ์ชื่อหรือรหัส")
    chips(b, ["ทุกรุ่น (12)", "เฉพาะที่มีของ"], ["ทุกรุ่น (12)"], "Filter")
    first = None
    for m in MODELS:
        c = catalogue_card(b, *m)
        first = first or c
    links.append((first, "catalogue_model"))
    links.append((order_bar(s), "url:" + SHOP_LINE))

    # 28 รุ่นในแคตตาล็อก
    s = screen(page, "catalogue_model", "28 แคตตาล็อก · รายละเอียดรุ่น", 1)
    top = box(s, "Back bar", hl(gap=4, padding=[8, 16, 8, 16], sizingH="fill", sizingV="hug", fill="#FFFFFF", minHeight=64))
    surface(top, fill="color/bg/surface", stroke="color/border/default")
    run([{"command": "node.set", "params": {"ids": [top], "strokeSides": [0, 0, 1, 0]}}])
    back = box(top, "Back", hl(mainAlign="center", fill="none"), w=40, h=48)
    icon_into(back, C["icons"]["chevron-left"], "color/icon/default")
    txt(top, SHOP, "Body/Strong")
    links.append((back, "back"))
    b = body(s, 16)
    photo = box(b, "Photo", hl(mainAlign="center", sizingH="fill", fill="none"), h=240)
    surface(photo, fill="color/bg/subtle", radius="radius/lg")
    icon_into(photo, C["icons"]["camera"], "color/icon/default")
    name, meta, price, variants = MODELS[0]
    txt(b, name, "Heading/H1")
    txt(b, meta, "Body/Default", "color/text/secondary")
    txt(b, price, "Heading/H2", "color/text/brand")
    txt(b, "ไซซ์และสี", "Heading/H3")
    for size in ("32", "34", "36"):
        row = box(b, "Size " + size, vl(gap=8, sizingH="fill", sizingV="hug", fill="none"))
        txt(row, f"ไซซ์ {size}", "Body/Strong")
        wrap = box(row, "Variants", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", wrap=True, crossGap=8))
        for v, st in variants:
            if v.startswith(size):
                variant_pill(wrap, v.split(" ", 1)[1], st)
    links.append((order_bar(s), "url:" + SHOP_LINE))

    # 29 ลิงก์ใช้ไม่ได้แล้ว
    s = screen(page, "catalogue_expired", "29 แคตตาล็อก · ลิงก์ใช้ไม่ได้", 2)
    b = body(s, 16)
    run([{"command": "node.set", "params": {"ids": [b], "padding": [120, 24, 24, 24], "crossAlign": "center"}}])
    circ = box(b, "Icon", hl(mainAlign="center", fill="none"), w=72, h=72)
    surface(circ, fill="color/bg/subtle", radius="radius/full")
    icon_into(circ, C["icons"]["alert"], "color/icon/default")
    t = txt(b, "ลิงก์นี้ใช้ไม่ได้แล้ว", "Heading/H2")
    m = txt(b, "ร้านเปลี่ยนลิงก์แคตตาล็อกใหม่ ทักแชตร้านเพื่อขอลิงก์ล่าสุด", "Body/Default", "color/text/secondary")
    run([{"command": "node.set", "params": {"ids": [t, m], "textAlign": "center"}}])

    # 30 แชร์แคตตาล็อก (เจ้าของร้าน)
    s = screen(page, "share", "30 แชร์แคตตาล็อก (เจ้าของร้าน)", 3)
    links.append((app_bar(s, "แชร์แคตตาล็อก", "ส่งลิงก์ให้ลูกค้าประจำในกลุ่ม LINE"), "back"))
    b = body(s, 24)
    c = card(b, "Link", 12)
    txt(c, "ลิงก์แคตตาล็อกของร้าน", "Body/Strong")
    lb = box(c, "Link box", hl(gap=8, padding=[12, 16, 12, 16], sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(lb, fill="color/bg/subtle", radius="radius/md")
    txt(lb, LINK, "Body/Default", "color/text/brand")
    links.append((button(c, "คัดลอกลิงก์", icon="check"), "share_copied"))
    links.append((button(c, "ดูแบบที่ลูกค้าเห็น", "Secondary", icon="search"), "catalogue"))
    c = card(b, "Rules", 8)
    txt(c, "ลูกค้าจะเห็นอะไรบ้าง", "Heading/H3")
    for line in ("รูป ชื่อรุ่น แพ็กละกี่ตัว และราคาแพ็ก",
                 "สถานะของแต่ละไซซ์ · สี: มีของ / ใกล้หมด / หมด ไม่เห็นจำนวนจริง",
                 "อัปเดตตามสต็อกทันที ไม่ต้องโพสต์ใหม่",
                 "รุ่นที่ซ่อนไว้ หรือยังไม่ได้กรอกสต็อกตั้งต้น จะไม่ขึ้น"):
        txt(c, "• " + line, "Body/Default")
    c = card(b, "Regenerate", 12)
    txt(c, "ลิงก์หลุดไปถึงคนอื่น?", "Heading/H3")
    txt(c, "สร้างลิงก์ใหม่ได้ ลิงก์เดิมจะใช้ไม่ได้ทันที แล้วส่งลิงก์ใหม่ในกลุ่ม LINE อีกครั้ง", "Body/Default", "color/text/secondary")
    links.append((button(c, "สร้างลิงก์ใหม่", "Secondary", icon="edit"), "overlay:regen"))

    # 30b คัดลอกแล้ว
    s = screen(page, "share_copied", "30b แชร์แคตตาล็อก · คัดลอกแล้ว", 4)
    links.append((app_bar(s, "แชร์แคตตาล็อก", "ส่งลิงก์ให้ลูกค้าประจำในกลุ่ม LINE"), "back"))
    b = body(s, 24)
    inst(b, C["alert"]["Type=Success"], {"Title": "คัดลอกลิงก์แล้ว", "Message": "เปิดกลุ่ม LINE ลูกค้าประจำ แล้วกดวางได้เลย"}, fill=True)
    c = card(b, "Link", 12)
    txt(c, "ลิงก์แคตตาล็อกของร้าน", "Body/Strong")
    lb = box(c, "Link box", hl(gap=8, padding=[12, 16, 12, 16], sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(lb, fill="color/bg/subtle", radius="radius/md")
    txt(lb, LINK, "Body/Default", "color/text/brand")
    links.append((button(c, "คัดลอกอีกครั้ง", "Secondary", icon="check"), "share_copied"))
    grow(spacer(s))

    # 31 dialog สร้างลิงก์ใหม่
    d = run([frame("31 ยืนยันสร้างลิงก์ใหม่ (overlay)", page, vl(fill="none", sizingH="hug", sizingV="hug"))])[0]["id"]
    run([{"command": "node.set", "params": {"ids": [d], "x": 5 * (W + 80), "y": 0}}])
    di = inst(d, C["dialog"], {"Title": "สร้างลิงก์แคตตาล็อกใหม่?",
                               "Message": "ลิงก์เดิมจะใช้ไม่ได้ทันที ลูกค้าที่มีลิงก์เดิมจะต้องได้ลิงก์ใหม่จากคุณ"})
    SCREENS["regen"] = d
    for a, label in zip([x for x in ds.descendants(ds.full(di)) if x["type"] == "INSTANCE" and x["name"] == "Button"],
                        ("สร้างลิงก์ใหม่", "ไม่สร้าง")):
        run([{"command": "instance.setProperties", "params": {"ids": [a["id"]], "properties": {"Label": label}}}])
        links.append((a["id"], "close"))
    return links


def main():
    s2.publish(PAGE_NAME, build, [("catalogue", "Public Catalogue"), ("share", "Share Catalogue")], PREVIEW)


if __name__ == "__main__":
    main()
