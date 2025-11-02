#!/usr/bin/env python3
"""
Test majority voting logic directly
"""

def test_majority_voting():
    """Test the majority voting logic"""
    
    print("=== Testing Majority Voting Logic ===")
    
    test_cases = [
        ([0, 0], "should be 0"),
        ([0, 1], "should be 1"),  
        ([1, 0], "should be 1"),
        ([1, 1], "should be 1")
    ]
    
    for votes, expected in test_cases:
        # Current logic 
        current_result = 1 if sum(votes) >= len(votes) / 2 else 0
        
        # Old logic
        old_result = 1 if sum(votes) > len(votes) // 2 else 0
        
        print(f"Votes {votes}: current={current_result}, old={old_result}, {expected}")
    
    print("\nAnalysis:")
    print("- [0,0]: sum=0, len/2=1.0, 0>=1.0=False -> 0 ✅")
    print("- [0,1]: sum=1, len/2=1.0, 1>=1.0=True -> 1 ✅")
    print("- [1,0]: sum=1, len/2=1.0, 1>=1.0=True -> 1 ✅") 
    print("- [1,1]: sum=2, len/2=1.0, 2>=1.0=True -> 1 ✅")

if __name__ == "__main__":
    test_majority_voting()