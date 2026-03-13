# ARUGULA Evolutionary Loop Improvements - PROJECT PLAN

**Date**: 2026-03-13
**Author**: Sisyphus (Orchestrator)
**Status**: IN PROGRESS

## Executive Summary

This plan outlines specific improvements to the ARUGULA (Autoresearch Universal General Utility Learning Architecture) fitness functions for memU, BuildBid, and Trading. The current implementation uses basic keyword matching; this plan introduces sophisticated scoring mechanisms including TF-IDF, semantic thresholds, and multi-metric fitness evaluation.

---

## Current State Analysis

### memU Fitness (main.py:252-348)
- **Current**: Simple keyword matching for quality checks
- **Weakness**: No semantic understanding, no recall/precision metrics
- **Score**: 0-1 based on keyword presence only

### BuildBid Fitness (main.py:11-128)
- **Current**: Basic keyword checks + optional Claude Vision API
- **Weakness**: No field-specific scoring, no extraction completeness
- **Score**: Binary keyword checks + API bonus

### Trading Fitness (main.py:131-249)
- **Current**: Keyword checks + Sharpe ratio from historical trades
- **Weakness**: Single metric (Sharpe), no risk-adjusted scoring
- **Score**: 40% prompt quality + 60% data quality

---

## Improvement Roadmap

### Phase 1: memU Fitness Enhancements (HIGH PRIORITY)

#### 1.1 TF-IDF Weighting for Search Term Relevance
**File**: `main.py` - `memu_fitness()`
**Description**: Implement TF-IDF scoring to weight search terms by importance
**Implementation**:
- Add term frequency calculation for query terms
- Add inverse document frequency using memU memory corpus
- Combine with existing keyword scoring

```python
def _calculate_tfidf(query_terms, memory_corpus):
    """Calculate TF-IDF scores for query terms against memory corpus."""
    # Implementation: sklearn TfidfVectorizer or custom
    pass
```

#### 1.2 Semantic Thresholding with Embeddings
**File**: `main.py` - `memu_fitness()`
**Description**: Add semantic similarity threshold for memory retrieval
**Implementation**:
- Use sentence embeddings (OpenAI or local model)
- Set threshold (e.g., 0.7 cosine similarity)
- Score based on % of results above threshold

#### 1.3 Multi-Hop Retrieval Support
**File**: `main.py` - `memu_fitness()`
**Description**: Evaluate prompts that can chain multiple memory retrievals
**Implementation**:
- Detect multi-hop query patterns ("find X, then find related to X")
- Score based on ability to chain retrievals
- Reward context-passing between hops

#### 1.4 Memory Freshness Scoring
**File**: `main.py` - `memu_fitness()`
**Description**: Weight recent memories higher in retrieval scoring
**Implementation**:
- Add timestamp decay function (exponential)
- Boost recent entries in scoring
- Penalize stale memory retrieval

---

### Phase 2: BuildBid Fitness Enhancements (MEDIUM PRIORITY)

#### 2.1 Field-Specific Extraction Scoring
**File**: `main.py` - `buildbid_fitness()`
**Description**: Score extraction quality per field type
**Implementation**:
- Define field categories: numeric, text, date, currency
- Score each category differently
- Aggregate field scores into final fitness

#### 2.2 Confidence Calibration Metrics
**File**: `main.py` - `buildbid_fitness()`
**Description**: Measure extraction confidence vs actual accuracy
**Implementation**:
- Track extraction confidence scores
- Compare to known ground truth (test images)
- Reward calibrated confidence (not over/under confident)

#### 2.3 Image Quality Detection
**File**: `main.py` - `buildbid_fitness()`
**Description**: Factor image quality into fitness scoring
**Implementation**:
- Detect blur, resolution, noise
- Down-weight poor quality images
- Graceful degradation scoring

---

### Phase 3: Trading Fitness Enhancements (MEDIUM PRIORITY)

#### 3.1 Multi-Period Sharpe Ratio
**File**: `main.py` - `trading_fitness()`
**Description**: Calculate Sharpe across multiple timeframes
**Implementation**:
- Daily, weekly, monthly Sharpe ratios
- Combine with weighted average
- Reward consistent performance across timeframes

#### 3.2 Maximum Drawdown Component
**File**: `main.py` - `trading_fitness()`
**Description**: Add drawdown penalty to fitness
**Implementation**:
- Calculate max drawdown from trade history
- Penalize large drawdowns exponentially
- Fitness = returns - λ * max_drawdown

#### 3.3 Sortino Ratio Integration
**File**: `main.py` - `trading_fitness()`
**Description**: Use Sortino (downside risk) instead of full volatility
**Implementation**:
- Calculate downside deviation only
- Sortino = excess return / downside deviation
- Better measure for asymmetric strategies

#### 3.4 Transaction Cost Modeling
**File**: `main.py` - `trading_fitness()`
**Description**: Factor trading costs into fitness
**Implementation**:
- Define cost per trade (e.g., $0.50)
- Subtract costs from returns
- Realistic net fitness

---

### Phase 4: Infrastructure Improvements

#### 4.1 Real NATS Integration
**File**: `core/nats_client.py`
**Description**: Replace mock with real NATS publishing
**Implementation**:
- Use `nats-py` library
- Connect to Railway NATS (from current config)
- Broadcast all status updates to `arugula.*` subjects

#### 4.2 Enhanced Evolution Strategy
**File**: `core/evaluator.py`
**Description**: Improve mutation strategy beyond random
**Implementation**:
- Add crossover between good prompts
- Track mutation history
- Adaptive mutation rates

---

## Implementation Order

1. **memU TF-IDF** (Highest ROI - improves core retrieval)
2. **memU Semantic Thresholds** (Complements TF-IDF)
3. **Trading Multi-Metric** (Immediate trading benefit)
4. **BuildBid Field Scoring** (Practical improvement)
5. **NATS Integration** (Required for coordination)
6. **Multi-Hop Retrieval** (Advanced feature)
7. **Evolution Strategy** (Later optimization)

---

## Testing Strategy

- Each fitness improvement must pass existing tests
- Add unit tests for new scoring functions
- Run evolution loop with before/after comparison
- Validate NATS messages are received

---

## Success Metrics

- **memU**: Retrieval precision > 80% on test queries
- **BuildBid**: Field extraction F1 > 0.85
- **Trading**: Risk-adjusted returns improved by 20%
- **NATS**: 100% message delivery confirmation
