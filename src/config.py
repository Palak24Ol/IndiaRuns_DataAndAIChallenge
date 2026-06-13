"""
Redrob Ranking System — Configuration Constants
All keyword lists, company tiers, title relevance scores, skill sets, and thresholds.
"""

# === TITLE RELEVANCE SCORES (continuous, per-title) ===
TITLE_RELEVANCE = {
    'Senior AI Engineer': 1.00,
    'Lead AI Engineer': 0.98,
    'Staff Machine Learning Engineer': 0.96,
    'Senior Machine Learning Engineer': 0.95,
    'Recommendation Systems Engineer': 0.97,
    'Search Engineer': 0.96,
    'Senior Applied Scientist': 0.93,
    'Applied ML Engineer': 0.92,
    'Machine Learning Engineer': 0.88,
    'AI Engineer': 0.85,
    'Senior NLP Engineer': 0.88,
    'NLP Engineer': 0.82,
    'Senior Data Scientist': 0.75,
    'Senior Software Engineer (ML)': 0.72,
    'Data Scientist': 0.65,
    'AI Research Engineer': 0.68,
    'AI Specialist': 0.60,
    'Computer Vision Engineer': 0.45,
    'Junior ML Engineer': 0.50,
    'Senior Data Engineer': 0.35,
    'Data Engineer': 0.32,
    'Backend Engineer': 0.30,
    'Analytics Engineer': 0.30,
    'Senior Software Engineer': 0.28,
    'Software Engineer': 0.25,
    'Data Analyst': 0.25,
    'Full Stack Developer': 0.20,
    'Cloud Engineer': 0.12,
    'DevOps Engineer': 0.12,
    'QA Engineer': 0.10,
    'Java Developer': 0.10,
    '.NET Developer': 0.08,
    'Mobile Developer': 0.08,
    'Frontend Engineer': 0.08,
}

# === AI/ML CAREER TITLES (for career history matching) ===
AI_CAREER_TITLES = {
    'ML Engineer', 'Machine Learning Engineer', 'AI Engineer', 'AI Specialist',
    'Data Scientist', 'Senior Data Scientist', 'AI Research Engineer',
    'NLP Engineer', 'Senior NLP Engineer', 'Computer Vision Engineer',
    'Applied ML Engineer', 'Search Engineer', 'Recommendation Systems Engineer',
    'Senior AI Engineer', 'Lead AI Engineer', 'Senior Applied Scientist',
    'Staff Machine Learning Engineer', 'Senior Machine Learning Engineer',
    'Junior ML Engineer', 'Senior Software Engineer (ML)',
    'Senior ML Engineer \u2014 Search & Ranking',  # observed in data
}

# === TITLES THAT ALWAYS PASS THE FILTER ===
AI_TITLES_ALWAYS_KEEP = {
    'ML Engineer', 'AI Research Engineer', 'Data Scientist',
    'Senior Software Engineer (ML)', 'Computer Vision Engineer', 'AI Specialist',
    'Recommendation Systems Engineer', 'Machine Learning Engineer',
    'Applied ML Engineer', 'Search Engineer', 'AI Engineer',
    'Senior Data Scientist', 'NLP Engineer', 'Senior NLP Engineer',
    'Senior Machine Learning Engineer', 'Staff Machine Learning Engineer',
    'Senior AI Engineer', 'Senior Applied Scientist', 'Lead AI Engineer',
    'Junior ML Engineer',
}

# === ADJACENT TECH TITLES (need description gate) ===
ADJACENT_TECH_TITLES = {
    'Senior Data Engineer', 'Data Engineer', 'Backend Engineer',
    'Analytics Engineer', 'Senior Software Engineer', 'Software Engineer',
    'Data Analyst', 'Full Stack Developer',
}

# === OTHER TECH TITLES (very high bar) ===
OTHER_TECH_TITLES = {
    'Cloud Engineer', 'DevOps Engineer', 'QA Engineer',
    'Java Developer', '.NET Developer', 'Mobile Developer', 'Frontend Engineer',
}

# === RETRIEVAL TITLE KEYWORDS ===
RETRIEVAL_TITLE_KEYWORDS = ['search', 'ranking', 'retrieval', 'recommendation', 'nlp']

