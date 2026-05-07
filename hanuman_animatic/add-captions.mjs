import fs from 'fs';

const transcript = JSON.parse(fs.readFileSync('transcript.json', 'utf8'));

// Filter raw transcript
const words = transcript.filter(w => {
  if (!w.text || w.text.trim().length === 0) return false;
  if (/^[♪\u266a\u266b\u266c\u266d\u266e\u266f]+$/.test(w.text)) return false;
  if (/^(huh|uh|um|ah|oh)$/i.test(w.text) && w.end - w.start < 0.1) return false;
  return true;
});

// Group words (Storytelling tone: 4-6 words)
const groups = [];
let currentGroup = [];
let currentGroupStart = 0;

for (let i = 0; i < words.length; i++) {
  const w = words[i];
  if (currentGroup.length === 0) currentGroupStart = w.start;
  
  currentGroup.push(w);
  
  const isSentenceEnd = /[.!?]$/.test(w.text);
  const nextWord = words[i + 1];
  const pause = nextWord ? nextWord.start - w.end : 0;
  
  if (currentGroup.length >= 5 || isSentenceEnd || pause >= 0.15 || i === words.length - 1) {
    groups.push({
      text: currentGroup.map(x => x.text).join(' '),
      start: currentGroupStart,
      end: w.end,
      words: currentGroup
    });
    currentGroup = [];
  }
}

// Generate HTML and JS
let html = fs.readFileSync('index.html', 'utf8');

// Inject caption container and styles
const styleInjection = `
      #captions {
        position: absolute;
        bottom: 100px;
        left: 0;
        width: 100%;
        text-align: center;
        z-index: 100;
        font-family: "Cinzel", "Playfair Display", serif;
        color: #fcebd2; /* warm muted */
        text-shadow: 0 4px 12px rgba(0,0,0,0.8);
      }
      .caption-group {
        position: absolute;
        width: 100%;
        opacity: 0;
        visibility: hidden;
      }
`;
html = html.replace('</style>', styleInjection + '    </style>');

const containerInjection = `
      <div id="captions"></div>
`;
html = html.replace('</div>\n\n    <script>', containerInjection + '    </div>\n\n    <script>');

const jsInjection = `
      // Captions Logic
      const captionGroups = ${JSON.stringify(groups)};
      const capContainer = document.getElementById('captions');
      
      captionGroups.forEach((group, i) => {
        const el = document.createElement('div');
        el.className = 'caption-group';
        el.id = 'cg-' + i;
        el.innerText = group.text;
        
        // Fit text size
        const fit = window.__hyperframes ? window.__hyperframes.fitTextFontSize(group.text, {
          fontFamily: '"Cinzel", serif',
          fontWeight: 400,
          maxWidth: 1600,
          baseFontSize: 56,
          minFontSize: 44
        }) : { fontSize: 50 };
        
        el.style.fontSize = fit.fontSize + "px";
        capContainer.appendChild(el);
        
        // Timeline animations for storytelling style
        // Slow fade, power2.out, 0.5-0.6s
        tl.set(el, { visibility: "visible" }, group.start);
        tl.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, group.start);
        
        // Exit
        tl.to(el, { opacity: 0, scale: 0.95, duration: 0.12, ease: "power2.in" }, group.end - 0.12);
        tl.set(el, { opacity: 0, visibility: "hidden" }, group.end);
      });
`;
html = html.replace('window.__timelines["main"] = tl;', jsInjection + '\n      window.__timelines["main"] = tl;');

fs.writeFileSync('index.html', html, 'utf8');
console.log('Captions added to index.html with ' + groups.length + ' groups.');
