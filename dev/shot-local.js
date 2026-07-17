const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = 'C:\\Users\\asche\\AppData\\Local\\Temp\\claude\\C--Users-asche-Downloads-claude-Oculus\\a0f3b3f1-a6c0-436f-b371-2c84443240cb\\scratchpad\\local-depth.png';

(async () => {
  const logs = [];
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--no-sandbox']
  });
  const page = await browser.newPage();
  page.on('pageerror', e => logs.push('[PAGEERROR] ' + e.message));
  page.on('console', m => { if (m.text().indexOf('HOUSE_SIZE') >= 0) logs.push(m.text()); });
  await page.setViewport({ width: 1280, height: 720 });
  await page.goto('http://localhost:8080/', { waitUntil: 'networkidle2', timeout: 40000 });
  await new Promise(r => setTimeout(r, 4000));
  await page.screenshot({ path: OUT });
  console.log('shot -> ' + OUT);
  console.log('errors: ' + (logs.length ? logs.join(' | ') : 'none'));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
