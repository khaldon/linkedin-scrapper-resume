import sqlite3
from collections import Counter
from pathlib import Path

# ------------------------------------------------------------
# 1️⃣ Dependencies (install via `uv add spacy scikit-learn pandas`)
# ------------------------------------------------------------
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd

# ------------------------------------------------------------
# 2️⃣ Skill vocabularies (you can extend these lists as needed)
# ------------------------------------------------------------
TECHNOLOGIES = [
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "tensorflow",
    "pytorch",
    "scikit‑learn",
    "huggingface",
    "transformers",
    "fastapi",
    "flask",
    "django",
    "react",
    "vue",
    "angular",
    "node.js",
    "typescript",
    "javascript",
    "html",
    "css",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "celery",
    "airflow",
    "git",
    "github",
    "gitlab",
    "ci/cd",
    "jenkins",
    "circleci",
    "travis",
    "terraform",
    "ansible",
    "linux",
    "windows",
    "macos",
    "bash",
    "powershell",
]

PROGRAMMING_LANGUAGES = [
    "python",
    "javascript",
    "java",
    "c++",
    "c#",
    "go",
    "rust",
    "typescript",
    "ruby",
    "php",
    "sql",
    "scala",
    "kotlin",
]

SOFT_SKILLS = [
    "communication",
    "teamwork",
    "leadership",
    "problem solving",
    "critical thinking",
    "adaptability",
    "time management",
    "collaboration",
    "creativity",
    "attention to detail",
]

HARD_SKILLS = [
    "machine learning",
    "data analysis",
    "software development",
    "project management",
    "cloud computing",
    "devops",
    "testing",
    "debugging",
    "algorithm design",
    "data engineering",
    "nlp",
    "natural language processing",
]

COMMON_IRRELEVANT_TERMS = {
    "experience", "year", "work", "job", "team", "project", "company", "role",
    "skill", "ability", "knowledge", "understanding", "opportunity", "business",
    "development", "application", "system", "service", "product", "client",
    "user", "customer", "environment", "requirement", "solution", "process",
    "support", "design", "implementation", "management", "technology", "platform",
    "tool", "framework", "language", "code", "software", "engineer", "developer",
    "degree", "bachelor", "master", "computer", "science", "engineering",
    "strong", "good", "excellent", "proficient", "familiar", "preferred", "plus",
    "working", "using", "based", "related", "new", "best", "high", "large",
    "looking", "seeking", "join", "help", "create", "build", "maintain",
    "provide", "ensure", "make", "take", "part", "member", "candidate",
    "position", "location", "salary", "benefit", "offer", "apply", "contact",
    "email", "resume", "cv", "cover", "letter", "click", "link", "website",
    "http", "https", "com", "www", "org", "net", "io", "co", "uk", "ca",
}

# ------------------------------------------------------------
# 3️⃣ Normalisation helpers (lemmatisation + synonym mapping)
# ------------------------------------------------------------
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# Simple synonym map – extend as you discover more aliases
SYNONYMS = {
    "aws": "amazon web services",
    "amazon web services": "aws",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "google cloud platform": "google cloud",
    "ci/cd": "ci cd",
    "ci cd": "ci/cd",
    "datum": "data",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
}

def _normalize(text: str) -> str:
    """Lower‑case, lemmatise, drop stop‑words and apply synonym map.
    Returns a space‑separated string ready for vectorisation.
    """
    doc = nlp(text.lower())
    tokens = []
    for tok in doc:
        if tok.is_stop or not tok.is_alpha:
            continue
        # Check text first (for acronyms like AWS which might lemmatize oddly)
        lemma = SYNONYMS.get(tok.text.lower())
        if not lemma:
            lemma = SYNONYMS.get(tok.lemma_, tok.lemma_)
            
        if lemma in COMMON_IRRELEVANT_TERMS:
            continue
        tokens.append(lemma)
    return " ".join(tokens)

# ------------------------------------------------------------
# 4️⃣ Vectorisers – built once and reused
# ------------------------------------------------------------
# We must normalise the vocabulary terms so they match the processed text
# e.g. "machine learning" -> "machine learning" (or "machine learn" depending on spacy)
def _prepare_vocab(term_list):
    return set(_normalize(t) for t in term_list)

VOCAB_TECH = _prepare_vocab(TECHNOLOGIES)
VOCAB_LANG = _prepare_vocab(PROGRAMMING_LANGUAGES)
VOCAB_SOFT = _prepare_vocab(SOFT_SKILLS)
VOCAB_HARD = _prepare_vocab(HARD_SKILLS)

VOCAB = VOCAB_TECH | VOCAB_LANG | VOCAB_SOFT | VOCAB_HARD

