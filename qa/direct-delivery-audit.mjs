import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const output=resolve(root,'.qa-results');await mkdir(output,{recursive:true});
const base=process.env.ISSUE16_BASE_URL;
assert.ok(base?.startsWith('http://127.0.0.1:'),'This audit only targets its isolated local harness');
const browser=await chromium.launch({headless:true});
const results=[];
async function check(name,fn){try{await fn();results.push({name,status:'PASS'});console.log('PASS '+name);}catch(error){results.push({name,status:'FAIL',error:error.message});throw error;}}
async function prepare(page,message='Synthetische Testanfrage für den vollständigen Versandweg.'){
  await page.goto(new URL('contact.html',base).href,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>!document.getElementById('delivery-fields').hidden);
  await page.locator('#inq-name').fill('Website Test Müller');
  await page.locator('#inq-email').fill('customer@example.org');
  await page.locator('#inq-message').fill(message);
  await page.locator('#delivery-photos').setInputFiles(process.env.ISSUE16_PHOTO);
  await page.locator('#inq-review').click();
}
async function state(page,key){await page.waitForFunction(k=>document.getElementById('delivery-status').textContent.includes(window.EFSINN_I18N.dict['delivery.'+k]),key,{timeout:15000});}
try{
  const context=await browser.newContext({locale:'de-DE',viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  let posts=0;page.on('request',r=>{if(r.method()==='POST')posts++;});
  await prepare(page);
  await check('Explicit review confirmation is required before any upload',async()=>{
    await page.locator('#delivery-send').tap();await state(page,'confirm_required');assert.equal(posts,0);
  });
  await check('Double-click sends one real request through backend and TLS SMTP',async()=>{
    await page.locator('#delivery-confirm').check();
    assert.equal(await page.locator('#delivery-send').isVisible(),true);
    await page.locator('#delivery-send').tap();
    await page.locator('#delivery-send').evaluate(button=>button.click());
    await state(page,'smtp_accepted');assert.equal(posts,1);
    assert.equal(await page.locator('#inq-name').inputValue(),'Website Test Müller');
    assert.equal(await page.locator('#delivery-send').isDisabled(),true);
    await page.locator('#delivery-status').scrollIntoViewIfNeeded();
    await page.screenshot({path:resolve(output,'direct-send-mobile.png')});
  });
  await check('Seven languages retain status, reference and user input',async()=>{
    for(const code of ['en','fr','el','it','es','de-AT','de']){
      await page.locator(`[data-lang-code="${code}"]`).tap();
      await page.waitForFunction(c=>document.documentElement.getAttribute('data-i18n-fallback-done')===c,code);
      await state(page,'smtp_accepted');
      assert.equal(await page.locator('#inq-name').inputValue(),'Website Test Müller');
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    }
  });
  const retry=await context.newPage();retry.on('pageerror',e=>errors.push(e.message));
  const identifiers=[];let lost=false;
  await retry.route('**/v1/inquiries',async route=>{
    if(route.request().method()!=='POST'){await route.continue();return;}
    identifiers.push(route.request().headers()['idempotency-key']);
    if(!lost){lost=true;await route.fetch();await route.abort();}else await route.continue();
  });
  await check('Lost HTTP response retries the same ID without a second email',async()=>{
    await prepare(retry,'Zweite synthetische Anfrage: Antwortverlust und idempotente Wiederholung.');
    await retry.locator('#delivery-confirm').check();await retry.locator('#delivery-send').tap();
    await state(retry,'unknown');assert.equal(await retry.locator('#inq-name').inputValue(),'Website Test Müller');
    await retry.locator('#delivery-send').tap();await state(retry,'smtp_accepted');
    assert.equal(identifiers.length,2);assert.equal(identifiers[0],identifiers[1]);
  });
  const invalid=await context.newPage();invalid.on('pageerror',e=>errors.push(e.message));
  await check('Server rejects fake image bytes and preserves editable input',async()=>{
    await prepare(invalid);await invalid.locator('#inq-edit').click();
    await invalid.locator('#delivery-photos').setInputFiles({name:'fake.png',mimeType:'image/png',buffer:Buffer.from('This is not an image')});
    await invalid.locator('#inq-review').click();await invalid.locator('#delivery-confirm').check();
    await invalid.locator('#delivery-send').tap();await state(invalid,'file_type');
    assert.equal(await invalid.locator('#inq-name').isDisabled(),false);
    assert.equal(await invalid.locator('#inq-name').inputValue(),'Website Test Müller');
  });
  const offline=await context.newPage();offline.on('pageerror',e=>errors.push(e.message));
  await check('Offline backend leaves existing local enquiry preparation usable',async()=>{
    await offline.route('**/v1/challenge',route=>route.abort());
    await offline.goto(new URL('contact.html',base).href,{waitUntil:'networkidle'});await state(offline,'offline');
    assert.equal(await offline.locator('#delivery-fields').isVisible(),false);
    await offline.locator('#inq-name').fill('Fallback Test');await offline.locator('#inq-message').fill('Diese Anfrage bleibt lokal vorbereitet.');
    await offline.locator('#inq-review').click();assert.equal(await offline.locator('#inquiry-preview').isVisible(),true);
  });
  assert.deepEqual(errors,[]);await context.close();
}finally{await browser.close();await writeFile(resolve(output,'direct-delivery-browser.json'),JSON.stringify({checks:results,passed:results.filter(r=>r.status==='PASS').length,failed:results.filter(r=>r.status==='FAIL').length,external_delivery:false},null,2)+'\n');}
