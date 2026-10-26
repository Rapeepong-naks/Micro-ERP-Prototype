"""Make FigCraft's page/layer sidebar readable when its UI font lacks Thai glyphs.

Only node and prototype-flow names are changed. Visible text, component IDs,
geometry, styles, variables, interactions, and embedded images are untouched.

Usage: python design/normalize_figcraft_names.py [path-to.figcraft]
"""

import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path


DEFAULT_FILE = Path(__file__).with_name("khonnai.figcraft")
THAI = re.compile(r"[\u0e00-\u0e7f]")

PAGE_NAMES = {
    "02 สมัคร ตั้งค่าร้าน รับของเข้า": "02 Onboarding and Receiving",
    "03 สต็อก ปรับยอด ใกล้หมด": "03 Stock and Adjustments",
    "04 บิลและการจอง": "04 Bills and Reservations",
    "05 แคตตาล็อก": "05 Public Catalogue",
}

SCREEN_NAMES = {
    "01 สมัครใช้งาน": "01 Sign Up",
    "02 เข้าสู่ระบบ": "02 Log In",
    "03 สร้างร้าน": "03 Create Shop",
    "04 หน้าแรก": "04 Home",
    "05 รายการรุ่น": "05 Model List",
    "06 เพิ่มรุ่น · ข้อมูลรุ่น": "06 Add Model - Details",
    "07 เพิ่มรุ่น · ไซซ์และราคา": "07 Add Model - Sizes and Prices",
    "07b เพิ่มรุ่น · สีของแต่ละไซซ์": "07b Add Model - Colours by Size",
    "08 เพิ่มรุ่น · สต็อกตั้งต้น": "08 Add Model - Opening Stock",
    "09 รับของเข้า": "09 Receive Goods",
    "10 รายละเอียดรับของเข้า": "10 Receiving Detail",
    "11 ยืนยันยกเลิกรับของเข้า (overlay)": "11 Cancel Receiving - Confirm",
    "12 สต็อกของรุ่น": "12 Model Stock",
    "13 ปรับยอด": "13 Adjust Stock",
    "13b ปรับยอด · ต่ำกว่าจำนวนที่จอง": "13b Adjust Stock - Below Reserved",
    "14 ประวัติสต็อก": "14 Stock History",
    "15 รายการใกล้หมด": "15 Low Stock",
    "16 สต็อกของรุ่น (ผู้ช่วยร้าน)": "16 Model Stock - Assistant",
    "17 ออกบิล": "17 Create Bill",
    "18 เพิ่มสินค้าในบิล": "18 Add Items to Bill",
    "19 ออกบิล · สต็อกไม่พอ": "19 Create Bill - Insufficient Stock",
    "20 ออกบิลแล้ว · รูปบิล": "20 Bill Created - Image",
    "21 รายการบิล": "21 Bill List",
    "22 แก้บิล": "22 Edit Bill",
    "23 จองของ": "23 Create Reservation",
    "24 รายการการจอง": "24 Reservation List",
    "25 รายละเอียดการจอง": "25 Reservation Detail",
    "26 ยืนยันยกเลิกการจอง (overlay)": "26 Cancel Reservation - Confirm",
    "27 แคตตาล็อก (ลูกค้าเห็น)": "27 Public Catalogue",
    "28 แคตตาล็อก · รายละเอียดรุ่น": "28 Catalogue Model Detail",
    "29 แคตตาล็อก · ลิงก์ใช้ไม่ได้": "29 Catalogue Link Expired",
    "30 แชร์แคตตาล็อก (เจ้าของร้าน)": "30 Share Catalogue",
    "30b แชร์แคตตาล็อก · คัดลอกแล้ว": "30b Catalogue Link Copied",
    "31 ยืนยันสร้างลิงก์ใหม่ (overlay)": "31 Regenerate Link - Confirm",
}

FLOW_NAMES = {
    "สมัครและตั้งค่าร้าน": "Sign Up and Shop Setup",
    "รับของเข้า": "Receive Goods",
    "ดูสต็อกและปรับยอด": "View and Adjust Stock",
    "รายการใกล้หมด": "Low Stock",
    "บิล": "Bills",
    "การจอง": "Reservations",
    "แคตตาล็อกที่ลูกค้าเห็น": "Public Catalogue",
    "แชร์แคตตาล็อก": "Share Catalogue",
}