count_vectoriser = CountVectorizer(
    lowercase=True,
    token_pattern=r"[a-zA-Z][a-zA-Z0-9\+\-\.]*",
    ngram_range=(1, 3),
    # vocabulary=VOCAB,  <-- Removed to allow discovery of new terms
)

tfidf_vectoriser = TfidfVectorizer(
    lowercase=True,
    token_pattern=r"[a-zA-Z][a-zA-Z0-9\+\-\.]*",
    ngram_range=(1, 3),
    # vocabulary=VOCAB,  <-- Removed to allow discovery of new terms
)

# ------------------------------------------------------------
# 5️⃣ Main statistics function
# ------------------------------------------------------------
def generate_job_stats(
    db_path: str = "data/jobs.db",
    top_n: int = 10,
    use_tfidf: bool = True,
    onet_path: str | None = None,
) -> str:
    """Generate a markdown report of the most‑demanded tech/skills.

    Parameters
    ----------
    db_path: Path to the SQLite DB containing a `jobs` table with a `full_description` column.
    top_n: How many top items to show per category.
    use_tfidf: If True, weight raw counts by TF‑IDF (helps surface rare but important skills).
    onet_path: Optional CSV with O*NET skill demand scores (columns: `skill_name`, `demand_score`).
    """
    # ---- Load job descriptions ------------------------------------------------
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT full_description FROM jobs")
    rows = cur.fetchall()
    conn.close()

    # Normalise each description (lemmatisation + synonym replacement)
    normalised = [_normalize(desc or "") for (desc,) in rows]

    # ---- Phrase counting ------------------------------------------------------
    X_cnt = count_vectoriser.fit_transform(normalised)
    raw_counts = Counter({term: int(cnt) for term, cnt in zip(count_vectoriser.get_feature_names_out(), X_cnt.sum(axis=0).A1)})

    # ---- Optional TF‑IDF weighting --------------------------------------------
    if use_tfidf:
        X_tfidf = tfidf_vectoriser.fit_transform(normalised)
        tfidf_scores = {term: float(score) for term, score in zip(tfidf_vectoriser.get_feature_names_out(), X_tfidf.mean(axis=0).A1)}
        weighted = Counter({term: raw_counts[term] * tfidf_scores.get(term, 1.0) for term in raw_counts})
    else:
        weighted = raw_counts

    # ---- Split into categories ------------------------------------------------
    def _filter(counter: Counter, vocab: list[str]) -> Counter:
        return Counter({k: v for k, v in counter.items() if k in vocab})

    def _filter_exclude(counter: Counter, vocab: set[str]) -> Counter:
        return Counter({k: v for k, v in counter.items() if k not in vocab})

    tech_counter = _filter(weighted, VOCAB_TECH)
    lang_counter = _filter(weighted, VOCAB_LANG)
    soft_counter = _filter(weighted, VOCAB_SOFT)
    hard_counter = _filter(weighted, VOCAB_HARD)
    
    # Find terms that are NOT in our known lists but have high scores
    # This helps discover new technologies or skills we missed
    uncategorized_counter = _filter_exclude(weighted, VOCAB)

    # ---- Load O*NET enrichment (if supplied) ---------------------------------
    onet_map: dict[str, str] = {}
    if onet_path and Path(onet_path).exists():
        df = pd.read_csv(onet_path)
        onet_map = {row.skill_name.lower(): row.demand_score for _, row in df.iterrows()}

    # ---- Helper to format a section ------------------------------------------
    def _section(title: str, counter: Counter) -> list[str]:
        lines = [f"## {title}"]
        for term, val in counter.most_common(top_n):
            extra = f" (O*NET demand: {onet_map.get(term, 'N/A')})" if onet_map else ""
            lines.append(f"- {term.title()}: {val}{extra}")
        lines.append("")
        return lines

    # ---- Build markdown report -------------------------------------------------
    report = ["# Job Market Statistics (Based on scraped job descriptions)", ""]
    report.extend(_section("Most Demanded Technologies", tech_counter))
    report.extend(_section("Most Requested Programming Languages", lang_counter))
    report.extend(_section("Top Soft Skills Mentioned", soft_counter))
    report.extend(_section("Top Hard Skills Mentioned", hard_counter))
    report.extend(_section("Top Uncategorized Terms (Potential New Skills)", uncategorized_counter))
    report.append("_Statistics are derived solely from the `full_description` column of the local SQLite database._")
    return "\n".join(report)

# ------------------------------------------------------------
# 6️⃣ CLI entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    print(generate_job_stats(use_tfidf=True, onet_path=None))
