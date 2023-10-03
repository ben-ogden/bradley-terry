from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
import pandas as pd
import os.path
import pickle

# Define the filename for the intermediate file
filename = 'team_results.pkl'

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


# Define the function to build the pairwise comparison matrix
def build_pairwise_matrix(team_results):

    # Get a list of all the teams
    teams = list(
        set([game[0] for team in team_results for game in team] +
            [game[1] for team in team_results for game in team]))

    # Initialize the pairwise comparison matrix
    pairwise_matrix = pd.DataFrame(index=teams, columns=teams)
    pairwise_matrix.fillna(0, inplace=True)

    # Populate the pairwise comparison matrix
    for team in team_results:
        home_team = team[0][0]
        for game in team:
            visitor_team = game[1]
            result = game[2]
            if result.startswith('W'):
                pairwise_matrix.loc[home_team, visitor_team] += 1
            # this will double count?
            #elif result.startswith('L'):
            #    pairwise_matrix.loc[visitor_team, home_team] += 1
            elif result.startswith('T'):
                pairwise_matrix.loc[home_team, visitor_team] += 0.5
            #    pairwise_matrix.loc[visitor_team, home_team] += 0.5

        #TODO - temp hack to add a missing game
        # add a missing game
        pairwise_matrix.loc["FREDERICK FREEZE 16U UA",
                            "AVIATOR HOCKEY CLUB 16U MINOR"] += 1

    return pairwise_matrix


# Define the function to solve for the KRACH rating for each team
def solve_krach(pairwise_matrix):
    # Set the alpha value
    alpha = 0.85

    # Initialize the P values
    P = pd.Series(np.ones(len(pairwise_matrix)), index=pairwise_matrix.index)

    # Iterate until convergence
    for i in range(200):
        P_old = P.copy()
        for team in P.index:
            numerator = pairwise_matrix.loc[team].dot(P_old)
            denominator = pairwise_matrix.loc[team].dot(
                P_old) + pairwise_matrix[team].sum() + alpha
            P[team] = numerator / denominator
        if abs(P - P_old).sum() < 0.00001:
            break

    # Scale the P values by 10000
    P_scaled = P * 10000 * 10000

    return P_scaled


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

            # exclude teams not in the division?
            exclude_teams = []
            if home_list[i] not in exclude_teams and visitor_list[
                    i] not in exclude_teams:

                # put the main team in the first column
                if home_list[i] != home_team:
                    game_list.append(
                        [home_team, home_list[i], details_list[i]])
                elif visitor_list[i] != home_team:
                    game_list.append(
                        [home_team, visitor_list[i], details_list[i]])

    return game_list


# Check if the intermediate file exists
if os.path.isfile(filename):
    # Load the team results from the intermediate file
    with open(filename, 'rb') as f:
        team_results = pickle.load(f)
else:
    # Get a list of the team urls from the division page
    team_urls = get_team_urls(division_url)

    # visit each team page and get the stats table
    team_results = []
    for team_url in team_urls:
        print('Getting results for {}'.format(team_url))
        team_results.append(get_team_results(team_url))
        time.sleep(2)  # be kind to the server

    # Save the team results to the intermediate file
    with open(filename, 'wb') as f:
        pickle.dump(team_results, f)

# Build the pairwise matrix for the remaining teams
pairwise_matrix = build_pairwise_matrix(team_results)

# Build the pairwise comparison matrix
pairwise_matrix = build_pairwise_matrix(team_results)

# Solve for the KRACH rating for each team
krach_ratings = solve_krach(pairwise_matrix)

# Sort the KRACH ratings from highest to lowest
sorted_ratings = krach_ratings.sort_values(ascending=False)

# Print the sorted KRACH ratings
print(sorted_ratings)