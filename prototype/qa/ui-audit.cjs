// Focused mobile UI checks. Run with Playwright and Chrome from the repo root.
const assert=require('node:assert/strict');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
  const browser=await chromium.launch({headless:true,channel:'chrome'});
  try{
    const page=await browser.newPage({viewport:{width:375,height:812}});
    await page.goto(pathToFileURL(path.resolve(process.argv[2]||'prototype/index.html')).href);
    for(const screen of ['home','models','stock','model-price','model-new','pick','bill-new','bill-shipping','bill-saved-address','bill-preview','bill-preview-shipping','bill-done','reservations','receive','catalogue','catalogue-basket']){
      await page.evaluate(screen=>{
        selectedModel='A-215';
        if(screen==='model-price')modelPriceDraft='320';
        if(screen==='model-new')newModel=blankModel();
        if(screen==='bill-new'||screen==='bill-preview')draft={customer:'ทดสอบ',lines:[{m:'A-215',v:'32-ดำ',qty:1,price:320,unit:'pack'}]};
        if(screen==='bill-shipping'||screen==='bill-preview-shipping')draft={customer:'ทดสอบ',lines:[{m:'A-215',v:'32-ดำ',qty:1,price:320,unit:'pack'}],delivery:{method:'shipping',carrier:'J&T',recipient:'ทดสอบ',phone:'0812345678',address:'123 ถนนตัวอย่าง กรุงเทพฯ 10110',fee:75}};
        if(screen==='bill-saved-address'){addressBook=[{id:'A-test',customer:'คุณแอน',recipient:'',phone:'0812345678',address:'123 ถนนตัวอย่าง กรุงเทพฯ 10110',usedAt:new Date().toISOString()}];draft={customer:'แอน',lines:[{m:'A-215',v:'32-ดำ',qty:1,price:320,unit:'pack'}],delivery:{method:'shipping',carrier:'',recipient:'',phone:'',address:'',fee:0}}}
        if(screen==='bill-preview')previewReservationId=null;
        if(screen==='bill-preview-shipping')previewReservationId=null;
        if(screen==='bill-done'){lastBillId='#0001';data.bills.push({id:lastBillId,customer:'ทดสอบ',lines:[{m:'A-215',v:'32-ดำ',qty:1,price:320,unit:'pack'}],total:320,when:'วันนี้'})}
        if(screen==='pick'){pickFor='bill';pickQty={};pickSearch=''}
        if(screen==='catalogue-basket'){catalogueView='basket';catalogueBasket=[{m:'A-215',v:'32-ดำ',qty:1}];page='catalogue'}
        else if(screen==='catalogue')catalogueView='list';
        if(screen!=='catalogue-basket')page=screen==='bill-shipping'||screen==='bill-saved-address'?'bill-new':screen==='bill-preview-shipping'?'bill-preview':screen;render();
      },screen);
      const issues=await page.evaluate(()=>{
        const root=document.querySelector('.phone');
        const visible=element=>{const rect=element.getBoundingClientRect(),style=getComputedStyle(element);return rect.width>0&&rect.height>0&&style.display!=='none'&&style.visibility!=='hidden'};
        return {
          overflow:root.scrollWidth>root.clientWidth,
          smallTargets:[...root.querySelectorAll('button')].filter(visible).filter(element=>{const rect=element.getBoundingClientRect();return rect.width<44||rect.height<44}).map(element=>element.dataset.action||element.textContent.trim().slice(0,25)),
          unlabelledInputs:[...root.querySelectorAll('input')].filter(visible).filter(element=>!element.labels?.length&&!element.getAttribute('aria-label')).map(element=>element.dataset.field||element.type)
        };
      });
      assert.equal(issues.overflow,false,`${screen}: horizontal overflow`);
      assert.deepEqual(issues.smallTargets,[],`${screen}: touch targets below 44px`);
      assert.deepEqual(issues.unlabelledInputs,[],`${screen}: unlabelled inputs`);
    }
    console.log('Mobile UI audit passed: 16 screens, no horizontal overflow, visible buttons at least 44 × 44 CSS px, and labelled inputs.');
  }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
