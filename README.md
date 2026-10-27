# Khonnai prototype

ต้นฉบับเว็บที่กดและกรอกได้อยู่ใน `prototype/` ส่วน `dist/user-test-site/` เป็นไฟล์เผยแพร่ที่สร้างจากต้นฉบับ ห้ามแก้ `dist/` โดยตรง แบบ FigCraft อยู่ใน `design/khonnai.figcraft` และกติกาธุรกิจ, flow, ขอบเขตงาน, วิธีทดสอบผู้ใช้ อยู่ใน [`docs/SPEC.md`](docs/SPEC.md) ไฟล์โลโก้อยู่ใน `brand/`.

## รันในเครื่อง

```powershell
cd D:\Dowload\Khonnai_new\Khonnai_new
node prototype/serve.cjs
```

เปิด `http://127.0.0.1:8765/` แล้วกด `Ctrl+C` เพื่อหยุดเซิร์ฟเวอร์ ไม่ต้อง `npm install` เพราะต้นแบบใช้โมดูลที่มากับ Node.js ข้อมูลตัวอย่างอยู่ในหน่วยความจำของเบราว์เซอร์ รีเฟรชแล้วเริ่มใหม่

## ตรวจและสร้างเว็บสำหรับส่งให้ผู้ใช้ลอง

```powershell
node prototype/smoke-check.cjs
node prototype/build-test-site.cjs
node prototype/check-test-site.cjs
```

ส่งเนื้อหาทั้งโฟลเดอร์ `dist/user-test-site/` ขึ้น static hosting หรือเปิด `dist/user-test-site/index.html` ในเครื่องได้ ตัวเว็บรวมฟอนต์และ asset แล้ว หากติดตั้ง Playwright และ Chrome ไว้ สามารถตรวจ flow เพิ่มด้วย:

```powershell
node prototype/qa/browser-smoke.cjs dist/user-test-site/index.html
node prototype/qa/ui-audit.cjs dist/user-test-site/index.html
```

## พุชขึ้น GitHub

`origin` ชี้ไปที่ [Micro-ERP-Prototype](https://github.com/Rapeepong-naks/Micro-ERP-Prototype) แล้ว หลังตรวจและสร้างเว็บทดสอบใหม่:

```powershell
git status
git add -A
git commit -m "อธิบายสิ่งที่แก้"
git push origin main
```

บัญชี GitHub ที่ใช้พุชต้องมีสิทธิ์เขียนรีโป การตั้ง `git config user.email` เปลี่ยนเพียงผู้เขียนคอมมิต
