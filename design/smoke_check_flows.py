"""Check the click-through destinations in the saved FigCraft design archive."""

import json
from pathlib import Path
import re
import zipfile

file = Path(__file__).with_name("khonnai.figcraft")
with zipfile.ZipFile(file) as archive:
    assert archive.testzip() is None
    document = json.loads(archive.read("document.json"))
nodes = document["nodes"]
by_name = {node["name"]: node["id"] for node in nodes.values()}


def walk(node_id):
    yield nodes[str(node_id)]
    for child in nodes[str(node_id)].get("children", []):
        yield from walk(child)


def action(screen, label, *, prop=False):
    root = by_name[screen]
    matches = [node for node in walk(root)
               if (node.get("props", {}).get("Label") if prop else node["name"]) == label]
    assert len(matches) == 1, (screen, label, len(matches))
    interactions = matches[0].get("interactions", [])
    assert len(interactions) == 1, (screen, label, interactions)
    return interactions[0]["actions"][0]


def leads(screen, label, target, *, prop=False):
    result = action(screen, label, prop=prop)
    assert result == {"type": "navigate", "dest": by_name[target]}, (screen, label, result)


leads("09 Receive Goods", "Button - Save Receiving", "10 Receiving Detail")
leads("10 Receiving Detail", "App Bar", "04 Home")
leads("10 Receiving Detail", "Button - Edit Receiving", "10a Edit Receiving")
leads("10a Edit Receiving", "Button - Save Changes", "10b Receiving Edited")
leads("11 Cancel Receiving - Confirm", "ยกเลิกการรับของเข้า", "10c Receiving Cancelled", prop=True)
assert action("11 Cancel Receiving - Confirm", "ไม่ยกเลิก", prop=True) == {"type": "closeOverlay"}
leads("10c Receiving Cancelled", "Button - Go Home", "04 Home")
leads("20 Bill Created - Image", "App Bar", "21 Bill List")
leads("14 Stock History", "App Bar", "12 Model Stock")
leads("25 Reservation Detail", "App Bar", "24 Reservation List")
leads("25 Reservation Detail", "Button - Edit Reservation", "25a Edit Reservation")
leads("25a Edit Reservation", "Button - Save Changes", "25 Reservation Detail")
leads("26 Cancel Reservation - Confirm", "ยกเลิกการจอง", "25b Reservation Cancelled", prop=True)
assert action("26 Cancel Reservation - Confirm", "ไม่ยกเลิก", prop=True) == {"type": "closeOverlay"}
leads("25b Reservation Cancelled", "Button - Back to Reservations", "24 Reservation List")

tabs = {"หน้าแรก": "04 Home", "สต็อก": "05 Model List", "บิล": "21 Bill List", "จอง": "24 Reservation List"}
page_ids = set(document["pages"])
for page_id in page_ids:
    page_node = nodes[str(page_id)]
    if page_node["name"].startswith(("02 ", "03 ", "04 ", "05 ")):
        settings = page_node["prototype"]
        assert settings["device"] == "Custom size" and settings["custom_size"] == [375.0, 812.0] and settings["responsive"] is False
store_screens = [node for node in nodes.values() if node.get("type") == "frame"
                 and node.get("parent") in page_ids and node.get("width", 0) >= 350
                 and re.match(r"^\d", node.get("name", ""))
                 and not node["name"].startswith(("01 ", "02 ", "03 ", "27 ", "28 ", "29 "))]
for screen in store_screens:
    nav = [nodes[str(child)] for child in screen["children"] if nodes[str(child)]["name"] == "Bottom Nav"]
    assert len(nav) == 1 and nav[0].get("fixed") is True, screen["name"]
    assert nav[0]["transform"][5] == screen["height"] - nav[0]["height"], screen["name"]
    assert nav[0]["child_layout"]["absolute"] and nav[0]["constraints"] == {"horizontal": "leftRight", "vertical": "bottom"}, screen["name"]
    content_bottom = max((nodes[str(child)].get("transform", [0, 0, 0, 0, 0, 0])[5] + nodes[str(child)].get("height", 0)
                          for child in screen["children"] if child != nav[0]["id"]), default=0)
    assert content_bottom <= nav[0]["transform"][5], (screen["name"], content_bottom)
    number = int(re.match(r"^\d+", screen["name"]).group())
    active = ("บิล" if 17 <= number <= 22 else "จอง" if 23 <= number <= 25
              else "สต็อก" if 5 <= number <= 8 or 12 <= number <= 16 else "หน้าแรก")
    for label, target in tabs.items():
        leads(screen["name"], label, target, prop=True)
    selected = [nodes[str(i)]["props"]["Label"] for i in nav[0]["children"] if nodes[str(i)].get("component") == 246]
    assert selected == [active], (screen["name"], selected, active)

for node in nodes.values():
    if node.get("type") == "text":
        assert node.get("style", {}).get("font_family") == "Leelawadee UI", node["name"]
    for interaction in node.get("interactions", []):
        for item in interaction.get("actions", []):
            if item["type"] in ("navigate", "openOverlay"):
                assert str(item["dest"]) in nodes, (node["id"], item)

print(f"FigCraft check passed: readable Thai font, 375x812 device settings, nonoverlapping fixed navigation on {len(store_screens)} screens, and valid flow destinations.")
