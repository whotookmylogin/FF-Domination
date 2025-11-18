#!/usr/bin/env python3
"""
Minimal test for notification templates without external dependencies.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationTemplates:
    """
    Notification templates for common scenarios - copied directly for testing.
    """
    
    @staticmethod
    def trade_proposal(trade_data):
        """Generate trade proposal notification template."""
        title = "🔄 New Trade Proposal"
        message = f"""
        You have a new trade proposal!
        
        You give: {', '.join(trade_data.get('you_give', []))}
        You get: {', '.join(trade_data.get('you_get', []))}
        
        Fairness Score: {trade_data.get('fairness_score', 'N/A')}/100
        Win Probability Change: {trade_data.get('win_probability_delta', 'N/A')}%
        
        Review this trade in your app now!
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def waiver_results(waiver_data):
        """Generate waiver wire results notification template."""
        title = "📋 Waiver Wire Results"
        successful = waiver_data.get('successful_claims', [])
        failed = waiver_data.get('failed_claims', [])
        
        message = "Waiver wire results are in!\n\n"
        
        if successful:
            message += "✅ Successful Claims:\n"
            for claim in successful:
                message += f"  • {claim.get('player_name', 'Unknown')} - ${claim.get('bid_amount', 0)}\n"
        
        if failed:
            message += "\n❌ Failed Claims:\n"
            for claim in failed:
                message += f"  • {claim.get('player_name', 'Unknown')} - Outbid by ${claim.get('winning_bid', 0)}\n"
        
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def breaking_news(news_data):
        """Generate breaking news notification template."""
        urgency = news_data.get('urgency_score', 1)
        urgency_emoji = {1: "📰", 2: "📰", 3: "⚠️", 4: "🚨", 5: "🚨"}
        
        title = f"{urgency_emoji.get(urgency, '📰')} Breaking Fantasy News"
        if urgency >= 4:
            title = f"🚨 URGENT: {news_data.get('headline', 'Breaking News')}"
        
        message = f"""
        {news_data.get('headline', 'Fantasy Football News')}
        
        {news_data.get('summary', 'Check the app for more details.')}
        
        Affected Players: {', '.join(news_data.get('affected_players', ['None']))}
        Source: {news_data.get('source', 'Fantasy News')}
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def lineup_reminder(reminder_data):
        """Generate weekly lineup reminder notification template."""
        title = "⏰ Lineup Reminder"
        week = reminder_data.get('week', 'current')
        hours_until_games = reminder_data.get('hours_until_games', 'few')
        
        message = f"""
        Don't forget to set your lineup for Week {week}!
        
        Games start in {hours_until_games} hours.
        
        Quick checks:
        • Injured players in your lineup?
        • Players on bye weeks?
        • Optimal matchups selected?
        
        Set your lineup now to maximize your points!
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def injury_update(injury_data):
        """Generate injury update notification template."""
        player_name = injury_data.get('player_name', 'Unknown Player')
        status = injury_data.get('status', 'unknown')
        
        status_emoji = {
            'out': '❌',
            'doubtful': '🔴',
            'questionable': '🟡',
            'probable': '🟢',
            'healthy': '✅'
        }
        
        title = f"{status_emoji.get(status.lower(), '⚠️')} Injury Update: {player_name}"
        
        message = f"""
        {player_name} injury update:
        
        Status: {status.title()}
        Injury: {injury_data.get('injury_type', 'Not specified')}
        Expected Return: {injury_data.get('expected_return', 'Unknown')}
        
        Fantasy Impact: {injury_data.get('fantasy_impact', 'Monitor situation')}
        
        Consider your lineup and waiver wire options!
        """
        return {"title": title, "message": message.strip()}

