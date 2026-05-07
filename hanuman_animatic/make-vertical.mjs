import fs from 'fs';

let html = fs.readFileSync('index.html', 'utf8');

// Change viewport
html = html.replace('width=1920, height=1080', 'width=1080, height=1920');

// Change CSS
html = html.replace('width: 1920px; height: 1080px;', 'width: 1080px; height: 1920px;');
html = html.replace('width: 1920px; height: 1080px;', 'width: 1080px; height: 1920px;');

// Change data attributes
html = html.replace('data-width="1920"\n      data-height="1080"', 'data-width="1080"\n      data-height="1920"');

// Fix caption max width
html = html.replace('maxWidth: 1478', 'maxWidth: 800');

fs.writeFileSync('index-vertical.html', html);
console.log('Created index-vertical.html');
