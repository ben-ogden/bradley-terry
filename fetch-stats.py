from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

division = 3659  # division id
team = 140689  # any team id from the division
base_url = 'https://gamesheetstats.com/seasons/{}/teams/{}/standings'
division_url = base_url.format(division, team)

options = Options()
options.headless = True
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
)


# Get a list of team urls from the division page
def get_team_urls(division_url):
    with webdriver.Chrome(options=options) as driver:
        driver.get(division_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "teamTitle")))

        team_title_div = driver.find_element(By.CLASS_NAME, 'teamTitle')
        team_title_links = team_title_div.find_elements(
            By.CSS_SELECTOR, 'div.team-title a')

        team_urls = [link.get_attribute('href') for link in team_title_links]
    return team_urls


def get_list_by_class(parent_element):
    rows = parent_element.find_elements(By.CSS_SELECTOR, 'div[class*="row-"]')
    result_list = []
    for row in rows:
        row_text = row.text.strip().upper()
        if row_text:
            result_list.append(row_text)
        else:
            result_list.append('ERROR')
    return result_list


def get_team_results(team_url):

    with webdriver.Chrome(options=options) as driver:

        # get stats page, waiting for stats table to load
        driver.get(team_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'gs-table')))
        table = driver.find_element(By.CLASS_NAME, 'gs-table')

        # get the home team for this page
        home_team = driver.find_element(By.CLASS_NAME,
                                        'title').text.strip().upper()

        # get list of visiting teams
        visitors = table.find_element(By.CLASS_NAME, 'visitor')
        visitor_list = get_list_by_class(visitors)

        # get list of home teams
        home = table.find_element(By.CLASS_NAME, 'home')
        home_list = get_list_by_class(home)

        # get list of details - a win or loss
        details = table.find_element(By.CLASS_NAME, 'details')
        details_list = get_list_by_class(details)

    game_list = []
    for i in range(len(home_list)):
        # only include games that have a result posted
        if details_list[i][0] in ['L', 'W', 'T']:
            # put the main team in the first column
            if home_list[i] != home_team:
                game_list.append([home_team, home_list[i], details_list[i]])
            elif visitor_list[i] != home_team:
                game_list.append([home_team, visitor_list[i], details_list[i]])
    return game_list


# get a list of the team urls from the division page
team_urls = get_team_urls(division_url)

# visit each team page and get the stats table
team_results = []
for team_url in team_urls:
    print('Getting results for {}'.format(team_url))
    team_results.append(get_team_results(team_url))
    time.sleep(10)  # be kind to the server

# print the results
for team in team_results:
    for game in team:
        print(game)