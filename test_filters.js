const { chromium } = require('playwright');

async function testFiltersAndSorting() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('Starting filter and sorting tests...');
  
  try {
    // Navigate to the main page
    await page.goto('http://localhost:9094');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of main page
    await page.screenshot({ path: 'screenshots/01_main_page.png', fullPage: true });
    console.log('✓ Main page screenshot saved');
    
    // Identify all filter options
    console.log('\n=== Identifying Filters ===');
    
    // Skills filter
    const skillsFilter = await page.locator('#skills-filter');
    const skillsOptions = await skillsFilter.locator('option').allTextContents();
    console.log('Skills filter options:', skillsOptions);
    
    // Priority filter
    const priorityFilter = await page.locator('#priority-filter');
    const priorityOptions = await priorityFilter.locator('option').allTextContents();
    console.log('Priority filter options:', priorityOptions);
    
    // Status filter
    const statusFilter = await page.locator('#status-filter');
    const statusOptions = await statusFilter.locator('option').allTextContents();
    console.log('Status filter options:', statusOptions);
    
    // Team filter
    const teamFilter = await page.locator('#team-filter');
    const teamOptions = await teamFilter.locator('option').allTextContents();
    console.log('Team filter options:', teamOptions);
    
    // Sort options
    const sortFilter = await page.locator('#sort-filter');
    const sortOptions = await sortFilter.locator('option').allTextContents();
    console.log('Sort options:', sortOptions);
    
    // Test each skill filter
    console.log('\n=== Testing Skills Filter ===');
    for (let i = 1; i < skillsOptions.length && i < 3; i++) {
      await skillsFilter.selectOption({ index: i });
      await page.waitForTimeout(1000);
      const count = await page.locator('.idea-card').count();
      console.log(`Skills: ${skillsOptions[i]} - Found ${count} ideas`);
      await page.screenshot({ path: `screenshots/02_skills_${i}_${skillsOptions[i].replace(/\s+/g, '_')}.png` });
    }
    await skillsFilter.selectOption({ index: 0 }); // Reset
    
    // Test each priority filter
    console.log('\n=== Testing Priority Filter ===');
    for (let i = 1; i < priorityOptions.length; i++) {
      await priorityFilter.selectOption({ index: i });
      await page.waitForTimeout(1000);
      const count = await page.locator('.idea-card').count();
      console.log(`Priority: ${priorityOptions[i]} - Found ${count} ideas`);
      await page.screenshot({ path: `screenshots/03_priority_${i}_${priorityOptions[i].replace(/\s+/g, '_')}.png` });
    }
    await priorityFilter.selectOption({ index: 0 }); // Reset
    
    // Test each status filter
    console.log('\n=== Testing Status Filter ===');
    for (let i = 1; i < statusOptions.length; i++) {
      await statusFilter.selectOption({ index: i });
      await page.waitForTimeout(1000);
      const count = await page.locator('.idea-card').count();
      console.log(`Status: ${statusOptions[i]} - Found ${count} ideas`);
      await page.screenshot({ path: `screenshots/04_status_${i}_${statusOptions[i].replace(/\s+/g, '_')}.png` });
    }
    await statusFilter.selectOption({ index: 0 }); // Reset
    
    // Test each sort option
    console.log('\n=== Testing Sort Options ===');
    for (let i = 0; i < sortOptions.length; i++) {
      await sortFilter.selectOption({ index: i });
      await page.waitForTimeout(1000);
      
      // Get first few idea titles to verify sorting
      const titles = await page.locator('.idea-card h3').allTextContents();
      console.log(`Sort: ${sortOptions[i]} - First 3 titles:`, titles.slice(0, 3));
      await page.screenshot({ path: `screenshots/05_sort_${i}_${sortOptions[i].replace(/\s+/g, '_')}.png` });
    }
    
    // Test combined filters
    console.log('\n=== Testing Combined Filters ===');
    if (skillsOptions.length > 1 && priorityOptions.length > 1) {
      await skillsFilter.selectOption({ index: 1 });
      await priorityFilter.selectOption({ index: 1 });
      await page.waitForTimeout(1000);
      const count = await page.locator('.idea-card').count();
      console.log(`Combined (${skillsOptions[1]} + ${priorityOptions[1]}): Found ${count} ideas`);
      await page.screenshot({ path: 'screenshots/06_combined_filters.png' });
    }
    
    console.log('\n✓ All tests completed successfully!');
    
  } catch (error) {
    console.error('Error during testing:', error);
  } finally {
    await browser.close();
  }
}

// Create screenshots directory
const fs = require('fs');
if (!fs.existsSync('screenshots')) {
  fs.mkdirSync('screenshots');
}

testFiltersAndSorting().catch(console.error);