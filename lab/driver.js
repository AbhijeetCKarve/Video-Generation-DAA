// Records the Problem-1 lab demo: drives lab/vscode/index.html like a person and logs when each narration line starts.
//   node lab/driver.js <project dir> <durations.json> <out dir>
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const [,, PROJ, DURS, OUT] = process.argv;
const dur = JSON.parse(fs.readFileSync(DURS, 'utf8'));            // {"01": seconds, ...}
const cpp = fs.readFileSync(path.join(PROJ, 'src/BubbleSort.cpp'), 'utf8');
const java = fs.readFileSync(path.join(PROJ, 'src/BubbleSort.java'), 'utf8');
const lines = cpp.split('\n');
const chunk = (a, b) => lines.slice(a - 1, b).join('\n') + '\n';   // 1-based inclusive line range
const CHUNKS = [chunk(1, 4), chunk(5, 8), chunk(9, 14), chunk(15, 25), chunk(26, lines.length - 1)];
if (CHUNKS.join('') !== cpp) throw new Error('chunks do not rebuild the source');
// the real program output, split at the input prompts
const run = (cmd, args, input) => execFileSync(cmd, args, { cwd: path.join(PROJ, 'src'), input }).toString();
execFileSync('g++', ['BubbleSort.cpp', '-o', 'BubbleSort'], { cwd: path.join(PROJ, 'src') });
execFileSync('javac', ['BubbleSort.java'], { cwd: path.join(PROJ, 'src') });
const INPUT = '5\n5 1 4 2 8\n';
const outC = run('./BubbleSort', [], INPUT), outJ = run('java', ['BubbleSort'], INPUT);
const [p1, restC] = outC.split('Enter n: ')[1].split('Enter 5 integers: ');
if (p1 !== '') throw new Error('unexpected output');
console.log('C++ output:', JSON.stringify(outC), 'Java output:', JSON.stringify(outJ));

