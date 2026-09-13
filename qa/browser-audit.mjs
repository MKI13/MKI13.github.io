import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import { dirname, resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUTPUT = resolve(ROOT, '.qa-results');
await mkdir(OUTPUT, {recursive:true});
const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.ico':'image/x-icon','.xml':'application/xml','.txt':'text/plain'};
const server = createServer(async (request,response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    const file = resolve(ROOT,'.'+(pathname.endsWith('/') ? pathname+'index.html' : pathname));
    if(!file.startsWith(ROOT+sep) || pathname.split('/').some(part=>part.startsWith('.')) || !types[extname(file)] || !(await stat(file)).isFile()) throw new Error('Not found');
    response.writeHead(200, {'Content-Type':types[extname(file)],'Cache-Control':'no-store'});
    response.end(await readFile(file));
  } catch { response.writeHead(404); response.end('Not found'); }
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const base = process.env.EFSINN_BASE_URL || `http://127.0.0.1:${server.address().port}/`;
const checks=[];
const browser = await chromium.launch({headless:true});
async function check(name, run) {
  try { await run(); checks.push({name,status:'PASS'}); console.log('PASS '+name); }
  catch(error) { checks.push({name,status:'FAIL',error:error.message}); console.error('FAIL '+name+': '+error.message); }
}
async function ready(page, path='contact.html') {
  await page.goto(new URL(path,base).href,{waitUntil:'networkidle',timeout:20000});
}
async function fillDraft(page, message='Bitte prüfen Sie die Reparatur unseres Bettes.') {
  await page.locator('#inq-name').fill('Website-Funktionstest Müller');
  await page.locator('#inq-message').fill(message);
}
async function captureMailto(page) {
  await page.evaluate(()=>{window.capturedMailto=null;document.addEventListener('click',event=>{const link=event.target.closest('a[href^="mailto:"]');if(link){event.preventDefault();window.capturedMailto=link.href;}},true);});
}
const pages=['index.html','about.html','contact.html','portfolio.html','schreiner-muenchen.html','impressum.html','datenschutz.html','404.html','leistungen/innenausbau.html','leistungen/kuechen.html','leistungen/moebelbau.html','leistungen/restaurierung.html','leistungen/terrassen.html','leistungen/treppen.html'];
try {
  for(const width of [360,768,1440]) {
    const context=await browser.newContext({locale:'de-DE',viewport:{width,height:900}});
    const page=await context.newPage();
    let errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    for(const path of pages) {
      await check(`Layout ${width}px ${path}`,async()=>{
        errors=[]; await ready(page,path);
        assert.deepEqual(errors,[],'JavaScript errors');
        const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-innerWidth,h1:document.querySelectorAll('h1').length,main:document.querySelectorAll('#main-content').length,broken:[...document.images].filter(image=>(image.currentSrc || image.getAttribute('src')) && image.complete && image.naturalWidth===0).map(image=>image.src)}));
        if(metrics.overflow>1) {
          const overflowElements=await page.evaluate(()=>[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,classes:e.className,text:e.innerText?.slice(0,90),right:e.getBoundingClientRect().right,transform:getComputedStyle(e).transform})).filter(e=>e.right>innerWidth+1).slice(0,12));
          console.error(JSON.stringify({page:path,width,overflowElements}));
          await page.screenshot({path:resolve(OUTPUT,`overflow-${width}-${path.replaceAll('/','-')}.png`)});
        }
        assert.ok(metrics.overflow<=1,'Horizontal overflow: '+metrics.overflow+'px');
        assert.equal(metrics.h1,1); assert.equal(metrics.main,1); assert.deepEqual(metrics.broken,[]);
        if(path==='index.html') {
          const heroFits=await page.evaluate(()=>{const hero=document.querySelector('.hero').getBoundingClientRect();return [...document.querySelector('.hero-content').children].every(e=>{const r=e.getBoundingClientRect();return r.top>=hero.top && r.bottom<=hero.bottom;});});
          assert.ok(heroFits,'Hero content clipped above or below its background');
        }
        if(path==='index.html' && width!==768) await page.screenshot({path:resolve(OUTPUT,`homepage-${width}.png`)});
        if(path==='leistungen/terrassen.html' && width===360) await page.screenshot({path:resolve(OUTPUT,'terraces-mobile.png')});
      });
    }
    await context.close();
  }
  const context=await browser.newContext({locale:'de-DE',viewport:{width:390,height:844},isMobile:true,hasTouch:true,acceptDownloads:true});
  const page=await context.newPage();
  await ready(page);
  await check('Required fields block empty enquiry',async()=>{
    await page.locator('#inq-review').tap();
    assert.equal(await page.locator('#inquiry-preview').isVisible(),false);
    assert.equal(await page.locator('#inq-name').evaluate(e=>e.validity.valueMissing),true);
  });
  await check('Invalid optional email is rejected',async()=>{
    await fillDraft(page); await page.locator('#inq-email').fill('invalid'); await page.locator('#inq-review').tap();
    assert.equal(await page.locator('#inquiry-preview').isVisible(),false);
    assert.equal(await page.locator('#inq-email').evaluate(e=>e.validity.typeMismatch),true);
    await page.locator('#inq-email').fill('');
  });
  await check('Touch enquiry preview preserves dimensions and timeframe',async()=>{
    await page.locator('#inq-measurements').fill('240 × 220 × 60 cm');
    await page.locator('#inq-timeframe').fill('Oktober, flexibel');
    await page.locator('[data-project-key="repair"]').tap();
    await page.locator('#inq-review').tap();
    assert.equal(await page.locator('#inquiry-preview').isVisible(),true);
    const text=await page.locator('#inquiry-preview-text').inputValue();
    assert.ok(text.includes('240 × 220 × 60 cm')); assert.ok(text.includes('Oktober, flexibel')); assert.ok(text.includes('Reparatur / Restaurierung'));
    await page.screenshot({path:resolve(OUTPUT,'inquiry-mobile.png')});
  });
  await check('Email handoff contains recipient and complete short draft',async()=>{
    await captureMailto(page); await page.locator('#inq-open-email').tap();
    const link=new URL(await page.evaluate(()=>window.capturedMailto));
    assert.equal(link.protocol,'mailto:'); assert.equal(link.pathname,'info@ef-sinn.de');
    assert.ok(link.searchParams.get('body')?.includes('Bitte prüfen Sie die Reparatur'));
    assert.match(await page.locator('#inquiry-status').innerText(),/selbst versenden/);
  });
  await check('Clipboard success reports copying, never delivery (API simulated)',async()=>{
    await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copiedText=text;}}}));
    await page.locator('#inq-copy').tap();
    assert.equal(await page.evaluate(()=>window.copiedText),await page.locator('#inquiry-preview-text').inputValue());
    assert.match(await page.locator('#inquiry-status').innerText(),/Text kopiert/);
  });
  await check('Clipboard denial selects entire text for manual copying (API simulated)',async()=>{
    await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new DOMException('Denied','NotAllowedError');}}}));
    await page.locator('#inq-copy').tap();
    const selection=await page.locator('#inquiry-preview-text').evaluate(e=>({start:e.selectionStart,end:e.selectionEnd,length:e.value.length}));
    assert.equal(selection.start,0); assert.equal(selection.end,selection.length);
    assert.match(await page.locator('#inquiry-status').innerText(),/Text ist markiert/);
  });
  await check('Text download contains the complete Unicode draft',async()=>{
    const expected=await page.locator('#inquiry-preview-text').inputValue();
    const downloadPromise=page.waitForEvent('download');
    await page.locator('#inq-download').tap(); const download=await downloadPromise;
    assert.equal(download.suggestedFilename(),'ef-sinn-projektanfrage.txt');
    assert.equal(await readFile(await download.path(),'utf8'),expected);
    assert.match(await page.locator('#inquiry-status').innerText(),/noch nicht versendet/);
  });
  await check('All seven languages preserve entered content and selected project',async()=>{
    for(const language of ['en','fr','el','it','es','de-AT','de']) {
      await page.locator(`[data-lang-code="${language}"]`).tap();
      await page.waitForFunction(code=>document.documentElement.lang===code,language);
      await page.waitForFunction(code=>document.documentElement.getAttribute('data-i18n-fallback-done')===code,language);
      assert.equal(await page.locator('#inq-name').inputValue(),'Website-Funktionstest Müller');
      assert.equal(await page.locator('.project-template-btn[aria-pressed="true"]').getAttribute('data-project-key'),'repair');
      assert.ok((await page.locator('#inquiry-preview-text').inputValue()).includes('240 × 220 × 60 cm'));
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    }
  });
  await check('Long enquiry is never truncated or passed through an oversized mailto',async()=>{
    await page.locator('#inq-edit').tap();
    const longText='Maßmöbel & Grüße aus München. '.repeat(140);
    await page.locator('#inq-message').fill(longText); await page.locator('#inq-review').tap();
    assert.ok((await page.locator('#inquiry-preview-text').inputValue()).includes(longText.trim()));
    assert.equal(await page.locator('#inquiry-long-note').isVisible(),true);
    await page.locator('#inq-open-email').tap(); const link=new URL(await page.evaluate(()=>window.capturedMailto));
    assert.equal(link.searchParams.has('body'),false); assert.ok(link.searchParams.get('subject'));
    assert.match(await page.locator('#inquiry-status').innerText(),/vollständigen Text/);
  });
  await check('User HTML remains inert text in preview',async()=>{
    await page.locator('#inq-edit').tap();
    await page.locator('#inq-name').fill('<img src=x onerror=alert(1)>');
    await page.locator('#inq-message').fill('Bitte <script>alert(1)</script> nur als Text behandeln.');
    await page.locator('#inq-review').tap();
    assert.equal(await page.locator('#inquiry-preview img, #inquiry-preview script').count(),0);
    assert.ok((await page.locator('#inquiry-preview-text').inputValue()).includes('<script>alert(1)</script>'));
  });
  await check('Project links resolve aliases and unknown input safely',async()=>{
    for(const [query,key] of [['project=treppen','stairs'],['type=kueche','kitchen'],['projekt=gartenhaus','outdoor'],['project=unbekannt','customFurniture']]) {
      await ready(page,'contact.html?'+query);
      assert.equal(await page.locator('.project-template-btn[aria-pressed="true"]').getAttribute('data-project-key'),key);
      assert.equal(await page.locator('.project-template-btn[aria-pressed="true"]').count(),1);
    }
  });
  await check('Portfolio image opens by keyboard and Escape restores focus',async()=>{
    await ready(page,'portfolio.html');
    const trigger=page.locator('[data-lightbox]').first();
    await trigger.focus(); await page.keyboard.press('Enter');
    await page.waitForFunction(()=>document.getElementById('lightbox-img').naturalWidth>0);
    assert.equal(await page.locator('#portfolio-lightbox').evaluate(e=>e.open),true);
    assert.equal(await page.locator('#portfolio-lightbox').evaluate(e=>getComputedStyle(e).opacity),'1');
    assert.equal(await page.locator('.lb-close').evaluate(e=>e===document.activeElement),true);
    await page.keyboard.press('Escape');
    await page.waitForFunction(()=>!document.getElementById('portfolio-lightbox').open);
    assert.equal(await trigger.evaluate(e=>e===document.activeElement),true);
    await page.waitForFunction(()=>document.getElementById('lightbox-img').getAttribute('src')===null);
    assert.equal(await page.locator('#lightbox-img').getAttribute('src'),null);
  });
  await check('Portfolio image opens by touch and closes without a broken empty source',async()=>{
    await page.locator('[data-lightbox]').first().tap();
    await page.waitForFunction(()=>document.getElementById('lightbox-img').naturalWidth>0);
    await page.screenshot({path:resolve(OUTPUT,'portfolio-lightbox-mobile.png')});
    await page.locator('.lb-close').tap();
    assert.equal(await page.locator('#portfolio-lightbox').evaluate(e=>e.open),false);
    await page.waitForFunction(()=>document.getElementById('lightbox-img').getAttribute('src')===null);
    assert.equal(await page.locator('#lightbox-img').getAttribute('src'),null);
  });
  await check('Portfolio category selection remains operable after closing a modal',async()=>{
    await page.locator('.portfolio-category-btn[data-filter="terrassen"]').tap();
    assert.equal(await page.locator('.portfolio-category-btn[aria-pressed="true"]').getAttribute('data-filter'),'terrassen');
    await page.locator('.portfolio-category-btn[data-filter="all"]').tap();
    assert.equal(await page.locator('.portfolio-category-btn[aria-pressed="true"]').count(),1);
  });
  await context.close();
  await check('Blocked browser storage does not break language switch or enquiry',async()=>{
    const isolated=await browser.newContext({locale:'de-DE'});
    await isolated.addInitScript(()=>{Storage.prototype.getItem=function(){throw new DOMException('Denied','SecurityError');};Storage.prototype.setItem=function(){throw new DOMException('Denied','SecurityError');};});
    const p=await isolated.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(e.message));
    await ready(p); await p.locator('[data-lang-code="en"]').click(); await p.waitForFunction(()=>document.documentElement.lang==='en');
    await fillDraft(p); await p.locator('#inq-review').click(); assert.equal(await p.locator('#inquiry-preview').isVisible(),true); assert.deepEqual(errors,[]);
    await isolated.close();
  });
  await check('Rapid language selection cannot be overwritten by a stale response',async()=>{
    const isolated=await browser.newContext({locale:'de-DE'}); const p=await isolated.newPage(); await ready(p);
    await p.route('**/i18n/en.json*',async route=>{const result=await route.fetch();await new Promise(done=>setTimeout(done,600));await route.fulfill({response:result});});
    await p.locator('[data-lang-code="en"]').click(); await p.locator('[data-lang-code="fr"]').click();
    await p.waitForFunction(()=>document.documentElement.lang==='fr'); await p.waitForTimeout(850);
    assert.equal(await p.locator('html').getAttribute('lang'),'fr'); assert.equal(await p.locator('.lang-btn-active').getAttribute('data-lang-code'),'fr');
    await isolated.close();
  });
  await check('Failed language request keeps current language and controls usable',async()=>{
    const isolated=await browser.newContext({locale:'de-DE'}); const p=await isolated.newPage(); await ready(p);
    await p.route('**/i18n/en.json*',route=>route.abort()); await p.locator('[data-lang-code="en"]').click(); await p.waitForTimeout(150);
    assert.equal(await p.locator('html').getAttribute('lang'),'de'); assert.equal(await p.locator('.lang-btn-active').getAttribute('data-lang-code'),'de');
    await fillDraft(p); await p.locator('#inq-review').click(); assert.equal(await p.locator('#inquiry-preview').isVisible(),true);
    await isolated.close();
  });
  await check('Without JavaScript, Enter cannot submit personal data or change the URL',async()=>{
    const isolated=await browser.newContext({javaScriptEnabled:false,locale:'de-DE',viewport:{width:390,height:844}});
    const p=await isolated.newPage(); const posts=[]; p.on('request',request=>{if(request.method()!=='GET')posts.push(request.url());});
    await p.goto(new URL('contact.html',base).href,{waitUntil:'networkidle'}); const before=p.url();
    assert.equal(await p.locator('#inq-review').isDisabled(),true); assert.equal(await p.locator('noscript').isVisible(),true);
    await p.locator('#inq-name').fill('PRIVATE_TEST_MARKER'); await p.locator('#inq-name').press('Enter'); await p.waitForTimeout(150);
    assert.equal(p.url(),before); assert.deepEqual(posts,[]); assert.ok(!p.url().includes('PRIVATE_TEST_MARKER'));
    await p.screenshot({path:resolve(OUTPUT,'contact-no-javascript.png')}); await isolated.close();
  });
} finally {
  await browser.close(); await new Promise(done=>server.close(done));
}
const report={generated_at:new Date().toISOString(),base_url:base,browser:'Chromium (Playwright 1.58.2)',passed:checks.filter(c=>c.status==='PASS').length,failed:checks.filter(c=>c.status==='FAIL').length,notes:['SMTP delivery is not tested: website intentionally prepares email only.','Clipboard success and denial use simulated browser API responses; downloaded text is verified as a real file.','All form inputs are synthetic test data; mailto navigation is intercepted, not sent.'],checks};
await writeFile(resolve(OUTPUT,'browser-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,failed:report.failed,report:resolve(OUTPUT,'browser-audit.json')}));
process.exitCode=report.failed ? 1 : 0;
