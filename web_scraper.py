"""
Web scraping module for hockey team statistics.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import CHROME_OPTIONS, PAGE_LOAD_TIMEOUT, REQUEST_DELAY


class HockeyWebScraper:
    """Web scraper for hockey team statistics from gamesheetstats.com"""
    
    def __init__(self):
        self.options = self._setup_chrome_options()
    
    def _setup_chrome_options(self):
        """Setup Chrome driver options"""
        options = Options()
        
        # Use modern headless mode
        if CHROME_OPTIONS['headless']:
            options.add_argument('--headless=new')
        
        # Add other options
        if CHROME_OPTIONS.get('no_sandbox'):
            options.add_argument('--no-sandbox')
        if CHROME_OPTIONS.get('disable_dev_shm_usage'):
            options.add_argument('--disable-dev-shm-usage')
        if CHROME_OPTIONS.get('disable_extensions'):
            options.add_argument('--disable-extensions')
        if CHROME_OPTIONS.get('disable_blink_features'):
            options.add_argument(f'--disable-blink-features={CHROME_OPTIONS["disable_blink_features"]}')
        
        # Set user agent
        if CHROME_OPTIONS.get('user_agent'):
            options.add_argument(f'--user-agent={CHROME_OPTIONS["user_agent"]}')
        
        # Modern Chrome options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def get_team_urls(self, division_url):
        """Get a list of team URLs from the division page"""
        try:
            with webdriver.Chrome(options=self.options) as driver:
                driver.get(division_url)
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "teamTitle")))

                team_title_div = driver.find_element(By.CLASS_NAME, 'teamTitle')
                team_title_links = team_title_div.find_elements(
                    By.CSS_SELECTOR, 'div.team-title a')

                team_urls = [link.get_attribute('href') for link in team_title_links]
                return team_urls
        except Exception as e:
            print(f"Error getting team URLs: {e}")
            return []
    
    def _get_list_by_class(self, parent_element):
        """Extract text from elements with row classes"""
        rows = parent_element.find_elements(By.CSS_SELECTOR, 'div[class*="row-"]')
        result_list = []
        for row in rows:
            row_text = row.text.strip().upper()
            if row_text:
                result_list.append(row_text)
            else:
                result_list.append('ERROR')
        return result_list
    
    def get_team_results(self, team_url):
        """Get game results for a specific team"""
        try:
            with webdriver.Chrome(options=self.options) as driver:
                # Get stats page, waiting for stats table to load
                driver.get(team_url)
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'gs-table')))
                table = driver.find_element(By.CLASS_NAME, 'gs-table')

                # Get the home team for this page
                home_team = driver.find_element(By.CLASS_NAME, 'title').text.strip().upper()

                # Get list of visiting teams
                visitors = table.find_element(By.CLASS_NAME, 'visitor')
                visitor_list = self._get_list_by_class(visitors)

                # Get list of home teams
                home = table.find_element(By.CLASS_NAME, 'home')
                home_list = self._get_list_by_class(home)

                # Get list of details - a win or loss
                details = table.find_element(By.CLASS_NAME, 'details')
                details_list = self._get_list_by_class(details)

            game_list = []
            for i in range(len(home_list)):
                # Only include games that have a result posted
                if details_list[i][0] in ['L', 'W', 'T']:
                    # Put the main team in the first column
                    if home_list[i] != home_team:
                        game_list.append([home_team, home_list[i], details_list[i]])
                    elif visitor_list[i] != home_team:
                        game_list.append([home_team, visitor_list[i], details_list[i]])
            
            return game_list
        except Exception as e:
            print(f"Error getting team results for {team_url}: {e}")
            return []
    
    def scrape_all_teams(self, team_urls):
        """Scrape results for all teams with proper delays"""
        team_results = []
        for i, team_url in enumerate(team_urls):
            print(f'Getting results for {team_url} ({i+1}/{len(team_urls)})')
            results = self.get_team_results(team_url)
            team_results.append(results)
            
            # Be kind to the server
            if i < len(team_urls) - 1:  # Don't sleep after the last request
                time.sleep(REQUEST_DELAY)
        
        return team_results
