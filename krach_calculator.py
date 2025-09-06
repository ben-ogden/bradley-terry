"""
KRACH (Ken's Ratings for American College Hockey) calculator implementation.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from config import KRACH_ALPHA, KRACH_SCALING_FACTOR, KRACH_MAX_ITERATIONS, KRACH_CONVERGENCE_THRESHOLD


class KRACHCalculator:
    """
    Calculator for KRACH ratings using the Bradley-Terry model.
    
    KRACH (Ken's Ratings for American College Hockey) is a rating system
    that uses the Bradley-Terry model to rank teams based on pairwise
    comparisons from game results.
    """
    
    def __init__(self, alpha=KRACH_ALPHA, scaling_factor=KRACH_SCALING_FACTOR):
        self.alpha = alpha
        self.scaling_factor = scaling_factor
    
    def build_pairwise_matrix(self, team_results: List[List[List[str]]]) -> pd.DataFrame:
        """
        Build the pairwise comparison matrix from team results.
        
        Args:
            team_results: List of team results, where each team result is a list of games
                         Each game is [home_team, away_team, result]
        
        Returns:
            pandas.DataFrame: Pairwise comparison matrix
            
        Raises:
            ValueError: If team_results is empty or contains invalid data
        """
        if not team_results:
            raise ValueError("team_results cannot be empty")
        
        # Validate and collect all teams with error handling
        teams = set()
        for team in team_results:
            if not team:  # Skip empty team results
                continue
            for game in team:
                if not isinstance(game, list) or len(game) < 3:
                    print(f"Warning: Skipping invalid game data: {game}")
                    continue
                teams.add(game[0])  # home_team
                teams.add(game[1])  # visitor_team
        
        if not teams:
            raise ValueError("No valid team data found in team_results")
        
        teams = list(teams)
        
        # Initialize the pairwise comparison matrix with float dtype
        pairwise_matrix = pd.DataFrame(0.0, index=teams, columns=teams, dtype=float)

        # Populate the pairwise comparison matrix with validation
        for team in team_results:
            if not team:  # Skip empty team results
                continue
                
            # Validate team has at least one game
            if not isinstance(team[0], list) or len(team[0]) < 3:
                print(f"Warning: Skipping team with invalid first game: {team[0] if team else 'empty'}")
                continue
                
            home_team = team[0][0]
            
            for game in team:
                if not isinstance(game, list) or len(game) < 3:
                    print(f"Warning: Skipping invalid game data: {game}")
                    continue
                    
                visitor_team = game[1]
                result = game[2]
                
                # Validate team names exist in our matrix
                if home_team not in teams or visitor_team not in teams:
                    print(f"Warning: Skipping game with unknown teams: {home_team} vs {visitor_team}")
                    continue
                
                if result.startswith('W'):
                    pairwise_matrix.loc[home_team, visitor_team] += 1.0
                elif result.startswith('T'):
                    pairwise_matrix.loc[home_team, visitor_team] += 0.5
                elif result.startswith('L'):
                    # Losses are already handled by the other team's win
                    pass
                else:
                    print(f"Warning: Unknown game result '{result}' for {home_team} vs {visitor_team}")

        return pairwise_matrix
    
    def solve_krach(self, pairwise_matrix: pd.DataFrame) -> pd.Series:
        """
        Solve for the KRACH rating for each team using iterative method.
        
        Args:
            pairwise_matrix: pandas.DataFrame containing pairwise comparisons
        
        Returns:
            pandas.Series: KRACH ratings scaled by the scaling factor
            
        Raises:
            ValueError: If pairwise_matrix is empty or invalid
        """
        if pairwise_matrix.empty:
            raise ValueError("pairwise_matrix cannot be empty")
        
        if len(pairwise_matrix) == 0:
            raise ValueError("pairwise_matrix must contain at least one team")
        
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
    
    def calculate_rankings(self, team_results: List[List[List[str]]]) -> pd.Series:
        """
        Calculate KRACH rankings from team results.
        
        Args:
            team_results: List of team results
        
        Returns:
            pandas.Series: Sorted KRACH ratings from highest to lowest
            
        Raises:
            ValueError: If team_results is empty or contains no valid data
        """
        if not team_results:
            raise ValueError("team_results cannot be empty")
        
        try:
            pairwise_matrix = self.build_pairwise_matrix(team_results)
            krach_ratings = self.solve_krach(pairwise_matrix)
            return krach_ratings.sort_values(ascending=False)
        except Exception as e:
            raise ValueError(f"Failed to calculate KRACH rankings: {str(e)}")
