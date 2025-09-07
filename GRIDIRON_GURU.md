# The Gridiron Guru System 🏈

## Overview

The Gridiron Guru is a comprehensive AI persona system that powers the fantasy football expertise in this application. With 35 years of simulated fantasy football experience, the Gridiron Guru provides championship-level analysis and recommendations across all aspects of fantasy football.

## Features

### 🎯 Core Expertise Areas

1. **Draft Strategy**
   - Mastery of auction drafts, snake drafts, superflex formats, dynasty startups, and best ball tournaments
   - Positional value understanding and tier break identification
   - ADP analysis across all platforms (ESPN, Yahoo, Sleeper, etc.)
   - Format-specific adjustments (standard vs. PPR vs. half-PPR vs. superflex vs. 2QB)

2. **In-Season Management**
   - Expert-level waiver wire tactics and timing strategies
   - FAAB bidding optimization and budget allocation
   - Streaming strategies for defenses, kickers, and QB matchups
   - Bye week planning and roster construction

3. **Trade Evaluation**
   - Deep understanding of value consolidation vs. fragmentation
   - Buy-low/sell-high window identification
   - Trade deadline strategies and positioning
   - Dynasty vs. redraft value considerations

4. **Player Analysis**
   - Identifying emerging talent before mainstream recognition
   - Usage trend analysis and snap count interpretation
   - Target share evolution and air yards analysis
   - Rookie integration patterns and breakout indicators

5. **PPR Format Specialization**
   - Advanced knowledge of reception-heavy scoring impacts
   - Understanding how PPR fundamentally changes player valuations
   - Target monster identification and volume-based strategies

## Implementation

### System Architecture

The Gridiron Guru system is implemented through:

1. **Core Module**: `backend/src/ai/gridiron_guru_prompt.py`
   - Contains the complete persona definition
   - Provides context-aware prompt generation
   - Includes quick takes and response formatting

2. **Integration Points**:
   - **Expert Draft Agent**: Uses Gridiron Guru for draft analysis and recommendations
   - **Trade Analyzer**: Leverages Gridiron Guru for trade evaluation and negotiation strategies
   - **Recommendation Engine**: Can access Gridiron Guru for general fantasy advice

### Using the Gridiron Guru

#### Basic Usage

```python
from src.ai.gridiron_guru_prompt import GridironGuru

# Get a context-specific prompt
draft_prompt = GridironGuru.get_full_prompt(context_type="draft")
trade_prompt = GridironGuru.get_full_prompt(context_type="trade")
waiver_prompt = GridironGuru.get_full_prompt(context_type="waiver")
general_prompt = GridironGuru.get_full_prompt(context_type="general")
```

#### Contextual Prompts

```python
# Get a prompt with specific context
prompt = GridironGuru.get_context_prompt(
    query="Should I trade Cooper Kupp for Jonathan Taylor?",
    context={
        "league_settings": "12-team PPR",
        "week": 8,
        "roster": ["List of current players"],
        "standings": "3-5 record, 8th place"
    }
)
```

#### Quick Takes

```python
# Get expert quick takes on specific topics
take = GridironGuru.get_quick_take("zero_rb")
# Returns: "Zero RB works brilliantly in full PPR with deep benches. I've won 7 championships with this strategy since 2015."
```

#### Response Formatting

```python
# Format responses with metadata
formatted = GridironGuru.format_response(
    response="Your analysis here",
    confidence_level="high"  # or "medium", "low"
)
```

## Context Types

The Gridiron Guru adapts its expertise based on the context:

### Draft Context
Focuses on:
- Draft strategy and player evaluation
- Positional tiers and value-based drafting
- ADP analysis and roster construction
- Format-specific adjustments

### Trade Context
Emphasizes:
- Trade evaluation and fairness assessment
- Player value analysis
- Negotiation strategies
- Team context considerations

### Waiver Context
Prioritizes:
- In-season management strategies
- FAAB bidding recommendations
- Player pickup priorities
- Drop candidate suggestions

### General Context
Includes all knowledge domains for comprehensive analysis

## Key Principles

The Gridiron Guru operates on these core principles:

1. **Volume is king** - Opportunities matter more than efficiency
2. **Situation over talent** - Great players in bad situations struggle
3. **Follow the targets** - In PPR, targets are currency
4. **Don't chase last week's points** - Look forward, not backward
5. **Injuries create opportunity** - Monitor practice reports closely
6. **Process over results** - Good decisions don't always yield immediate results

## Communication Style

The Gridiron Guru communicates with:
- **Veteran Confidence**: 35 years of experience backing every recommendation
- **Data-Driven Analysis**: Specific statistics and historical patterns
- **Practical Wisdom**: Not just what to do, but why and when
- **Competitive Focus**: Every recommendation aimed at winning championships

## Testing

Run the integration tests to verify the Gridiron Guru system:

```bash
cd backend
source venv312/bin/activate  # or your virtual environment
python test_gridiron_guru.py
```

## API Integration

The Gridiron Guru works with both OpenAI and OpenRouter APIs:

### OpenAI Configuration
```python
from src.ai.expert_draft_agent import ExpertDraftAgent

agent = ExpertDraftAgent(openai_key="your_openai_key")
```

### OpenRouter Configuration
```python
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer

analyzer = AITradeAnalyzer(openrouter_key="your_openrouter_key")
```

## Quick Reference

### Available Topics for Quick Takes
- `zero_rb` - Zero RB draft strategy
- `handcuffs` - Handcuff strategy
- `streaming` - Streaming positions strategy
- `faab` - FAAB bidding strategy
- `trades` - Trade timing and strategy
- `rookies` - Rookie evaluation
- `te_premium` - TE premium scoring
- `dynasty` - Dynasty league strategy
- `playoffs` - Playoff preparation
- `injuries` - Injury impact assessment

### Confidence Levels
- **High**: Strong historical patterns and clear data support
- **Medium**: Good indicators but some uncertainty
- **Low**: Limited data or highly unpredictable situation

## Future Enhancements

Potential improvements to the Gridiron Guru system:

1. **Learning Module**: Ability to update knowledge based on current season trends
2. **League-Specific Adaptation**: Customize advice based on specific league history
3. **Multi-Agent Collaboration**: Different expert personas for specialized areas
4. **Real-Time Updates**: Integration with live data feeds for instant analysis
5. **Voice Interface**: Natural conversation mode for draft day decisions

## Support

For questions or issues with the Gridiron Guru system:
1. Check the test script: `backend/test_gridiron_guru.py`
2. Review the main module: `backend/src/ai/gridiron_guru_prompt.py`
3. See integration examples in `expert_draft_agent.py` and `enhanced_trade_analyzer.py`

---

*"After 35 years of fantasy football, I've seen it all. Trust the process, and championships will follow."*  
**- The Gridiron Guru**