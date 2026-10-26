"""Build the khonnai design system (ticket 01) as a FigCraft file.

Usage: python -I design/build_design_system.py
Writes design/khonnai.figcraft and PNG previews under design/preview/.
Text uses Google Sans from design/fonts (loaded per session, not installed).
"""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from normalize_figcraft_names import normalize  # noqa: E402
CLI = r"C:\Program Files\FigCraft\figcraft-cli.exe"
OUT = os.path.join(ROOT, "khonnai.figcraft")
FONT = os.path.join(ROOT, "fonts", "GoogleSans[GRAD,opsz,wght].ttf")
BRAND = os.path.join(os.path.dirname(ROOT), "brand")
PREVIEW = os.path.join(ROOT, "preview")
FONT_FAMILY = "Google Sans"


def run(cmds, new=False):
    """Run commands in one headless session on OUT and return their results."""
    steps = [{"command": "text.loadFont", "params": {"path": FONT}}] + cmds
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False)
        script = f.name
    args = [CLI, "run", script, "--out", OUT] + ([] if new else ["--in", OUT])
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    os.unlink(script)
    results = []
    for line in proc.stdout.splitlines():
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        if not r.get("ok"):
            sys.exit(f"step failed: {r}")
        results.append(r.get("result"))
    if proc.returncode != 0:
        sys.exit(proc.stdout + proc.stderr)
    return results[1:]


def ids_of(results):
    return [r["id"] for r in results]


# ---------------------------------------------------------------- tokens
PRIMITIVES = {
    "white": "#FFFFFF", "gray/50": "#F6F7F9", "gray/100": "#EDEFF3", "gray/200": "#DDE1E8",
    "gray/400": "#9AA3B2", "gray/600": "#5B6474", "gray/900": "#1A1F29",
    "blue/50": "#EEF3FD", "blue/100": "#D9E4FA", "blue/600": "#1F56D6", "blue/700": "#1A47B3", "blue/800": "#163B91",
    "orange/50": "#FFF3E8", "orange/500": "#FF8A33", "orange/600": "#F07316", "orange/700": "#9A4A0C",
    "green/50": "#EAF7EF", "green/700": "#1B7A3E", "red/50": "#FDECEC", "red/600": "#C62828", "red/700": "#A61F1F",
}
SEMANTIC = {
    "color/bg/canvas": "gray/50", "color/bg/surface": "white", "color/bg/subtle": "gray/100",
    "color/bg/brand": "blue/600", "color/bg/brand-pressed": "blue/800", "color/bg/brand-subtle": "blue/50",
    "color/bg/accent": "orange/500", "color/bg/accent-pressed": "orange/600", "color/bg/danger": "red/600",
    "color/bg/disabled": "gray/100", "color/bg/success-subtle": "green/50", "color/bg/warning-subtle": "orange/50",
    "color/bg/danger-subtle": "red/50",
    "color/text/primary": "gray/900", "color/text/secondary": "gray/600", "color/text/disabled": "gray/400",
    "color/text/on-brand": "white", "color/text/on-accent": "gray/900", "color/text/brand": "blue/600",
    "color/text/success": "green/700", "color/text/warning": "orange/700", "color/text/danger": "red/700",
    "color/border/default": "gray/200", "color/border/strong": "gray/400", "color/border/focus": "blue/600",
    "color/border/danger": "red/600",
    "color/icon/default": "gray/600", "color/icon/brand": "blue/600", "color/icon/on-brand": "white",
    "color/icon/warning": "orange/700", "color/icon/danger": "red/700", "color/icon/success": "green/700",
}
DIMENSIONS = {
    "spacing/xs": 4, "spacing/sm": 8, "spacing/md": 12, "spacing/lg": 16, "spacing/xl": 24, "spacing/2xl": 32,
    "radius/sm": 8, "radius/md": 12, "radius/lg": 16, "radius/full": 999,
    "size/touch": 48, "size/touch-lg": 56,
}
# name: (style, size, line height)
TEXT_STYLES = {
    "Display": ("Bold", 32, 44), "Heading/H1": ("Bold", 28, 40), "Heading/H2": ("Bold", 24, 34),
    "Heading/H3": ("Medium", 20, 30), "Body/Large": ("Regular", 20, 32), "Body/Default": ("Regular", 18, 28),
    "Body/Strong": ("Medium", 18, 28), "Label/Default": ("Medium", 16, 24), "Button/Default": ("Medium", 18, 24),
    "Number/Large": ("Bold", 28, 36),
}


def hexval(sem):
    return PRIMITIVES[SEMANTIC[sem]]


def text_cmd(text, style, color, parent, x=0, y=0, name=None, width=None):
    size = TEXT_STYLES[style]
    props = {"fontFamily": FONT_FAMILY, "fontStyle": size[0], "fontSize": size[1], "lineHeight": size[2],
             "fill": hexval(color)}
    if name:
        props["name"] = name
    params = {"text": text, "x": x, "y": y, "parent": parent, "props": props}
    if width:
        params["width"] = width
    return {"command": "text.create", "params": params}


def style_text(ids, style, color):
    return [{"command": "style.apply", "params": {"ids": ids, "style": style}},
            {"command": "variable.bind", "params": {"ids": ids, "field": "fill", "variable": color}}]


def bind(ids, field, var):
    return {"command": "variable.bind", "params": {"ids": ids, "field": field, "variable": var}}


