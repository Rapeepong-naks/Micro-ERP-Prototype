"""Ticket 04: bills and reservations in design/khonnai.figcraft.

Usage: python -I design/build_screens_04.py
Adds (or rebuilds) the page "04 Bills and Reservations". Previews go to design/preview/04/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_design_system as ds  # noqa: E402
import build_screens_02 as s2  # noqa: E402
from build_screens_02 import (C, app_bar, body, box, button, card, chips, field, footer, grow, hl, icon_into,  # noqa: E402
                              inst, run, screen, section_label, spacer, surface, txt, vl, frame, W, SCREENS)

PAGE_NAME = "04 Bills and Reservations"
PREVIEW = os.path.join(ds.ROOT, "preview", "04")

# model, variant, packs, price per pack, sellable, dozen (None when the model's pack can't make 12)
LINES = [("เสื้อใน A-215 ไร้โครง", "ไซซ์ 34 · ดำ", 2, 320, 5, None),
         ("เสื้อใน A-102 ลูกไม้", "ไซซ์ 32 · คละสี", 4, 180, 9, 1),
         ("กางเกงใน P-310 เอวสูง", "ไซซ์ L · คละสี", 3, 240, 6, None)]


def baht(n):
    return f"฿{n:,}"


def line_item(parent, model, variant, packs, price, sellable, dozen, error=False, price_edited=False):
    c = card(parent, "Line " + model, 12)
    if error:
        surface(c, stroke="color/border/danger", weight=2)
    top = box(c, "Top", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", crossAlign="min"))
    col = box(top, "Name", vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
    txt(col, model, "Body/Strong")
    txt(col, f"{variant} · ขายได้ {sellable} แพ็ก", "Label/Default", "color/text/danger" if error else "color/text/secondary")
    rm = box(top, "Remove", hl(mainAlign="center", fill="none"), w=40, h=40)
    icon_into(rm, C["icons"]["close"], "color/icon/default")
    if dozen:
        unit = box(c, "Unit", hl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
        chips(unit, ["แพ็ก", "โหล"], ["โหล"], "Unit chips")
        run([{"command": "node.set", "params": {"ids": [ds.node(unit)["children"][0]["id"]], "sizingH": "hug"}}])
        txt(unit, f"1 โหล = {packs} แพ็ก", "Label/Default", "color/text/secondary")
    inst(c, C["stepper"], {"Count": str(dozen if dozen else packs), "Unit": "โหล" if dozen else "แพ็ก"})
    bottom = box(c, "Price", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
    left = box(bottom, "Unit price", hl(gap=4, sizingH="hug", sizingV="hug", fill="none"))
    txt(left, f"{baht(price)} / แพ็ก", "Body/Default", "color/text/brand" if price_edited else "color/text/secondary", fill=False)
    icon_into(left, C["icons"]["edit"], "color/icon/brand", size=20)
    txt(bottom, baht(packs * price), "Body/Strong", fill=False)
    return c


def total_footer(s, total, label, icon="check", disabled=False, secondary=None, note=None):
    f = footer(s)
    row = box(f, "Total", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
    txt(row, note or "ยอดรวม", "Body/Default", "color/text/secondary", fill=False)
    txt(row, baht(total), "Heading/H2", fill=False)
    if disabled:
        b = inst(f, C["btn"]["Style=Primary, Size=Large, State=Disabled"], {"Label": label, "Show icon": False}, fill=True)
    else:
        b = button(f, label, icon=icon)
    sec = button(f, secondary, "Secondary") if secondary else None
    return b, sec


def nav_on(s, index):
    nav = inst(s, C["bottom_nav"], fill=True)
    items = [c["id"] for c in ds.node(nav)["children"]]
    run([{"command": "instance.setProperties", "params": {"ids": [items[0]], "properties": {"Active": "False"}}},
         {"command": "instance.setProperties", "params": {"ids": [items[index]], "properties": {"Active": "True"}}}])


def list_row(parent, i, title, sub, right, right_sub=None, badge=None, name="Row"):
    r = box(parent, f"{name} {i}", hl(gap=12, sizingH="fill", sizingV="hug", fill="none", padding=[12, 0, 12, 0], minHeight=64))
    if i:
        surface(r, stroke="color/border/default")
        run([{"command": "node.set", "params": {"ids": [r], "strokeSides": [1, 0, 0, 0]}}])
    mid = box(r, "Text", vl(gap=4, sizingH="fill", sizingV="hug", fill="none"))
    txt(mid, title, "Body/Strong")
    txt(mid, sub, "Label/Default", "color/text/secondary")
    if badge:
        inst(mid, C["badge"][badge])
    rt = box(r, "Right", vl(gap=2, sizingH="hug", sizingV="hug", fill="none", crossAlign="max"))
    txt(rt, right, "Body/Strong", fill=False)
    if right_sub:
        txt(rt, right_sub, "Label/Default", "color/text/secondary", fill=False)
    return r


def list_card(parent, name):
    c = card(parent, name, 0)
    run([{"command": "node.set", "params": {"ids": [c], "padding": [4, 16, 4, 16]}}])
    return c


def bill_image(parent):
    """The picture of the bill the owner saves and sends to the customer on LINE."""
    paper = box(parent, "Bill image", vl(gap=12, padding=20, sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(paper, fill="color/bg/surface", stroke="color/border/strong", radius="radius/md")
    head = box(paper, "Head", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
    col = box(head, "Shop", vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
    txt(col, "ร้านเจ๊หน่อยชุดชั้นใน", "Heading/H3")
    txt(col, "บิล #0013 · 26 ต.ค. 2569 15:20", "Label/Default", "color/text/secondary")
    txt(paper, "ลูกค้า: คุณวิไล", "Body/Default")
    lines = box(paper, "Lines", vl(gap=6, sizingH="fill", sizingV="hug", fill="none"))
    for model, variant, packs, price, _, _ in LINES:
        r = box(lines, "Line", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween", crossAlign="min"))
        lcol = box(r, "Item", vl(gap=0, sizingH="fill", sizingV="hug", fill="none"))
        txt(lcol, model.split(" ", 1)[1], "Body/Default")
        txt(lcol, f"{variant} · {packs} แพ็ก × {baht(price)}", "Label/Default", "color/text/secondary")
        txt(r, baht(packs * price), "Body/Default", fill=False)
    tot = box(paper, "Total", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween", padding=[12, 0, 0, 0]))
    surface(tot, stroke="color/border/default")
    run([{"command": "node.set", "params": {"ids": [tot], "strokeSides": [1, 0, 0, 0]}}])
    txt(tot, "ยอดรวม 9 แพ็ก", "Body/Strong", fill=False)
    txt(tot, baht(sum(p * pr for _, _, p, pr, _, _ in LINES)), "Heading/H3", fill=False)
    return paper


def build(page):
    links = []
    total = sum(p * pr for _, _, p, pr, _, _ in LINES)

    # 17 ออกบิล
    s = screen(page, "bill_new", "17 ออกบิล", 0)
    links.append((app_bar(s, "ออกบิล", "หน้าร้าน หรือจากการจอง"), "back"))
    b = body(s, 16)
    field(b, "ลูกค้า", "คุณวิไล", "เลือกจากชื่อที่เคยใช้ หรือพิมพ์ชื่อใหม่ได้เลย")
    for i, ln in enumerate(LINES):
        line_item(b, *ln, price_edited=(i == 2))
    links.append((button(b, "เพิ่มสินค้า", "Secondary", icon="plus"), "pick"))
    ok, _ = total_footer(s, total, "ยืนยันออกบิล")
    links.append((ok, "bill_done"))

    # 18 เลือกสินค้า (ไซซ์/สี ของรุ่น)
    s = screen(page, "pick", "18 เพิ่มสินค้าในบิล", 1)
    links.append((app_bar(s, "เพิ่มสินค้า", "เสื้อใน A-215 ไร้โครง · ฿320 / แพ็ก"), "back"))
    b = body(s, 16)
    field(b, "ค้นหารุ่น", "A-215")
    txt(b, "เลือกจำนวนแพ็กของแต่ละไซซ์ · สี", "Body/Default", "color/text/secondary")
    rows = [("32 · ดำ", 10, 0), ("32 · ขาว", 3, 0), ("34 · ดำ", 5, 2), ("34 · ขาว", 6, 0), ("34 · เนื้อ", 0, 0), ("36 · เนื้อ", 8, 1)]
    c = list_card(b, "Variants")
    stepper_off = s2.variant(s2.lookup()[2]["Pack Stepper"], "State=Disabled")
    for i, (v, sell, n) in enumerate(rows):
        r = box(c, f"Variant {v}", hl(gap=12, sizingH="fill", sizingV="hug", fill="none", padding=[10, 0, 10, 0]))
        if i:
            surface(r, stroke="color/border/default")
            run([{"command": "node.set", "params": {"ids": [r], "strokeSides": [1, 0, 0, 0]}}])
        mid = box(r, "Text", vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))
        txt(mid, v, "Body/Strong")
        if sell == 0:
            inst(mid, C["badge"]["หมด"])
        else:
            txt(mid, f"ขายได้ {sell} แพ็ก", "Label/Default", "color/text/secondary")
        inst(r, stepper_off if sell == 0 else C["stepper"],
             {"Count": str(n), "Unit": "แพ็ก"})
    f = footer(s)
    links.append((button(f, "ใส่ในบิล 3 แพ็ก", icon="plus"), "back"))

    # 19 สต็อกไม่พอ
    s = screen(page, "bill_error", "19 ออกบิล · สต็อกไม่พอ", 2)
    links.append((app_bar(s, "ออกบิล", "หน้าร้าน หรือจากการจอง"), "back"))
    b = body(s, 16)
    inst(b, C["alert"]["Type=Error"], {"Title": "สต็อกไม่พอ", "Message": "A-215 ไซซ์ 34 ดำ เหลือขายได้ 5 แพ็ก ลดจำนวนแล้วลองอีกครั้ง"}, fill=True)
    field(b, "ลูกค้า", "คุณวิไล")
    model, variant, _, price, sell, dz = LINES[0]
    line_item(b, model, variant, 7, price, sell, dz, error=True)
    line_item(b, *LINES[1])
    total_footer(s, total + 5 * 320, "ยืนยันออกบิล", disabled=True)

    # 20 บิลสำเร็จ + รูปบิล
    s = screen(page, "bill_done", "20 ออกบิลแล้ว · รูปบิล", 3)
    links.append((app_bar(s, "บิล #0013", "ออกเมื่อ 15:20"), "back"))
    b = body(s, 16)
    inst(b, C["alert"]["Type=Success"], {"Title": "ออกบิลแล้ว", "Message": "สต็อกถูกตัด 9 แพ็ก"}, fill=True)
    bill_image(b)
    grow(spacer(s))
    f = footer(s)
    row = box(f, "Share", hl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    button(row, "บันทึกรูป", "Secondary", icon="camera")
    button(row, "แชร์", "Secondary")
    links.append((button(f, "ออกบิลใหม่", icon="plus"), "bill_new"))

    # 21 รายการบิล
    s = screen(page, "bills", "21 รายการบิล", 4)
    app_bar(s, "บิล", "วันนี้ 6 บิล · ฿12,480", back=False)
    b = body(s, 16)
    field(b, "ค้นหาด้วยชื่อลูกค้า", "พิมพ์ชื่อลูกค้า")
    txt(b, "วันนี้", "Heading/H3")
    c = list_card(b, "Today")
    first = None
    for i, (no, cust, when, items, amt) in enumerate((("#0013", "คุณวิไล", "15:20", "9 แพ็ก", total),
                                                     ("#0012", "ร้านแม่ศรี", "13:05", "14 แพ็ก", 3260),
                                                     ("#0011", "หน้าร้าน · คุณต้อม", "11:40", "2 แพ็ก", 480))):
        r = list_row(c, i, f"{no} · {cust}", f"{when} · {items}", baht(amt), name="Bill")
        first = first or r
    txt(b, "เมื่อวาน", "Heading/H3")
    c = list_card(b, "Yesterday")
    for i, (no, cust, when, items, amt) in enumerate((("#0010", "คุณสมชาย", "17:30", "6 แพ็ก", 1440),
                                                     ("#0009", "ร้านแม่ศรี", "10:10", "20 แพ็ก", 4800))):
        list_row(c, i, f"{no} · {cust}", f"{when} · {items}", baht(amt), name="Bill")
    f = footer(s)
    links.append((button(f, "ออกบิล", icon="plus"), "bill_new"))
    nav_on(s, 2)
    links.append((first, "bill_edit"))

    # 22 แก้บิล
    s = screen(page, "bill_edit", "22 แก้บิล", 5)
    links.append((app_bar(s, "แก้บิล #0013", "คุณวิไล · 26 ต.ค. 15:20"), "back"))
    b = body(s, 16)
    note = box(b, "Edit note", hl(gap=12, padding=12, sizingH="fill", sizingV="hug", fill="#FFFFFF", crossAlign="min"))
    surface(note, fill="color/bg/brand-subtle", radius="radius/md")
    icon_into(note, C["icons"]["edit"], "color/icon/brand")
    txt(note, "แก้จำนวนหรือราคาได้ สต็อกจะปรับตามส่วนต่างเมื่อกดบันทึก", "Body/Default")
    model, variant, packs, price, sell, dz = LINES[0]
    line_item(b, model, variant, 1, price, sell + packs, dz)
    for ln in LINES[1:]:
        line_item(b, *ln)
    diff = box(b, "Diff", hl(gap=8, padding=12, sizingH="fill", sizingV="hug", fill="#FFFFFF"))
    surface(diff, fill="color/bg/subtle", radius="radius/md")
    txt(diff, "A-215 ไซซ์ 34 ดำ: คืนสต็อก 1 แพ็ก", "Body/Default")
    ok, _ = total_footer(s, total - 320, "บันทึกการแก้บิล")
    links.append((ok, "bill_done"))

    # 23 สร้างการจอง
    s = screen(page, "res_new", "23 จองของ", 0, 1)
    links.append((app_bar(s, "จองของ", "ลูกค้าสั่งทาง LINE"), "back"))
    b = body(s, 16)
    field(b, "ลูกค้า", "คุณสมชาย", "ต้องใส่ชื่อลูกค้าทุกการจอง")
    for ln in LINES[:2]:
        line_item(b, *ln)
    links.append((button(b, "เพิ่มสินค้า", "Secondary", icon="plus"), "pick"))
    note = box(b, "Hold note", hl(gap=12, padding=12, sizingH="fill", sizingV="hug", fill="#FFFFFF", crossAlign="min"))
    surface(note, fill="color/bg/brand-subtle", radius="radius/md")
    icon_into(note, C["icons"]["bookmark"], "color/icon/brand")
    txt(note, "ของที่จองไว้จะขายให้คนอื่นไม่ได้ จนกว่าจะเปลี่ยนเป็นบิลหรือยกเลิก", "Body/Default")
    ok, _ = total_footer(s, 640 + 720, "ยืนยันการจอง", icon="bookmark")
    links.append((ok, "res_detail"))

    # 24 รายการการจอง
    s = screen(page, "reservations", "24 รายการการจอง", 1, 1)
    app_bar(s, "การจอง", "5 รายการที่ยังไม่เป็นบิล", back=False)
    b = body(s, 16)
    inst(b, C["alert"]["Type=Warning"], {"Title": "ค้างเกิน 2 วัน 2 รายการ", "Message": "ทักลูกค้าเรื่องโอนเงิน หรือยกเลิกเพื่อปล่อยของกลับมาขาย"}, fill=True)
    txt(b, "ค้างเกิน 2 วัน", "Heading/H3")
    c = list_card(b, "Stale")
    first = None
    for i, (cust, sub, amt, age) in enumerate((("คุณสมชาย", "2 รายการ · 6 แพ็ก", 1360, "จองเมื่อ 3 วันก่อน"),
                                               ("ร้านป้าแดง", "1 รายการ · 4 แพ็ก", 960, "จองเมื่อ 4 วันก่อน"))):
        r = list_row(c, i, cust, f"{sub} · {age}", baht(amt), name="Reservation")
        first = first or r
    txt(b, "ล่าสุด", "Heading/H3")
    c = list_card(b, "Recent")
    for i, (cust, sub, amt, age) in enumerate((("คุณวิไล", "3 รายการ · 9 แพ็ก", 2080, "วันนี้ 09:15"),
                                               ("ร้านแม่ศรี", "1 รายการ · 2 แพ็ก", 640, "เมื่อวาน 18:40"),
                                               ("คุณต้อม", "2 รายการ · 5 แพ็ก", 1150, "เมื่อวาน 14:00"))):
        list_row(c, i, cust, f"{sub} · {age}", baht(amt), name="Reservation")
    f = footer(s)
    links.append((button(f, "จองของ", icon="plus"), "res_new"))
    nav_on(s, 3)
    links.append((first, "res_detail"))

    # 25 รายละเอียดการจอง
    s = screen(page, "res_detail", "25 รายละเอียดการจอง", 2, 1)
    links.append((app_bar(s, "การจองของคุณสมชาย", "จองเมื่อ 23 ต.ค. · 3 วันก่อน"), "back"))
    b = body(s, 16)
    inst(b, C["alert"]["Type=Warning"], {"Title": "ค้างเกิน 2 วัน", "Message": "ยังไม่ได้รับสลิป ของ 6 แพ็กยังถูกกันไว้"}, fill=True)
    c = list_card(b, "Lines")
    for i, (model, variant, packs, price, _, _) in enumerate(LINES[:2]):
        list_row(c, i, model, f"{variant} · {packs} แพ็ก × {baht(price)}", baht(packs * price), name="Line")
    tot = box(b, "Total", hl(gap=8, sizingH="fill", sizingV="hug", fill="none", mainAlign="spaceBetween"))
    txt(tot, "ยอดที่ต้องโอน", "Body/Default", "color/text/secondary", fill=False)
    txt(tot, baht(1360), "Heading/H2", fill=False)
    grow(spacer(s))
    f = footer(s)
    links.append((button(f, "เห็นสลิปแล้ว เปลี่ยนเป็นบิล", icon="receipt"), "bill_done"))
    row = box(f, "More", hl(gap=12, sizingH="fill", sizingV="hug", fill="none"))
    links.append((button(row, "แก้การจอง", "Secondary", icon="edit"), "res_new"))
    links.append((button(row, "ยกเลิก", "Danger", icon="close"), "overlay:res_cancel"))

    # 26 dialog ยกเลิกการจอง
    d = run([frame("26 ยืนยันยกเลิกการจอง (overlay)", page, vl(fill="none", sizingH="hug", sizingV="hug"))])[0]["id"]
    run([{"command": "node.set", "params": {"ids": [d], "x": 3 * (W + 80), "y": 1100}}])
    di = inst(d, C["dialog"], {"Title": "ยกเลิกการจองของคุณสมชาย?",
                               "Message": "ของ 6 แพ็กจะกลับมาขายได้ทันที ลูกค้าจะไม่ได้รับแจ้งอัตโนมัติ"})
    SCREENS["res_cancel"] = d
    for a in [x for x in ds.descendants(ds.full(di)) if x["type"] == "INSTANCE" and x["name"] == "Button"]:
        links.append((a["id"], "close"))
    return links


def main():
    s2.publish(PAGE_NAME, build, [("bills", "Bills"), ("reservations", "Reservations")], PREVIEW)


if __name__ == "__main__":
    main()
