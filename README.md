# Khonnai — current files

| ใช้ทำอะไร | ไฟล์ปัจจุบัน |
| --- | --- |
| เปิดดูและแก้แบบใน FigCraft | `design/khonnai.figcraft` |
| เปิด prototype ที่กรอกข้อมูลและกดได้จริง | `prototype/index.html` |
| ส่งเว็บให้ผู้ใช้ทดสอบ | `dist/user-test-site/index.html` (สร้างจาก `prototype/` ล่าสุด) |
| วิธีทดสอบกับผู้ใช้ | `docs/user-test-plan.md` |
| กติกาหลังบันทึก แก้ไข ยกเลิก | `docs/flow-transitions.md` |
| ขอบเขตธุรกิจและคำศัพท์ | `GLOSSARY.md`, `docs/adr/` |

`prototype/` คือ **source of truth** ของเว็บทดสอบ ส่วน `dist/user-test-site/` คือชุดไฟล์ที่สร้างเพื่อส่งขึ้น static hosting ห้ามแก้ไฟล์ใน `dist/` โดยตรง หลังแก้ prototype ให้รัน:

```powershell
node prototype/smoke-check.cjs
node prototype/build-test-site.cjs
node prototype/check-test-site.cjs
```

`design/khonnai.figcraft` เป็นแบบ click-through แยกจากเว็บทดสอบ ฟอร์มใน FigCraft ไม่เก็บตัวเลขจริง ใช้ `python design/smoke_check_flows.py` ตรวจลิงก์ในแบบ (เครื่องนี้ใช้ Python ที่มากับ Codex: `& 'C:\Users\BANK\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' design/smoke_check_flows.py`) และปิดเปิดไฟล์ใน FigCraft ใหม่หลังสคริปต์แก้ไฟล์

`brand/` เก็บโลโก้ที่ใช้อยู่ และ `brand/references/` เก็บบอร์ดทดลองสีสำหรับอ้างอิงเท่านั้น ไฟล์สำรองและ PNG preview ที่ไม่ตรงกับแบบปัจจุบันถูกลบแล้ว

## GitHub / เว็บทดสอบ

ไฟล์ที่นำไปเผยแพร่เป็น static site อยู่ใน `dist/user-test-site/` เปิด `index.html` ในเครื่องหรืออัปโหลด **เนื้อหาทั้งโฟลเดอร์** ไปยังผู้ให้บริการ static hosting ได้ โดยไม่ต้องติดตั้งแพ็กเกจ Node บนเซิร์ฟเวอร์ ก่อนเผยแพร่หลังแก้ source ให้รันคำสั่งด้านบนเพื่อสร้างและตรวจ `dist` ใหม่ ข้อมูลทดสอบอยู่ในหน่วยความจำของเบราว์เซอร์และหายเมื่อรีเฟรช ดูขั้นตอนให้ผู้ใช้ลองใน `docs/user-test-plan.md`

### รันในเครื่อง (PowerShell)

```powershell
cd D:\Dowload\Khonnai_new\Khonnai_new
node prototype/serve.cjs
```

เปิด `http://127.0.0.1:8765/` ในเบราว์เซอร์ กด `Ctrl+C` ใน PowerShell เพื่อหยุดเซิร์ฟเวอร์ เครื่องนี้มี Node.js แล้วและ prototype ใช้โมดูลที่มากับ Node จึงไม่ต้องรัน `npm install`

### ส่งการแก้ไขขึ้น GitHub

โฟลเดอร์นี้เป็น Git repository แล้ว และ `origin` ชี้ไปที่ `https://github.com/Rapeepong-naks/Micro-ERP-Prototype.git` ไม่ต้อง `git init` หรือ `git remote add` ซ้ำ ก่อน push หลังแก้ prototype ให้สร้างเว็บทดสอบชุดใหม่แล้วตรวจ:

```powershell
node prototype/smoke-check.cjs
node prototype/build-test-site.cjs
node prototype/check-test-site.cjs
git status
git add -A
git commit -m "อธิบายสิ่งที่แก้"
git push -u origin main
```

`git add -A` จะรวม `prototype/` ซึ่งเป็นต้นฉบับ, `dist/user-test-site/` ซึ่งเป็นเว็บทดสอบที่สร้างล่าสุด, `design/`, `brand/`, `docs/` และ README ที่เปลี่ยน แต่ไม่รวม `.scratch/`, `node_modules/` หรือ Python cache ตาม `.gitignore` ถ้า `git status` บอกว่าไม่มีอะไรเปลี่ยนแล้ว ไม่ต้องสร้างคอมมิตใหม่ ใช้ `git push -u origin main` เพื่อส่งคอมมิตที่ยังอยู่ในเครื่องได้เลย การตั้ง `git config user.email` มีผลต่อชื่อผู้เขียนคอมมิตเท่านั้น การ push ต้องล็อกอินด้วยบัญชี GitHub ที่มีสิทธิ์เขียน repo