# === CAREER DESCRIPTION KEYWORD LISTS ===
RETRIEVAL_KEYWORDS = [
    'retrieval', 'ranking', 'ranked', 'search', 'recommendation',
    'embedding', 'vector', 'semantic search', 'information retrieval',
    'learning to rank', 'reranking', 're-ranking', 'dense retrieval',
    'hybrid search', 'bm25', 'ndcg', 'mrr', 'candidate matching',
    'relevance', 'query', 'index', 'recall@', 'precision@',
    'faiss', 'pinecone', 'weaviate', 'milvus', 'opensearch',
    'elasticsearch', 'qdrant', 'annoy', 'hnsw',
    'sentence-transformer', 'sentence transformer',
    'bi-encoder', 'cross-encoder', 'contrastive learning',
]

PRODUCTION_KEYWORDS = [
    'production', 'deployed', 'deploy', 'shipped', 'ship', 'served',
    'serving', 'real-time', 'realtime', 'latency', 'throughput',
    'scale', 'scaled', 'users', 'user-facing', 'traffic',
    'sla', 'monitoring', 'a/b test', 'ab test', 'experiment',
    'real users', 'end-to-end', 'batch', 'inference',
    'api', 'microservice', 'pipeline', 'ci/cd',
]

ML_KEYWORDS = [
    'model', 'training', 'fine-tun', 'neural', 'transformer',
    'deep learning', 'machine learning', 'nlp', 'classification',
    'prediction', 'feature engineering', 'feature store',
    'pytorch', 'tensorflow', 'scikit', 'sklearn', 'xgboost',
    'bert', 'gpt', 'llm', 'large language model',
    'tokeniz', 'attention', 'gradient', 'loss function',
    'backpropagation', 'hyperparameter', 'cross-validation',
    'evaluation', 'metric', 'benchmark', 'data science',
]

LEADERSHIP_KEYWORDS = [
    'led', 'lead', 'managed', 'mentor', 'hired', 'team of',
    'grew the team', 'architecture', 'design review', 'tech lead',
    'owned', 'drove', 'stakeholder',
]

# === ULTRA-SPECIFIC RETRIEVAL KEYWORDS (for calibration stage) ===
ULTRA_SPECIFIC_KEYWORDS = [
    'ranking system', 'retrieval system', 'search system',
    'recommendation system', 'search engine', 'search quality',
    'ranking model', 'retrieval model', 'candidate ranking',
    'learning to rank', 'semantic search', 'hybrid retrieval',
    'embedding-based retrieval', 'vector search', 'query understanding',
    'relevance model', 'matching model', 're-ranking',
    'search infrastructure', 'search platform',
    'ndcg', 'mrr', 'map@', 'recall@', 'precision@',
]

SCALE_KEYWORDS = [
    'million', 'billions', 'thousands', 'large-scale', 'high-traffic',
    'serving', 'qps', 'latency', 'p99', 'sla', 'real-time',
    '100k', '10m', 'per second', 'concurrent',
]

EVAL_KEYWORDS = [
    'ndcg', 'mrr', 'map', 'recall@', 'precision@',
    'a/b test', 'ab test', 'experiment', 'offline eval',
    'online eval', 'evaluation framework', 'benchmark',
    'metric', 'regression test',
]

# === SKILL SETS ===
CORE_RETRIEVAL_SKILLS = {
    'FAISS', 'Pinecone', 'Weaviate', 'Milvus', 'OpenSearch', 'Elasticsearch',
    'Sentence Transformers', 'Embeddings', 'Information Retrieval', 'BM25',
    'Learning to Rank', 'Vector Search', 'Recommendation Systems',
    'Qdrant', 'Haystack', 'pgvector', 'OpenCV',
}

NICE_TO_HAVE_SKILLS = {
    'Fine-tuning LLMs', 'LoRA', 'QLoRA', 'PEFT',
    'LangChain', 'LlamaIndex', 'RAG',
    'Hugging Face Transformers', 'NLP',
    'Deep Learning', 'PyTorch', 'TensorFlow',
    'Machine Learning', 'scikit-learn', 'XGBoost',
    'MLOps', 'MLflow', 'Kubeflow', 'BentoML',
    'Data Science', 'Feature Engineering',
    'Prompt Engineering', 'Diffusion Models',
    'Reinforcement Learning', 'Computer Vision',
    'CNN', 'Object Detection', 'GANs',
}

ALL_RELEVANT_SKILLS = CORE_RETRIEVAL_SKILLS | NICE_TO_HAVE_SKILLS

PYTHON_NAMES = {'Python'}

