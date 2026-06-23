(function(){
  var LANGS=[
    {code:'de',flag:'🇩🇪',labelKey:'lang.de.label',fallbackLabel:'Deutsch auswählen'},
    {code:'en',flag:'🇬🇧',labelKey:'lang.en.label',fallbackLabel:'Englisch auswählen'},
    {code:'fr',flag:'🇫🇷',labelKey:'lang.fr.label',fallbackLabel:'Französisch auswählen'},
    {code:'el',flag:'🇬🇷',labelKey:'lang.el.label',fallbackLabel:'Griechisch auswählen'},
    {code:'it',flag:'🇮🇹',labelKey:'lang.it.label',fallbackLabel:'Italienisch auswählen'},
    {code:'es',flag:'🇪🇸',labelKey:'lang.es.label',fallbackLabel:'Spanisch auswählen'},
    {code:'de-AT',flag:'🇦🇹',labelKey:'lang.de-AT.label',fallbackLabel:'Deutsch Österreich auswählen'}
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
    x.open('GET',prefix()+'i18n/'+lang+'.json?v=20260623-growth');
    x.onload=function(){if(x.status===200){try{cb(JSON.parse(x.responseText))}catch(e){cb({})}}else cb({})};
    x.onerror=function(){cb({})};
    x.send();
  }

  var BASE_GERMAN=null;
  var BASE_WAITING=[];

  function loadBaseGerman(cb){
    if(BASE_GERMAN){cb(BASE_GERMAN);return;}
    BASE_WAITING.push(cb);
    if(BASE_WAITING.length>1) return;
    load('de',function(d){
      BASE_GERMAN=d||{};
      var waiting=BASE_WAITING.slice();
      BASE_WAITING=[];
      for(var i=0;i<waiting.length;i++) waiting[i](BASE_GERMAN);
    });
  }

  function normText(s){return String(s||'').replace(/\s+/g,' ').trim();}

  function fallbackReverse(base){
    var out={};
    for(var k in base){
      if(!Object.prototype.hasOwnProperty.call(base,k)) continue;
      if(typeof base[k]==='string') out[normText(base[k])]=k;
    }
    return out;
  }

  function translateNodeText(node,key,dict){
    var v=key&&dict[key];
    if(!v) return;
    node.__efSinnI18nKey=key;
    node.nodeValue=v;
  }

  function applyFallbackTranslations(dict,lang,base){
    var reverse=fallbackReverse(base||{});
    var root=document.documentElement;
    var titleKey=root.getAttribute('data-i18n-fallback-title')||reverse[normText(document.title)];
    if(titleKey&&dict[titleKey]){
      root.setAttribute('data-i18n-fallback-title',titleKey);
      document.title=dict[titleKey];
    }

    if(document.body&&document.createTreeWalker){
      var walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:function(node){
        var parent=node.parentElement;
        if(!parent) return NodeFilter.FILTER_REJECT;
        var tag=parent.tagName;
        if(tag==='SCRIPT'||tag==='STYLE'||tag==='NOSCRIPT'||tag==='SVG') return NodeFilter.FILTER_REJECT;
        if(parent.closest&&parent.closest('[data-i18n]')) return NodeFilter.FILTER_REJECT;
        if(!normText(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }});
      var textNodes=[];
      while(walker.nextNode()) textNodes.push(walker.currentNode);
      for(var n=0;n<textNodes.length;n++){
        var node=textNodes[n];
        var key=node.__efSinnI18nKey||reverse[normText(node.nodeValue)];
        translateNodeText(node,key,dict);
      }
    }

    var attrNames=['aria-label','title','placeholder','alt','value'];
    var all=document.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      var el=all[i];
      if(el.closest&&el.closest('[data-i18n]')) continue;
      for(var a=0;a<attrNames.length;a++){
        var attr=attrNames[a];
        if(!el.hasAttribute(attr)) continue;
        if(el.hasAttribute('data-i18n-'+attr)||el.hasAttribute('data-i18n-aria-label')) continue;
        var store='data-i18n-fallback-'+attr.replace(/[^a-z0-9]+/g,'-');
        var key=el.getAttribute(store)||reverse[normText(el.getAttribute(attr))];
        if(key&&dict[key]){
          el.setAttribute(store,key);
          el.setAttribute(attr,dict[key]);
        }
      }
    }
    root.setAttribute('data-i18n-fallback-done',lang);
  }

  function apply(dict,lang){
    document.documentElement.lang=lang;
    window.EFSINN_I18N={lang:lang,dict:dict};

    function val(key){return key&&dict[key]?dict[key]:null}

    var els=document.querySelectorAll('[data-i18n]');
    for(var i=0;i<els.length;i++){
      var k=els[i].getAttribute('data-i18n');
      var v=val(k);
      if(v){
        if((els[i].tagName==='INPUT'||els[i].tagName==='TEXTAREA')&&!els[i].hasAttribute('data-i18n-text')){
          els[i].placeholder=v;
        } else {
          els[i].innerHTML=v;
        }
      }
    }

    var attrMap=[
      ['data-i18n-placeholder','placeholder'],
      ['data-i18n-aria-label','aria-label'],
      ['data-i18n-title','title'],
      ['data-i18n-alt','alt'],
      ['data-i18n-value','value'],
      ['data-i18n-data-project-type','data-project-type']
    ];
    for(var a=0;a<attrMap.length;a++){
      var found=document.querySelectorAll('['+attrMap[a][0]+']');
      for(var j=0;j<found.length;j++){
        var ak=found[j].getAttribute(attrMap[a][0]);
        var av=val(ak);
        if(av) found[j].setAttribute(attrMap[a][1],av);
      }
    }

    loadBaseGerman(function(base){
      applyFallbackTranslations(dict,lang,base);
      updateLanguageButtonLabels();
      document.dispatchEvent(new CustomEvent('efSinn:i18nApplied',{detail:{lang:lang,dict:dict}}));
    });
  }

  function languageLabel(langDef){
    var current=window.EFSINN_I18N&&window.EFSINN_I18N.dict;
    return current&&current[langDef.labelKey]?current[langDef.labelKey]:langDef.fallbackLabel;
  }

  function updateLanguageButtonLabels(){
    var buttons=document.querySelectorAll('#lang-sw .lang-btn');
    for(var i=0;i<buttons.length;i++){
      var code=buttons[i].getAttribute('data-lang-code');
      for(var j=0;j<LANGS.length;j++){
        if(LANGS[j].code===code){
          var label=languageLabel(LANGS[j]);
          buttons[i].title=label;
          buttons[i].setAttribute('aria-label',label);
          break;
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
        b.title=languageLabel(l);
        b.setAttribute('aria-label',languageLabel(l));
        b.setAttribute('data-lang-code',l.code);
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
