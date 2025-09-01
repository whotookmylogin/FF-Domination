#!/usr/bin/env python3
"""
Test ESPN mock data functionality without external dependencies.
This test verifies the mock data system works independently.
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mock_data_provider():
    """Test the ESPN mock data provider directly."""
    try:
        from platforms.espn_mock_data import ESPNMockDataProvider
        
        logger.info("=== Testing ESPN Mock Data Provider ===")
        
        provider = ESPNMockDataProvider()
        
        # Test roster data
        logger.info("Testing mock roster data...")
        roster_data = provider.get_mock_roster_data(2024, "test_league")
        assert isinstance(roster_data, dict), "Roster data should be a dictionary"
        assert "status" in roster_data, "Roster data should have status"
        assert "teams" in roster_data, "Roster data should have teams"
        assert len(roster_data["teams"]) >= 10, "Should have at least 10 teams"
        logger.info(f"✓ Mock roster data: {len(roster_data['teams'])} teams generated")
        
        # Test transactions data
        logger.info("Testing mock transactions data...")
        transactions_data = provider.get_mock_transactions_data(2024, "test_league")
        assert isinstance(transactions_data, dict), "Transactions data should be a dictionary"
        assert "status" in transactions_data, "Transactions data should have status"
        assert "transactions" in transactions_data, "Transactions data should have transactions"
        logger.info(f"✓ Mock transactions data: {len(transactions_data['transactions'])} transactions generated")
        
        # Test players data
        logger.info("Testing mock players data...")
        players_data = provider.get_mock_players_data(2024)
        assert isinstance(players_data, dict), "Players data should be a dictionary"
        assert "status" in players_data, "Players data should have status"
        assert "players" in players_data, "Players data should have players"
        logger.info(f"✓ Mock players data: {len(players_data['players'])} players generated")
        
        # Test user data
        logger.info("Testing mock user data...")
        user_data = provider.get_mock_user_data("test_user")
        assert isinstance(user_data, dict), "User data should be a dictionary"
        assert "status" in user_data, "User data should have status"
        assert "user" in user_data, "User data should have user"
        logger.info("✓ Mock user data generated successfully")
        
        # Test API format data
        logger.info("Testing mock API format data...")
        api_roster = provider.get_mock_api_roster_data("test_user")
        assert isinstance(api_roster, list), "API roster data should be a list"
        assert len(api_roster) > 0, "API roster should have players"
        logger.info(f"✓ Mock API roster data: {len(api_roster)} players generated")
        
        api_user = provider.get_mock_api_user_data("test_user")
        assert isinstance(api_user, dict), "API user data should be a dictionary"
        assert "user_id" in api_user, "API user data should have user_id"
        logger.info("✓ Mock API user data generated successfully")
        
        api_transactions = provider.get_mock_api_transactions("test_user")
        assert isinstance(api_transactions, list), "API transactions should be a list"
        logger.info(f"✓ Mock API transactions data: {len(api_transactions)} transactions generated")
        
        logger.info("=== All Mock Data Tests Passed! ===")
        return True
        
    except Exception as e:
        logger.error(f"Mock data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_structure():
    """Test that integration classes can be imported and initialized without credentials."""
    logger.info("=== Testing Integration Structure ===")
    
    # Test mock-only ESPN integration
    try:
        # This should work without external dependencies since we're not making HTTP requests
        logger.info("Testing ESPN integration structure...")
        
        # Import test - this will show if our imports are structured correctly
        from platforms.espn_mock_data import ESPNMockDataProvider
        from platforms import espn
        
        logger.info("✓ ESPN integration imports successful")
        
        # Test ESPN integration initialization without cookie (should use mock data)
        espn_integration = espn.ESPNIntegration(cookie=None)
        assert espn_integration.use_mock_data == True, "Should be in mock data mode"
        logger.info("✓ ESPN integration initializes in mock data mode")
        
        return True
        
    except ImportError as e:
        logger.error(f"Import error - missing dependencies: {e}")
        return False
    except Exception as e:
        logger.error(f"Integration structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    logger.info("Starting ESPN Mock Data Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Mock Data Provider", test_mock_data_provider),
        ("Integration Structure", test_integration_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if test_func():
                logger.info(f"✓ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name}: ERROR - {e}")
    
    logger.info(f"\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Mock data system is working correctly.")
        logger.info("The app can run without ESPN credentials using realistic mock data.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)