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
  const say = async (n) => { if (t0 === null) t0 = Date.now(); marks.push([n, Date.now() - t0]); await api('mark'); };   // the 6-px flash lets the mixer find this moment in the video
  const hold = async (n, extra = 600) => { const start = marks[marks.length - 1][1]; const need = dur[String(n).padStart(2, '0')] * 1000 + extra;
    const left = need - (Date.now() - t0 - start); if (left > 0) await sleep(left); };
  const typeTerm = async (s, cps = 12) => { await api('termType', s, cps); await sleep(350); await api('termWrite', '\n'); };

  const chunkLine = [6, 7, 8, 9, 10];                              // narration line for each code chunk
  const pill = '<div class="pill">DAA LAB · ASSIGNMENT 1</div>';
  // 1 hook on the title card
  await api('overlay', `${pill}<h1>Problem 1<br><span>Bubble Sort with swap count</span></h1><div class="sub">C++ and Java, step by step in VS Code</div><div class="by"><small>PREPARED BY</small><b>Abhijeet Karve</b></div>`);
  await say(1); await hold(1, 300);
  // 2 welcome
  await api('overlay', `<div class="head">DAA SERIES</div><div class="big">by Abhijeet Karve</div><div class="guide">your guide, step by step</div>`);
  await say(2); await hold(2, 300);
  // 3 today's plan, 4 the viva star
  await api('overlay', `${pill}<div class="rows"><div class="row"><span class="n">1</span>The program in C++, written and run in VS Code</div><div class="row"><span class="n">2</span>Check against the sample output</div><div class="row"><span class="n">3</span>The same program in Java</div></div><div class="star" style="opacity:0" id="star">★  Viva tips at the end</div>`);
  await say(3); await sleep(Math.max(1200, dur['03'] * 1000 * 0.35));
  for (let i = 0; i < 3; i++) { await api('reveal', '#overlay .row', i); await sleep(800); }
  await hold(3, 300);
  await say(4); await sleep(600); await page.evaluate(() => { document.getElementById('star').style.opacity = 1; }); await hold(4, 300);
  await api('overlay', '');
  // 5 new file
  await say(5);
  await sleep(1500);
  await api('cursor', 253, 87, 900); await api('hoverNew', true); await sleep(600); await api('click'); await api('hoverNew', false);
  await api('newFile', 'BubbleSort.cpp', 9);
  await api('cursor', 1100, 700, 700); await api('hideCursor');
  await hold(5);
  // 6-10 type the program in chunks, each paced to its narration line
  for (let i = 0; i < CHUNKS.length; i++) {
    const n = chunkLine[i];
    await say(n);
    const need = dur[String(n).padStart(2, '0')];
    const cps = Math.max(12, Math.min(26, CHUNKS[i].length / Math.max(need - 1.0, 3)));
    await api('type', CHUNKS[i], cps);
    await hold(n, 500);
  }
  // 11 save
  await say(11); await sleep(800); await api('toast', '<kbd>Ctrl</kbd> + <kbd>S</kbd>', 1500); await api('save'); await hold(11);
  // 12 terminal
  await say(12); await sleep(600);
  await api('cursor', 487, 19, 900); await api('click');
  await api('menu', 'Terminal', [['New Terminal', 'Ctrl+Shift+`'], ['Split Terminal', 'Ctrl+Shift+5'], ['Run Task...', ''], ['Run Build Task...', 'Ctrl+Shift+B'], ['Run Active File', ''], ['Configure Tasks...', '']], 0, 1600);
  await api('cursor', 1100, 900, 500); await api('hideCursor');
  await api('openTerminal'); await api('prompt'); await hold(12);
  // 13 compile
  await say(13); await sleep(500); await typeTerm('g++ BubbleSort.cpp -o BubbleSort'); await sleep(1400); await api('prompt'); await hold(13);
  // 14 run with the sample input
  await say(14); await sleep(400); await typeTerm('./BubbleSort'); await sleep(300);
  await api('termWrite', 'Enter n: '); await sleep(900); await typeTerm('5', 6); await sleep(200);
  await api('termWrite', 'Enter 5 integers: '); await sleep(900); await typeTerm('5 1 4 2 8', 7); await sleep(250);
  await api('termWrite', restC); await api('prompt'); await hold(14);
  // 15 compare with the expected output
  await say(15); await sleep(300);
  await api('note', `<b>Expected output (from the problem sheet)</b><br>Sorted array: 1 2 4 5 8<br>Number of swaps: 4<br><br><span style="color:#22C55E;font-weight:800">✓ matches exactly</span>`);
  await hold(15, 900); await api('hideNote');
  // 16 the Java version
  await say(16); await sleep(600);
  await api('cursor', 253, 87, 900); await api('hoverNew', true); await sleep(400); await api('click'); await api('hoverNew', false);
  await api('newFile', 'BubbleSort.java', 12);
  await api('cursor', 1100, 500, 600); await api('hideCursor');
  { const need = dur['16']; const cps = Math.max(60, Math.min(140, java.length / Math.max(need - 4.0, 4))); await api('type', java, cps); }
  await api('toast', '<kbd>Ctrl</kbd> + <kbd>S</kbd>', 1000); await api('save'); await hold(16);
  // 17 compile and run the Java version
  await say(17); await sleep(300);
  await typeTerm('javac BubbleSort.java'); await sleep(1600); await api('prompt');
  await typeTerm('java BubbleSort'); await sleep(400);
  await api('termWrite', 'Enter n: '); await sleep(500); await typeTerm('5', 7); await sleep(150);
  await api('termWrite', 'Enter 5 integers: '); await sleep(500); await typeTerm('5 1 4 2 8', 9); await sleep(300);
  await api('termWrite', outJ.split('Enter 5 integers: ')[1]); await api('prompt'); await hold(17, 1200);
  // 18-20 viva tips
  await api('overlay', `<div class="head">VIVA TIPS</div><div class="rows">
    <div class="row"><span class="n gold">1</span><div>Say what the two loops do<small>n − 1 passes; each pass compares neighbours and bubbles the largest to the end</small></div></div>
    <div class="row"><span class="n gold">2</span><div>State the time complexity: O(n²)<small>≈ n² / 2 comparisons in the worst case; swaps depend on the input (4 here)</small></div></div>
    <div class="row"><span class="n gold">3</span><div>Read input with a prompt, label every output line<small>exactly as the problem statement shows it</small></div></div></div>`);
  for (let i = 0; i < 3; i++) { await say(18 + i); await sleep(500); await api('reveal', '#overlay .row', i); await hold(18 + i, 400); }
  // 21 recap
  await api('overlay', `<div class="head">RECAP</div><div class="rows">
    <div class="row"><span class="tick">✓</span>Two nested loops, a swap counter inside the if</div>
    <div class="row"><span class="tick">✓</span>Compile with g++ or javac, run, type the input</div>
    <div class="row"><span class="tick">✓</span>Always compare with the sample output before the viva</div></div>`);
  await say(21);
  { const d = dur['21'] * 1000; for (let i = 0; i < 3; i++) { await sleep(i === 0 ? d * 0.12 : d * 0.28); await api('reveal', '#overlay .row', i); } }
  await hold(21, 400);
  // 22 next video, then the end card
  await api('overlay', `<div class="nextbox"><small>NEXT VIDEO</small><b>Problem 2<br>Selection Sort pass by pass</b></div>`);
  await say(22); await hold(22, 300);
  await api('overlay', `<h1>Thanks for watching</h1><div class="by"><small>CREATED BY</small><b>Abhijeet Karve</b></div>`);
  await sleep(7000);
  const total = Date.now() - t0;
  await ctx.close(); await browser.close();
  const video = fs.readdirSync(OUT).filter(f => f.endsWith('.webm')).map(f => path.join(OUT, f)).sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
  fs.writeFileSync(path.join(OUT, 'marks.json'), JSON.stringify({ marks, total, video }, null, 1));
  console.log('done', video, 'total ms', total);
})();
