"""
Redrob Ranking System — Feature Extraction
Extracts 42 numeric features from each candidate profile.
"""
from datetime import date
from typing import Any

from config import (
    TITLE_RELEVANCE, AI_CAREER_TITLES, RETRIEVAL_TITLE_KEYWORDS,
    AI_TITLES_ALWAYS_KEEP,
    RETRIEVAL_KEYWORDS, PRODUCTION_KEYWORDS, ML_KEYWORDS, LEADERSHIP_KEYWORDS,
    CORE_RETRIEVAL_SKILLS, NICE_TO_HAVE_SKILLS, ALL_RELEVANT_SKILLS,
    PYTHON_NAMES, PROFICIENCY_WEIGHT, IRRELEVANT_SKILLS,
    COMPANY_TIER, DEFAULT_COMPANY_SCORE, SERVICES_COMPANIES,
    RELEVANT_FIELDS, ADVANCED_DEGREES, TIER_SCORE,
    INDIA_METRO_CITIES, WORK_MODE_SCORE,
    REFERENCE_DATE_STR,
)

_REF_DATE = date.fromisoformat(REFERENCE_DATE_STR)


def _company_score(company_name: str) -> float:
    """Look up company tier score."""
    return COMPANY_TIER.get(company_name, DEFAULT_COMPANY_SCORE)


def _skill_depth(skills: list[dict], target_set: set[str]) -> float:
    """Compute depth-weighted score for skills in target_set."""
    total = 0.0
    for s in skills:
        if s['name'] in target_set:
            prof_w = PROFICIENCY_WEIGHT.get(s['proficiency'], 0.05)
            duration_w = min(s['duration_months'], 72) / 72.0
            endorsement_w = 1.0 + 0.02 * min(s['endorsements'], 30)
            total += prof_w * duration_w * endorsement_w
    return total


def _compute_description_features(career_history: list[dict]) -> dict[str, float]:
    """Compute Group B features from career descriptions."""
    all_descriptions = ' '.join(
        h['description'].lower() for h in career_history
    )

    retrieval_count = sum(1 for kw in RETRIEVAL_KEYWORDS if kw in all_descriptions)
    production_count = sum(1 for kw in PRODUCTION_KEYWORDS if kw in all_descriptions)
    ml_count = sum(1 for kw in ML_KEYWORDS if kw in all_descriptions)
    leadership_count = sum(1 for kw in LEADERSHIP_KEYWORDS if kw in all_descriptions)

    return {
        'B1': min(retrieval_count / 10.0, 1.0),
        'B2': min(production_count / 6.0, 1.0),
        'B3': min(ml_count / 8.0, 1.0),
        'B4': min(leadership_count / 4.0, 1.0),
        'B5': min(len(all_descriptions) / 2000.0, 1.0),
        'B6': 1.0 if ml_count >= 2 else 0.0,
        '_retrieval_raw': retrieval_count,
        '_production_raw': production_count,
        '_ml_raw': ml_count,
    }


