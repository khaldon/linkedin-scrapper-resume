from collections import Counter
from pathlib import Path
import json

# ------------------------------------------------------------
# 1️⃣ Dependencies
# ------------------------------------------------------------
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# 2️⃣ Skill vocabularies
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
    "experience",
    "year",
    "work",
    "job",
    "team",
    "project",
    "company",
    "role",
    "skill",
    "ability",
    "knowledge",
    "understanding",
    "opportunity",
    "business",
    "development",
    "application",
    "system",
    "service",
    "product",
    "client",
    "user",
    "customer",
    "environment",
    "requirement",
    "solution",
    "process",
    "support",
    "design",
    "implementation",
    "management",
    "technology",
    "platform",
    "tool",
    "framework",
    "language",
    "code",
    "software",
    "engineer",
    "developer",
    "degree",
    "bachelor",
    "master",
    "computer",
    "science",
    "engineering",
    "strong",
    "good",
    "excellent",
    "proficient",
    "familiar",
    "preferred",
    "plus",
    "working",
    "using",
    "based",
    "related",
    "new",
    "best",
    "high",
    "large",
    "looking",
    "seeking",
    "join",
    "help",
    "create",
    "build",
    "maintain",
    "provide",
    "ensure",
    "make",
    "take",
    "part",
    "member",
    "candidate",
    "position",
    "location",
    "salary",
    "benefit",
    "offer",
    "apply",
    "contact",
    "email",
    "resume",
    "cv",
    "cover",
    "letter",
    "click",
    "link",
    "website",
    "http",
    "https",
    "com",
    "www",
    "org",
    "net",
    "io",
    "co",
    "uk",
    "ca",
}

# ------------------------------------------------------------
# 3️⃣ Normalisation helpers
# ------------------------------------------------------------
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

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
    """Lower‑case, lemmatise, drop stop‑words and apply synonym map."""
    doc = nlp(text.lower())
    tokens = []
    for tok in doc:
        if tok.is_stop or not tok.is_alpha:
            continue
        lemma = SYNONYMS.get(tok.text.lower())
        if not lemma:
            lemma = SYNONYMS.get(tok.lemma_, tok.lemma_)
        if lemma in COMMON_IRRELEVANT_TERMS:
            continue
        tokens.append(lemma)
    return " ".join(tokens)


# ------------------------------------------------------------
# 4️⃣ Vectorisers
# ------------------------------------------------------------
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
)

tfidf_vectoriser = TfidfVectorizer(
    lowercase=True,
    token_pattern=r"[a-zA-Z][a-zA-Z0-9\+\-\.]*",
    ngram_range=(1, 3),
)


