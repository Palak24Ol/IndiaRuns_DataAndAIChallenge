"""
Redrob Ranking System — Candidate Filtering & Honeypot Detection
"""
from typing import Any
from config import (
    AI_TITLES_ALWAYS_KEEP, ADJACENT_TECH_TITLES, OTHER_TECH_TITLES,
    ALL_RELEVANT_SKILLS, ML_KEYWORDS, AI_CAREER_TITLES,
    IRRELEVANT_SKILLS, CORE_RETRIEVAL_SKILLS, NICE_TO_HAVE_SKILLS,
    PROFICIENCY_WEIGHT,
)


def should_keep(candidate: dict) -> bool:
    """Stage 1 filter: decide if candidate survives initial screening."""
    title = candidate['profile']['current_title']

    # AI/ML titles: always keep
    if title in AI_TITLES_ALWAYS_KEEP:
        return True

    # Adjacent tech: keep only with description + skill evidence
    if title in ADJACENT_TECH_TITLES:
        ai_skill_count = sum(
            1 for s in candidate['skills']
            if s['name'] in ALL_RELEVANT_SKILLS
        )
        if ai_skill_count < 2:
            return False

        all_desc = ' '.join(
            h['description'].lower() for h in candidate['career_history']
        )
        ml_count = sum(1 for kw in ML_KEYWORDS if kw in all_desc)
        if ml_count < 3:
            # Also check if past titles include AI roles
            past_ai = any(
                h['title'] in AI_CAREER_TITLES
                for h in candidate['career_history']
            )
            if not past_ai:
                return False

        return True

    # Other tech: very high bar
    if title in OTHER_TECH_TITLES:
        ai_skill_count = sum(
            1 for s in candidate['skills']
            if s['name'] in ALL_RELEVANT_SKILLS
        )
        if ai_skill_count < 4:
            return False
        all_desc = ' '.join(
            h['description'].lower() for h in candidate['career_history']
        )
        ml_count = sum(1 for kw in ML_KEYWORDS if kw in all_desc)
        if ml_count < 5:
            return False
        return True

    # Everything else (non-tech titles): DROP
    return False


def is_honeypot(candidate: dict) -> bool:
    """Stage 2: detect subtly impossible profiles (~80 in dataset).

    Key insight: skill duration_months overlap (a person practices many
    skills concurrently), so summing expert months will ALWAYS exceed
    calendar time.  We must NOT flag based on that.
    """
    profile = candidate['profile']
    skills = candidate['skills']
    career = candidate['career_history']
    signals = candidate['redrob_signals']
    yoe = profile['years_of_experience']

    expert_count = sum(1 for s in skills if s['proficiency'] == 'expert')

    # Rule 1: Salary range min > max (data corruption / impossible)
    sal = signals['expected_salary_range_inr_lpa']
    if sal['min'] > sal['max']:
        return True

    # Rule 2: Expert in contradictory domains — expert/advanced in
    #         non-tech skills AND AI skills simultaneously
    has_nontech_expert = any(
        s['proficiency'] in ('expert', 'advanced')
        and s['name'] in IRRELEVANT_SKILLS
        for s in skills
    )
    has_ai_expert = any(
        s['proficiency'] in ('expert', 'advanced')
        and s['name'] in (CORE_RETRIEVAL_SKILLS | NICE_TO_HAVE_SKILLS)
        for s in skills
    )
    if has_nontech_expert and has_ai_expert and expert_count >= 5:
        return True

    # Rule 3: Career duration MASSIVELY exceeds stated experience
    #         Allow generous overlap (parallel roles), only flag extreme cases
    total_career_months = sum(h['duration_months'] for h in career)
    if total_career_months > (yoe + 5) * 12:
        return True

    # Rule 4: Non-tech career descriptions for an AI-titled candidate
    #         If all career descriptions talk about accounting/marketing/etc
    #         but title says ML Engineer, that's suspicious
    NON_TECH_DESC_KEYWORDS = [
        'accounting', 'month-end close', 'financial reporting',
        'brand identity', 'logo design', 'typography',
        'warehouse', 'supply chain', 'fulfillment operations',
        'customer support agent', 'ticket resolution',
        'sales pipeline', 'cold calling', 'quota',
        'hr policy', 'payroll', 'recruitment drive',
        'civil engineering', 'structural design', 'autocad',
        'mechanical design', 'solidworks', 'thermodynamics',
    ]
    if profile['current_title'] in AI_TITLES_ALWAYS_KEEP:
        all_desc = ' '.join(h['description'].lower() for h in career)
        nontech_hits = sum(1 for kw in NON_TECH_DESC_KEYWORDS if kw in all_desc)
        if nontech_hits >= 3:
            return True

    return False

