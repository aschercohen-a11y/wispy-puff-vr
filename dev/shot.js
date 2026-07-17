const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = 'C:\\Users\\asche\\Downloads\\claude\\Oculus\\preview-vr.png';

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--ignore-gpu-blocklist','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--no-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });
  await page.goto('https://wispyvr.swipego.app/', { waitUntil: 'networkidle2', timeout: 40000 });
  await new Promise(r => setTimeout(r, 5000));
  await page.screenshot({ path: OUT });
  console.log('screenshot -> ' + OUT);
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
