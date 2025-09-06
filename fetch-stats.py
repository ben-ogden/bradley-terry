"""
Fetch hockey team statistics from gamesheetstats.com
"""

from web_scraper import HockeyWebScraper
from data_manager import DataManager
from config import DIVISION_ID, TEAM_ID, BASE_URL


def main():
    """Main function to fetch and display team statistics"""
    # Build the division URL
    division_url = BASE_URL.format(DIVISION_ID, TEAM_ID)
    
    # Initialize components
    scraper = HockeyWebScraper()
    data_manager = DataManager()
    
    # Get team URLs from the division page
    print("Fetching team URLs...")
    team_urls = scraper.get_team_urls(division_url)
    
    if not team_urls:
        print("No team URLs found. Exiting.")
        return
    
    print(f"Found {len(team_urls)} teams")
    
    # Scrape results for all teams
    print("Scraping team results...")
    team_results = scraper.scrape_all_teams(team_urls)
    
    # Save results to file
    data_manager.save_team_results(team_results)
    
    # Print the results
    print("\nTeam Results:")
    print("=" * 50)
    for i, team in enumerate(team_results):
        if team:  # Only print teams with results
            print(f"\nTeam {i+1}:")
            for game in team:
                print(f"  {game[0]} vs {game[1]}: {game[2]}")


if __name__ == "__main__":
    main()