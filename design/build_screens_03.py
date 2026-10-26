"""Ticket 03: stock view, adjustments, stock history and low-stock list in design/khonnai.figcraft.

Usage: python -I design/build_screens_03.py
Adds (or rebuilds) the page "03 Stock and Adjustments". Previews go to design/preview/03/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_design_system as ds  # noqa: E402
import build_screens_02 as s2  # noqa: E402
from build_screens_02 import (C, app_bar, body, box, button, card, chips, footer, grow, hl, icon_into,  # noqa: E402
                              inst, run, screen, section_label, spacer, surface, txt, vl)

PAGE_NAME = "03 Stock and Adjustments"
PREVIEW = os.path.join(ds.ROOT, "preview", "03")
MODEL = "เสื้อใน A-215 ไร้โครง"
MIN_STOCK = 3
# variant, in shop, reserved
ROWS = [("32 · ดำ", 12, 2), ("32 · ขาว", 3, 0), ("34 · ดำ", 8, 3), ("34 · ขาว", 6, 0),
        ("34 · เนื้อ", 2, 2), ("36 · ดำ", 0, 0), ("36 · เนื้อ", 9, 1)]


def status(sellable):
    return "หมด" if sellable == 0 else "ใกล้หมด" if sellable <= MIN_STOCK else None


def num_cell(parent, value, style="Body/Default", color="color/text/primary", w=60):
    c = box(parent, "Num", hl(mainAlign="center", fill="none"), w=w, h=32)
    txt(c, str(value), style, color, "Value", fill=False)
    return c


def stock_table(parent, rows, tappable=None):
    """A card listing each ตัวเลือกสินค้า with จำนวนในร้าน / จอง / ขายได้. Returns {variant: row id}."""
    t = card(parent, "Stock table", 0)
    run([{"command": "node.set", "params": {"ids": [t], "padding": [8, 12, 8, 12]}}])
    head = box(t, "Header", hl(gap=0, sizingH="fill", sizingV="hug", fill="none", minHeight=40))
    txt(head, "ไซซ์ · สี", "Label/Default", "color/text/secondary", "Variant")
    for lab in ("ในร้าน", "จอง", "ขายได้"):
        c = box(head, "Col " + lab, hl(mainAlign="center", fill="none"), w=60, h=32)
        txt(c, lab, "Label/Default", "color/text/secondary", "Text", fill=False)
    out = {}
    for variant, shop, reserved in rows:
        sell = shop - reserved
        st = status(sell)
        r = box(t, "Row " + variant, hl(gap=0, sizingH="fill", sizingV="hug", fill="none", minHeight=56, padding=[8, 0, 8, 0]))
        surface(r, stroke="color/border/default")
        run([{"command": "node.set", "params": {"ids": [r], "strokeSides": [1, 0, 0, 0]}}])
        left = box(r, "Variant", vl(gap=4, sizingH="fill", sizingV="hug", fill="none"))
        txt(left, variant, "Body/Strong", fill=False)
        if st:
            inst(left, C["badge"][st])
        num_cell(r, shop)
        num_cell(r, reserved, color="color/text/secondary")
        num_cell(r, sell, "Body/Strong", "color/text/danger" if st == "หมด" else "color/text/primary")
        if tappable:
            icon_into(r, C["icons"]["chevron-right"], "color/icon/default", name="Chevron", size=20)
        out[variant] = r
    return out


def summary(parent, rows):
    shop = sum(r[1] for r in rows)
    reserved = sum(r[2] for r in rows)
    row = box(parent, "Summary", hl(gap=8, sizingH="fill", sizingV="hug", fill="none"))
    for lab, val, color in (("ในร้าน", shop, "color/text/primary"), ("จองไว้", reserved, "color/text/secondary"),
                            ("ขายได้", shop - reserved, "color/text/brand")):
        c = card(row, "Stat " + lab, 2)
        run([{"command": "node.set", "params": {"ids": [c], "sizingH": "fill", "padding": [12, 12, 12, 12]}}])
        txt(c, lab, "Label/Default", "color/text/secondary")
        txt(c, f"{val}", "Number/Large", color)
        txt(c, "แพ็ก", "Label/Default", "color/text/secondary")


def nav_on_stock(s):
    nav = inst(s, C["bottom_nav"], fill=True)
    items = [c["id"] for c in ds.node(nav)["children"]]
    run([{"command": "instance.setProperties", "params": {"ids": [items[0]], "properties": {"Active": "False"}}},
         {"command": "instance.setProperties", "params": {"ids": [items[1]], "properties": {"Active": "True"}}}])


def info_rows(parent, pairs):
    c = card(parent, "Info", 8)
    for k, v in pairs:
        r = box(c, "Row " + k, hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
        txt(r, k, "Body/Default", "color/text/secondary", fill=False)
        txt(r, v, "Body/Strong", fill=False)
    return c


def stock_screen(page, key, title, col, assistant=False):
    links = []
    s = screen(page, key, title, col)
    links.append((app_bar(s, MODEL, f"แพ็กละ 6 ตัว · สีเดียว · ขั้นต่ำ {MIN_STOCK} แพ็ก"), "back"))
    b = body(s, 16)
    if assistant:
        note = box(b, "Role note", hl(gap=12, padding=12, sizingH="fill", sizingV="hug", fill="#FFFFFF", crossAlign="min"))
        surface(note, fill="color/bg/brand-subtle", radius="radius/md")
        icon_into(note, C["icons"]["eye-off"], "color/icon/brand")
        txt(note, "คุณเข้าใช้ในฐานะผู้ช่วยร้าน ดูสต็อกได้ แต่ปรับยอดหรือแก้ราคาไม่ได้", "Body/Default", "color/text/primary")
    summary(b, ROWS)
    txt(b, "ขายได้ = ของในร้าน − ของที่ลูกค้าจองไว้", "Label/Default", "color/text/secondary")
    rows = stock_table(b, ROWS, tappable=not assistant)
    if not assistant:
        links.append((rows["34 · ดำ"], "adjust"))
    acts = box(b, "Actions", hl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    if not assistant:
        links.append((button(acts, "ปรับยอด", "Secondary", icon="edit"), "adjust"))
    links.append((button(acts, "ประวัติ", "Secondary", icon="calendar"), "history"))
    nav_on_stock(s)
    return links


def adjust_screen(page, key, title, col, counted, error=False):
    links = []
    s = screen(page, key, title, col, 1)
    links.append((app_bar(s, "ปรับยอด", "A-215 · ไซซ์ 34 ดำ"), "back"))
    b = body(s, 24)
    info_rows(b, (("ในร้านตามระบบ", "8 แพ็ก"), ("ลูกค้าจองไว้", "3 แพ็ก"), ("ขายได้", "5 แพ็ก")))
    sec = box(b, "Count", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "นับได้จริงกี่แพ็ก?", "นับของบนชั้นทั้งหมด รวมของที่ลูกค้าจองไว้ด้วย")
    inst(sec, C["stepper"], {"Count": str(counted)})
    if error:
        inst(sec, C["alert"]["Type=Error"], {"Title": "ตั้งต่ำกว่าจำนวนที่จองไม่ได้",
                                             "Message": "ไซซ์ 34 ดำ มีลูกค้าจองไว้ 3 แพ็ก ต้องแก้หรือยกเลิกการจองก่อน แล้วค่อยปรับยอด"}, fill=True)
    else:
        diff = counted - 8
        res = box(sec, "Result", hl(gap=8, padding=12, sizingH="fill", sizingV="hug", fill="#FFFFFF"))
        surface(res, fill="color/bg/subtle", radius="radius/md")
        txt(res, f"ในร้านจะ{'ลดลง' if diff < 0 else 'เพิ่มขึ้น'} {abs(diff)} แพ็ก · ขายได้จะเหลือ {counted - 3} แพ็ก", "Body/Default")
    sec = box(b, "Reason", vl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    section_label(sec, "เหตุผล (ต้องเลือก)", "ช่วยให้รู้ว่าสต็อกหายไปเพราะอะไร")
    chips(sec, ["นับผิด", "ของเสีย", "ของหาย", "สต็อกตั้งต้น"], [] if error else ["ของเสีย"])
    if not error:
        grow(spacer(s))
    f = footer(s)
    if error:
        inst(f, C["btn"]["Style=Primary, Size=Large, State=Disabled"], {"Label": "บันทึกการปรับยอด", "Show icon": False}, fill=True)
        links.append((button(f, "ดูการจองของไซซ์นี้", "Secondary", icon="bookmark"), "back"))
    else:
        links.append((button(f, "บันทึกการปรับยอด", icon="check"), "history"))
    return links


def history_screen(page):
    links = []
    s = screen(page, "history", "14 ประวัติสต็อก", 2, 1)
    links.append((app_bar(s, "ประวัติสต็อก", "A-215 · ไซซ์ 34 ดำ"), "back"))
    b = body(s, 16)
    inst(b, C["alert"]["Type=Success"], {"Title": "ปรับยอดแล้ว", "Message": "ในร้านเหลือ 7 แพ็ก เหตุผล: ของเสีย"}, fill=True)
    entries = [("วันนี้ 14:05", "ปรับยอด · ของเสีย", "เจ๊หน่อย", "−1", "edit", "color/text/danger", "เหลือ 7"),
               ("25 ต.ค. 16:40", "บิล #0012 · คุณวิไล", "เจ๊หน่อย", "−2", "receipt", "color/text/danger", "เหลือ 8"),
               ("24 ต.ค. 10:15", "รับของเข้า · ยี่ปั๊วสำเพ็ง ซอย 3", "มิ้น (ผู้ช่วยร้าน)", "+6", "truck", "color/text/success", "เหลือ 10"),
               ("20 ต.ค. 09:00", "ปรับยอด · สต็อกตั้งต้น", "เจ๊หน่อย", "+4", "edit", "color/text/success", "เหลือ 4")]
    c = card(b, "Entries", 0)
    run([{"command": "node.set", "params": {"ids": [c], "padding": [4, 16, 4, 16]}}])
    for i, (when, what, who, delta, icn, color, left) in enumerate(entries):
        r = box(c, "Entry " + when, hl(gap=12, sizingH="fill", sizingV="hug", fill="none", padding=[12, 0, 12, 0], crossAlign="min"))
        if i:
            surface(r, stroke="color/border/default")
            run([{"command": "node.set", "params": {"ids": [r], "strokeSides": [1, 0, 0, 0]}}])
        ib = box(r, "Icon bg", hl(mainAlign="center", fill="none"), w=40, h=40)
        surface(ib, fill="color/bg/subtle", radius="radius/full")
        icon_into(ib, C["icons"][icn], "color/icon/default", size=20)
        mid = box(r, "Text", vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
        txt(mid, what, "Body/Strong")
        txt(mid, f"{when} · {who}", "Label/Default", "color/text/secondary")
        right = box(r, "Delta", vl(gap=2, sizingV="hug", sizingH="hug", fill="none", crossAlign="max"))
        txt(right, f"{delta} แพ็ก", "Body/Strong", color, fill=False)
        txt(right, left, "Label/Default", "color/text/secondary", fill=False)
    return links


def low_stock_screen(page):
    links = []
    s = screen(page, "low_stock", "15 รายการใกล้หมด", 3, 1)
    links.append((app_bar(s, "ใกล้หมด", "6 รายการ · ใช้ตอนสั่งของจากยี่ปั๊ว"), "back"))
    b = body(s, 16)
    groups = [("หมดแล้ว (2)", "หมด", [("เสื้อใน A-215 ไร้โครง", "ไซซ์ 34 เนื้อ", 0, 3), ("เสื้อใน A-215 ไร้โครง", "ไซซ์ 36 ดำ", 0, 3)]),
              ("ใกล้หมด (4)", "ใกล้หมด", [("เสื้อใน A-215 ไร้โครง", "ไซซ์ 32 ขาว", 3, 3),
                                          ("กางเกงใน P-310 เอวสูง", "ไซซ์ L", 2, 5),
                                          ("เสื้อใน A-102 ลูกไม้", "ไซซ์ 36", 4, 5),
                                          ("กางเกงใน P-118 เด็ก", "ไซซ์ M", 1, 4)])]
    first = None
    for title, st, items in groups:
        txt(b, title, "Heading/H3")
        c = card(b, "Group " + st, 0)
        run([{"command": "node.set", "params": {"ids": [c], "padding": [4, 16, 4, 16]}}])
        for i, (model, variant, sell, minimum) in enumerate(items):
            r = box(c, "Item " + variant, hl(gap=12, sizingH="fill", sizingV="hug", fill="none", padding=[12, 0, 12, 0]))
            if i:
                surface(r, stroke="color/border/default")
                run([{"command": "node.set", "params": {"ids": [r], "strokeSides": [1, 0, 0, 0]}}])
            mid = box(r, "Text", vl(gap=4, sizingH="fill", sizingV="hug", fill="none"))
            txt(mid, f"{model}", "Body/Strong")
            txt(mid, f"{variant} · ขายได้ {sell} / ขั้นต่ำ {minimum}", "Label/Default", "color/text/secondary")
            inst(r, C["badge"][st])
            first = first or r
    links.append((first, "stock"))
    return links


def build(page):
    links = []
    links += stock_screen(page, "stock", "12 สต็อกของรุ่น", 0)
    links += stock_screen(page, "stock_assistant", "16 สต็อกของรุ่น (ผู้ช่วยร้าน)", 1, assistant=True)
    links += adjust_screen(page, "adjust", "13 ปรับยอด", 0, 7)
    links += adjust_screen(page, "adjust_error", "13b ปรับยอด · ต่ำกว่าจำนวนที่จอง", 1, 2, error=True)
    links += history_screen(page)
    links += low_stock_screen(page)
    return links


def main():
    s2.publish(PAGE_NAME, build, [("stock", "View and Adjust Stock"), ("low_stock", "Low Stock")], PREVIEW)


if __name__ == "__main__":
    main()
