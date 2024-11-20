module.exports = async (page, scenario) => {
  console.log('Logging in for scenario:', scenario.label);

  // Navigate to the login page
  await page.goto('http://localhost:8000/login/');

  // Enter credentials
  await page.type('input[name="username"]', 'admin');
  await page.type('input[name="password"]', 'password');

  // Submit login form and wait for navigation
  await Promise.all([
    page.waitForNavigation({ timeout: 60000 }),
    page.click('button[type="submit"]')
  ]);

  console.log('Logged in successfully! Navigating to scenario URL...');
  await page.goto(scenario.url);
};
