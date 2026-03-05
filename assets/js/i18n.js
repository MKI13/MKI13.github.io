(function(){
  const SUPPORTED = ['de','en','fr','el','it','es','de-AT'];

  function detectLang(){
    const saved = localStorage.getItem('site_lang');
    if(saved && SUPPORTED.includes(saved)) return saved;
    const n = (navigator.language||'de').toLowerCase();
    if(n.startsWith('de-at')) return 'de-AT';
    if(n.startsWith('de')) return 'de';
    if(n.startsWith('en')) return 'en';
    if(n.startsWith('fr')) return 'fr';
    if(n.startsWith('el') || n.startsWith('gr')) return 'el';
    if(n.startsWith('it')) return 'it';
    if(n.startsWith('es')) return 'es';
    return 'de';
  }

  function basePrefix(){
    const p = location.pathname;
    if(p.includes('/leistungen/')) return '../';
    return './';
  }

  async function loadDict(lang){
    const url = `${basePrefix()}i18n/${lang}.json`;
    const res = await fetch(url, {cache:'no-store'});
    if(!res.ok) throw new Error('i18n load failed');
    return await res.json();
  }

  function applyDict(dict){
    document.documentElement.lang = localStorage.getItem('site_lang') || 'de';
    document.querySelectorAll('[data-i18n]').forEach(el=>{
      const k = el.getAttribute('data-i18n');
      if(dict[k]) el.textContent = dict[k];
    });
  }

  function ensureSwitcher(current){
    if(document.getElementById('lang-switcher')) return;
    const wrap = document.createElement('div');
    wrap.id = 'lang-switcher';
    wrap.style.cssText = 'position:fixed;top:10px;right:10px;z-index:9999;background:#fff;border:1px solid #ddd;border-radius:8px;padding:6px 8px;font-family:inherit;font-size:13px;box-shadow:0 2px 10px rgba(0,0,0,.08)';
    const select = document.createElement('select');
    select.setAttribute('aria-label','Sprache wechseln');
    select.style.cssText = 'border:none;background:transparent;outline:none;font-size:13px;';
    const opts = [
      ['de','Deutsch'],['en','English'],['fr','Français'],['el','Ελληνικά'],['it','Italiano'],['es','Español'],['de-AT','Deutsch (AT)']
    ];
    opts.forEach(([v,l])=>{ const o=document.createElement('option'); o.value=v; o.textContent=l; if(v===current) o.selected=true; select.appendChild(o); });
    select.addEventListener('change', async (e)=>{
      const lang=e.target.value;
      localStorage.setItem('site_lang', lang);
      try { const dict = await loadDict(lang); applyDict(dict); } catch(err){ console.error(err); }
    });
    wrap.appendChild(select);
    document.body.appendChild(wrap);
  }

  async function boot(){
    const lang = detectLang();
    localStorage.setItem('site_lang', lang);
    ensureSwitcher(lang);
    try{
      const dict = await loadDict(lang);
      applyDict(dict);
    }catch(e){
      console.warn('i18n fallback to de', e);
      if(lang!=='de'){
        try { const dict = await loadDict('de'); applyDict(dict);} catch(_e){}
      }
    }
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
