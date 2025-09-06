"""
Data management utilities for saving and loading team results.
"""

import pickle
import os
from config import TEAM_RESULTS_FILE


class DataManager:
    """Manages saving and loading of team results data"""
    
    def __init__(self, filename=TEAM_RESULTS_FILE):
        self.filename = filename
    
    def save_team_results(self, team_results):
        """Save team results to pickle file"""
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(team_results, f)
            print(f"Team results saved to {self.filename}")
        except Exception as e:
            print(f"Error saving team results: {e}")
    
    def load_team_results(self):
        """Load team results from pickle file"""
        try:
            if os.path.isfile(self.filename):
                with open(self.filename, 'rb') as f:
                    team_results = pickle.load(f)
                print(f"Team results loaded from {self.filename}")
                return team_results
            else:
                print(f"No existing data file found at {self.filename}")
                return None
        except Exception as e:
            print(f"Error loading team results: {e}")
            return None
    
    def data_exists(self):
        """Check if data file exists"""
        return os.path.isfile(self.filename)