def frame(name, parent, props, x=0, y=0, w=None, h=None):
    p = {"name": name, "parent": parent, "x": x, "y": y, "props": props}
    if w:
        p["width"] = w
    if h:
        p["height"] = h
    return {"command": "frame.create", "params": p}


def node(nid):
    return run([{"command": "node.get", "params": {"id": nid}}])[0]


def descendants(n, kind=None):
    out = []
    for c in n.get("children", []):
        if kind is None or c["type"] == kind:
            out.append(c)
        out += descendants(c, kind)
    return out


def full(nid):
    """node.get only lists one level of children; walk instances/frames to collect vectors."""
    n = node(nid)
    for c in n.get("children", []):
        if c.get("childCount") and "children" not in c:
            c.update(full(c["id"]))
    return n


# ---------------------------------------------------------------- stage 1
def foundations():
    cmds = [{"command": "file.new", "params": {"name": "khonnai — App Design"}},
            {"command": "page.rename", "params": {"id": 1, "name": "Foundations"}},
            {"command": "page.add", "params": {"name": "Components"}},
            {"command": "page.add", "params": {"name": "Decisions"}},
            {"command": "variable.createCollection", "params": {"name": "Primitives", "modes": ["Value"]}},
            {"command": "variable.createCollection", "params": {"name": "Color", "modes": ["Light"]}},
            {"command": "variable.createCollection", "params": {"name": "Dimension", "modes": ["Value"]}}]
    for k, v in PRIMITIVES.items():
        cmds.append({"command": "variable.create", "params": {"collection": "Primitives", "name": k, "type": "color", "value": v}})
    for k, ref in SEMANTIC.items():
        cmds.append({"command": "variable.create", "params": {"collection": "Color", "name": k, "type": "color", "value": PRIMITIVES[ref]}})
        cmds.append({"command": "variable.set", "params": {"variable": k, "value": {"alias": ref}}})
    for k, v in DIMENSIONS.items():
        cmds.append({"command": "variable.create", "params": {"collection": "Dimension", "name": k, "type": "number", "value": v}})
    res = run(cmds, new=True)
    pages = {"Foundations": 1, "Components": res[2]["id"], "Decisions": res[3]["id"]}
    # text styles from sample layers
    samples = run([{"command": "page.select", "params": {"id": 1}}] +
                  [text_cmd(n, n, "color/text/primary", 1, 0, -2000 - 60 * i) for i, n in enumerate(TEXT_STYLES)])[1:]
    sids = ids_of(samples)
    run([{"command": "style.create", "params": {"type": "text", "name": n, "from": sids[i]}} for i, n in enumerate(TEXT_STYLES)] +
        [{"command": "edit.delete", "params": {"ids": sids}}])
    return pages


# ---------------------------------------------------------------- icons
ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    "package": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>',
    "receipt": '<path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    "bookmark": '<path d="M6 3h12v18l-6-4-6 4z"/>',
    "truck": '<path d="M3 6h11v10H3z"/><path d="M14 9h4l3 3v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "chevron-right": '<path d="M9 6l6 6-6 6"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
}


def icons(page):
    cmds = [{"command": "page.select", "params": {"id": page}}]
    for i, (name, body) in enumerate(ICONS.items()):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
               f'stroke="#5B6474" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
        cmds.append({"command": "file.import", "params": {"data": base64.b64encode(svg.encode()).decode(),
                                                          "name": f"{name}.svg", "x": i * 48, "y": 0}})
    res = run(cmds)[1:]
    fids = ids_of(res)
    cmds = []
    for fid, name in zip(fids, ICONS):
        cmds += [{"command": "component.create", "params": {"ids": [fid]}},
                 {"command": "object.rename", "params": {"ids": [fid], "name": f"Icon/{name}"}},
                 {"command": "node.set", "params": {"ids": [fid], "description": f"ไอคอน {name} 24px เส้น 2px สีจากตัวแปร color/icon/*"}}]
    run(cmds)
    vec = []
    for fid in fids:
        vec += [d["id"] for d in descendants(full(fid)) if d["type"] != "FRAME" and d["type"] != "GROUP"]
    run([bind(vec, "stroke", "color/icon/default")])
    return dict(zip(ICONS, fids))


def recolor_icon(instance_id, var):
    vec = [d["id"] for d in descendants(full(instance_id)) if d["type"] not in ("FRAME", "GROUP", "INSTANCE")]
    return bind(vec, "stroke", var)