IRRELEVANT_SKILLS = {
    'Marketing', 'Sales', 'Accounting', 'SAP', 'Six Sigma',
    'Content Writing', 'SEO', 'Photoshop', 'Illustrator',
    'PowerPoint', 'Excel', 'Figma', 'InDesign',
    'Salesforce CRM', 'Project Management', 'Scrum',
    'HR', 'Recruiting', 'Event Management', 'Canva',
}

PROFICIENCY_WEIGHT = {
    'expert': 1.0,
    'advanced': 0.55,
    'intermediate': 0.20,
    'beginner': 0.05,
}

# === COMPANY TIERS ===
COMPANY_TIER = {
    # Tier S (FAANG/MAANG)
    'Apple': 1.0, 'Google': 1.0, 'Meta': 1.0, 'Amazon': 1.0,
    'Microsoft': 1.0, 'Netflix': 1.0, 'DeepMind': 1.0,
    # Tier A (top global tech)
    'Uber': 0.95, 'LinkedIn': 0.95, 'Twitter': 0.90, 'Spotify': 0.90,
    # Tier B (top Indian product companies)
    'Flipkart': 0.90, 'Swiggy': 0.88, 'Zomato': 0.88,
    'Razorpay': 0.88, 'CRED': 0.85, 'Dream11': 0.85,
    'PhonePe': 0.85, 'Meesho': 0.82, 'Ola': 0.80,
    'Paytm': 0.80, 'PolicyBazaar': 0.78, 'InMobi': 0.80,
    'Nykaa': 0.75, 'Unacademy': 0.72,
    # Tier C (Indian AI-native)
    'Sarvam AI': 0.88, 'Mad Street Den': 0.85, 'Krutrim': 0.85,
    'Haptik': 0.82, 'Observe.AI': 0.82, 'Yellow.ai': 0.82,
    'Verloop.io': 0.80, 'Wysa': 0.78, 'Saarthi.ai': 0.78,
    'Rephrase.ai': 0.78, 'Niramai': 0.75, 'Aganitha': 0.75,
    'Locobuzz': 0.72,
    # Tier D (good mid-tier)
    'Glance': 0.75, 'Vedantu': 0.72, 'upGrad': 0.72,
    "BYJU'S": 0.68, 'Zoho': 0.70,
    # Tier E (services with AI arms)
    'Genpact AI': 0.55,
    # Tier F (pure services)
    'TCS': 0.30, 'Infosys': 0.30, 'Wipro': 0.30,
    'Cognizant': 0.30, 'Accenture': 0.35, 'Capgemini': 0.30,
    'HCL': 0.30, 'Tech Mahindra': 0.30,
    # Fictional companies in dataset
    'Pied Piper': 0.50, 'Stark Industries': 0.50,
    'Wayne Enterprises': 0.50, 'Dunder Mifflin': 0.40,
    'Initech': 0.45, 'Acme Corp': 0.40, 'Globex Inc': 0.45,
    'Mindtree': 0.35, 'LTIMindtree': 0.35, 'Mphasis': 0.35,
}
DEFAULT_COMPANY_SCORE = 0.55

SERVICES_COMPANIES = {
    'TCS', 'Infosys', 'Wipro', 'Accenture', 'Cognizant', 'Capgemini',
    'HCL', 'Tech Mahindra', 'Deloitte', 'EY', 'PwC', 'KPMG',
    'McKinsey', 'BCG', 'Bain', 'IBM', 'DXC', 'LTIMindtree', 'Mphasis',
    'Mindtree',
}

# === EDUCATION ===
RELEVANT_FIELDS = {
    'Computer Science', 'Machine Learning', 'Artificial Intelligence',
    'Data Science', 'Computer Engineering', 'Information Technology',
    'Statistics', 'Mathematics', 'Electrical Engineering', 'Electronics', 'ECE',
}

ADVANCED_DEGREES = {'M.S.', 'M.Tech', 'M.E.', 'M.Sc', 'Ph.D'}

TIER_SCORE = {
    'tier_1': 1.0,
    'tier_2': 0.75,
    'tier_3': 0.45,
    'tier_4': 0.25,
    'unknown': 0.35,
}

# === LOCATION ===
INDIA_METRO_CITIES = [
    'mumbai', 'delhi', 'hyderabad', 'bangalore', 'bengaluru',
    'gurgaon', 'chennai', 'kolkata',
]

WORK_MODE_SCORE = {
    'flexible': 1.0,
    'hybrid': 0.95,
    'onsite': 0.85,
    'remote': 0.75,
}

# === REFERENCE DATE for recency calculations ===
REFERENCE_DATE_STR = '2026-05-28'
