const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const app = {innerHTML: ''};
const handlers = {};
const context = vm.createContext({
  document: {
    querySelector: selector => selector === '#app' ? app : null,
    querySelectorAll: () => [],
    addEventListener: (type, callback) => { handlers[type] = callback; }
  },
  location: {href: 'http://localhost:8000/prototype/', hash: ''},
  navigator: {}, window: {}, console, Date, CSS: {escape: x => x},
  structuredClone, prompt: () => null
});
vm.runInContext(fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8'), context);
const run = code => vm.runInContext(code, context);
const click = async (action, extras = {}) => handlers.click({target: {closest: () => ({dataset: {action, ...extras}})}});

(async () => {
  assert.match(app.innerHTML, /แพ็กขายได้/);
  assert.match(app.innerHTML, /การจองที่รอปิดบิล/);
  assert.match(app.innerHTML, /<h1>ร้านเจ๊หน่อยชุดชั้นใน<\/h1>/);
  assert.equal(context.document.title, 'หน้าแรก · Khonnai');
  run("go('models')");
  assert.equal(context.document.title, 'สต็อก · รุ่นทั้งหมด · Khonnai');
  assert.match(app.innerHTML, /<h1>รุ่นทั้งหมด<\/h1>/);
  run("selectedModel='A-215';go('stock')");
  assert.equal(context.document.title, 'สต็อก · A-215 · Khonnai');
  run("go('home')");
  run("switchTab('bills')");
  assert.equal(run('page'), 'bill-new');
  assert.match(app.innerHTML, /ดูประวัติบิล/);
  run("switchTab('home')");
  run("role='assistant';switchTab('bills')");
  assert.equal(run('page'), 'bills');
  assert.doesNotMatch(app.innerHTML, /data-action="new-bill"/);
  run("role='owner';switchTab('home')");
  assert.match(app.innerHTML, /<svg class="icon"/);
  assert.match(app.innerHTML, /<span class="nav-label">หน้าแรก<\/span>/);
  assert.doesNotMatch(app.innerHTML, /[⌂⬡▤♧▣]/);
  run("newDraft('bill');draft.customer='ลูกค้าบิล';render()");
  assert.match(app.innerHTML, /data-action="switch-tab"/);
  assert.match(app.innerHTML, /ลูกค้าบิล/);
  run("switchTab('models');go('stock');switchTab('reservations');newDraft('reservation');draft.customer='ลูกค้าจอง';render()");
  run("switchTab('bills')");
  assert.equal(run('page'), 'bill-new');
  assert.equal(run('draft.customer'), 'ลูกค้าบิล');
  run("switchTab('models')");
  assert.equal(run('page'), 'stock');
  run("switchTab('reservations')");
  assert.equal(run('page'), 'reservation-new');
  assert.equal(run('draft.customer'), 'ลูกค้าจอง');
  run("switchTab('reservations')");
  assert.equal(run('page'), 'reservations');
  run("switchTab('home')");
  const deviceCss = fs.readFileSync(path.join(__dirname, 'device.css'), 'utf8');
  assert.match(deviceCss, /width: 375px/);
  assert.match(deviceCss, /height: 812px/);
  assert.match(deviceCss, /overflow-y: auto/);
  assert.ok(fs.existsSync(path.join(__dirname, 'fonts/NotoSansThai.ttf')));
  assert.ok(fs.existsSync(path.join(__dirname, 'assets/khonnai-wordmark.png')));
  assert.equal(run("validSize('50','numeric')"), true);
  assert.equal(run("validSize('XL','numeric')"), false);
  assert.equal(run("validSize('2XL','alpha')"), true);
  assert.equal(run("validSize('50','alpha')"), false);
  assert.equal(run("validSize('ฟรีไซซ์','custom')"), true);
  assert.equal(run("data.reservations[0].lines[0].qty"), 3);
  run("selectedModel='A-215';selectedVariant='34-ดำ';page='adjust';reservationFilter={m:selectedModel,v:selectedVariant};page='reservations';render()");
  assert.match(app.innerHTML, /คุณนิด/);
  assert.match(app.innerHTML, /กำลังแสดงการจองของ/);

  run("draft={customer:'คุณสมชาย',lines:[{m:'A-215',v:'34-ดำ',qty:2,price:320,unit:'pack'}]}; saveReservation()");
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 8);
  assert.equal(run("available(variant('A-215','34-ดำ'))"), 3);
  assert.match(app.innerHTML, /คุณสมชาย/);
  await click('preview-reservation-bill');
  assert.equal(run('page'), 'bill-preview');
  assert.match(app.innerHTML, /ยังไม่ใช่บิลเงินสด/);
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 8);
  await click('convert-reservation');
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 8);
  assert.match(app.innerHTML, /ยืนยันขายและเปิดบิล/);
  await click('modal-confirm');
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 6);
  assert.equal(run("variant('A-215','34-ดำ').reserved"), 3);
  assert.equal(run("available(variant('A-215','34-ดำ'))"), 3);
  assert.match(app.innerHTML, /cash-slip-customer/);
  assert.match(app.innerHTML, /คุณสมชาย/);
  assert.match(app.innerHTML, /ดูรายการจองเดิม/);
  await click('open-source-reservation', {id: run('data.reservations.at(-1).id')});
  assert.equal(run('page'), 'reservation-detail');
  assert.match(app.innerHTML, /ขายแล้ว/);
  assert.doesNotMatch(app.innerHTML, /data-action="convert-reservation"/);
  await click('open-linked-bill');
  assert.equal(run('page'), 'bill-done');

  run("draft={customer:'คุณวิไล',lines:[{m:'A-102',v:'32',qty:4,price:180,unit:'dozen'}]};page='bill-new';render()");
  await click('preview-bill');
  assert.equal(run('page'), 'bill-preview');
  assert.match(app.innerHTML, /฿720/);
  assert.equal(run("variant('A-102','32').onHand"), 9);
  await click('save-bill');
  assert.equal(run('data.bills.at(-1).total'), 720);
  assert.equal(run("variant('A-102','32').onHand"), 5);
  assert.match(app.innerHTML, /฿720/);
  run("go('bills')");
  assert.match(app.innerHTML, /data-action="open-bill"/);
  await click('open-bill', {id: run('data.bills.at(-1).id')});
  assert.equal(run('page'), 'bill-done');
  await click('edit-bill', {id: run('data.bills.at(-1).id')});
  assert.equal(run('page'), 'bill-new');

  run("receipt={supplier:'ยี่ปั๊วสำเพ็ง',date:'2026-10-27',model:'A-215',variant:'34-ดำ',qty:0};receiptLines=[{m:'A-215',v:'34-ดำ',qty:4},{m:'A-102',v:'32',qty:2}]");
  run("page='receive';receiptOpenModel='A-215';render()");
  assert.match(app.innerHTML, /data-field="receipt-grid:A-215:34-ดำ"/);
  await click('save-receipt');
  assert.equal(run('data.receipts[0].lines.length'), 2);
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 10);
  assert.equal(run("variant('A-102','32').onHand"), 7);
  await click('edit-receipt');
  assert.equal(run('page'), 'receive');
  assert.equal(run('editingReceiptId'), 'IN-01');
  run("changeStock('A-215','34-ดำ',-5,'ทดสอบขายหลังรับของ');receiptLines[0].qty=1");
  await click('save-receipt');
  assert.equal(run('page'), 'receive');
  assert.match(app.innerHTML, /แก้ไขไม่ได้/);
  run("changeStock('A-215','34-ดำ',5,'คืนสภาพทดสอบ');receiptLines[0].qty=5");
  await click('save-receipt');
  assert.equal(run('page'), 'receipt-detail');
  assert.equal(run('editingReceiptId'), null);
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 11);
  await click('back');
  assert.equal(run('page'), 'home');
  run("page='receipt-detail';render()");
  run("modal={kind:'cancel-receipt'};confirmModal()");
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 6);
  assert.equal(run("variant('A-102','32').onHand"), 5);
  assert.equal(run("data.receipts[0].status"), 'cancelled');

  run("selectedModel='A-215';page='stock';render()");
  await click('ask-hide-model');
  assert.equal(run("model('A-215').hidden"), false);
  assert.match(app.innerHTML, /เลิกขายไม่ได้/);
  run("selectedModel='P-118';page='stock';toast='';render()");
  await click('ask-hide-model');
  assert.match(app.innerHTML, /เลิกขายรุ่นนี้/);
  await click('modal-confirm');
  assert.equal(run("model('P-118').hidden"), true);
  assert.doesNotMatch(run("renderCatalogue()"), /กางเกงใน P-118 เด็ก/);
  await click('restore-model');
  assert.equal(run("model('P-118').hidden"), false);

  run("selectedModel='A-215';selectedVariant='34-ดำ';adjustment={count:2,reason:'ของเสีย'};page='adjust';render()");
  assert.match(app.innerHTML, /ตั้งต่ำกว่าจำนวนที่จองไม่ได้/);
  await click('save-adjust');
  assert.equal(run("variant('A-215','34-ดำ').onHand"), 6);

  run("newModel={...blankModel(),name:'ทดสอบ T-100',category:'เสื้อใน',pack:6,mixed:false,price:100,min:2,sizes:['32','34'],colors:{'32':['ดำ'],'34':['ขาว']},stocks:{'32:ดำ':2,'34:ขาว':3},step:4};finishModel(false)");
  assert.equal(run("model('T-100').variants.length"), 2);
  assert.equal(run("model('T-100').variants.some(v=>v.label==='32 · ขาว')"), false);
  run("draft={customer:'ลูกค้าทดลอง',lines:[{m:'A-102',v:'34',qty:1,price:180,unit:'pack'}]};saveReservation()");
  assert.equal(run("variant('A-102','34').reserved"), 1);
  await click('edit-reservation');
  assert.equal(run('page'), 'reservation-new');
  run("draft.customer='ลูกค้าที่แก้แล้ว';draft.lines[0].qty=2");
  await click('save-reservation');
  assert.equal(run('page'), 'reservation-detail');
  assert.equal(run("variant('A-102','34').reserved"), 2);
  assert.equal(run("data.reservations.at(-1).customer"), 'ลูกค้าที่แก้แล้ว');
  await click('back');
  assert.equal(run('page'), 'reservations');
  console.log('Prototype smoke check passed: persistent tabs and separate drafts, receiving and reservation edits, cancel and stock guards, post-save back routes, reservation → bill, dozen, adjustment guard, model colors, font asset.');
})().catch(err => { console.error(err); process.exitCode = 1; });
