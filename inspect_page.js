const { chromium } = require('playwright');

async function inspectPage() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Navigate to the main page
    await page.goto('http://localhost:9094');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({ path: 'main_page.png', fullPage: true });
    console.log('Screenshot saved as main_page.png');
    
    // Get page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for filter elements
    console.log('\nChecking for filter elements:');
    
    const selectors = [
      '#skills-filter',
      '#priority-filter', 
      '#status-filter',
      '#team-filter',
      '#sort-filter',
      'select[name="skills"]',
      'select[name="priority"]',
      'select[name="status"]',
      'select[name="team"]',
      'select[name="sort"]',
      '.filter-section',
      '.filters',
      'select'
    ];
    
    for (const selector of selectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        console.log(`✓ Found ${count} element(s) matching: ${selector}`);
        const firstElement = page.locator(selector).first();
        const tagName = await firstElement.evaluate(el => el.tagName);
        const id = await firstElement.getAttribute('id');
        const name = await firstElement.getAttribute('name');
        console.log(`  Tag: ${tagName}, ID: ${id}, Name: ${name}`);
      }
    }
    
    // Get all select elements and their options
    const selects = await page.locator('select').all();
    console.log(`\nFound ${selects.length} select elements:`);
    
    for (let i = 0; i < selects.length; i++) {
      const select = selects[i];
      const id = await select.getAttribute('id');
      const name = await select.getAttribute('name');
      const options = await select.locator('option').allTextContents();
      console.log(`\nSelect ${i + 1}:`);
      console.log(`  ID: ${id}`);
      console.log(`  Name: ${name}`);
      console.log(`  Options: ${JSON.stringify(options)}`);
    }
    
    // Check for idea cards
    const ideaCount = await page.locator('.idea-card').count();
    console.log(`\nFound ${ideaCount} idea cards on the page`);
    
    // Save the HTML for inspection
    const html = await page.content();
    require('fs').writeFileSync('page_content.html', html);
    console.log('\nPage HTML saved to page_content.html');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

inspectPage().catch(console.error);