#!/usr/bin/env python3
"""
Simple example: Using Google Gemini API with JSON data
This demonstrates the minimal code needed to generate a tailored CV.
"""

import json
from src.llm_generator import LLMGenerator

# Step 1: Load the scraped job data from JSON
with open("data/last_scrape.json", "r") as f:
    job_data = json.load(f)

print(f"📋 Job: {job_data['title']}")
print(f"🏢 Company: {job_data['company']}\n")

# Step 2: Load your current CV
with open("cv.md", "r") as f:
    current_cv = f.read()

# Step 3: Initialize the LLM Generator (reads GOOGLE_API_KEY from .env)
llm = LLMGenerator()

# Step 4: Generate tailored CV
print("🧠 Generating tailored CV...\n")
tailored_cv = llm.generate_tailored_cv(
    job_description=job_data['full_description'],
    current_cv=current_cv
)

# Step 5: Save the result
output_file = "data/my_tailored_cv.md"
with open(output_file, "w") as f:
    f.write(tailored_cv)

print(f"✅ Saved to: {output_file}")

# Optional: Preview the result
print("\n" + "="*60)
print("PREVIEW:")
print("="*60)
print(tailored_cv[:300])
print("...")
