"""
Redrob Ranking System — Reasoning Generation
Per-candidate explanation strings for the reasoning column.
"""
from config import CORE_RETRIEVAL_SKILLS, NICE_TO_HAVE_SKILLS


def generate_reasoning(
    candidate: dict,
    features: dict[str, float],
) -> str:
    """Generate a specific, factual reasoning string for a candidate."""
    p = candidate['profile']
    s = candidate['redrob_signals']
    ch = candidate['career_history']

    title = p['current_title']
    company = p['current_company']
    industry = p['current_industry']
    yoe = p['years_of_experience']

    # Career trajectory (up to 3 roles)
    parts_traj = []
    for h in ch[:3]:
        parts_traj.append(f"{h['title']} at {h['company']}")
    trajectory = ' -> '.join(parts_traj)

    # Top relevant skills (expert/advanced only)
    relevant_skills = [
        sk for sk in candidate['skills']
        if sk['name'] in (CORE_RETRIEVAL_SKILLS | NICE_TO_HAVE_SKILLS)
        and sk['proficiency'] in ('expert', 'advanced')
    ]
    skill_names = [sk['name'] for sk in relevant_skills[:5]]
    skill_str = ', '.join(skill_names) if skill_names else 'general ML skills'

    # Behavioral
    notice = s['notice_period_days']
    rr = s['recruiter_response_rate']
    active = s['last_active_date']
    status = 'actively seeking' if s['open_to_work_flag'] else 'passive candidate'
    github = s['github_activity_score']

    # Description evidence
    retrieval_raw = features.get('_retrieval_raw', 0)
    production_raw = features.get('_production_raw', 0)

    parts = []
    parts.append(f"{title} with {yoe:.1f}y experience")
    parts.append(f"career: {trajectory}")
    if retrieval_raw > 0:
        parts.append(
            f"descriptions show retrieval/ranking work ({retrieval_raw} indicators)"
        )
    if production_raw > 0:
        parts.append(
            f"production deployment evidence ({production_raw} indicators)"
        )
    parts.append(f"core skills: {skill_str}")
    parts.append(f"{status}, {notice}d notice, {rr:.0%} response rate")
    if github >= 0:
        parts.append(f"GitHub activity: {github:.0f}/100")
    parts.append(f"last active {active}")

    return '; '.join(parts)