const sleep = ms => new Promise(r => setTimeout(r, ms));
const marks = [];                                                   // [line number, ms since the title card]
let t0 = null;

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: OUT, size: { width: 1920, height: 1080 } } });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.setContent('<body style="background:#000;margin:0"></body>');
  await sleep(1500);
  await page.goto('http://127.0.0.1:8765/index.html?overlay=1');
  await page.evaluate(() => api.ready());
  const api = (fn, ...args) => page.evaluate(([fn, args]) => window.api[fn](...args), [fn, args]);
  const say = async (n) => { if (t0 === null) t0 = Date.now(); marks.push([n, Date.now() - t0]); };
  const hold = async (n, extra = 600) => { const start = marks[marks.length - 1][1]; const need = dur[String(n).padStart(2, '0')] * 1000 + extra;
    const left = need - (Date.now() - t0 - start); if (left > 0) await sleep(left); };
  const typeTerm = async (s, cps = 12) => { await api('termType', s, cps); await sleep(350); await api('termWrite', '\n'); };

  // 1 title card
  await api('overlay', `<div class="pill">DAA LAB · ASSIGNMENT 1</div><h1>Problem 1<br><span>Bubble Sort with swap count</span></h1><div class="sub">C++ and Java, step by step in VS Code</div><div class="by"><small>PREPARED BY</small><b>Abhijeet Karve</b></div>`);
  await say(1); await hold(1, 400);
  await api('overlay', '');
  // 2 new file
  await say(2);
  await sleep(1500);
  await api('cursor', 253, 87, 900); await api('hoverNew', true); await sleep(600); await api('click'); await api('hoverNew', false);
  await api('newFile', 'BubbleSort.cpp', 9);
  await api('cursor', 1100, 700, 700); await api('hideCursor');
  await hold(2);
  // 3-7 type the program in chunks, each paced to its narration line
  for (let i = 0; i < CHUNKS.length; i++) {
    await say(3 + i);
    const need = dur[String(3 + i).padStart(2, '0')];
    const cps = Math.max(12, Math.min(26, CHUNKS[i].length / Math.max(need - 1.0, 3)));   // finish typing just before the line ends
    await api('type', CHUNKS[i], cps);
    await hold(3 + i, 500);
  }
  // 8 save
  await say(8); await sleep(800); await api('toast', '<kbd>Ctrl</kbd> + <kbd>S</kbd>', 1500); await api('save'); await hold(8);
  // 9 terminal
  await say(9); await sleep(600);
  await api('cursor', 487, 19, 900); await api('click');
  await api('menu', 'Terminal', [['New Terminal', 'Ctrl+Shift+`'], ['Split Terminal', 'Ctrl+Shift+5'], ['Run Task...', ''], ['Run Build Task...', 'Ctrl+Shift+B'], ['Run Active File', ''], ['Configure Tasks...', '']], 0, 1600);
  await api('cursor', 1100, 900, 500); await api('hideCursor');
  await api('openTerminal'); await api('prompt'); await hold(9);
  // 10 compile
  await say(10); await sleep(500); await typeTerm('g++ BubbleSort.cpp -o BubbleSort'); await sleep(1400); await api('prompt'); await hold(10);
  // 11 run with the sample input
  await say(11); await sleep(400); await typeTerm('./BubbleSort'); await sleep(300);
  await api('termWrite', 'Enter n: '); await sleep(900); await typeTerm('5', 6); await sleep(200);
  await api('termWrite', 'Enter 5 integers: '); await sleep(900); await typeTerm('5 1 4 2 8', 7); await sleep(250);
  await api('termWrite', restC); await api('prompt'); await hold(11);
  // 12 compare with the expected output
  await say(12); await sleep(300);
  await api('note', `<b>Expected output (from the problem sheet)</b><br>Sorted array: 1 2 4 5 8<br>Number of swaps: 4<br><br><span style="color:#22C55E;font-weight:800">✓ matches exactly</span>`);
  await hold(12, 900); await api('hideNote');
  // 13 viva note
  await say(13); await sleep(300);
  await api('note', `<b>For the viva</b><br>Passes: n − 1<br>Comparisons: ≈ n² / 2 in the worst case<br>Time complexity: <b>O(n²)</b><br>Swaps: depends on the input (4 here)`);
  await hold(13, 900); await api('hideNote');
  // 14 the Java version
  await say(14); await sleep(600);
  await api('cursor', 253, 87, 900); await api('hoverNew', true); await sleep(400); await api('click'); await api('hoverNew', false);
  await api('newFile', 'BubbleSort.java', 12);
  await api('cursor', 1100, 500, 600); await api('hideCursor');
  { const need = dur['14']; const cps = Math.max(60, Math.min(140, java.length / Math.max(need - 4.0, 4))); await api('type', java, cps); }
  await api('toast', '<kbd>Ctrl</kbd> + <kbd>S</kbd>', 1000); await api('save'); await hold(14);
  // 15 compile and run the Java version
  await say(15); await sleep(300);
  await typeTerm('javac BubbleSort.java'); await sleep(1600); await api('prompt');
  await typeTerm('java BubbleSort'); await sleep(400);
  await api('termWrite', 'Enter n: '); await sleep(500); await typeTerm('5', 7); await sleep(150);
  await api('termWrite', 'Enter 5 integers: '); await sleep(500); await typeTerm('5 1 4 2 8', 9); await sleep(300);
  await api('termWrite', outJ.split('Enter 5 integers: ')[1]); await api('prompt'); await hold(15, 1200);
  // 16 end card
  await say(16);
  await api('overlay', `<h1>Thanks for watching</h1><div class="sub">Next: Problem 2 · Selection Sort pass by pass</div><div class="by"><small>CREATED BY</small><b>Abhijeet Karve</b></div>`);
  await hold(16, 6000);
  const total = Date.now() - t0;
  await ctx.close(); await browser.close();
  const video = fs.readdirSync(OUT).filter(f => f.endsWith('.webm')).map(f => path.join(OUT, f)).sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
  fs.writeFileSync(path.join(OUT, 'marks.json'), JSON.stringify({ marks, total, video }, null, 1));
  console.log('done', video, 'total ms', total);
})();
