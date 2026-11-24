/* Ma'agal Tov reader: the scan panel. "Show the scan beside the text" puts the page scan of the paragraph being read
   in the right margin and follows the reading as you scroll. Off by default; the choice is kept (localStorage
   key "mt-scan"); images load only while the panel is on. Rows carry data-scans="8:7 9:8" (image file : viewer no.). */
(function () {
  var box = document.getElementById('opt-scan');
  var panel = document.querySelector('.scanpanel');
  if (!box || !panel) return;
  var img = panel.querySelector('img'), tabs = panel.querySelector('.scantabs'), ext = panel.querySelector('.scanext');
  var IA = 'https://archive.org/details/maagaltob00azul/page/n';
  var rows = Array.prototype.slice.call(document.querySelectorAll('.row[data-scans]'));
  var current = null, shown = null, observer = null;

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function scansOf(row) {
    return row.getAttribute('data-scans').split(' ').map(function (x) { var p = x.split(':'); return { file: p[0], n: p[1] }; });
  }
  function show(sc) {
    if (shown && shown.file === sc.file) return;
    shown = sc;
    img.src = 'scans/s' + ('000' + sc.file).slice(-4) + '.jpg';
    img.alt = 'Scan ' + sc.n + ' of the 1885 printing';
    ext.href = IA + sc.n + '/mode/1up';
    ext.textContent = 'Scan ' + sc.n + ' on archive.org ↗';
    Array.prototype.forEach.call(tabs.children, function (b) { b.setAttribute('aria-pressed', String(b.dataset.file === sc.file)); });
  }
  function setRow(row) {
    if (row === current) return;
    current = row;
    var list = scansOf(row);
    tabs.textContent = '';
    if (list.length > 1) {
      list.forEach(function (sc) {
        var b = document.createElement('button');
        b.type = 'button'; b.dataset.file = sc.file; b.textContent = 'scan ' + sc.n;
        b.addEventListener('click', function () { shown = null; show(sc); });
        tabs.appendChild(b);
      });
    }
    var keep = shown && list.some(function (sc) { return sc.file === shown.file; });
    show(keep ? shown : list[0]);
  }
  function apply(on) {
    document.body.classList.toggle('show-scan', on);
    box.checked = on;
    set('mt-scan', on ? '1' : '0');
    if (on && !observer && 'IntersectionObserver' in window) {
      // the active row is the one crossing a line 30% down the window
      observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) setRow(en.target); });
      }, { rootMargin: '-30% 0px -69% 0px' });
      rows.forEach(function (r) { observer.observe(r); });
    }
    if (on && !current && rows.length) {
      var target = location.hash && document.querySelector(location.hash + '.row');
      setRow(target || rows[0]);
    }
  }
  box.addEventListener('change', function () { apply(box.checked); });
  // a click on a "scan N" box in the text shows that scan in the panel when the panel is on
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a.scanlink');
    if (!a || !document.body.classList.contains('show-scan')) return;
    var m = a.href.match(/page\/n(\d+)\//);
    var row = a.closest('.row');
    if (!m || !row) return;
    ev.preventDefault();
    setRow(row);
    scansOf(row).forEach(function (sc) { if (sc.n === m[1]) { shown = null; show(sc); } });
  });
  apply(get('mt-scan') === '1');
})();
