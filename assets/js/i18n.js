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
    var container=document.querySelector('.nav-container');
    var menu=document.querySelector('.nav-menu');
    if(!container||!menu) return;

    /* Wrap nav-menu in #nav-right so flags sit above nav links */
    var navRight=document.createElement('div');
    navRight.id='nav-right';
    container.insertBefore(navRight,menu);
    navRight.appendChild(menu);

    /* Build flag bar */
    var bar=document.createElement('div');
    bar.id='lang-sw';

    for(var i=0;i<LANGS.length;i++){
      (function(l){
        var b=document.createElement('button');
        b.type='button';
        b.textContent=l.flag;
        b.title=l.code;
        b.setAttribute('aria-label','Language '+l.code);
        b.className='lang-btn'+(l.code===cur?' lang-btn-active':'');
        b.addEventListener('click',function(){
          localStorage.setItem('site_lang',l.code);
          load(l.code,function(d){apply(d,l.code)});
          var bs=bar.querySelectorAll('.lang-btn');
          for(var j=0;j<bs.length;j++) bs[j].classList.remove('lang-btn-active');
          b.classList.add('lang-btn-active');
        });
        bar.appendChild(b);
      })(LANGS[i]);
    }

    /* Flags ABOVE nav-menu */
    navRight.insertBefore(bar,menu);
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
