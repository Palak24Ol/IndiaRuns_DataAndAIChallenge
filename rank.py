"""
Redrob Ranking System — Main Pipeline
Usage: python rank.py --candidates ./candidates.jsonl --out ./submission.csv
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from filters import should_keep, is_honeypot
from features import extract_all_features
from scoring import coarse_score, precision_score, calibration_score
from reasoning import generate_reasoning


def main():
    parser = argparse.ArgumentParser(description='Redrob Candidate Ranker')
    parser.add_argument('--candidates', required=True, help='Path to candidates.jsonl')
    parser.add_argument('--out', required=True, help='Path to output submission.csv')
    args = parser.parse_args()

    t_start = time.time()

    # STAGE 1: STREAM + FILTER 
    print('[Stage 1] Streaming and filtering candidates...')
    survivors = []
    total_read = 0
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_read += 1
            candidate = json.loads(line)
            if should_keep(candidate):
                survivors.append(candidate)

    t_filter = time.time()
    print(f'  Read {total_read:,} candidates in {t_filter - t_start:.1f}s')
    print(f'  Survivors after filter: {len(survivors)}')

    #  STAGE 2: HONEYPOT DETECTION 
    print('[Stage 2] Detecting honeypots...')
    for cand in survivors:
        cand['_honeypot'] = is_honeypot(cand)

    honeypot_count = sum(1 for c in survivors if c['_honeypot'])
    t_honeypot = time.time()
    print(f'  Honeypots flagged: {honeypot_count} ({t_honeypot - t_filter:.1f}s)')

    # STAGE 3: FEATURE EXTRACTION  
    print('[Stage 3] Extracting features...')
    for cand in survivors:
        cand['_features'] = extract_all_features(cand)

    t_features = time.time()
    print(f'  Features extracted for {len(survivors)} candidates ({t_features - t_honeypot:.1f}s)')

    #  STAGE 4: COARSE SCORING 
    print('[Stage 4] Computing coarse scores...')
    for cand in survivors:
        cand['_coarse'] = coarse_score(cand['_features'], cand['_honeypot'])

    survivors.sort(key=lambda c: (-c['_coarse'], c['candidate_id']))
    top_200 = survivors[:200]

    t_coarse = time.time()
    print(f'  Top 200 selected ({t_coarse - t_features:.1f}s)')
    print(f'  Score range: {top_200[0]["_coarse"]:.4f} - {top_200[-1]["_coarse"]:.4f}')

    # STAGE 5: PRECISION RERANKING 
    print('[Stage 5] Precision reranking top 200...')
    for cand in top_200:
        cand['_precision'] = precision_score(cand['_features'])

    top_200.sort(key=lambda c: (-c['_precision'], c['candidate_id']))
    top_100 = top_200[:100]

    t_precision = time.time()
    print(f'  Top 100 selected ({t_precision - t_coarse:.1f}s)')

    # STAGE 6: TOP-10 CALIBRATION 
    print('[Stage 6] Calibrating top 10...')
    top_20 = top_100[:20]
    rest_80 = top_100[20:]

    for cand in top_20:
        cand['_calibration'] = calibration_score(cand, cand['_features'])

    top_20.sort(key=lambda c: (-c['_calibration'], c['candidate_id']))
    final_100 = top_20 + rest_80

    t_calibration = time.time()
    print(f'  Calibration done ({t_calibration - t_precision:.1f}s)')

    # STAGE 7: REASONING + CSV 
    print('[Stage 7] Generating reasoning and writing CSV...')

    # Assign final scores: rank-based linear, ensuring non-increasing
    rows = []
    for rank_idx, cand in enumerate(final_100):
        rank = rank_idx + 1
        # Use rank-based score to guarantee strict non-increasing order
        score = round(1.0 - (rank - 1) * (0.99 / 99), 4)
        reason = generate_reasoning(cand, cand['_features'])
        rows.append((cand['candidate_id'], rank, score, reason))

    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for cid, rank, score, reason in rows:
            writer.writerow([cid, rank, f'{score:.4f}', reason])

    t_end = time.time()
    print(f'  CSV written to {args.out} ({t_end - t_calibration:.1f}s)')
    print(f'\n[DONE] Total runtime: {t_end - t_start:.1f}s')
    print(f'  Memory: ~{sys.getsizeof(survivors) / 1024 / 1024:.0f} MB for {len(survivors)} candidates')

    # Print top 10 for inspection
    print('\n' + '=' * 80)
    print('TOP 10 CANDIDATES')
    print('=' * 80)
    for rank_idx, cand in enumerate(final_100[:10]):
        p = cand['profile']
        s = cand['redrob_signals']
        title = p['current_title']
        company = p['current_company']
        yoe = p['years_of_experience']
        notice = s['notice_period_days']
        rr = s['recruiter_response_rate']
        saved = s['saved_by_recruiters_30d']
        gh = s['github_activity_score']
        f = cand['_features']
        print(f'\n  #{rank_idx + 1}: {cand["candidate_id"]}')
        print(f'    {title} at {company} | {yoe:.1f}y | {p["location"]} ({p["country"]})')
        print(f'    Retrieval desc={f["_retrieval_raw"]:.0f} | Production desc={f["_production_raw"]:.0f}')
        print(f'    Notice={notice}d | RR={rr:.0%} | Saved={saved} | GitHub={gh:.0f}')
        print(f'    Coarse={cand["_coarse"]:.4f} | Precision={cand["_precision"]:.4f}', end='')
        if '_calibration' in cand:
            print(f' | Calibration={cand["_calibration"]:.4f}')
        else:
            print()
        career = ' -> '.join(h['title'] for h in cand['career_history'][:3])
        print(f'    Career: {career}')


if __name__ == '__main__':
    main()
