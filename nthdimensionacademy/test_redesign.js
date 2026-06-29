const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

  const filePath = path.resolve(__dirname, 'index.html');
  const fileUrl = `file://${filePath}`;
  
  console.log(`Loading ${fileUrl}...`);
  await page.goto(fileUrl);

  let passed = true;

  // 1. Assert background color
  const bgColor = await page.evaluate(() => {
    return window.getComputedStyle(document.body).backgroundColor;
  });
  if (bgColor === 'rgb(5, 7, 15)') {
    console.log('PASS: Background color is #05070f');
  } else {
    console.log(`FAIL: Background color is ${bgColor}, expected rgb(5, 7, 15)`);
    passed = false;
  }

  // 2. Assert navbar is visible
  const isNavbarVisible = await page.isVisible('.navbar');
  if (isNavbarVisible) {
    console.log('PASS: Navbar is visible');
  } else {
    console.log('FAIL: Navbar is not visible');
    passed = false;
  }

  // 3. Simulate hover on .stat-card and check transform
  const cards = await page.locator('.stat-card, .glass-card');
  const count = await cards.count();
  console.log(`Found ${count} cards`);

  if (count > 0) {
    const card = cards.first();
    
    // Scroll element into view
    await card.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);

    const box = await card.boundingBox();
    console.log('Card bounding box:', box);

    // Move mouse to trigger mousemove
    // box.x and box.y are relative to the main frame's viewport
    await page.mouse.move(box.x + box.width / 2 + 20, box.y + box.height / 2 + 20);
    
    // Wait for any animation/style change
    await page.waitForTimeout(500);
    
    const transform = await card.evaluate(el => {
        return window.getComputedStyle(el).transform;
    });
    console.log(`Computed transform style on hover: ${transform}`);
    
    if (transform !== 'none' && transform !== '') {
      console.log('PASS: Tilt transform applied (matrix detected)');
    } else {
      const inlineTransform = await card.evaluate(el => el.style.transform);
      console.log(`Inline transform style on hover: ${inlineTransform}`);
      if (inlineTransform.includes('rotateX')) {
          console.log('PASS: Tilt transform applied (inline style detected)');
      } else {
          console.log('FAIL: Tilt transform not applied on hover');
          passed = false;
      }
    }
  } else {
    console.log('SKIP: No .stat-card or .glass-card found');
  }

  await browser.close();
  
  if (!passed) {
    process.exit(1);
  }
})();
