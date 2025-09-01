#!/usr/bin/env python3
"""
Comprehensive ESPN Integration Test Script
Tests all ESPN integration methods with proper authentication handling and mock data fallback.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from platforms.service import PlatformIntegrationService
from platforms.espn import ESPNIntegration
from platforms.espn_api_integration import ESPNAPIIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESPNIntegrationTester:
    """
    Comprehensive tester for ESPN integration functionality.
    Tests both authenticated and mock data scenarios.
    """
    
    def __init__(self):
        """Initialize the ESPN integration tester."""
        self.results = {
            'credential_status': {},
            'custom_integration_tests': {},
            'api_integration_tests': {},
            'platform_service_tests': {},
            'mock_data_tests': {}
        }
        
        # Check for credentials
        self.espn_cookie = os.getenv('ESPN_COOKIE', '')
        self.espn_s2 = os.getenv('ESPN_S2', '')
        self.swid = os.getenv('SWID', '')
        self.league_id = os.getenv('ESPN_LEAGUE_ID', '83806')  # Default test league ID
        
        # Initialize integrations
        self.platform_service = None
        self.espn_integration = None
        self.espn_api_integration = None
        
    def check_credentials(self) -> None:
        """Check availability of ESPN credentials."""
        logger.info("=== Checking ESPN Credentials ===")
        
        # Check ESPN cookie format
        has_cookie = bool(self.espn_cookie)
        has_s2_in_cookie = 'espn_s2=' in self.espn_cookie if has_cookie else False
        has_swid_in_cookie = 'SWID=' in self.espn_cookie if has_cookie else False
        
        # Check individual credentials
        has_separate_s2 = bool(self.espn_s2)
        has_separate_swid = bool(self.swid)
        
        self.results['credential_status'] = {
            'espn_cookie_provided': has_cookie,
            'espn_s2_in_cookie': has_s2_in_cookie,
            'swid_in_cookie': has_swid_in_cookie,
            'separate_espn_s2': has_separate_s2,
            'separate_swid': has_separate_swid,
            'league_id': self.league_id
        }
        
        # Log credential status
        if has_cookie:
            logger.info(f"✓ ESPN_COOKIE provided (length: {len(self.espn_cookie)})")
            if has_s2_in_cookie:
                logger.info("✓ espn_s2 found in cookie")
            else:
                logger.warning("✗ espn_s2 not found in cookie")
                
            if has_swid_in_cookie:
                logger.info("✓ SWID found in cookie")
            else:
                logger.warning("✗ SWID not found in cookie")
        else:
            logger.warning("✗ ESPN_COOKIE not provided")
            
        if has_separate_s2:
            logger.info("✓ Separate ESPN_S2 provided")
        if has_separate_swid:
            logger.info("✓ Separate SWID provided")
            
        logger.info(f"League ID: {self.league_id}")
        
        # Initialize integrations based on available credentials
        if has_cookie:
            try:
                self.platform_service = PlatformIntegrationService(espn_cookie=self.espn_cookie)
                logger.info("✓ Platform service initialized with cookie")
            except Exception as e:
                logger.error(f"✗ Failed to initialize platform service: {e}")
                
            try:
                self.espn_integration = ESPNIntegration(self.espn_cookie)
                logger.info("✓ Custom ESPN integration initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize custom ESPN integration: {e}")
        
        if has_separate_s2 and has_separate_swid:
            try:
                self.espn_api_integration = ESPNAPIIntegration(
                    league_id=self.league_id,
                    year=2024,
                    espn_s2=self.espn_s2,
                    swid=self.swid
                )
                logger.info("✓ ESPN API integration initialized with separate credentials")
            except Exception as e:
                logger.error(f"✗ Failed to initialize ESPN API integration: {e}")
    
    def test_custom_espn_integration(self) -> None:
        """Test the custom ESPN integration methods."""
        logger.info("\n=== Testing Custom ESPN Integration ===")
        
        if not self.espn_integration:
            logger.warning("Custom ESPN integration not available - no credentials")
            self.results['custom_integration_tests'] = {
                'status': 'skipped',
                'reason': 'no_credentials'
            }
            return
            
        tests = {
            'roster_data': lambda: self.espn_integration.get_roster_data(2024, self.league_id),
            'transactions_data': lambda: self.espn_integration.get_transactions_data(2024, self.league_id),
            'players_data': lambda: self.espn_integration.get_players_data(2024),
            'user_data': lambda: self.espn_integration.get_user_data('1')  # Test user ID
        }
        
        results = {}
        for test_name, test_func in tests.items():
            try:
                logger.info(f"Testing {test_name}...")
                result = test_func()
                
                if result is not None:
                    logger.info(f"✓ {test_name}: Success (data type: {type(result).__name__})")
                    if isinstance(result, dict):
                        logger.info(f"  - Keys: {list(result.keys())[:5]}{'...' if len(result.keys()) > 5 else ''}")
                    elif isinstance(result, list):
                        logger.info(f"  - Items: {len(result)}")
                    results[test_name] = {'status': 'success', 'data_available': True}
                else:
                    logger.warning(f"✗ {test_name}: No data returned")
                    results[test_name] = {'status': 'no_data', 'data_available': False}
                    
            except Exception as e:
                logger.error(f"✗ {test_name}: Error - {e}")
                results[test_name] = {'status': 'error', 'error': str(e)}
                
        self.results['custom_integration_tests'] = results
    
    def test_espn_api_integration(self) -> None:
        """Test the ESPN API integration (community library) methods."""
        logger.info("\n=== Testing ESPN API Integration (Community Library) ===")
        
        if not self.espn_api_integration:
            logger.warning("ESPN API integration not available - no credentials")
            self.results['api_integration_tests'] = {
                'status': 'skipped',
                'reason': 'no_credentials'
            }
            return
            
        # Test connection first
        try:
            connection_success = self.espn_api_integration.connect()
            logger.info(f"Connection test: {'✓ Success' if connection_success else '✗ Failed'}")
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            connection_success = False
            
        if not connection_success:
            self.results['api_integration_tests'] = {
                'status': 'connection_failed',
                'connection': False
            }
            return
            
        tests = {
            'user_data': lambda: self.espn_api_integration.get_user_data('1'),  # Test team ID
            'roster_data': lambda: self.espn_api_integration.get_roster_data('1'),  # Test team ID
            'transactions': lambda: self.espn_api_integration.get_transactions('1'),  # Test team ID
            'all_players': lambda: self.espn_api_integration.get_all_players()
        }
        
        results = {'connection': True}
        for test_name, test_func in tests.items():
            try:
                logger.info(f"Testing {test_name}...")
                result = test_func()
                
                if result:
                    logger.info(f"✓ {test_name}: Success (data type: {type(result).__name__})")
                    if isinstance(result, dict):
                        logger.info(f"  - Keys: {list(result.keys())[:5]}{'...' if len(result.keys()) > 5 else ''}")
                    elif isinstance(result, list):
                        logger.info(f"  - Items: {len(result)}")
                    results[test_name] = {'status': 'success', 'data_available': True}
                else:
                    logger.warning(f"✗ {test_name}: No data returned")
                    results[test_name] = {'status': 'no_data', 'data_available': False}
                    
            except Exception as e:
                logger.error(f"✗ {test_name}: Error - {e}")
                results[test_name] = {'status': 'error', 'error': str(e)}
                
        self.results['api_integration_tests'] = results
    
    def test_platform_service(self) -> None:
        """Test the platform service integration methods."""
        logger.info("\n=== Testing Platform Service ===")
        
        if not self.platform_service:
            # Try to create platform service without credentials to test mock data
            try:
                self.platform_service = PlatformIntegrationService()
                logger.info("✓ Platform service initialized without credentials for mock data testing")
            except Exception as e:
                logger.error(f"✗ Failed to initialize platform service even without credentials: {e}")
                self.results['platform_service_tests'] = {
                    'status': 'initialization_failed',
                    'error': str(e)
                }
                return
        
        tests = {
            'league_data': lambda: self.platform_service.get_league_data('espn', self.league_id, 2024),
            'transactions_data': lambda: self.platform_service.get_transactions_data('espn', self.league_id, 2024, 1),
            'user_data': lambda: self.platform_service.get_user_data('espn', '1'),
            'roster_data': lambda: self.platform_service.get_roster_data('espn', '1')
        }
        
        results = {}
        for test_name, test_func in tests.items():
            try:
                logger.info(f"Testing {test_name}...")
                result = test_func()
                
                if result is not None:
                    logger.info(f"✓ {test_name}: Success (data type: {type(result).__name__})")
                    if isinstance(result, dict):
                        logger.info(f"  - Keys: {list(result.keys())[:5]}{'...' if len(result.keys()) > 5 else ''}")
                    elif isinstance(result, list):
                        logger.info(f"  - Items: {len(result)}")
                    results[test_name] = {'status': 'success', 'data_available': True}
                else:
                    logger.warning(f"✗ {test_name}: No data returned")
                    results[test_name] = {'status': 'no_data', 'data_available': False}
                    
            except Exception as e:
                logger.error(f"✗ {test_name}: Error - {e}")
                results[test_name] = {'status': 'error', 'error': str(e)}
                
        self.results['platform_service_tests'] = results
    
    def test_mock_data_functionality(self) -> None:
        """Test mock data functionality when credentials are not available."""
        logger.info("\n=== Testing Mock Data Functionality ===")
        
        # Test platform service without any credentials
        try:
            mock_service = PlatformIntegrationService()
            
            tests = {
                'mock_league_data': lambda: mock_service.get_league_data('espn', 'mock_league', 2024),
                'mock_roster_data': lambda: mock_service.get_roster_data('espn', 'mock_user'),
                'mock_user_data': lambda: mock_service.get_user_data('espn', 'mock_user'),
                'mock_transactions': lambda: mock_service.get_transactions_data('espn', 'mock_league', 2024, 1)
            }
            
            results = {}
            for test_name, test_func in tests.items():
                try:
                    logger.info(f"Testing {test_name}...")
                    result = test_func()
                    
                    if result is not None:
                        logger.info(f"✓ {test_name}: Mock data available (type: {type(result).__name__})")
                        results[test_name] = {'status': 'success', 'has_mock_data': True}
                    else:
                        logger.warning(f"✗ {test_name}: No mock data available")
                        results[test_name] = {'status': 'no_mock_data', 'has_mock_data': False}
                        
                except Exception as e:
                    logger.error(f"✗ {test_name}: Error - {e}")
                    results[test_name] = {'status': 'error', 'error': str(e)}
                    
            self.results['mock_data_tests'] = results
            
        except Exception as e:
            logger.error(f"✗ Failed to test mock data functionality: {e}")
            self.results['mock_data_tests'] = {
                'status': 'test_failed',
                'error': str(e)
            }
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report of all tests."""
        report = ["=" * 60]
        report.append("ESPN INTEGRATION TEST SUMMARY REPORT")
        report.append("=" * 60)
        
        # Credentials section
        report.append("\n📋 CREDENTIALS STATUS:")
        cred_status = self.results['credential_status']
        if cred_status.get('espn_cookie_provided'):
            report.append("  ✓ ESPN Cookie provided")
            if cred_status.get('espn_s2_in_cookie'):
                report.append("    ✓ espn_s2 found in cookie")
            else:
                report.append("    ✗ espn_s2 missing in cookie")
            if cred_status.get('swid_in_cookie'):
                report.append("    ✓ SWID found in cookie")
            else:
                report.append("    ✗ SWID missing in cookie")
        else:
            report.append("  ✗ No ESPN Cookie provided")
            
        if cred_status.get('separate_espn_s2'):
            report.append("  ✓ Separate ESPN_S2 provided")
        if cred_status.get('separate_swid'):
            report.append("  ✓ Separate SWID provided")
        
        # Test results sections
        sections = [
            ('🔧 CUSTOM ESPN INTEGRATION', 'custom_integration_tests'),
            ('📚 ESPN API INTEGRATION (Community Library)', 'api_integration_tests'),
            ('🚀 PLATFORM SERVICE', 'platform_service_tests'),
            ('🎭 MOCK DATA FUNCTIONALITY', 'mock_data_tests')
        ]
        
        for section_name, results_key in sections:
            report.append(f"\n{section_name}:")
            results = self.results.get(results_key, {})
            
            if not results or results.get('status') == 'skipped':
                report.append("  ⏭️  Skipped (no credentials)")
            elif results.get('status') == 'connection_failed':
                report.append("  ✗ Connection failed")
            elif results.get('status') == 'initialization_failed':
                report.append(f"  ✗ Initialization failed: {results.get('error', 'Unknown error')}")
            else:
                # Count successes and failures
                successes = sum(1 for r in results.values() 
                              if isinstance(r, dict) and r.get('status') == 'success')
                failures = sum(1 for r in results.values() 
                             if isinstance(r, dict) and r.get('status') in ['error', 'no_data'])
                
                if successes > 0:
                    report.append(f"  ✓ {successes} tests passed")
                if failures > 0:
                    report.append(f"  ✗ {failures} tests failed")
                if successes == 0 and failures == 0:
                    report.append("  ℹ️  No tests executed")
        
        # Recommendations section
        report.append(f"\n💡 RECOMMENDATIONS:")
        
        if not cred_status.get('espn_cookie_provided'):
            report.append("  1. Set ESPN_COOKIE environment variable with your ESPN session cookie")
            report.append("     - Cookie should contain both espn_s2 and SWID values")
            report.append("     - See ESPN_CREDENTIALS_GUIDE.md for detailed instructions")
        elif not cred_status.get('espn_s2_in_cookie') or not cred_status.get('swid_in_cookie'):
            report.append("  1. Update ESPN_COOKIE to include missing credentials:")
            if not cred_status.get('espn_s2_in_cookie'):
                report.append("     - Add espn_s2 value to cookie")
            if not cred_status.get('swid_in_cookie'):
                report.append("     - Add SWID value to cookie")
                
        # Check if any tests passed
        total_successes = 0
        for results in [self.results.get('custom_integration_tests', {}),
                       self.results.get('api_integration_tests', {}),
                       self.results.get('platform_service_tests', {})]:
            if isinstance(results, dict):
                total_successes += sum(1 for r in results.values() 
                                     if isinstance(r, dict) and r.get('status') == 'success')
        
        if total_successes == 0:
            report.append("  2. Consider using mock data mode for development and testing")
            report.append("  3. Verify ESPN API endpoints are still accessible (check for anti-bot measures)")
        else:
            report.append(f"  2. {total_successes} integration methods are working correctly")
            
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def save_detailed_results(self) -> None:
        """Save detailed test results to JSON file."""
        results_file = 'espn_integration_test_results.json'
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"✓ Detailed results saved to {results_file}")
        except Exception as e:
            logger.error(f"✗ Failed to save detailed results: {e}")
    
    def run_all_tests(self) -> None:
        """Run all ESPN integration tests."""
        logger.info("Starting comprehensive ESPN integration testing...")
        
        # Run all test phases
        self.check_credentials()
        self.test_custom_espn_integration()
        self.test_espn_api_integration()
        self.test_platform_service()
        self.test_mock_data_functionality()
        
        # Generate and display summary
        summary = self.generate_summary_report()
        print(summary)
        
        # Save detailed results
        self.save_detailed_results()
        
        logger.info("ESPN integration testing completed!")


def main():
    """Main function to run ESPN integration tests."""
    print("ESPN Integration Test Suite")
    print("=" * 50)
    print("This script tests all ESPN integration methods and provides")
    print("clear feedback on what's working and what needs credentials.")
    print()
    
    # Check if we should show credential help
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("USAGE:")
        print("  python test_espn_complete.py")
        print()
        print("ENVIRONMENT VARIABLES:")
        print("  ESPN_COOKIE    - Full ESPN session cookie (preferred)")
        print("  ESPN_S2        - ESPN s2 cookie value (alternative)")
        print("  SWID           - ESPN SWID cookie value (alternative)")
        print("  ESPN_LEAGUE_ID - Your ESPN league ID (optional, defaults to 83806)")
        print()
        print("For help obtaining ESPN credentials, see ESPN_CREDENTIALS_GUIDE.md")
        return
    
    # Run the tests
    tester = ESPNIntegrationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()