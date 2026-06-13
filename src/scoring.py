"""
Redrob Ranking System — Scoring Functions
Three-stage scoring: coarse → precision rerank → top-10 calibration.
"""
from config import ULTRA_SPECIFIC_KEYWORDS, SCALE_KEYWORDS, EVAL_KEYWORDS


def behavioral_multiplier(features: dict[str, float]) -> float:
    """Compute multiplicative behavioral modifier in [0.50, 1.15]."""
    raw = (
        0.20 * features['H1'] +   # recency
        0.20 * features['H2'] +   # recruiter_response_rate
        0.05 * features['H3'] +   # response_time
        0.10 * features['H4'] +   # open_to_work
        0.05 * features['H5'] +   # profile_completeness
        0.05 * features['H6'] +   # verification
        0.10 * features['H7'] +   # github
        0.15 * features['H8'] +   # saved_by_recruiters
        0.05 * features['I1'] +   # assessment_avg
        0.05 * features['I2']     # high_assessment_count
    )
    return 0.50 + raw * 0.65


def coarse_score(features: dict[str, float], honeypot: bool) -> float:
    """Stage 4: coarse scoring over all ~1,500 survivors."""
    if honeypot:
        return 0.0

    score = (
        0.15 * features['A1'] +   # title_relevance
        0.08 * features['A2'] +   # career_title_ai_ratio
        0.05 * features['A3'] +   # career_title_retrieval_ratio
        0.02 * features['A4'] +   # current_role_is_ai

        0.15 * features['B1'] +   # retrieval_keyword_density
        0.08 * features['B2'] +   # production_keyword_density
        0.07 * features['B3'] +   # ml_keyword_density

        0.08 * features['C1'] +   # core_retrieval_skill_depth
        0.04 * features['C2'] +   # nice_to_have_skill_depth
        0.02 * features['C3'] +   # python_depth
        0.03 * features['C4'] +   # expert_skill_count

        0.05 * features['D1'] +   # yoe_fit
        0.03 * features['D2'] +   # ai_career_months
        0.02 * features['D3'] +   # recent_ai_role

        0.04 * features['E1'] +   # weighted_company_score
        0.02 * features['E2'] +   # best_company_score
        0.01 * features['E3'] +   # product_company_ratio
        0.01 * features['A7'] +   # consulting_only_penalty

        0.02 * features['F1'] +   # location_score
        0.01 * features['F4'] +   # india_based

        0.01 * features['G1'] +   # education_relevance
        0.01 * features['G2']     # institution_tier
    )
    # Weights sum to 1.00

    bm = behavioral_multiplier(features)
    return score * bm


def precision_score(features: dict[str, float]) -> float:
    """Stage 5: precision reranking for top 200."""
    raw = (
        0.25 * features['B1'] +    # retrieval_keyword_density
        0.15 * features['B2'] +    # production_keyword_density
        0.10 * features['B3'] +    # ml_keyword_density
        0.10 * features['E1'] +    # weighted_company_score
        0.08 * features['C1'] +    # core_retrieval_skill_depth
        0.07 * features['A1'] +    # title_relevance
        0.05 * features['A3'] +    # career_title_retrieval_ratio
        0.05 * features['A2'] +    # career_title_ai_ratio
        0.03 * features['D1'] +    # yoe_fit
        0.02 * features['D4'] +    # career_depth
        0.02 * features['A6'] +    # avg_tenure_months
        0.02 * features['F1'] +    # location_score
        0.02 * features['F2'] +    # notice_period_score
        0.02 * features['H8'] +    # saved_by_recruiters
        0.02 * features['B4']      # leadership_keyword_density
    )
    # Weights sum to 1.00

    bm = behavioral_multiplier(features)
    return raw * bm


def calibration_score(candidate: dict, features: dict[str, float]) -> float:
    """Stage 6: top-10 calibration for top 20 candidates."""
    descs = ' '.join(
        h['description'].lower() for h in candidate['career_history']
    )

    # 1. Retrieval specificity
    specificity = sum(1 for kw in ULTRA_SPECIFIC_KEYWORDS if kw in descs)
    spec_score = min(specificity / 5.0, 1.0)

    # 2. Scale evidence
    scale_count = sum(1 for kw in SCALE_KEYWORDS if kw in descs)
    scale_score = min(scale_count / 3.0, 1.0)

    # 3. Evaluation framework evidence
    eval_count = sum(1 for kw in EVAL_KEYWORDS if kw in descs)
    eval_score = min(eval_count / 3.0, 1.0)

    # 4. Availability composite
    avail = (
        features['F2'] * 0.35 +
        features['H4'] * 0.25 +
        features['H1'] * 0.25 +
        features['H2'] * 0.15
    )

    # 5. Company prestige
    company = features['E2']

    # 6. Market validation
    market = features['H8']

    return (
        0.30 * spec_score +
        0.15 * scale_score +
        0.10 * eval_score +
        0.15 * avail +
        0.15 * company +
        0.10 * market +
        0.05 * features['H7']
    )
