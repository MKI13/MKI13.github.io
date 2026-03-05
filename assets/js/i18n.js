(function(){
  var LANGS=[
    {code:'de',flag:'🇩🇪'},{code:'en',flag:'🇬🇧'},{code:'fr',flag:'🇫🇷'},
    {code:'el',flag:'🇬🇷'},{code:'it',flag:'🇮🇹'},{code:'es',flag:'🇪🇸'},
    {code:'de-AT',flag:'🇦🇹'}
  ];
  var CODES=LANGS.map(function(l){return l.code});

  function detect(){
    var s=localStorage.getItem('site_lang');
    if(s&&CODES.indexOf(s)>-1) return s;
    var n=(navigator.language||'de').toLowerCase();
    if(n.indexOf('de-at')===0) return 'de-AT';
    for(var i=0;i<CODES.length;i++){if(n.indexOf(CODES[i])===0) return CODES[i]}
    return 'de';
  }

  function prefix(){return location.pathname.indexOf('/leistungen/')>-1?'../':'./'}

  function load(lang,cb){
    var x=new XMLHttpRequest();
    x.open('GET',prefix()+'i18n/'+lang+'.json?v='+Date.now());
    x.onload=function(){if(x.status===200){try{cb(JSON.parse(x.responseText))}catch(e){cb({})}}else cb({})};
    x.onerror=function(){cb({})};
    x.send();
  }

  function apply(dict,lang){
    document.documentElement.lang=lang;
    var els=document.querySelectorAll('[data-i18n]');
    for(var i=0;i<els.length;i++){
      var k=els[i].getAttribute('data-i18n');
      if(dict[k]){
        if(els[i].tagName==='INPUT'||els[i].tagName==='TEXTAREA'){
          els[i].placeholder=dict[k];
        } else {
          els[i].innerHTML=dict[k];
        }
      }
    }
  }

  function switcher(cur){
    if(document.getElementById('lang-sw')) return;
    var menu=document.querySelector('.nav-menu');
    if(!menu) return;

    var w=document.createElement('div');
    w.id='lang-sw';
    w.style.cssText='display:flex;align-items:center;gap:4px;';

    for(var i=0;i<LANGS.length;i++){
      (function(l){
        var b=document.createElement('button');
        b.type='button';
        b.textContent=l.flag;
        b.title=l.code;
        b.setAttribute('aria-label','Language '+l.code);
        b.style.cssText='font-size:18px;background:none;border:'+(l.code===cur?'2px solid #00C5E8':'2px solid transparent')+';border-radius:4px;cursor:pointer;padding:2px 4px;line-height:1;';
        b.addEventListener('click',function(){
          localStorage.setItem('site_lang',l.code);
          load(l.code,function(d){apply(d,l.code)});
          var bs=w.querySelectorAll('button');
          for(var j=0;j<bs.length;j++) bs[j].style.borderColor='transparent';
          b.style.borderColor='#00C5E8';
        });
        w.appendChild(b);
      })(LANGS[i]);
    }

    var li=document.createElement('li');
    li.style.cssText='display:flex;align-items:center;';
    li.appendChild(w);

    // Desktop: rechts, Mobile: oben
    if(window.innerWidth <= 520 && menu.firstChild) menu.insertBefore(li, menu.firstChild);
    else menu.appendChild(li);
  }

  function boot(){
    var lang=detect();
    localStorage.setItem('site_lang',lang);
    switcher(lang);
    if(lang!=='de'){load(lang,function(d){apply(d,lang)})}
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot);
  else boot();
})();