LABELS = {
    "สมัครใช้งาน": "Sign Up", "เข้าสู่ระบบ": "Log In", "สร้างร้าน": "Create Shop",
    "ดูสต็อก": "View Stock", "ออกบิล": "Create Bill", "จองของ": "Create Reservation",
    "รับของเข้า": "Receive Goods", "เพิ่มรุ่นแรก": "Add First Model", "เพิ่มรุ่น": "Add Model",
    "ถัดไป: ไซซ์": "Next - Sizes", "ถัดไป: สต็อกตั้งต้น": "Next - Opening Stock",
    "บันทึกรุ่น": "Save Model", "ข้ามไปก่อน กรอกทีหลัง": "Skip Opening Stock",
    "เพิ่มรุ่นในรอบนี้": "Add Model to Receipt", "บันทึกรับของเข้า": "Save Receiving",
    "แก้ไขการรับของเข้า": "Edit Receiving", "ยกเลิกการรับของเข้า": "Cancel Receiving",
    "ปรับยอด": "Adjust Stock", "ประวัติ": "History", "บันทึกการปรับยอด": "Save Adjustment",
    "ดูการจองของไซซ์นี้": "View Related Reservations", "ยืนยันออกบิล": "Confirm Bill",
    "เพิ่มสินค้า": "Add Items", "ใส่ในบิล 3 แพ็ก": "Add 3 Packs to Bill",
    "บันทึกรูป": "Save Bill Image", "แชร์": "Share", "ออกบิลใหม่": "Create Another Bill",
    "บันทึกการแก้บิล": "Save Bill Changes", "ยืนยันการจอง": "Confirm Reservation",
    "เห็นสลิปแล้ว เปลี่ยนเป็นบิล": "Convert Reservation to Bill",
    "แก้การจอง": "Edit Reservation", "ยกเลิก": "Cancel",
    "คัดลอกลิงก์": "Copy Link", "คัดลอกอีกครั้ง": "Copy Again",
    "ดูแบบที่ลูกค้าเห็น": "View Public Catalogue", "ทักแชต LINE ของร้าน": "Open Shop LINE",
    "สร้างลิงก์ใหม่": "Regenerate Link",
    "ค้นหาด้วยชื่อลูกค้า": "Search Customer", "ค้นหารุ่น": "Search Model",
    "ชื่อร้าน": "Shop Name", "ชื่อหรือรหัสรุ่น": "Model Name or Code",
    "ตั้งรหัสผ่าน": "Set Password", "รหัสผ่าน": "Password", "ยี่ปั๊ว": "Wholesaler",
    "ราคาแพ็ก (บาท)": "Pack Price (THB)", "ลิงก์ LINE ของร้าน (ไม่บังคับ)": "Shop LINE Link",
    "ลูกค้า": "Customer", "วันที่รับของ": "Received Date", "เบอร์มือถือหรืออีเมล": "Phone or Email",
    "ไซซ์ 32": "Size 32", "ไซซ์ 34": "Size 34", "ไซซ์ 36": "Size 36",
    "ในร้าน": "On Hand", "จองไว้": "Reserved", "จอง": "Reserved", "ขายได้": "Available",
    "ดำ": "Black", "ขาว": "White", "เนื้อ": "Nude",
    "หมด": "Out of Stock", "ใกล้หมด": "Low Stock", "มีของ": "In Stock",
    "พื้นหลัง": "Background", "สถานะ": "Status", "ตัวอักษรและเส้น": "Text and Borders",
    "ราคาแพ็ก": "Pack Price", "สต็อกขั้นต่ำ": "Minimum Stock", "สีในแพ็ก": "Pack Colour",
    "ไซซ์ที่มี": "Available Sizes", "แพ็กละกี่ตัว": "Pieces per Pack",
}


def english_name(node):
    original = node.get("name", "")
    kind = node.get("type", "node")
    node_id = node["id"]
    if not THAI.search(original):
        return original
    if kind == "page":
        return PAGE_NAMES.get(original, f"Page {node_id}")
    if original in SCREEN_NAMES:
        return SCREEN_NAMES[original]
    if original.startswith("Status="):
        return "Status=" + LABELS.get(original[7:], "Variant")
    for prefix in ("Button ", "Input ", "Stat ", "Col ", "Row ", "Label ", "Tile ", "Group ", "Variant "):
        if original.startswith(prefix):
            value = original[len(prefix):]
            if value in LABELS:
                return prefix.strip() + " - " + LABELS[value]
            for thai, english in LABELS.items():
                value = value.replace(thai, english)
            value = re.sub(r"[^\x20-\x7E]", " ", value)
            value = " ".join(value.split())
            if value:
                return prefix.strip() + " - " + value[:60]
    model_code = re.search(r"[A-Z]-\d+", original)
    if model_code and kind in ("frame", "instance"):
        return f"{kind.title()} - {model_code.group()} #{node_id}"
    return f"{kind.title()} #{node_id}"


def normalize(path: Path | str) -> tuple[int, int]:
    path = Path(path)
    with zipfile.ZipFile(path, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    document = json.loads(next(body for info, body in members if info.filename == "document.json"))
    changed = 0
    for node in document["nodes"].values():
        updated = english_name(node)
        if updated != node.get("name"):
            node["name"] = updated
            changed += 1
        if node.get("type") == "page":
            for flow in node.get("flows", []):
                name = flow.get("name", "")
                if THAI.search(name):
                    flow["name"] = FLOW_NAMES.get(name, f"Flow {flow.get('id', '')}".strip())
    if any(THAI.search(node.get("name", "")) for node in document["nodes"].values()):
        raise RuntimeError("Thai node names remain after normalization")
    updated_document = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".figcraft", delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        with zipfile.ZipFile(temp_path, "w") as destination:
            for info, body in members:
                destination.writestr(info, updated_document if info.filename == "document.json" else body)
        with zipfile.ZipFile(temp_path, "r") as verify:
            result = json.loads(verify.read("document.json"))
            if set(verify.namelist()) != {info.filename for info, _ in members}:
                raise RuntimeError("Archive members changed")
            if len(result["nodes"]) != len(document["nodes"]) or result["pages"] != document["pages"]:
                raise RuntimeError("Document structure changed")
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return changed, len(document["nodes"])


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    changed, total = normalize(target)
    print(f"Renamed {changed} of {total} nodes in {target}")