# ------------------------------------------------------------
# 5️⃣ Visualization helpers
# ------------------------------------------------------------
def create_bar_chart(data: dict, title: str, filename: str, color_palette: list):
    """Create a colorful horizontal bar chart."""
    if not data:
        return

    items = list(data.keys())[:10]  # Top 10
    values = list(data.values())[:10]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(items, values, color=color_palette[: len(items)])

    ax.set_xlabel("Relevance Score", fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
    ax.invert_yaxis()

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        width = bar.get_width()
        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {val:.2f}",
            ha="left",
            va="center",
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()


# ------------------------------------------------------------
# 6️⃣ Main statistics function
# ------------------------------------------------------------
def generate_job_stats(
    top_n: int = 10,
    use_tfidf: bool = True,
    onet_path: str | None = None,
    output_dir: str = "data",
    use_llm: bool = False,
) -> str:
    """Generate a user‑friendly markdown report with visualizations.

    If ``use_llm`` is True, each job description is enriched via the LLM
    (e.g., summarised or expanded) before the statistical analysis.
    """

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # ---- Load job descriptions via Database (Supabase only) -------------------
    from src.database import Database
    from src.llm_generator import LLMGenerator

    db = Database()
    # Fetch all jobs (paginated)
    all_jobs = db.get_all_jobs(limit=1000, offset=0, include_description=True)
    offset = 1000
    while True:
        more_jobs = db.get_all_jobs(limit=1000, offset=offset, include_description=True)
        if not more_jobs:
            break
        all_jobs.extend(more_jobs)
        offset += 1000

    # Ensure we have unique job IDs (prevent accidental duplicates)
    seen_ids = set()
    unique_jobs = []
    for job in all_jobs:
        jid = job.get("id")
        if jid is None or jid in seen_ids:
            continue
        seen_ids.add(jid)
        unique_jobs.append(job)

    rows = [(job.get("full_description", ""),) for job in unique_jobs]
    total_jobs = len(rows)

    # Guard clauses for empty data
    if total_jobs == 0:
        empty_stats = {
            "total_jobs": 0,
            "technologies": [],
            "languages": [],
            "soft_skills": [],
            "hard_skills": [],
            "recommendations": [],
            "market_summary": "No jobs found in database. Please scrape some jobs first.",
        }
        with open(f"{output_dir}/stats_data.json", "w") as f:
            json.dump(empty_stats, f, indent=2)
        return "# 📊 Job Market Analysis Report\n\n**No jobs found in database.**\n\nPlease scrape some job postings first before generating statistics."

    # Filter out empty descriptions
    valid_rows = [r for r in rows if r[0] and len(r[0].strip()) > 0]

    if not valid_rows:
        empty_stats = {
            "total_jobs": total_jobs,
            "technologies": [],
            "languages": [],
            "soft_skills": [],
            "hard_skills": [],
            "recommendations": [],
            "market_summary": "Jobs found, but they have no descriptions to analyze.",
        }
        with open(f"{output_dir}/stats_data.json", "w") as f:
            json.dump(empty_stats, f, indent=2)
        return "# 📊 Job Market Analysis Report\n\n**No job descriptions found.**\n\nThe jobs in the database don't have descriptions to analyze."

    rows = valid_rows
    normalised = [_normalize(desc) for (desc,) in rows]

    # ---- Phrase counting ------------------------------------------------------
    X_cnt = count_vectoriser.fit_transform(normalised)
    raw_counts = Counter(
        {
            term: int(cnt)
            for term, cnt in zip(
                count_vectoriser.get_feature_names_out(), X_cnt.sum(axis=0).A1
            )
        }
    )

    # ---- TF‑IDF weighting ----------------------------------------------------
    if use_tfidf:
        X_tfidf = tfidf_vectoriser.fit_transform(normalised)
        tfidf_scores = {
            term: float(score)
            for term, score in zip(
                tfidf_vectoriser.get_feature_names_out(), X_tfidf.mean(axis=0).A1
            )
        }
        weighted = Counter(
            {
                term: raw_counts[term] * tfidf_scores.get(term, 1.0)
                for term in raw_counts
            }
        )
    else:
        weighted = raw_counts

    # ---- Split into categories ------------------------------------------------
    def _filter(counter: Counter, vocab: set) -> Counter:
        return Counter({k: v for k, v in counter.items() if k in vocab})

    def _filter_exclude(counter: Counter, vocab: set) -> Counter:
        return Counter({k: v for k, v in counter.items() if k not in vocab})

    tech_counter = _filter(weighted, VOCAB_TECH)
    lang_counter = _filter(weighted, VOCAB_LANG)
    soft_counter = _filter(weighted, VOCAB_SOFT)
    hard_counter = _filter(weighted, VOCAB_HARD)
    uncategorized_counter = _filter_exclude(weighted, VOCAB)

    # ---- Calculate job counts (unique jobs containing each term) --------------
    # This counts how many jobs contain each skill, not total occurrences
    job_counts = Counter()
    for desc in normalised:
        # Get unique terms in this job description
        terms_in_job = set()
        for term in raw_counts.keys():
            if term in desc:
                terms_in_job.add(term)
        # Increment count for each unique term
        for term in terms_in_job:
            job_counts[term] += 1

    # ---- Create visualizations ------------------------------------------------
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Color palettes (unchanged) ... (rest of function unchanged)

    # Check if we have any jobs
    if total_jobs == 0:
        return "# 📊 Job Market Analysis Report\\n\\n**No jobs found in database.**\\n\\nPlease scrape some job postings first before generating statistics."

    normalised = [_normalize(desc or "") for (desc,) in rows]

    # Check if we have any meaningful content after normalization
    if not any(normalised) or all(len(n.strip()) == 0 for n in normalised):
        return "# 📊 Job Market Analysis Report\\n\\n**No job descriptions found.**\\n\\nThe jobs in the database don't have descriptions to analyze."

    # ---- Phrase counting ------------------------------------------------------
    X_cnt = count_vectoriser.fit_transform(normalised)
    raw_counts = Counter(
        {
            term: int(cnt)
            for term, cnt in zip(
                count_vectoriser.get_feature_names_out(), X_cnt.sum(axis=0).A1
            )
        }
    )

    # ---- TF‑IDF weighting --------------------------------------------
    if use_tfidf:
        X_tfidf = tfidf_vectoriser.fit_transform(normalised)
        tfidf_scores = {
            term: float(score)
            for term, score in zip(
                tfidf_vectoriser.get_feature_names_out(), X_tfidf.mean(axis=0).A1
            )
        }
        weighted = Counter(
            {
                term: raw_counts[term] * tfidf_scores.get(term, 1.0)
                for term in raw_counts
            }
        )
    else:
        weighted = raw_counts

    # ---- Split into categories ------------------------------------------------
    def _filter(counter: Counter, vocab: set) -> Counter:
        return Counter({k: v for k, v in counter.items() if k in vocab})

    def _filter_exclude(counter: Counter, vocab: set) -> Counter:
        return Counter({k: v for k, v in counter.items() if k not in vocab})

    tech_counter = _filter(weighted, VOCAB_TECH)
    lang_counter = _filter(weighted, VOCAB_LANG)
    soft_counter = _filter(weighted, VOCAB_SOFT)
    hard_counter = _filter(weighted, VOCAB_HARD)
    uncategorized_counter = _filter_exclude(weighted, VOCAB)

    # ---- Create visualizations ------------------------------------------------
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Color palettes for different categories
    tech_colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#FFA07A",
        "#98D8C8",
        "#F7DC6F",
        "#BB8FCE",
        "#85C1E2",
        "#F8B739",
        "#52B788",
    ]
    lang_colors = [
        "#6C5CE7",
        "#A29BFE",
        "#74B9FF",
        "#0984E3",
        "#00B894",
        "#00CEC9",
        "#FDCB6E",
        "#E17055",
        "#D63031",
        "#FD79A8",
    ]
    soft_colors = [
        "#FF7675",
        "#FD79A8",
        "#FDCB6E",
        "#FFEAA7",
        "#55EFC4",
        "#81ECEC",
        "#74B9FF",
        "#A29BFE",
        "#DFE6E9",
        "#B2BEC3",
    ]
    hard_colors = [
        "#00B894",
        "#00CEC9",
        "#0984E3",
        "#6C5CE7",
        "#A29BFE",
        "#FD79A8",
        "#FF7675",
        "#E17055",
        "#FDCB6E",
        "#55EFC4",
    ]

    if tech_counter:
        create_bar_chart(
            dict(tech_counter.most_common(top_n)),
            "Most In-Demand Technologies",
            f"{output_dir}/chart_technologies.png",
            tech_colors,
        )

    if lang_counter:
        create_bar_chart(
            dict(lang_counter.most_common(top_n)),
            "Most Requested Programming Languages",
            f"{output_dir}/chart_languages.png",
            lang_colors,
        )

    if soft_counter:
        create_bar_chart(
            dict(soft_counter.most_common(top_n)),
            "Top Soft Skills",
            f"{output_dir}/chart_soft_skills.png",
            soft_colors,
        )

    if hard_counter:
        create_bar_chart(
            dict(hard_counter.most_common(top_n)),
            "Top Technical Skills",
            f"{output_dir}/chart_hard_skills.png",
            hard_colors,
        )

    # ---- Export data as JSON for HTML report ----------------------------------
    stats_data = {
        "date": pd.Timestamp.now().strftime("%B %d, %Y"),
        "total_jobs": total_jobs,
        "technologies": (
            [
                {
                    "name": tech.title(),
                    "percentage": round(
                        (job_counts.get(tech, 0) / total_jobs) * 100, 1
                    ),
                    "count": job_counts.get(tech, 0),
                }
                for tech, _ in tech_counter.most_common(10)
            ]
            if tech_counter
            else []
        ),
        "languages": (
            [
                {
                    "name": lang.title(),
                    "percentage": round(
                        (job_counts.get(lang, 0) / total_jobs) * 100, 1
                    ),
                    "count": job_counts.get(lang, 0),
                }
                for lang, _ in lang_counter.most_common(10)
            ]
            if lang_counter
            else []
        ),
        "soft_skills": (
            [
                {
                    "name": skill.title(),
                    "percentage": round(
                        (job_counts.get(skill, 0) / total_jobs) * 100, 1
                    ),
                    "count": job_counts.get(skill, 0),
                }
                for skill, _ in soft_counter.most_common(10)
            ]
            if soft_counter
            else []
        ),
        "hard_skills": (
            [
                {
                    "name": skill.title(),
                    "percentage": round(
                        (job_counts.get(skill, 0) / total_jobs) * 100, 1
                    ),
                    "count": job_counts.get(skill, 0),
                }
                for skill, _ in hard_counter.most_common(10)
            ]
            if hard_counter
            else []
        ),
        "recommendations": [],
        # Chart data for Plotly
        "chart_data": {
            "technologies": {
                "labels": (
                    [tech.title() for tech, _ in tech_counter.most_common(10)]
                    if tech_counter
                    else []
                ),
                "values": (
                    [float(score) for _, score in tech_counter.most_common(10)]
                    if tech_counter
                    else []
                ),
            },
            "languages": {
                "labels": (
                    [lang.title() for lang, _ in lang_counter.most_common(10)]
                    if lang_counter
                    else []
                ),
                "values": (
                    [float(score) for _, score in lang_counter.most_common(10)]
                    if lang_counter
                    else []
                ),
            },
            "soft_skills": {
                "labels": (
                    [skill.title() for skill, _ in soft_counter.most_common(10)]
                    if soft_counter
                    else []
                ),
                "values": (
                    [float(score) for _, score in soft_counter.most_common(10)]
                    if soft_counter
                    else []
                ),
            },
            "hard_skills": {
                "labels": (
                    [skill.title() for skill, _ in hard_counter.most_common(10)]
                    if hard_counter
                    else []
                ),
                "values": (
                    [float(score) for _, score in hard_counter.most_common(10)]
                    if hard_counter
                    else []
                ),
            },
        },
    }

    # Add recommendations
    if lang_counter:
        top_lang = lang_counter.most_common(1)[0][0]
        stats_data["recommendations"].append(
            f"Master {top_lang.title()} - It's the most requested programming language"
        )
    if tech_counter:
        top_tech_item = tech_counter.most_common(1)[0][0]
        stats_data["recommendations"].append(
            f"Learn {top_tech_item.title()} - This technology appears in the most job postings"
        )
    if soft_counter:
        top_soft_item = soft_counter.most_common(1)[0][0]
        stats_data["recommendations"].append(
            f"Highlight your {top_soft_item.title()} skills - Employers value this quality"
        )

    # ---- LLM Market Insights --------------------------------------------------
    if use_llm:
        try:
            from src.llm_generator import LLMGenerator

            llm = LLMGenerator()
            logger.info("Generating market insights with LLM...")
            market_summary = llm.generate_market_insights(stats_data)
            stats_data["market_summary"] = market_summary
        except Exception as e:
            logger.error(f"Failed to generate market insights: {e}")
            stats_data["market_summary"] = "Market insights currently unavailable."

    # Save JSON
    with open(f"{output_dir}/stats_data.json", "w") as f:
        json.dump(stats_data, f, indent=2)

    # ---- Build user-friendly markdown report ----------------------------------
    report = []
    report.append("# 📊 Job Market Analysis Report")
    report.append("")
    report.append(f"**Analysis Date:** {pd.Timestamp.now().strftime('%B %d, %Y')}")
    report.append(f"**Total Jobs Analyzed:** {total_jobs}")
    report.append("")

    # Executive Summary
    report.append("## 🎯 Executive Summary")
    report.append("")
    report.append(
        "This report analyzes job postings to identify the most in-demand skills, "
    )
    report.append(
        "technologies, and qualifications in the current job market. The insights "
    )
    report.append(
        "can help you focus your learning and highlight the right skills on your resume."
    )
    report.append("")

    # Top Technologies
    if tech_counter:
        top_tech = tech_counter.most_common(3)
        report.append("### 💻 Key Technology Trends")
        report.append("")
        report.append("The top 3 most demanded technologies are:")
        for i, (tech, score) in enumerate(top_tech, 1):
            percentage = (raw_counts.get(tech, 0) / total_jobs) * 100
            report.append(
                f"{i}. **{tech.title()}** - Mentioned in {percentage:.1f}% of jobs"
            )
        report.append("")
        report.append("![Technologies Chart](chart_technologies.png)")
        report.append("")

    # Programming Languages
    if lang_counter:
        top_langs = lang_counter.most_common(3)
        report.append("### 🔤 Programming Languages in Demand")
        report.append("")
        for i, (lang, score) in enumerate(top_langs, 1):
            percentage = (raw_counts.get(lang, 0) / total_jobs) * 100
            report.append(
                f"{i}. **{lang.title()}** - Required in {percentage:.1f}% of positions"
            )
        report.append("")
        report.append("![Languages Chart](chart_languages.png)")
        report.append("")

    # Soft Skills
    if soft_counter:
        top_soft = soft_counter.most_common(3)
        report.append("### 🤝 Essential Soft Skills")
        report.append("")
        report.append(
            "Employers are looking for candidates with these interpersonal abilities:"
        )
        for i, (skill, score) in enumerate(top_soft, 1):
            percentage = (raw_counts.get(skill, 0) / total_jobs) * 100
            report.append(
                f"{i}. **{skill.title()}** - Valued in {percentage:.1f}% of roles"
            )
        report.append("")
        report.append("![Soft Skills Chart](chart_soft_skills.png)")
        report.append("")

    # Hard Skills
    if hard_counter:
        top_hard = hard_counter.most_common(3)
        report.append("### 🎓 Technical Competencies")
        report.append("")
        for i, (skill, score) in enumerate(top_hard, 1):
            percentage = (raw_counts.get(skill, 0) / total_jobs) * 100
            report.append(
                f"{i}. **{skill.title()}** - Needed in {percentage:.1f}% of jobs"
            )
        report.append("")
        report.append("![Hard Skills Chart](chart_hard_skills.png)")
        report.append("")

    # Emerging Trends
    if uncategorized_counter:
        top_emerging = uncategorized_counter.most_common(5)
        report.append("### 🚀 Emerging Trends & Buzzwords")
        report.append("")
        report.append(
            "These terms are frequently mentioned but may represent new or evolving concepts:"
        )
        for term, score in top_emerging:
            if len(term) > 2:  # Filter out very short terms
                percentage = (raw_counts.get(term, 0) / total_jobs) * 100
                report.append(f"- **{term.title()}** ({percentage:.1f}% of jobs)")
        report.append("")

    # Actionable Recommendations
    report.append("## 💡 What This Means For You")
    report.append("")
    report.append("**To maximize your job prospects:**")
    report.append("")

    if lang_counter:
        top_lang = lang_counter.most_common(1)[0][0]
        report.append(
            f"1. **Master {top_lang.title()}** - It's the most requested programming language"
        )

    if tech_counter:
        top_tech_item = tech_counter.most_common(1)[0][0]
        report.append(
            f"2. **Learn {top_tech_item.title()}** - This technology appears in the most job postings"
        )

    if soft_counter:
        top_soft_item = soft_counter.most_common(1)[0][0]
        report.append(
            f"3. **Highlight your {top_soft_item.title()} skills** - Employers value this quality"
        )

    report.append("")
    report.append("---")
    report.append("")
    report.append(
        "*This analysis is based on job descriptions stored in your local database. "
    )
    report.append("Results may vary based on industry, location, and job level.*")

    return "\n".join(report)


# ------------------------------------------------------------
# 7️⃣ CLI entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    print(generate_job_stats(use_tfidf=True, onet_path=None))
