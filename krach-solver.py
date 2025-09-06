"""
KRACH (Ken's Ratings for American College Hockey) solver for hockey team rankings.
"""

from web_scraper import HockeyWebScraper
from krach_calculator import KRACHCalculator
from data_manager import DataManager
from config import DIVISION_ID, TEAM_ID, BASE_URL


def main():
    """Main function to calculate and display KRACH rankings"""
    # Build the division URL
    division_url = BASE_URL.format(DIVISION_ID, TEAM_ID)
    
    # Initialize components
    scraper = HockeyWebScraper()
    calculator = KRACHCalculator()
    data_manager = DataManager()
    
    # Try to load existing data first
    team_results = data_manager.load_team_results()
    
    # If no existing data, scrape fresh data
    if team_results is None:
        print("No existing data found. Scraping fresh data...")
        
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
    else:
        print("Using existing data from file")
    
    # Calculate KRACH rankings
    print("Calculating KRACH rankings...")
    try:
        sorted_ratings = calculator.calculate_rankings(team_results)
        
        if sorted_ratings.empty:
            print("No valid rankings could be calculated from the data.")
            return
        
        # Display results
        print("\nKRACH Rankings:")
        print("=" * 60)
        print(f"{'Rank':<4} {'Team':<40} {'Rating':<12}")
        print("-" * 60)
        
        for rank, (team, rating) in enumerate(sorted_ratings.items(), 1):
            print(f"{rank:<4} {team:<40} {rating:<12.2f}")
            
    except ValueError as e:
        print(f"Error calculating rankings: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return


if __name__ == "__main__":
    main()