"""Complete the saved, edited, and cancelled click-through paths in khonnai.figcraft.

This operates on the FigCraft archive because the FigCraft CLI is not available
on every workstation. It writes atomically and is idempotent.
"""

import copy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from normalize_figcraft_names import normalize

DEFAULT_FILE = Path(__file__).with_name("khonnai.figcraft")
ENGLISH_BUTTONS = {"บันทึกการแก้ไข": "Save Changes", "กลับหน้าแรก": "Go Home", "กลับรายการจอง": "Back to Reservations"}


def refine(path: str | Path = DEFAULT_FILE) -> dict:
    path = Path(path)
    with zipfile.ZipFile(path) as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    doc = json.loads(next(data for info, data in members if info.filename == "document.json"))
    nodes = doc["nodes"]
    created = []
    changed = []

    def named(name):
        return next((n for n in nodes.values() if n.get("name") == name), None)

    def descendants(node_id):
        yield node_id
        for child in nodes[str(node_id)].get("children", []):
            yield from descendants(child)

    def find_child(root_id, label):
        return next((i for i in descendants(root_id) if nodes[str(i)].get("name") == label), None)

    def clone_screen(source_name, target_name, x, y):
        existing = named(target_name)
        if existing:
            return existing["id"], None
        source = named(source_name)
        if not source:
            return None, None
        originals = list(descendants(source["id"]))
        remap = {}
        for old_id in originals:
            remap[old_id] = doc["next_id"]
            doc["next_id"] += 1
        for old_id in originals:
            node = copy.deepcopy(nodes[str(old_id)])
            node["id"] = remap[old_id]
            node["parent"] = remap.get(node.get("parent"), node.get("parent"))
            node["children"] = [remap[i] for i in node.get("children", [])]
            for interaction in node.get("interactions", []):
                for action in interaction.get("actions", []):
                    if action.get("dest") in remap:
                        action["dest"] = remap[action["dest"]]
            nodes[str(node["id"])] = node
        root = nodes[str(remap[source["id"]])]
        root["name"] = target_name
        root["transform"] = list(root["transform"])
        root["transform"][4:6] = [float(x), float(y)]
        nodes[str(source["parent"])]["children"].append(root["id"])
        created.append(target_name)
        return root["id"], remap

    def link(node_id, destination=None, action="navigate"):
        if node_id is None:
            return
        target = nodes[str(node_id)]
        new_action = {"type": action}
        if action == "navigate":
            new_action["dest"] = destination
        target["interactions"] = [{
            "trigger": {"type": "onClick"}, "actions": [new_action],
            "transition": {"type": "dissolve" if action == "navigate" else "instant"},
            "duration_ms": 200 if action == "navigate" else 300, "easing": "easeOut"
        }]
        if target["type"] == "instance":
            target["overrides"] = sorted(set(target.get("overrides", [])) | {"interactions"})
        changed.append(node_id)

    def label(node_id, value):
        node = nodes[str(node_id)]
        node["props"] = {**node.get("props", {}), "Label": value}
        node["name"] = "Button - " + ENGLISH_BUTTONS.get(value, value) if node["type"] == "instance" else node["name"]
        if node["type"] == "instance":
            node["overrides"] = sorted(set(node.get("overrides", [])) | {"name", "props"})
        for child_id in descendants(node_id):
            child = nodes[str(child_id)]
            if child.get("name") == "Label" and child.get("type") == "text":
                child["characters"] = value
                break

    def text(node_id, value):
        if node_id is not None:
            node = nodes[str(node_id)]
            node["characters"] = value
            parent = nodes[str(node["parent"])]
            if parent.get("name") in ("Titles", "Content") and parent.get("parent") is not None:
                instance = nodes[str(parent["parent"])]
                if instance.get("type") == "instance" and node.get("name") in ("Title", "Subtitle", "Message"):
                    instance["props"] = {**instance.get("props", {}), node["name"]: value}
                    instance["overrides"] = sorted(set(instance.get("overrides", [])) | {"props"})

    def remove_subtree(node_id):
        node = nodes[str(node_id)]
        nodes[str(node["parent"])]["children"].remove(node_id)
        for i in list(descendants(node_id))[::-1]:
            del nodes[str(i)]

    home, receive, detail, cancel = [named(name) for name in (
        "04 Home", "09 Receive Goods", "10 Receiving Detail", "11 Cancel Receiving - Confirm")]
    if all((home, receive, detail, cancel)):
        detail_id = detail["id"]
        edit_id, edit_map = clone_screen("09 Receive Goods", "10a Edit Receiving", 1820, 2200)
        edited_id, edited_map = clone_screen("10 Receiving Detail", "10b Receiving Edited", 2275, 2200)
        cancelled_id, cancelled_map = clone_screen("10 Receiving Detail", "10c Receiving Cancelled", 2730, 2200)

        link(find_child(detail_id, "App Bar"), home["id"])
        link(find_child(detail_id, "Button - Edit Receiving"), edit_id)
        confirm = [i for i in descendants(cancel["id"]) if nodes[str(i)].get("type") == "instance"
                   and nodes[str(i)].get("props", {}).get("Label") in ("ยกเลิกการรับของเข้า", "ไม่ยกเลิก")]
        for i in confirm:
            if nodes[str(i)]["props"]["Label"] == "ยกเลิกการรับของเข้า":
                link(i, cancelled_id)
            else:
                link(i, action="closeOverlay")

        if edit_map:
            link(find_child(edit_id, "App Bar"), detail_id)
            save = find_child(edit_id, "Button - Save Receiving")
            label(save, "บันทึกการแก้ไข")
            link(save, edited_id)
            title = find_child(edit_id, "Titles")
            text(find_child(title, "Title"), "แก้ไขรับของเข้า")
            text(find_child(title, "Subtitle"), "แก้รายการที่บันทึกแล้ว")
        if edited_map:
            link(find_child(edited_id, "App Bar"), home["id"])
            link(find_child(edited_id, "Button - Edit Receiving"), edit_id)
            title = find_child(edited_id, "Titles")
            text(find_child(title, "Subtitle"), "แก้ไขแล้ว")
            content = find_child(edited_id, "Content")
            text(find_child(content, "Title"), "แก้ไขแล้ว")
            text(find_child(content, "Message"), "ยอดสต็อกปรับตามรายการที่แก้ไข")
        if cancelled_map:
            link(find_child(cancelled_id, "App Bar"), home["id"])
            title = find_child(cancelled_id, "Titles")
            text(find_child(title, "Subtitle"), "ยกเลิกแล้ว")
            content = find_child(cancelled_id, "Content")
            text(find_child(content, "Title"), "ยกเลิกแล้ว")
            text(find_child(content, "Message"), "สต็อกลดลง 68 แพ็ก")
            return_home = find_child(cancelled_id, "Button - Edit Receiving")
            label(return_home, "กลับหน้าแรก")
            link(return_home, home["id"])
            remove_subtree(find_child(cancelled_id, "Button - Cancel Receiving"))

    bills, bill_done, stock, history = [named(name) for name in (
        "21 Bill List", "20 Bill Created - Image", "12 Model Stock", "14 Stock History")]
    if bills and bill_done:
        link(find_child(bill_done["id"], "App Bar"), bills["id"])
    if stock and history:
        link(find_child(history["id"], "App Bar"), stock["id"])

    reservations, res_new, res_detail, res_cancel = [named(name) for name in (
        "24 Reservation List", "23 Create Reservation", "25 Reservation Detail", "26 Cancel Reservation - Confirm")]
    if all((reservations, res_new, res_detail, res_cancel)):
        edit_id, edit_map = clone_screen("23 Create Reservation", "25a Edit Reservation", 0, 2200)
        cancelled_id, cancelled_map = clone_screen("25 Reservation Detail", "25b Reservation Cancelled", 455, 2200)
        link(find_child(res_detail["id"], "App Bar"), reservations["id"])
        link(find_child(res_detail["id"], "Button - Edit Reservation"), edit_id)
        confirm = [i for i in descendants(res_cancel["id"]) if nodes[str(i)].get("type") == "instance"
                   and nodes[str(i)].get("props", {}).get("Label") in ("ยกเลิกการจอง", "ไม่ยกเลิก")]
        for i in confirm:
            if nodes[str(i)]["props"]["Label"] == "ยกเลิกการจอง":
                link(i, cancelled_id)
            else:
                link(i, action="closeOverlay")
        if edit_map:
            link(find_child(edit_id, "App Bar"), res_detail["id"])
            save = find_child(edit_id, "Button - Confirm Reservation")
            if save is None:
                save = next((i for i in descendants(edit_id) if nodes[str(i)].get("props", {}).get("Label") == "ยืนยันการจอง"), None)
            if save:
                label(save, "บันทึกการแก้ไข")
                link(save, res_detail["id"])
            title = find_child(edit_id, "Titles")
            text(find_child(title, "Title"), "แก้ไขการจอง")
            text(find_child(title, "Subtitle"), "ตรวจรายการก่อนบันทึก")
        if cancelled_map:
            link(find_child(cancelled_id, "App Bar"), reservations["id"])
            title = find_child(cancelled_id, "Titles")
            text(find_child(title, "Title"), "ยกเลิกการจองแล้ว")
            text(find_child(title, "Subtitle"), "สถานะยกเลิก")
            content = find_child(cancelled_id, "Content")
            text(find_child(content, "Title"), "ยกเลิกแล้ว")
            text(find_child(content, "Message"), "ของ 6 แพ็กกลับมาขายได้")
            primary = find_child(cancelled_id, "Button - Convert Reservation to Bill")
            label(primary, "กลับรายการจอง")
            link(primary, reservations["id"])
            remove_subtree(find_child(cancelled_id, "More"))

    destinations = {
        "หน้าแรก": named("04 Home"), "สต็อก": named("05 Model List"),
        "บิล": named("21 Bill List"), "จอง": named("24 Reservation List"),
    }
    if all(destinations.values()):
        page_ids = set(doc["pages"])
        template = find_child(destinations["หน้าแรก"]["id"], "Bottom Nav")
        store_screens = [node["id"] for node in list(nodes.values())
                         if node.get("type") == "frame" and node.get("parent") in page_ids
                         and node.get("width", 0) >= 350 and re.match(r"^\d", node.get("name", ""))
                         and not node["name"].startswith(("01 ", "02 ", "03 ", "27 ", "28 ", "29 "))]
        for screen_id in store_screens:
            current = nodes[str(screen_id)]
            nav = next((child for child in current.get("children", [])
                        if nodes[str(child)].get("name") == "Bottom Nav"), None)
            if nav is None:
                original = list(descendants(template))
                remap = {}
                for old_id in original:
                    remap[old_id] = doc["next_id"]
                    doc["next_id"] += 1
                for old_id in original:
                    copy_node = copy.deepcopy(nodes[str(old_id)])
                    copy_node["id"] = remap[old_id]
                    copy_node["parent"] = screen_id if old_id == template else remap[copy_node["parent"]]
                    copy_node["children"] = [remap[i] for i in copy_node.get("children", [])]
                    nodes[str(copy_node["id"])] = copy_node
                nav = remap[template]
                current["children"].append(nav)
                current["height"] += 81
                created.append(current["name"] + " / Bottom Nav")
            nav_node = nodes[str(nav)]
            if not nav_node.get("fixed"):
                current["layout"]["padding"][2] += 81
                nav_node["fixed"] = True
                nav_node["child_layout"]["absolute"] = True
                nav_node["child_layout"]["sizing_h"] = "fixed"
                changed.append(nav)
            # Keep the design canvas readable: place the menu after the content.
            # Bottom constraints pin that same fixed layer to the device viewport in play mode.
            target_y = current["height"] - nav_node["height"]
            if nav_node["transform"][5] != target_y or nav_node.get("constraints") != {"horizontal": "leftRight", "vertical": "bottom"}:
                nav_node["transform"][5] = target_y
                nav_node["constraints"] = {"horizontal": "leftRight", "vertical": "bottom"}
                changed.append(nav)
            number = int(re.match(r"^\d+", current["name"]).group())
            section = ("บิล" if 17 <= number <= 22 else "จอง" if 23 <= number <= 25
                       else "สต็อก" if 5 <= number <= 8 or 12 <= number <= 16 else "หน้าแรก")
            source_nav_id = find_child(destinations[section]["id"], "Bottom Nav")
            source_nav = nodes[str(source_nav_id)]
            for source_item, target_item in zip(source_nav["children"], nav_node["children"]):
                source_tree = list(descendants(source_item))
                target_tree = list(descendants(target_item))
                if len(source_tree) != len(target_tree):
                    raise RuntimeError(f"Bottom Nav component shape differs on {current['name']}")
                for source_id, target_id in zip(source_tree, target_tree):
                    source_node, target_node = nodes[str(source_id)], nodes[str(target_id)]
                    for field in ("component", "props", "fills", "strokes", "effects", "opacity", "styles", "bound", "overrides"):
                        if field in source_node:
                            target_node[field] = copy.deepcopy(source_node[field])
                        else:
                            target_node.pop(field, None)
                    if target_node.get("interactions") and target_node.get("type") == "instance":
                        target_node["overrides"] = sorted(set(target_node.get("overrides", [])) | {"interactions"})
            for item_id in nav_node["children"]:
                label_text = nodes[str(item_id)].get("props", {}).get("Label")
                if label_text in destinations:
                    link(item_id, destinations[label_text]["id"])

        home_root = destinations["หน้าแรก"]["id"]
        bill_new, res_new_screen, share, stock_screen = [named(name) for name in (
            "17 Create Bill", "23 Create Reservation", "30 Share Catalogue", "12 Model Stock")]
        for child_name, target in (("Tile - Create Bill", bill_new), ("Tile - Reserved", res_new_screen),
                                   ("Share catalogue", share)):
            if target:
                link(find_child(home_root, child_name), target["id"])
        if stock_screen:
            model_list = destinations["สต็อก"]["id"]
            for child_id in descendants(model_list):
                if nodes[str(child_id)].get("name") == "Model Card":
                    link(child_id, stock_screen["id"])

    for node in nodes.values():
        value = node.get("props", {}).get("Label")
        english = ENGLISH_BUTTONS.get(value) if isinstance(value, str) else None
        if english and node.get("name", "").startswith("Button - -"):
            node["name"] = "Button - " + english
            changed.append(node["id"])

    # Use one fixed mobile viewport for every page; responsive iPhone 17 on
    # onboarding resized only that page and made its flow look stretched.
    for page_id in doc["pages"]:
        page_node = nodes[str(page_id)]
        if page_node["name"].startswith(("02 ", "03 ", "04 ", "05 ")):
            prototype = page_node.setdefault("prototype", {})
            wanted = {"device": "Custom size", "custom_size": [375.0, 812.0], "responsive": False, "rotation": "portrait"}
            if any(prototype.get(key) != value for key, value in wanted.items()):
                prototype.update(wanted)
                changed.append(page_id)

    # Google Sans has no Thai glyphs in this file; the native player drew square boxes.
    # Leelawadee UI is installed with Windows and renders Thai in FigCraft's player/export.
    for node in nodes.values():
        if node.get("type") == "text" and node.get("style", {}).get("font_family") == "Google Sans":
            node["style"]["font_family"] = "Leelawadee UI"
            changed.append(node["id"])
    for style in doc["styles"]:
        if style.get("type") == "text" and style.get("style", {}).get("font_family") == "Google Sans":
            style["style"]["font_family"] = "Leelawadee UI"
            changed.append(style["id"])

    if not (created or changed):
        return {"created": [], "rewired": 0}
    output = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".figcraft", delete=False) as file:
        temporary = Path(file.name)
    try:
        with zipfile.ZipFile(temporary, "w") as target:
            for info, data in members:
                target.writestr(info, output if info.filename == "document.json" else data)
        with zipfile.ZipFile(temporary) as check:
            if check.testzip() or len(json.loads(check.read("document.json"))["nodes"]) != len(nodes):
                raise RuntimeError("Refined FigCraft archive failed validation")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    normalize(path)
    return {"created": created, "rewired": len(changed)}


if __name__ == "__main__":
    print(json.dumps(refine(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE), ensure_ascii=False))
