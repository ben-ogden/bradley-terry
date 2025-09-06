"""
KRACH (Ken's Ratings for American College Hockey) calculator implementation.
"""

import numpy as np
import pandas as pd
from config import KRACH_ALPHA, KRACH_SCALING_FACTOR, KRACH_MAX_ITERATIONS, KRACH_CONVERGENCE_THRESHOLD


class KRACHCalculator:
    """Calculator for KRACH ratings using the Bradley-Terry model"""
    
    def __init__(self, alpha=KRACH_ALPHA, scaling_factor=KRACH_SCALING_FACTOR):
        self.alpha = alpha
        self.scaling_factor = scaling_factor
    
    def build_pairwise_matrix(self, team_results):
        """
        Build the pairwise comparison matrix from team results.
        
        Args:
            team_results: List of team results, where each team result is a list of games
                         Each game is [home_team, away_team, result]
        
        Returns:
            pandas.DataFrame: Pairwise comparison matrix
        """
        # Get a list of all the teams
        teams = list(
            set([game[0] for team in team_results for game in team] +
                [game[1] for team in team_results for game in team]))

        # Initialize the pairwise comparison matrix with float dtype
        pairwise_matrix = pd.DataFrame(0.0, index=teams, columns=teams, dtype=float)

        # Populate the pairwise comparison matrix
        for team in team_results:
            if not team:  # Skip empty team results
                continue
                
            home_team = team[0][0]
            for game in team:
                visitor_team = game[1]
                result = game[2]
                
                if result.startswith('W'):
                    pairwise_matrix.loc[home_team, visitor_team] += 1.0
                elif result.startswith('T'):
                    pairwise_matrix.loc[home_team, visitor_team] += 0.5

        return pairwise_matrix
    
    def solve_krach(self, pairwise_matrix):
        """
        Solve for the KRACH rating for each team using iterative method.
        
        Args:
            pairwise_matrix: pandas.DataFrame containing pairwise comparisons
        
        Returns:
            pandas.Series: KRACH ratings scaled by the scaling factor
        """
        # Initialize the P values
        P = pd.Series(np.ones(len(pairwise_matrix)), index=pairwise_matrix.index)

        # Iterate until convergence
        for i in range(KRACH_MAX_ITERATIONS):
            P_old = P.copy()
            for team in P.index:
                numerator = pairwise_matrix.loc[team].dot(P_old)
                denominator = pairwise_matrix.loc[team].dot(P_old) + pairwise_matrix[team].sum() + self.alpha
                P[team] = numerator / denominator
            
            # Check for convergence
            if abs(P - P_old).sum() < KRACH_CONVERGENCE_THRESHOLD:
                print(f"Converged after {i+1} iterations")
                break
        else:
            print(f"Did not converge after {KRACH_MAX_ITERATIONS} iterations")

        # Scale the P values
        P_scaled = P * self.scaling_factor

        return P_scaled
    
    def calculate_rankings(self, team_results):
        """
        Calculate KRACH rankings from team results.
        
        Args:
            team_results: List of team results
        
        Returns:
            pandas.Series: Sorted KRACH ratings from highest to lowest
        """
        pairwise_matrix = self.build_pairwise_matrix(team_results)
        krach_ratings = self.solve_krach(pairwise_matrix)
        return krach_ratings.sort_values(ascending=False)
