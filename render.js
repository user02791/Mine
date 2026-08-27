const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('JS: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
  await page.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // report any page section taller than its box (would spill to a blank page)
  const spill = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.page').forEach((el, i) => {
      if (el.scrollHeight > el.clientHeight + 2) {
        out.push({ page: i + 1, over: el.scrollHeight - el.clientHeight });
      }
    });
    return out;
  });
  const fam = await page.evaluate(() => {
    const s = new Set();
    document.fonts.forEach(f => s.add(f.family + ' ' + f.weight + ' ' + f.status));
    return [...s];
  });
  await page.pdf({ path: process.argv[3], printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('fonts:', fam.join(' | '));
  console.log('overflowing pages:', spill.length ? JSON.stringify(spill) : 'none');
  if (errs.length) console.log('errors:', errs.join('\n'));
})();
