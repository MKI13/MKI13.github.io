(function(){
      var form = document.getElementById('inquiry-form');
      if(!form) return;
      var templateBtns = form.querySelectorAll('.project-template-btn');
      var typeValueInput = document.getElementById('inq-type-value');
      var projectTypeAliases = {
        moebel: 'customFurniture', furniture: 'customFurniture', customFurniture: 'customFurniture', einbauschrank: 'customFurniture',
        kitchen: 'kitchen', kueche: 'kitchen', kuechen: 'kitchen',
        parquet: 'parquetInstall', parkett: 'parquetInstall', parquetInstall: 'parquetInstall', parquetSand: 'parquetSand',
        terrace: 'terrace', terrassen: 'terrace', balkon: 'terrace', balcony: 'terrace',
        stairs: 'stairs', treppen: 'stairs',
        bathroomFurniture: 'bathroomFurniture', badmoebel: 'bathroomFurniture', bath: 'bathroomFurniture',
        interior: 'interior', innenausbau: 'interior', wandverkleidung: 'interior',
        outdoor: 'outdoor', aussenbau: 'outdoor', gardenhouse: 'outdoor', gartenhaus: 'outdoor',
        repair: 'repair', consultation: 'consultation'
      };
      function normalizeProjectKey(value){
        return projectTypeAliases[value] || value || '';
      }
      function selectProjectType(key){
        key = normalizeProjectKey(key);
        var selected = null;
        templateBtns.forEach(function(btn){
          var isActive = btn.getAttribute('data-project-key') === key;
          btn.classList.toggle('active', isActive);
          btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
          if(isActive) selected = btn;
        });
        if(!selected && templateBtns[0]) {
          selected = templateBtns[0];
          selected.classList.add('active');
          selected.setAttribute('aria-pressed', 'true');
        }
        if(selected && typeValueInput) typeValueInput.value = selected.getAttribute('data-project-type') || '';
      }
      templateBtns.forEach(function(btn){
        btn.addEventListener('click', function(){
          selectProjectType(btn.getAttribute('data-project-key'));
        });
      });
      function requestedProjectType(){
        try {
          var params = new URLSearchParams(window.location.search || '');
          return params.get('project') || params.get('type') || params.get('projekt') || '';
        } catch(e) { return ''; }
      }
      function syncSelectedProjectType(){
        var active = form.querySelector('.project-template-btn.active');
        if(active && typeValueInput) typeValueInput.value = active.getAttribute('data-project-type') || '';
      }
      document.addEventListener('efSinn:i18nApplied', syncSelectedProjectType);
      selectProjectType(requestedProjectType() || 'customFurniture');
      syncSelectedProjectType();


      var review = document.getElementById('inquiry-preview');
      var reviewText = document.getElementById('inquiry-preview-text');
      var status = document.getElementById('inquiry-status');
      var emailButton = document.getElementById('inq-open-email');
      var statusKey = '';
      var MAX_MAILTO_LENGTH = 1800;
      function t(key, fallback) {
        return ((window.EFSINN_I18N || {}).dict || {})[key] || fallback || key;
      }
      function get(id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : '';
      }
      function draft() {
        var type = get('inq-custom-type') || get('inq-type-value') || t('contact.inquiry.defaultProject', 'Schreinerprojekt');
        var subject = t('contact.mail.subjectPrefix', 'Projektanfrage ef-sinn: ') + type.replace(/[\r\n]/g, ' ');
        var body = [
          t('contact.mail.greeting', 'Hallo ef-sinn,'), '',
          t('contact.mail.intro', 'ich möchte eine Anfrage für folgendes Projekt senden:'), '',
          t('contact.mail.name', 'Name: ') + get('inq-name'),
          t('contact.mail.phone', 'Telefon: ') + get('inq-phone'),
          t('contact.mail.email', 'E-Mail: ') + get('inq-email'),
          t('contact.mail.projectType', 'Projektart: ') + type,
          t('contact.mail.location', 'Ort / Stadtteil: ') + get('inq-location'),
          t('contact.inquiry.measurements.label', 'Maße / Raumgröße') + ': ' + get('inq-measurements'),
          t('contact.inquiry.timeframe.label', 'Gewünschter Zeitraum') + ': ' + get('inq-timeframe'),
          t('contact.mail.appointment1', 'Terminvorschlag 1 für Besichtigung: ') + get('inq-appointment-1'),
          t('contact.mail.appointment2', 'Terminvorschlag 2 für Besichtigung: ') + get('inq-appointment-2'), '',
          t('contact.mail.description', 'Beschreibung:'), get('inq-message'), '',
          t('contact.mail.freeNote', 'Eine kurze Ersteinschätzung anhand von Fotos, Maßen und Telefonat ist kostenlos. Ein Vor-Ort-Termin wird persönlich abgestimmt.'),
          t('contact.mail.nextStep', 'Bitte melden Sie sich für eine erste Einschätzung bei mir.'), '',
          t('contact.mail.regards', 'Viele Grüße')
        ].join('\n');
        var recipient = 'mailto:info@ef-sinn.de?subject=' + encodeURIComponent(subject);
        return {subject: subject, body: body, recipient: recipient, uri: recipient + '&body=' + encodeURIComponent(body)};
      }
      function announce(key) {
        statusKey = key;
        status.textContent = key ? t(key) : '';
      }
      function renderReview() {
        var message = draft();
        reviewText.value = 'info@ef-sinn.de\n' + message.subject + '\n\n' + message.body;
        var longMessage = message.uri.length > MAX_MAILTO_LENGTH;
        document.getElementById('inquiry-long-note').hidden = !longMessage;
        emailButton.textContent = t(longMessage ? 'contact.inquiry.openEmpty' : 'contact.inquiry.openEmail');
        if(statusKey) status.textContent = t(statusKey);
      }
      function showReview() {
        if(!form.reportValidity()) return;
        announce('');
        review.hidden = false;
        renderReview();
        review.focus();
      }
      form.addEventListener('submit', function(event) {
        event.preventDefault();
        showReview();
      });
      form.addEventListener('input', function(event) {
        // The explicit send confirmation belongs to the already reviewed draft.
        if(event.target.closest && event.target.closest('#delivery-controls')) return;
        review.hidden = true;
        announce('');
      });
      templateBtns.forEach(function(button) {
        button.addEventListener('click', function() { review.hidden = true; announce(''); });
      });
      document.getElementById('inq-edit').addEventListener('click', function() {
        review.hidden = true;
        announce('');
        document.getElementById('inq-name').focus();
      });
      emailButton.addEventListener('click', function() {
        var message = draft();
        var link = document.createElement('a');
        link.href = message.uri.length > MAX_MAILTO_LENGTH ? message.recipient : message.uri;
        announce(message.uri.length > MAX_MAILTO_LENGTH ? 'contact.inquiry.emptyOpened' : 'contact.inquiry.emailOpened');
        document.body.appendChild(link);
        link.click();
        link.remove();
      });
      document.getElementById('inq-copy').addEventListener('click', async function() {
        renderReview();
        try {
          if(!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
          await navigator.clipboard.writeText(reviewText.value);
          announce('contact.inquiry.copied');
        } catch(error) {
          reviewText.focus();
          reviewText.select();
          announce('contact.inquiry.manualCopy');
        }
      });
      document.getElementById('inq-download').addEventListener('click', function() {
        renderReview();
        var url = URL.createObjectURL(new Blob([reviewText.value], {type: 'text/plain;charset=utf-8'}));
        var link = document.createElement('a');
        link.href = url;
        link.download = 'ef-sinn-projektanfrage.txt';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(function() { URL.revokeObjectURL(url); }, 1000);
        announce('contact.inquiry.downloaded');
      });
      document.addEventListener('efSinn:i18nApplied', function() {
        if(!review.hidden) renderReview();
        else if(statusKey) status.textContent = t(statusKey);
      });
      // Enable only after every handler is installed. Without JavaScript there is no native GET submission.
      document.getElementById('inq-review').disabled = false;
      form.setAttribute('data-inquiry-ready', 'true');
    })();
