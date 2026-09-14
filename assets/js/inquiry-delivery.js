/* Direct delivery is separate from the always-available local enquiry assistant. */
(function () {
  'use strict';
  var config = window.EFSINN_DELIVERY;
  if (!config || config.enabled !== true) return;
  var form = document.getElementById('inquiry-form');
  var fields = document.getElementById('delivery-fields');
  var controls = document.getElementById('delivery-controls');
  var output = document.getElementById('delivery-status');
  if (!form || !fields || !controls || !output) return;
  var endpoint;
  try {
    var url = new URL(config.endpoint);
    var local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && /^(localhost|127\.0\.0\.1)$/.test(url.hostname);
    if ((url.protocol !== 'https:' && !(local && url.protocol === 'http:')) || url.username || url.password || url.search || url.hash || url.pathname !== '/') return;
    endpoint = url.origin;
  } catch (error) { return; }
  var sendButton = document.getElementById('delivery-send');
  var checkButton = document.getElementById('delivery-check');
  var photos = document.getElementById('delivery-photos');
  var confirm = document.getElementById('delivery-confirm');
  var pending = null, busy = false, challenge = null, disabled = [], lastState = '', reference = '';
  var states = ['queued', 'processing', 'smtp_accepted', 'receipt_verified', 'uncertain', 'failed'];
  var limits = {max_files: 5, file_bytes: 4 * 1024 * 1024, total_bytes: 10 * 1024 * 1024};
  var pollTimer = null, polls = 0;
  function t(key) { return ((window.EFSINN_I18N || {}).dict || {})['delivery.' + key] || key; }
  function display(key) {
    lastState = key;
    output.textContent = t(key) + (reference ? ' ' + t('reference') + ' ' + reference : '');
    var previewNote = document.querySelector('[data-delivery-preview-note], [data-i18n="delivery.preview"]');
    if (previewNote) {
      var noteKey = ['sending', 'queued', 'processing', 'smtp_accepted', 'receipt_verified', 'uncertain', 'unknown'].indexOf(key) >= 0 ? key : 'preview';
      previewNote.setAttribute('data-delivery-preview-note', 'true');
      previewNote.setAttribute('data-i18n', 'delivery.' + noteKey);
      previewNote.textContent = t(noteKey);
    }
  }
  function lock(value) {
    if (value && !disabled.length) {
      form.querySelectorAll('input, textarea, .project-template-btn, #inq-review, #inq-edit, #inq-open-email').forEach(function (el) {
        disabled.push({element: el, previous: el.disabled}); el.disabled = true;
      });
    } else if (!value) {
      disabled.forEach(function (entry) { entry.element.disabled = entry.previous; }); disabled = [];
    }
  }
  function refreshButtons() {
    sendButton.disabled = busy || !!(pending && states.indexOf(pending.state) !== -1 && pending.state !== 'failed');
    sendButton.textContent = t(pending ? 'retry' : 'send');
    checkButton.hidden = !pending;
    checkButton.disabled = busy;
  }
  async function call(path, options) {
    var abort = new AbortController();
    var timer = setTimeout(function () { abort.abort(); }, 20000);
    try {
      var response = await fetch(endpoint + path, Object.assign({mode: 'cors', credentials: 'omit', cache: 'no-store', signal: abort.signal}, options));
      var data = await response.json();
      return {status: response.status, data: data};
    } finally { clearTimeout(timer); }
  }
  async function newChallenge() {
    var result = await call('/v1/challenge');
    if (result.status !== 200 || typeof result.data.challenge !== 'string') throw new Error('unavailable');
    challenge = {value: result.data.challenge, time: Date.now(), age: Math.max(2, result.data.min_age || 2)};
    return challenge;
  }
  function randomHex() {
    return Array.from(crypto.getRandomValues(new Uint8Array(32)), function (value) { return value.toString(16).padStart(2, '0'); }).join('');
  }
  function snapshot() {
    var selected = Array.from(photos.files || []);
    if (selected.length > limits.max_files) throw new Error('too_many_files');
    var total = 0;
    selected.forEach(function (file) {
      total += file.size;
      if (!file.size || file.size > limits.file_bytes || total > limits.total_bytes) throw new Error('file_size');
      if (['image/jpeg', 'image/png', 'image/webp'].indexOf(file.type) < 0) throw new Error('file_type');
    });
    var get = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
    if (!get('inq-email') && !get('inq-phone')) throw new Error('contact_required');
    var data = new FormData();
    var mapping = {name:'name', phone:'phone', email:'email', location:'location', measurements:'measurements', timeframe:'timeframe', appointment1:'appointment-1', appointment2:'appointment-2', message:'message'};
    Object.keys(mapping).forEach(function (key) { data.set(key, get('inq-' + mapping[key])); });
    data.set('project', get('inq-custom-type') || get('inq-type-value'));
    data.set('language', (window.EFSINN_I18N || {}).lang || 'de');
    data.set('website', document.getElementById('delivery-website').value);
    selected.forEach(function (file) { data.append('photos', file, file.name); });
    return data;
  }
  function applyResult(result) {
    if (!pending || result.data.request_id !== pending.id || states.indexOf(result.data.state) < 0) throw new Error('unknown');
    pending.state = result.data.state; reference = pending.id; display(pending.state);
    if (pending.state === 'failed') { pending = null; challenge = null; lock(false); }
    refreshButtons();
    if (pending && ['queued', 'processing'].indexOf(pending.state) !== -1 && polls < 12) {
      clearTimeout(pollTimer);
      pollTimer = setTimeout(function () { polls++; checkStatus(); }, 2500);
    }
  }
  async function checkStatus() {
    if (!pending || busy) return;
    busy = true; refreshButtons();
    try {
      var result = await call('/v1/inquiries/' + pending.id, {headers: {'X-Status-Token': pending.token}});
      if (result.status === 200) applyResult(result);
      else { pending.state = 'unknown'; display(result.status === 404 ? 'not_found' : 'unknown'); }
    } catch (error) { if (pending) pending.state = 'unknown'; display('unknown'); }
    finally { busy = false; refreshButtons(); }
  }
  async function send() {
    if (busy || (pending && states.indexOf(pending.state) >= 0)) return;
    if (!pending) {
      if (!form.reportValidity()) return;
      if (!confirm.checked) { confirm.focus(); display('confirm_required'); return; }
      try { pending = {id: crypto.randomUUID(), token: randomHex(), data: snapshot(), state: 'new'}; }
      catch (error) { display(['too_many_files', 'file_size', 'file_type', 'contact_required'].includes(error.message) ? error.message : 'invalid_fields'); return; }
    }
    busy = true; polls = 0; clearTimeout(pollTimer); lock(true); refreshButtons(); display('sending');
    try {
      if (!challenge || Date.now() - challenge.time > 1000000) await newChallenge();
      var delay = challenge.age * 1000 - (Date.now() - challenge.time) + 50;
      if (delay > 0) await new Promise(function (resolve) { setTimeout(resolve, delay); });
      pending.data.set('challenge', challenge.value);
      var result = await call('/v1/inquiries', {method:'POST', headers:{'Idempotency-Key':pending.id, 'X-Status-Token':pending.token}, body:pending.data});
      if (result.status === 200 || result.status === 202) applyResult(result);
      else if ([400, 413, 415, 422, 429].indexOf(result.status) >= 0) {
        var errorKey = result.data.error;
        var translated = ['file_size', 'file_type', 'too_many_files', 'contact_required', 'rate_limited'].indexOf(errorKey) >= 0 ? errorKey : 'invalid_fields';
        pending = null; challenge = null; lock(false); display(translated);
      } else { pending.state = 'unknown'; reference = pending.id; display('unknown'); }
    } catch (error) {
      if (pending) { pending.state = 'unknown'; reference = pending.id; } display('unknown');
    } finally { busy = false; refreshButtons(); }
  }
  form.addEventListener('input', function(event) {
    if (!pending && !event.target.closest('#delivery-controls')) confirm.checked = false;
  });
  form.querySelectorAll('.project-template-btn').forEach(function(button) {
    button.addEventListener('click', function() { if (!pending) confirm.checked = false; });
  });
  sendButton.addEventListener('click', send);
  checkButton.addEventListener('click', checkStatus);
  document.addEventListener('efSinn:i18nApplied', function () { if (lastState) display(lastState); refreshButtons(); });
  // No upload or persistence occurs when selecting files; only the explicit send action transmits them.
  newChallenge().then(function () {
    fields.hidden = false; controls.hidden = false;
    [['contact.inquiry.intro','intro'], ['contact.inquiry.requiredNote','required'], ['contact.inquiry.previewNote','preview']].forEach(function (entry) {
      var el = document.querySelector('[data-i18n="' + entry[0] + '"]');
      if (el) { el.setAttribute('data-i18n', 'delivery.' + entry[1]); el.textContent = t(entry[1]); }
    });
    display('ready'); refreshButtons();
  }).catch(function () { display('offline'); });
})();