def extract_all_features(candidate: dict) -> dict[str, float]:
    """Extract all 42 features for a single candidate."""
    profile = candidate['profile']
    skills = candidate['skills']
    career = candidate['career_history']
    education = candidate.get('education', [])
    signals = candidate['redrob_signals']

    f: dict[str, float] = {}

    # ── Group A: Title & Role ──
    f['A1'] = TITLE_RELEVANCE.get(profile['current_title'], 0.15)

    ai_roles = sum(1 for h in career if h['title'] in AI_CAREER_TITLES)
    f['A2'] = ai_roles / len(career)

    retrieval_roles = sum(
        1 for h in career
        if any(kw in h['title'].lower() for kw in RETRIEVAL_TITLE_KEYWORDS)
    )
    f['A3'] = retrieval_roles / len(career)

    f['A4'] = 1.0 if profile['current_title'] in AI_TITLES_ALWAYS_KEEP else 0.0

    senior_kws = ['senior', 'lead', 'staff', 'principal']
    senior_roles = sum(
        1 for h in career
        if any(kw in h['title'].lower() for kw in senior_kws)
    )
    f['A5'] = min(senior_roles / max(len(career), 1), 1.0)

    avg_tenure = sum(h['duration_months'] for h in career) / len(career)
    f['A6'] = min(avg_tenure / 30.0, 1.0)

    all_companies = set(h['company'] for h in career)
    f['A7'] = 1.0 if not all_companies.issubset(SERVICES_COMPANIES) else 0.3

    # ── Group B: Career Description Content ──
    desc_features = _compute_description_features(career)
    f.update(desc_features)

    # ── Group C: Skill Depth ──
    f['C1'] = min(_skill_depth(skills, CORE_RETRIEVAL_SKILLS) / 4.0, 1.0)
    f['C2'] = min(_skill_depth(skills, NICE_TO_HAVE_SKILLS) / 5.0, 1.0)

    python_skills = [s for s in skills if s['name'] in PYTHON_NAMES]
    if python_skills:
        ps = python_skills[0]
        f['C3'] = PROFICIENCY_WEIGHT.get(ps['proficiency'], 0.05) * min(ps['duration_months'], 72) / 72.0
    else:
        f['C3'] = 0.0

    f['C4'] = min(
        sum(1 for s in skills if s['proficiency'] == 'expert') / 8.0, 1.0
    )

    trusted = sum(
        1 for s in skills
        if s['endorsements'] > 0
        and s['duration_months'] >= 12
        and s['name'] in ALL_RELEVANT_SKILLS
    )
    f['C5'] = min(trusted / 6.0, 1.0)

    if len(skills) > 0:
        irr = sum(1 for s in skills if s['name'] in IRRELEVANT_SKILLS)
        f['C6'] = 1.0 - irr / len(skills)
    else:
        f['C6'] = 0.5

    f['C7'] = min(
        sum(1 for s in skills if s['name'] in ALL_RELEVANT_SKILLS) / 12.0, 1.0
    )

    # ── Group D: Experience ──
    yoe = profile['years_of_experience']
    if 4.5 <= yoe <= 8.5:
        f['D1'] = 1.0
    elif yoe < 4.5:
        f['D1'] = max(0.25, 1.0 - ((4.5 - yoe) / 3.0) ** 2)
    else:
        f['D1'] = max(0.30, 1.0 - ((yoe - 8.5) / 6.0) ** 2)

    ai_months = sum(
        h['duration_months'] for h in career if h['title'] in AI_CAREER_TITLES
    )
    f['D2'] = min(ai_months / 72.0, 1.0)

    f['D3'] = 1.0 if career[0]['title'] in AI_CAREER_TITLES else 0.3

    total_months = sum(h['duration_months'] for h in career)
    f['D4'] = ai_months / max(total_months, 1)

    # ── Group E: Company Quality ──
    weights_co = [2.0 if i == 0 else 1.0 for i in range(len(career))]
    scores_co = [_company_score(h['company']) for h in career]
    f['E1'] = sum(w * s for w, s in zip(weights_co, scores_co)) / sum(weights_co)
    f['E2'] = max(scores_co)
    product_roles = sum(1 for h in career if h['company'] not in SERVICES_COMPANIES)
    f['E3'] = product_roles / len(career)

    # ── Group F: Location & Logistics ──
    country = profile['country']
    location = profile['location'].lower()
    willing = signals['willing_to_relocate']

    if country == 'India':
        if 'pune' in location or 'noida' in location:
            f['F1'] = 1.0
        elif any(c in location for c in INDIA_METRO_CITIES):
            f['F1'] = 0.90
        else:
            f['F1'] = 0.80
    else:
        f['F1'] = 0.55 if willing else 0.35

    notice = signals['notice_period_days']
    if notice <= 15:
        f['F2'] = 1.0
    elif notice <= 30:
        f['F2'] = 0.95
    elif notice <= 45:
        f['F2'] = 0.85
    elif notice <= 60:
        f['F2'] = 0.75
    elif notice <= 90:
        f['F2'] = 0.55
    else:
        f['F2'] = 0.35

    f['F3'] = WORK_MODE_SCORE.get(signals['preferred_work_mode'], 0.75)
    f['F4'] = 1.0 if country == 'India' else 0.4

    # ── Group G: Education ──
    f['G1'] = 1.0 if any(
        e['field_of_study'] in RELEVANT_FIELDS for e in education
    ) else 0.5

    if education:
        f['G2'] = max(
            TIER_SCORE.get(e.get('tier', 'unknown'), 0.35) for e in education
        )
    else:
        f['G2'] = 0.3

    f['G3'] = 1.0 if any(
        e['degree'] in ADVANCED_DEGREES and e['field_of_study'] in RELEVANT_FIELDS
        for e in education
    ) else 0.5

    # ── Group H: Behavioral Signals ──
    last_active = date.fromisoformat(signals['last_active_date'])
    days_since = (_REF_DATE - last_active).days
    if days_since <= 30:
        f['H1'] = 1.0
    elif days_since <= 60:
        f['H1'] = 0.90
    elif days_since <= 90:
        f['H1'] = 0.75
    elif days_since <= 180:
        f['H1'] = 0.50
    else:
        f['H1'] = 0.25

    f['H2'] = min(signals['recruiter_response_rate'], 1.0)

    avg_hours = signals['avg_response_time_hours']
    if avg_hours <= 12:
        f['H3'] = 1.0
    elif avg_hours <= 24:
        f['H3'] = 0.90
    elif avg_hours <= 48:
        f['H3'] = 0.80
    elif avg_hours <= 96:
        f['H3'] = 0.60
    else:
        f['H3'] = 0.35

    f['H4'] = 1.0 if signals['open_to_work_flag'] else 0.6
    f['H5'] = signals['profile_completeness_score'] / 100.0

    verified_count = sum([
        signals['verified_email'],
        signals['verified_phone'],
        signals['linkedin_connected'],
    ])
    f['H6'] = verified_count / 3.0

    gh = signals['github_activity_score']
    f['H7'] = (0.3 + 0.7 * (gh / 100.0)) if gh >= 0 else 0.3

    f['H8'] = min(signals['saved_by_recruiters_30d'] / 30.0, 1.0)

    # ── Group I: Assessment Scores ──
    assessment_scores = signals['skill_assessment_scores']
    relevant_assess_skills = ALL_RELEVANT_SKILLS | PYTHON_NAMES
    relevant_scores = [
        score for skill_name, score in assessment_scores.items()
        if skill_name in relevant_assess_skills
    ]
    if relevant_scores:
        f['I1'] = sum(relevant_scores) / len(relevant_scores) / 100.0
        f['I2'] = min(sum(1 for s in relevant_scores if s >= 70) / 4.0, 1.0)
    else:
        f['I1'] = 0.0
        f['I2'] = 0.0

    return f
