# 📊 Job Market Data Analysis

## Overview

The **Analyze Data** feature provides comprehensive insights into the job market by analyzing all the job descriptions you've scraped. It uses advanced natural language processing (NLP) and statistical methods to identify trends, in-demand skills, and emerging technologies.

## Features

### 🎯 What It Analyzes

1. **Technologies** - Tools, frameworks, and platforms (e.g., Docker, AWS, PyTorch)
2. **Programming Languages** - Languages employers are looking for (e.g., Python, JavaScript)
3. **Soft Skills** - Interpersonal abilities valued by employers (e.g., Communication, Leadership)
4. **Hard Skills** - Technical competencies (e.g., Machine Learning, Data Analysis)
5. **Emerging Trends** - New buzzwords and concepts not in predefined lists

### 📈 Advanced Statistical Methods

The analysis uses several sophisticated techniques for accuracy:

- **Lemmatization** - Normalizes words to their base form (e.g., "running" → "run")
- **Synonym Mapping** - Recognizes different names for the same thing (e.g., "AWS" = "Amazon Web Services")
- **N-gram Analysis** - Detects multi-word phrases (e.g., "machine learning", "problem solving")
- **TF-IDF Weighting** - Identifies truly important skills by balancing frequency with uniqueness
- **Noise Filtering** - Removes common irrelevant terms to focus on meaningful skills

### 📊 Output Formats

The analysis generates **two types of reports**:

1. **Markdown Report** (`data/job_market_report.md`)
   - Plain text format
   - Easy to read and share
   - Contains all statistics and recommendations

2. **Interactive HTML Report** (`view_report.html`)
   - Beautiful, colorful visualizations
   - Bar charts for each category
   - Automatically opens in your browser
   - User-friendly for non-technical people

### 🎨 Visualizations

Each category gets its own **colorful bar chart**:

- **Technologies Chart** - Shows the most demanded tools and platforms
- **Languages Chart** - Displays programming language requirements
- **Soft Skills Chart** - Highlights valued interpersonal abilities
- **Hard Skills Chart** - Reveals technical competencies in demand

Charts are saved as PNG images in the `data/` directory.

## How to Use

### From the Main Menu

1. Run the main script:
   ```bash
   uv run python main.py
   ```

2. After scraping a job, select **Option 2: Analyze Data**

3. The report will:
   - Display in your terminal
   - Save to `data/job_market_report.md`
   - Generate colorful charts
   - Open an interactive HTML report in your browser

### Standalone Usage

You can also run the analysis directly:

```bash
uv run python src/stats_generator.py
```

This will analyze all jobs in your database and print the report to the console.

## Understanding the Results

### Percentages

The percentages show how often a skill appears across all analyzed jobs:

- **100%** - Appears in every job posting
- **50%** - Appears in half of the job postings
- **>100%** - Appears multiple times in some job postings (very important!)

### Relevance Scores

The raw scores combine:
- **Frequency** - How often the term appears
- **Importance** - How unique/significant it is (via TF-IDF)

Higher scores = more important to focus on.

### Recommendations

The "What This Means For You" section provides **actionable advice**:

1. Which programming language to master
2. Which technology to learn
3. Which soft skills to highlight on your resume

## Example Output

```markdown
# 📊 Job Market Analysis Report

**Analysis Date:** November 20, 2025
**Total Jobs Analyzed:** 3

## 🎯 Executive Summary

This report analyzes job postings to identify the most in-demand skills...

### 💻 Key Technology Trends

The top 3 most demanded technologies are:
1. **PyTorch** - Mentioned in 100.0% of jobs
2. **TensorFlow** - Mentioned in 100.0% of jobs
3. **Amazon Web Services** - Mentioned in 66.7% of jobs

![Technologies Chart](chart_technologies.png)

### 🔤 Programming Languages in Demand

1. **Python** - Required in 133.3% of positions
2. **SQL** - Required in 66.7% of positions

...
```

## Technical Details

### Dependencies

- **spacy** - Natural language processing
- **scikit-learn** - Machine learning algorithms (TF-IDF, vectorization)
- **pandas** - Data manipulation
- **matplotlib** - Chart generation

### Database Requirements

The analysis reads from `data/jobs.db` and expects:
- A `jobs` table
- A `full_description` column containing job descriptions

### Customization

You can extend the skill vocabularies in `src/stats_generator.py`:

```python
TECHNOLOGIES = [
    "docker", "kubernetes", "aws", ...
    # Add your own technologies here
]

PROGRAMMING_LANGUAGES = [
    "python", "javascript", ...
    # Add more languages
]
```

## Tips for Better Results

1. **Scrape More Jobs** - The more data, the more accurate the insights
2. **Focus on Your Field** - Scrape jobs in your target industry for relevant insights
3. **Regular Updates** - Re-run analysis as you add more jobs to track trends
4. **Compare Over Time** - Save reports periodically to see how the market evolves

## Troubleshooting

### Missing Dependencies

If you see an error about missing packages:

```bash
uv add spacy scikit-learn pandas matplotlib
uv run python -m spacy download en_core_web_sm
```

### No Data

If the analysis shows no results:
- Make sure you've scraped at least one job
- Check that `data/jobs.db` exists and contains data

### Charts Not Displaying

If charts don't appear in the HTML report:
- Ensure the `data/` directory contains the PNG files
- Check that the HTML file can access the `data/` directory

## Privacy Note

All analysis is performed **locally** on your machine. No data is sent to external servers. The reports contain aggregated statistics only, not individual job descriptions.

---

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub.