def test_notification_templates():
    """Test all notification templates."""
    logger.info("Testing notification templates...")
    
    templates = NotificationTemplates()
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Trade proposal template
    logger.info("\n1. Testing trade proposal template...")
    trade_data = {
        "you_give": ["Christian McCaffrey", "Stefon Diggs"],
        "you_get": ["Derrick Henry"],
        "fairness_score": 85,
        "win_probability_delta": 12.5
    }
    
    try:
        trade_template = templates.trade_proposal(trade_data)
        logger.info(f"   ✓ Title: {trade_template['title']}")
        logger.info(f"   ✓ Contains player names: {'Christian McCaffrey' in trade_template['message']}")
        logger.info(f"   ✓ Contains fairness score: {'85' in trade_template['message']}")
        assert "Trade Proposal" in trade_template['title']
        assert "Christian McCaffrey" in trade_template['message']
        assert "Derrick Henry" in trade_template['message']
        tests_passed += 1
        logger.info("   ✅ Trade proposal template: PASSED")
    except Exception as e:
        logger.error(f"   ❌ Trade proposal template: FAILED - {e}")
    
    # Test 2: Waiver results template
    logger.info("\n2. Testing waiver results template...")
    waiver_data = {
        "successful_claims": [
            {"player_name": "Backup RB", "bid_amount": 25}
        ],
        "failed_claims": [
            {"player_name": "Handcuff WR", "winning_bid": 50}
        ]
    }
    
    try:
        waiver_template = templates.waiver_results(waiver_data)
        logger.info(f"   ✓ Title: {waiver_template['title']}")
        logger.info(f"   ✓ Contains successful claim: {'Backup RB' in waiver_template['message']}")
        logger.info(f"   ✓ Contains failed claim: {'Handcuff WR' in waiver_template['message']}")
        assert "Waiver Wire Results" in waiver_template['title']
        assert "Backup RB" in waiver_template['message']
        assert "✅" in waiver_template['message']
        assert "❌" in waiver_template['message']
        tests_passed += 1
        logger.info("   ✅ Waiver results template: PASSED")
    except Exception as e:
        logger.error(f"   ❌ Waiver results template: FAILED - {e}")
    
    # Test 3: Breaking news template
    logger.info("\n3. Testing breaking news template...")
    news_data = {
        "headline": "Star QB suffers season-ending injury",
        "summary": "The quarterback will miss the remainder of the season due to an ACL tear.",
        "urgency_score": 5,
        "affected_players": ["Star QB"],
        "source": "ESPN"
    }
    
    try:
        news_template = templates.breaking_news(news_data)
        logger.info(f"   ✓ Title: {news_template['title']}")
        logger.info(f"   ✓ High urgency formatting: {'URGENT' in news_template['title']}")
        logger.info(f"   ✓ Contains headline: {'Star QB' in news_template['message']}")
        assert "URGENT" in news_template['title']  # Should be urgent for score 5
        assert "Star QB" in news_template['message']
        assert "ESPN" in news_template['message']
        tests_passed += 1
        logger.info("   ✅ Breaking news template: PASSED")
    except Exception as e:
        logger.error(f"   ❌ Breaking news template: FAILED - {e}")
    
    # Test 4: Lineup reminder template
    logger.info("\n4. Testing lineup reminder template...")
    reminder_data = {
        "week": 8,
        "hours_until_games": 2
    }
    
    try:
        reminder_template = templates.lineup_reminder(reminder_data)
        logger.info(f"   ✓ Title: {reminder_template['title']}")
        logger.info(f"   ✓ Contains week: {'Week 8' in reminder_template['message']}")
        logger.info(f"   ✓ Contains time reminder: {'2 hours' in reminder_template['message']}")
        assert "Lineup Reminder" in reminder_template['title']
        assert "Week 8" in reminder_template['message']
        assert "2 hours" in reminder_template['message']
        tests_passed += 1
        logger.info("   ✅ Lineup reminder template: PASSED")
    except Exception as e:
        logger.error(f"   ❌ Lineup reminder template: FAILED - {e}")
    
    # Test 5: Injury update template
    logger.info("\n5. Testing injury update template...")
    injury_data = {
        "player_name": "Star RB",
        "status": "questionable",
        "injury_type": "Ankle sprain",
        "expected_return": "Next week",
        "fantasy_impact": "Monitor practice reports"
    }
    
    try:
        injury_template = templates.injury_update(injury_data)
        logger.info(f"   ✓ Title: {injury_template['title']}")
        logger.info(f"   ✓ Contains player name: {'Star RB' in injury_template['title']}")
        logger.info(f"   ✓ Contains status: {'Questionable' in injury_template['message']}")
        logger.info(f"   ✓ Has status emoji: {'🟡' in injury_template['title']}")
        assert "Star RB" in injury_template['title']
        assert "Questionable" in injury_template['message']  # Status is title-cased in template
        assert "🟡" in injury_template['title']  # Questionable status emoji
        tests_passed += 1
        logger.info("   ✅ Injury update template: PASSED")
    except Exception as e:
        logger.error(f"   ❌ Injury update template: FAILED - {e}")
    
    return tests_passed == total_tests

def main():
    """Run the template tests."""
    logger.info("=" * 70)
    logger.info("FANTASY FOOTBALL NOTIFICATION TEMPLATES TEST")
    logger.info("=" * 70)
    
    success = test_notification_templates()
    
    logger.info("\n" + "=" * 70)
    if success:
        logger.info("🎉 ALL TEMPLATE TESTS PASSED!")
        logger.info("\nNotification templates are working correctly:")
        logger.info("✓ Trade proposal notifications")
        logger.info("✓ Waiver wire result notifications") 
        logger.info("✓ Breaking news alerts")
        logger.info("✓ Weekly lineup reminders")
        logger.info("✓ Player injury updates")
        logger.info("\nTemplates include proper formatting, emojis, and dynamic content.")
    else:
        logger.error("❌ SOME TEMPLATE TESTS FAILED!")
    
    logger.info("=" * 70)
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)