# ---------------------------------------------------------------- components
def variant_set(page, specs, build, set_name, cols, cw, ch, x, y, description):
    """specs: list of (variant name, data). build(frame_id, data) -> list of extra commands (after frame exists).
    Returns (set id, variant frame ids)."""
    res = run([{"command": "page.select", "params": {"id": page}}] +
              [frame(name, page, data["frame"], x + (i % cols) * cw, y + (i // cols) * ch, data.get("w"), data.get("h"))
               for i, (name, data) in enumerate(specs)])[1:]
    fids = ids_of(res)
    for fid, (_, data) in zip(fids, specs):
        build(fid, data)
    run([{"command": "component.createMultiple" if len(fids) > 1 else "component.create", "params": {"ids": fids}}])
    if len(fids) == 1:
        run([{"command": "node.set", "params": {"ids": fids, "description": description, "name": set_name}}])
        return fids[0], fids
    res = run([{"command": "component.combineVariants", "params": {"ids": fids}}])
    set_id = res[0]["id"] if isinstance(res[0], dict) and "id" in res[0] else res[0]
    run([{"command": "node.set", "params": {"ids": [set_id], "name": set_name, "description": description}}])
    return set_id, fids


def add_props(set_id, fids, props):
    """props: list of (name, type, child-name, field, default). Binds the named child layer in every variant."""
    cmds = []
    for name, ptype, child, field, default in props:
        first = None
        for fid in fids:
            kid = [c for c in descendants(full(fid)) if c["name"] == child][0]["id"]
            if first is None:
                p = {"id": set_id, "name": name, "type": ptype, "layer": kid}
                if default is not None:
                    p["default"] = default
                cmds.append({"command": "component.addProperty", "params": p})
                first = kid
            else:
                cmds.append({"command": "component.bindProperty", "params": {"layer": kid, "property": name, "field": field}})
    run(cmds)


def text_into(fid, text, style, color, name, fill_width=False):
    r = run([text_cmd(text, style, color, fid, name=name)])[0]
    tid = r["id"]
    cmds = style_text([tid], style, color)
    if fill_width:
        cmds.append({"command": "node.set", "params": {"ids": [tid], "sizingH": "fill", "textAutoResize": "height"}})
    run(cmds)
    return tid


def icon_into(fid, icon_id, var, name="Icon", size=None):
    r = run([{"command": "instance.create", "params": {"component": icon_id, "parent": fid}}])[0]
    iid = r["id"]
    cmds = [{"command": "object.rename", "params": {"ids": [iid], "name": name}}, recolor_icon(iid, var)]
    if size:
        cmds.append({"command": "node.set", "params": {"ids": [iid], "width": size, "height": size}})
    run(cmds)
    return iid


def surface(fid, fill=None, stroke=None, weight=1, radius=None, gap=None):
    cmds = []
    if fill:
        cmds.append(bind([fid], "fill", fill))
    if stroke:
        cmds += [{"command": "node.set", "params": {"ids": [fid], "stroke": hexval(stroke), "strokeWeight": weight, "strokeAlign": "inside"}},
                 bind([fid], "stroke", stroke)]
    if radius:
        cmds.append(bind([fid], "cornerRadius", radius))
    if gap:
        cmds.append(bind([fid], "gap", gap))
    if cmds:
        run(cmds)


def hl(**kw):
    p = {"layout": "horizontal", "crossAlign": "center"}
    p.update(kw)
    return p


def vl(**kw):
    p = {"layout": "vertical"}
    p.update(kw)
    return p


def components(page, ic):
    out = {}
    # Button ------------------------------------------------------------
    styles = {"Primary": ("color/bg/brand", "color/text/on-brand", "color/icon/on-brand", None),
              "Secondary": ("color/bg/surface", "color/text/brand", "color/icon/brand", "color/border/focus"),
              "Accent": ("color/bg/accent", "color/text/on-accent", "color/icon/default", None),
              "Danger": ("color/bg/danger", "color/text/on-brand", "color/icon/on-brand", None)}
    specs = []
    for s, colors in styles.items():
        for size, h, px in (("Large", 56, 24), ("Default", 48, 20)):
            for state in ("Default", "Disabled"):
                specs.append((f"Style={s}, Size={size}, State={state}",
                              {"frame": hl(mainAlign="center", padding=[0, px, 0, px], sizingH="hug", minWidth=h, fill="#FFFFFF"),
                               "h": h, "w": 160, "colors": colors, "disabled": state == "Disabled"}))

    def build_button(fid, d):
        bg, tx, icv, border = d["colors"]
        dis = d["disabled"]
        icon_into(fid, ic["plus"], "color/text/disabled" if dis else icv)
        text_into(fid, "ออกบิล", "Button/Default", "color/text/disabled" if dis else tx, "Label")
        surface(fid, fill="color/bg/disabled" if dis else bg, stroke=None if dis else border, weight=2,
                radius="radius/md", gap="spacing/sm")

    sid, fids = variant_set(page, specs, build_button, "Button", 4, 200, 88, 0, 120,
                            "ปุ่มหลักของแอป สูงขั้นต่ำ 48px (Default) / 56px (Large) — Primary: การกระทำหลักของหน้า, "
                            "Secondary: การกระทำรอง, Accent: ใช้น้อย เช่น CTA บน Landing page, Danger: ยกเลิก/ลบ")
    add_props(sid, fids, [("Label", "text", "Label", "characters", None),
                          ("Show icon", "boolean", "Icon", "visible", True),
                          ("Icon", "instanceSwap", "Icon", "mainComponent", None)])
    out["Button"] = (sid, fids)

    # Input -------------------------------------------------------------
    specs = [(f"State={s}", {"frame": vl(gap=8, sizingV="hug", fill="#FFFFFF"), "w": 343, "h": 100, "state": s})
             for s in ("Default", "Focus", "Error", "Disabled")]

    def build_input(fid, d):
        s = d["state"]
        run([{"command": "node.set", "params": {"ids": [fid], "fill": "none"}}])
        text_into(fid, "ชื่อรุ่น", "Label/Default", "color/text/disabled" if s == "Disabled" else "color/text/primary", "Label")
        box = run([frame("Field", fid, hl(padding=[0, 16, 0, 16], sizingH="fill"), h=56)])[0]["id"]
        surface(box, fill="color/bg/disabled" if s == "Disabled" else "color/bg/surface",
                stroke={"Focus": "color/border/focus", "Error": "color/border/danger"}.get(s, "color/border/strong"),
                weight=2 if s in ("Focus", "Error") else 1, radius="radius/md")
        text_into(box, "เช่น A-102", "Body/Default", "color/text/disabled" if s == "Disabled" else "color/text/secondary", "Value", True)
        text_into(fid, "กรุณาใส่ชื่อรุ่น" if s == "Error" else "ชื่อหรือรหัสที่ร้านใช้เรียก", "Label/Default",
                  "color/text/danger" if s == "Error" else "color/text/secondary", "Helper")

    sid, fids = variant_set(page, specs, build_input, "Input", 4, 380, 140, 0, 520,
                            "ช่องกรอกข้อความ สูง 56px ตัวอักษร 18px มีป้ายชื่ออยู่เหนือช่องเสมอ (ห้ามใช้ placeholder แทนป้ายชื่อ)")
    add_props(sid, fids, [("Label", "text", "Label", "characters", None), ("Value", "text", "Value", "characters", None),
                          ("Helper", "text", "Helper", "characters", None), ("Show helper", "boolean", "Helper", "visible", True)])
    out["Input"] = (sid, fids)

    # Pack Stepper ------------------------------------------------------
    specs = [(f"State={s}", {"frame": hl(gap=8, sizingH="hug", sizingV="hug", fill="#FFFFFF"), "state": s}) for s in ("Default", "Disabled")]

    def build_stepper(fid, d):
        dis = d["state"] == "Disabled"
        run([{"command": "node.set", "params": {"ids": [fid], "fill": "none"}}])
        for icon, nm in ((ic["minus"], "Decrease"), (None, "Value"), (ic["plus"], "Increase")):
            if icon:
                b = run([frame(nm, fid, hl(mainAlign="center"), w=56, h=56)])[0]["id"]
                surface(b, fill="color/bg/disabled" if dis else "color/bg/brand-subtle", radius="radius/md")
                icon_into(b, icon, "color/text/disabled" if dis else "color/icon/brand")
            else:
                v = run([frame("Value", fid, vl(crossAlign="center", mainAlign="center", fill="none"), w=72, h=56)])[0]["id"]
                text_into(v, "3", "Number/Large", "color/text/disabled" if dis else "color/text/primary", "Count")
                text_into(v, "แพ็ก", "Label/Default", "color/text/secondary", "Unit")

    sid, fids = variant_set(page, specs, build_stepper, "Pack Stepper", 2, 260, 110, 0, 720,
                            "ช่องกรอกจำนวนแพ็กแบบกด +/− ปุ่ม 56px แตะเลขตรงกลางเพื่อพิมพ์จำนวนเองได้")
    add_props(sid, fids, [("Count", "text", "Count", "characters", None), ("Unit", "text", "Unit", "characters", None)])
    out["Pack Stepper"] = (sid, fids)

    # Status Badge -------------------------------------------------------
    badge = {"มีของ": ("color/bg/success-subtle", "color/text/success", "color/icon/success", "check"),
             "ใกล้หมด": ("color/bg/warning-subtle", "color/text/warning", "color/icon/warning", "alert"),
             "หมด": ("color/bg/danger-subtle", "color/text/danger", "color/icon/danger", "close")}
    english_status = {"มีของ": "In Stock", "ใกล้หมด": "Low Stock", "หมด": "Out of Stock"}
    specs = [(f"Status={english_status[k]}", {"frame": hl(gap=4, padding=[6, 14, 6, 10], sizingH="hug", sizingV="hug", fill="#FFFFFF"), "v": v})
             for k, v in badge.items()]

    def build_badge(fid, d):
        bg, tx, icv, icn = d["v"]
        icon_into(fid, ic[icn], icv, size=20)
        text_into(fid, [k for k, v in badge.items() if v == d["v"]][0], "Label/Default", tx, "Label")
        surface(fid, fill=bg, radius="radius/full")

    sid, fids = variant_set(page, specs, build_badge, "Status Badge", 3, 160, 70, 600, 720,
                            "ป้ายสถานะสต็อก ใช้ทั้งไอคอนและข้อความ ไม่สื่อด้วยสีอย่างเดียว")
    out["Status Badge"] = (sid, fids)

    # Alert --------------------------------------------------------------
    alerts = {"Error": ("color/bg/danger-subtle", "color/border/danger", "color/icon/danger", "alert", "สต็อกไม่พอ",
                        "รุ่น A-102 ไซซ์ 34 สีดำ เหลือขายได้ 2 แพ็ก"),
              "Warning": ("color/bg/warning-subtle", "color/text/warning", "color/icon/warning", "alert", "การจองค้างเกิน 2 วัน",
                          "มี 3 รายการที่ยังไม่ได้เปลี่ยนเป็นบิล"),
              "Success": ("color/bg/success-subtle", "color/text/success", "color/icon/success", "check", "ออกบิลแล้ว",
                          "สต็อกถูกตัดเรียบร้อย")}
    specs = [(f"Type={k}", {"frame": hl(gap=12, padding=16, crossAlign="min", sizingV="hug", fill="#FFFFFF"), "w": 343, "v": v})
             for k, v in alerts.items()]

    def build_alert(fid, d):
        bg, bd, icv, icn, title, msg = d["v"]
        icon_into(fid, ic[icn], icv)
        col = run([frame("Content", fid, vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))])[0]["id"]
        text_into(col, title, "Body/Strong", "color/text/primary", "Title", True)
        text_into(col, msg, "Body/Default", "color/text/primary", "Message", True)
        surface(fid, fill=bg, stroke=bd, radius="radius/md")
        run([{"command": "node.set", "params": {"ids": [fid], "strokeLeftWeight": 4}}])

    sid, fids = variant_set(page, specs, build_alert, "Alert", 3, 380, 130, 0, 900,
                            "ข้อความแจ้งเตือนในหน้า บอกเป็นภาษาธรรมดาว่าเกิดอะไรขึ้นและต้องทำอะไรต่อ")
    add_props(sid, fids, [("Title", "text", "Title", "characters", None), ("Message", "text", "Message", "characters", None)])
    out["Alert"] = (sid, fids)

    # Model Card ---------------------------------------------------------
    specs = [("Model Card", {"frame": hl(gap=12, padding=12, sizingV="hug", fill="#FFFFFF"), "w": 343})]

    def build_card(fid, d):
        img = run([frame("Image", fid, hl(mainAlign="center"), w=72, h=72)])[0]["id"]
        surface(img, fill="color/bg/subtle", radius="radius/md")
        icon_into(img, ic["camera"], "color/icon/default")
        info = run([frame("Info", fid, vl(gap=2, sizingH="fill", sizingV="hug", fill="none"))])[0]["id"]
        text_into(info, "เสื้อใน A-102", "Body/Strong", "color/text/primary", "Name", True)
        text_into(info, "แพ็กละ 3 ตัว · คละสี", "Label/Default", "color/text/secondary", "Meta")
        text_into(info, "฿180 / แพ็ก", "Body/Strong", "color/text/brand", "Price")
        icon_into(fid, ic["chevron-right"], "color/icon/default", name="Chevron")
        surface(fid, fill="color/bg/surface", stroke="color/border/default", radius="radius/lg")

    cid, fids = variant_set(page, specs, build_card, "Model Card", 1, 0, 0, 0, 1120,
                            "การ์ดรุ่นในรายการรุ่นและผลค้นหา แตะทั้งการ์ดเพื่อเปิดรุ่น")
    add_props(cid, fids, [("Name", "text", "Name", "characters", None), ("Meta", "text", "Meta", "characters", None),
                          ("Price", "text", "Price", "characters", None)])
    out["Model Card"] = (cid, fids)

    # Grid Cell ----------------------------------------------------------
    cells = {"Filled": ("12", "Body/Strong", "color/text/primary", "color/bg/surface", "color/border/strong"),
             "Empty": ("0", "Body/Default", "color/text/secondary", "color/bg/surface", "color/border/strong"),
             "Unavailable": ("—", "Body/Default", "color/text/disabled", "color/bg/disabled", None)}
    specs = [(f"State={k}", {"frame": hl(mainAlign="center", fill="#FFFFFF"), "w": 64, "h": 56, "v": v}) for k, v in cells.items()]

    def build_cell(fid, d):
        val, st, tx, bg, bd = d["v"]
        text_into(fid, val, st, tx, "Value")
        surface(fid, fill=bg, stroke=bd, radius="radius/sm")

    sid, fids = variant_set(page, specs, build_cell, "Grid Cell", 3, 88, 0, 400, 1120,
                            "ช่องจำนวนแพ็กในตารางไซซ์ × สี — Unavailable คือคู่ไซซ์/สีที่รุ่นนี้ไม่มี")
    add_props(sid, fids, [("Value", "text", "Value", "characters", None)])
    out["Grid Cell"] = (sid, fids)
    cell = dict(zip(cells, fids))

    # Size Grid ----------------------------------------------------------
    gid = run([frame("Size Grid", page, vl(gap=8, padding=12, sizingH="hug", sizingV="hug", fill="#FFFFFF"), 400, 1280)])[0]["id"]
    surface(gid, fill="color/bg/surface", stroke="color/border/default", radius="radius/lg")
    rows = [("ไซซ์", ["ดำ", "ขาว", "เนื้อ"]), ("32", [("Filled", "12"), ("Empty", "0"), ("Unavailable", "—")]),
            ("34", [("Filled", "8"), ("Filled", "5"), ("Empty", "0")]), ("36", [("Empty", "0"), ("Unavailable", "—"), ("Filled", "3")])]
    for label, items in rows:
        header = label == "ไซซ์"
        r = run([frame("Header" if header else f"Row {label}", gid, hl(gap=8, sizingH="hug", sizingV="hug", fill="none"))])[0]["id"]
        lb = run([frame("Size", r, hl(fill="none"), w=56, h=28 if header else 56)])[0]["id"]
        text_into(lb, label, "Label/Default" if header else "Body/Strong", "color/text/secondary" if header else "color/text/primary", "Text")
        for it in items:
            if header:
                col = run([frame("Col", r, hl(mainAlign="center", fill="none"), w=64, h=28)])[0]["id"]
                text_into(col, it, "Label/Default", "color/text/secondary", "Text")
            else:
                inst = run([{"command": "instance.create", "params": {"component": cell[it[0]], "parent": r}}])[0]["id"]
                run([{"command": "instance.setProperties", "params": {"ids": [inst], "properties": {"Value": it[1]}}}])
    run([{"command": "component.create", "params": {"ids": [gid]}},
         {"command": "node.set", "params": {"ids": [gid], "description": "ตารางกรอกจำนวนแพ็กตามไซซ์ × สี ใช้กับรับของเข้า สต็อกตั้งต้น และดูสต็อก รุ่นที่แพ็กคละสีจะมีคอลัมน์เดียว"}}])
    out["Size Grid"] = (gid, [gid])

    # Nav Item / Bottom Nav ----------------------------------------------
    specs = [(f"Active={a}", {"frame": vl(gap=4, mainAlign="center", crossAlign="center", fill="none"), "w": 88, "h": 64, "a": a})
             for a in ("True", "False")]

    def build_nav(fid, d):
        act = d["a"] == "True"
        icon_into(fid, ic["home"], "color/icon/brand" if act else "color/icon/default")
        text_into(fid, "หน้าแรก", "Label/Default", "color/text/brand" if act else "color/text/secondary", "Label")

    nsid, nfids = variant_set(page, specs, build_nav, "Nav Item", 2, 112, 0, 0, 1280, "เมนูหนึ่งช่องในแถบนำทางล่าง")
    add_props(nsid, nfids, [("Label", "text", "Label", "characters", None), ("Icon", "instanceSwap", "Icon", "mainComponent", None)])
    out["Nav Item"] = (nsid, nfids)
    bn = run([frame("Bottom Nav", page, hl(mainAlign="spaceBetween", padding=8, sizingV="hug", fill="#FFFFFF"), 0, 1440, w=375)])[0]["id"]
    surface(bn, fill="color/bg/surface", stroke="color/border/default")
    run([{"command": "node.set", "params": {"ids": [bn], "strokeSides": [1, 0, 0, 0]}}])
    for lab, icn, act in (("หน้าแรก", "home", True), ("สต็อก", "package", False), ("บิล", "receipt", False), ("จอง", "bookmark", False)):
        inst = run([{"command": "instance.create", "params": {"component": nfids[0 if act else 1], "parent": bn}}])[0]["id"]
        run([{"command": "instance.setProperties", "params": {"ids": [inst], "properties": {"Label": lab, "Icon": ic[icn]}}}])
    run([{"command": "component.create", "params": {"ids": [bn]}},
         {"command": "node.set", "params": {"ids": [bn], "description": "แถบนำทางล่าง 4 เมนูหลัก: หน้าแรก / สต็อก / บิล / จอง"}}])
    out["Bottom Nav"] = (bn, [bn])

    # Confirm Dialog -----------------------------------------------------
    bfids = out["Button"][1]
    names = [f"Style={s}, Size={z}, State={t}" for s in styles for z in ("Large", "Default") for t in ("Default", "Disabled")]
    danger = bfids[names.index("Style=Danger, Size=Large, State=Default")]
    secondary = bfids[names.index("Style=Secondary, Size=Large, State=Default")]
    dl = run([frame("Confirm Dialog", page, vl(gap=16, padding=24, sizingV="hug", fill="#FFFFFF"), 900, 1120, w=327)])[0]["id"]
    surface(dl, fill="color/bg/surface", radius="radius/lg")
    run([{"command": "effect.add", "params": {"ids": [dl], "type": "dropShadow"}}])
    text_into(dl, "ยกเลิกการจองนี้?", "Heading/H3", "color/text/primary", "Title", True)
    text_into(dl, "ของ 3 แพ็กจะกลับมาขายได้ทันที", "Body/Default", "color/text/secondary", "Message", True)
    acts = run([frame("Actions", dl, vl(gap=8, sizingH="fill", sizingV="hug", fill="none"))])[0]["id"]
    for comp, label in ((danger, "ยกเลิกการจอง"), (secondary, "ไม่ยกเลิก")):
        inst = run([{"command": "instance.create", "params": {"component": comp, "parent": acts}}])[0]["id"]
        run([{"command": "instance.setProperties", "params": {"ids": [inst], "properties": {"Label": label, "Show icon": False}}},
             {"command": "node.set", "params": {"ids": [inst], "sizingH": "fill"}}])
    run([{"command": "component.create", "params": {"ids": [dl]}},
         {"command": "node.set", "params": {"ids": [dl], "description": "dialog ยืนยันก่อนการกระทำที่ย้อนกลับยาก ปุ่มเรียงแนวตั้งเต็มความกว้าง"}}])
    add_props(dl, [dl], [("Title", "text", "Title", "characters", None), ("Message", "text", "Message", "characters", None)])
    out["Confirm Dialog"] = (dl, [dl])

    # Logo ---------------------------------------------------------------
    logos = {}
    for name, file, (fw, fh), (iw, ix, iy) in (
            ("Logo/Icon", "khonnai-icon.png", (64, 64), (94, -15, -16)),
            ("Logo/Wordmark", "khonnai-wordmark.png", (228, 52), (296, -33, -69))):
        f = run([frame(name, page, {"fill": "none", "clip": True}, 1300 if "Icon" in name else 1400, 0, w=fw, h=fh)])[0]["id"]
        r = run([{"command": "image.place", "params": {"path": os.path.join(BRAND, file), "parent": f, "x": ix, "y": iy,
                                                        "width": iw, "mode": "fit"}}])[0]
        run([{"command": "component.create", "params": {"ids": [f]}},
             {"command": "node.set", "params": {"ids": [f], "description": f"โลโก้ khonnai (ไฟล์ต้นฉบับ brand/{file}) — ควรขอ SVG พื้นโปร่งใสมาแทน"}}])
        logos[name] = f
    out["Logo"] = logos
    return out


# ---------------------------------------------------------------- docs pages
def sheet(page, name, width, x=0, y=0):
    run([{"command": "page.select", "params": {"id": page}}])
    sid = run([frame(name, page, vl(gap=32, padding=48, sizingV="hug", fill="#FFFFFF"), x, y, w=width)])[0]["id"]
    surface(sid, fill="color/bg/surface")
    return sid


def add_text(parent, text, style, color="color/text/primary"):
    return text_into(parent, text, style, color, text[:24], True)


def foundations_page(page, word_logo):
    s = sheet(page, "Foundations Sheet", 1200)
    head = run([frame("Header", s, hl(gap=24, sizingV="hug", sizingH="fill", fill="none"))])[0]["id"]
    run([{"command": "instance.create", "params": {"component": word_logo, "parent": head}}])
    t = run([frame("Title", head, vl(gap=4, sizingH="fill", sizingV="hug", fill="none"))])[0]["id"]
    add_text(t, "Design system v1", "Heading/H1")
    add_text(t, "สำหรับเจ้าของร้านอายุ 40+ ที่ใช้มือถือเป็นหลัก — ตัวอักษรใหญ่ ปุ่มใหญ่ ภาษาไทยทั้งหมด", "Body/Default", "color/text/secondary")
    add_text(s, "สี", "Heading/H2")
    add_text(s, "สีแบรนด์เป็นค่าประมาณจากรูปโลโก้ (น้ำเงิน #1F56D6, ส้ม #FF8A33) — แก้ที่ตัวแปร Primitives แล้วทุกหน้าเปลี่ยนตาม",
             "Label/Default", "color/text/warning")
    groups = [("พื้นหลัง", ["color/bg/canvas", "color/bg/surface", "color/bg/brand", "color/bg/brand-subtle", "color/bg/accent", "color/bg/danger"]),
              ("สถานะ", ["color/bg/success-subtle", "color/bg/warning-subtle", "color/bg/danger-subtle", "color/text/success", "color/text/warning", "color/text/danger"]),
              ("ตัวอักษรและเส้น", ["color/text/primary", "color/text/secondary", "color/text/brand", "color/border/default", "color/border/strong", "color/border/focus"])]
    for g, vars_ in groups:
        add_text(s, g, "Body/Strong")
        row = run([frame(g, s, hl(gap=16, crossAlign="min", sizingH="hug", sizingV="hug", fill="none"))])[0]["id"]
        for v in vars_:
            sw = run([frame(v, row, vl(gap=8, sizingH="hug", sizingV="hug", fill="none"))])[0]["id"]
            r = run([{"command": "shape.rectangle", "params": {"x": 0, "y": 0, "width": 160, "height": 72, "parent": sw,
                                                                "props": {"cornerRadius": 12, "fill": hexval(v), "stroke": "#DDE1E8"}}}])[0]["id"]
            run([bind([r], "fill", v)])
            text_into(sw, v.replace("color/", ""), "Label/Default", "color/text/secondary", "Label")
    add_text(s, "ตัวอักษร", "Heading/H2")
    add_text(s, "Google Sans ทั้งหมด (มีตัวอักษรไทย ใบอนุญาต OFL) · น้ำหนักที่ใช้: Regular / Medium / Bold", "Label/Default", "color/text/secondary")
    samples = {"Display": "สต็อกวันนี้", "Heading/H1": "เสื้อใน A-102", "Heading/H2": "รายการใกล้หมด", "Heading/H3": "ยกเลิกการจองนี้?",
               "Body/Large": "ไซซ์ 34 สีดำ เหลือขายได้ 5 แพ็ก", "Body/Default": "แพ็กละ 3 ตัว ราคาแพ็กละ 180 บาท",
               "Body/Strong": "ยอดรวม 1,260 บาท", "Label/Default": "ชื่อหรือรหัสที่ร้านใช้เรียก", "Button/Default": "ออกบิล", "Number/Large": "12"}
    for st, ex in samples.items():
        w, sz, lh = TEXT_STYLES[st]
        row = run([frame(st, s, hl(gap=24, sizingH="hug", sizingV="hug", fill="none"))])[0]["id"]
        lab = run([frame("Spec", row, hl(fill="none"), w=240, h=lh)])[0]["id"]
        text_into(lab, f"{st} · {sz}/{lh} {w}", "Label/Default", "color/text/secondary", "Spec")
        text_into(row, ex, st, "color/text/primary", "Sample")
    add_text(s, "ระยะห่างและขนาด", "Heading/H2")
    for line in ("ระยะห่าง: 4 · 8 · 12 · 16 · 24 · 32 (spacing/xs → spacing/2xl)",
                 "มุมโค้ง: 8 · 12 · 16 · เต็ม (radius/sm → radius/full)",
                 "พื้นที่กดขั้นต่ำ 48px (size/touch) ปุ่มหลักของหน้าใช้ 56px (size/touch-lg)",
                 "ตัวอักษรเนื้อหาไม่ต่ำกว่า 18px ป้ายชื่อและข้อความรองไม่ต่ำกว่า 16px",
                 "สถานะสื่อด้วยไอคอน + ข้อความเสมอ ไม่ใช้สีอย่างเดียว",
                 "ทุกคู่สีตัวอักษร/พื้นผ่าน WCAG AA (4.5:1)"):
        add_text(s, "• " + line, "Body/Default")
    return s


def decisions_page(page):
    s = sheet(page, "Decisions Sheet", 900)
    add_text(s, "การตัดสินใจของ Design system v1", "Heading/H1")
    items = [
        ("1. ชุด UI component ตอนเขียนโค้ด: shadcn/ui",
         "ใช้ shadcn/ui เป็นฐาน เพราะเป็นโค้ดที่คัดลอกเข้าโปรเจกต์ ใช้ Tailwind ตรง ๆ และอิง CSS variables "
         "ตั้งชื่อตามตัวแปรในไฟล์นี้ได้เลย (เช่น var(--color-bg-brand)) ต้องปรับขนาดเริ่มต้นให้ใหญ่ขึ้น: ปุ่มสูง 48/56px ตัวอักษร 18px"),
        ("2. transitions.dev ใช้กับ motion เท่านั้น",
         "ใช้กับ: เปิด/ปิด dialog, toast หลังออกบิล, การเปลี่ยนตัวเลขในตัวกรอกจำนวนแพ็ก และการเปลี่ยนหน้า "
         "ห้ามใช้ motion ที่ทำให้ต้องรอก่อนกดได้ ต้องเคารพ prefers-reduced-motion และตรวจเงื่อนไขของรายการ Pro only ก่อนใช้"),
        ("3. ฟอนต์: Google Sans",
         "ใช้ Google Sans ทั้งหัวข้อและเนื้อหา (ตัวปกติ ไม่ใช่ Google Sans Flex เพราะ Flex ไม่มีตัวอักษรไทย) "
         "ใบอนุญาต OFL ไฟล์อยู่ที่ design/fonts ในโปรเจกต์ ตอนเขียนโค้ดโหลดจาก Google Fonts"),
        ("4. ไม่สร้าง Dark mode ในระยะแรก",
         "ใช้ในร้านช่วงกลางวันเป็นหลัก ตัวแปรสีแยกเป็นชั้น Primitives → Color ไว้แล้ว เพิ่ม mode ภายหลังได้"),
        ("5. สีส้มใช้เป็นสีเน้นเท่านั้น",
         "ส้ม #FF8A33 บนพื้นขาวมี contrast ต่ำกว่า 4.5:1 จึงไม่ใช้เป็นสีตัวอักษร ตัวอักษรบนปุ่มส้มใช้สีเข้ม "
         "และป้าย \"ใกล้หมด\" ใช้ส้มเข้ม #9A4A0C บนพื้นส้มอ่อน"),
        ("6. ไฟล์ออกแบบอยู่ใน FigCraft",
         "ย้ายจาก Figma มาที่ FigCraft (design/khonnai.figcraft) เพราะโควตา Figma MCP ของแพ็กเกจ Starter เต็ม "
         "ไฟล์นี้สร้างจากสคริปต์ design/build_design_system.py"),
    ]
    for h, b in items:
        add_text(s, h, "Heading/H3")
        add_text(s, b, "Body/Default", "color/text/secondary")
    add_text(s, "ยังเปิดอยู่", "Heading/H2")
    for line in ("รหัสสีแบรนด์จริง (ตอนนี้เป็นค่าประมาณจากรูปโลโก้)",
                 "ไฟล์โลโก้ SVG พื้นโปร่งใส (ตอนนี้เป็น PNG พื้นขาว)",
                 "ไอคอนเป็นชุดวาดเองแบบเส้น 2px ถ้าจะใช้ lucide-react ตอนเขียนโค้ด ควรสลับเป็นไอคอน lucide ในไฟล์นี้ด้วย"):
        add_text(s, "• " + line, "Body/Default")
    return s


def preview(ids_names):
    os.makedirs(PREVIEW, exist_ok=True)
    cmds = []
    for nid, _ in ids_names:
        cmds.append({"command": "export.add", "params": {"ids": [nid], "setting": {"size": "1x", "format": "png"}}})
    cmds.append({"command": "file.exportLayers", "params": {"ids": [i for i, _ in ids_names], "dir": PREVIEW}})
    return run(cmds)[-1]


def main():
    pages = foundations()
    run([{"command": "page.select", "params": {"id": pages["Components"]}}])
    ic = icons(pages["Components"])
    comps = components(pages["Components"], ic)
    f = foundations_page(pages["Foundations"], comps["Logo"]["Logo/Wordmark"])
    d = decisions_page(pages["Decisions"])
    targets = [(f, "Foundations"), (d, "Decisions")] + [(v[0], k) for k, v in comps.items() if k != "Logo"]
    print(json.dumps({"file": OUT, "pages": pages, "icons": ic,
                      "components": {k: (v[0] if k != "Logo" else v) for k, v in comps.items()},
                      "preview": preview(targets)}, ensure_ascii=False, indent=1))
    normalize(Path(OUT))


if __name__ == "__main__":
    main()
