import os
import logging
from typing import Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    LLM Generator using Google's Gemini API for CV tailoring.
    """

    def __init__(
        self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize the LLM Generator with Google Gemini API.

        Args:
            api_key: Google API key. If not provided, will try to get from GOOGLE_API_KEY env var
            model_name: Gemini model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.model = None

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set. CV generation will be simulated.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    },
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
                logger.info(
                    f"✅ Google Gemini API initialized successfully with model: {self.model_name}"
                )
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini API: {str(e)}")
                self.model = None

    def generate_tailored_cv(self, job_description: str, current_cv: str) -> str:
        """
        Generates a tailored CV based on the job description and current CV.

        Args:
            job_description: The job description to tailor the CV for
            current_cv: The current CV content (text extracted from PDF or raw text)

        Returns:
            Tailored CV in Markdown format
        """
        if not self.model:
            logger.warning("Model not initialized. Using simulated response.")
            return self._simulate_response(job_description)

        prompt = self._create_prompt(job_description, current_cv)

        try:
            logger.info("🧠 Sending request to Google Gemini API...")
            response = self.model.generate_content(prompt)

            if response and response.text:
                logger.info("✅ Successfully generated tailored CV")
                # Clean up the response - remove markdown code blocks if present
                cleaned_text = response.text.strip()
                if cleaned_text.startswith("```markdown"):
                    cleaned_text = cleaned_text[len("```markdown") :].strip()
                elif cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:].strip()
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3].strip()
                return cleaned_text
            else:
                logger.warning("Empty response from API. Using simulated response.")
                return self._simulate_response(job_description)

        except Exception as e:
            logger.error(f"❌ Error calling Gemini API: {str(e)}")
            logger.info("Falling back to simulated response")
            return self._simulate_response(job_description)

    def _create_prompt(self, job_description: str, current_cv: str) -> str:
        """
        Creates the prompt for the LLM to generate a tailored CV.
        """
        return f"""You are an expert CV writer and ATS (Applicant Tracking System) optimization specialist with years of experience helping candidates land their dream jobs.

**JOB DESCRIPTION:**
{job_description}

**CURRENT CV CONTENT:**
{current_cv}

**YOUR TASK:**
Rewrite the current CV to be perfectly tailored for the job description above. Follow these guidelines:

1. **ATS Optimization**: Extract key skills, technologies, and keywords from the job description and naturally incorporate them throughout the CV.
2. **Relevance**: Highlight and expand on experiences and skills that directly relate to the job requirements.
3. **Truthfulness**: Maintain complete honesty - only reframe existing experiences, never fabricate.
4. **Impact**: Use action-oriented language and quantify achievements where possible.
5. **Structure**: Create a professional layout with the following sections:
   - **Header**: Name and Contact Info (keep from original)
   - **Professional Summary**: A strong 3-4 line summary tailored to the role
   - **Skills**: A categorized list of relevant technical and soft skills
   - **Experience**: Chronological work history with bullet points focusing on achievements relevant to this job
   - **Education**: Degree, University, and Year
   - **Projects** (if applicable): Relevant projects that demonstrate required skills

6. **Professional Tone**: Use professional, confident language that showcases expertise.
7. **Format**: Output in clean Markdown format. Use # for main headers and ## for subheaders. Do NOT use code blocks for the entire output.

**IMPORTANT NOTES:**
- Keep the candidate's name and contact information unchanged.
- Focus on making existing experiences more relevant to the target role.
- If the current CV lacks certain required skills, don't add them - instead emphasize transferable skills.
- Maintain the same level of seniority - don't inflate or deflate the candidate's position.

Generate the tailored CV now in Markdown format:"""

    def generate_market_insights(self, stats_data: dict) -> str:
        """
        Generate AI-powered market insights based on job statistics.

        Args:
            stats_data: Dictionary containing job market statistics

        Returns:
            Market insights as a string
        """
        if not self.model:
            logger.warning("Model not initialized. Skipping market insights.")
            return "Market insights currently unavailable. Configure GOOGLE_API_KEY to enable AI-powered analysis."

        # Create a summary of the stats for the prompt
        total_jobs = stats_data.get("total_jobs", 0)
        top_techs = [t["name"] for t in stats_data.get("technologies", [])[:3]]
        top_langs = [lang["name"] for lang in stats_data.get("languages", [])[:3]]
        top_soft = [s["name"] for s in stats_data.get("soft_skills", [])[:3]]
        top_hard = [h["name"] for h in stats_data.get("hard_skills", [])[:3]]

        prompt = f"""You are a career advisor and job market analyst. Based on the following job market data, provide actionable insights for job seekers.

**JOB MARKET DATA:**
- Total Jobs Analyzed: {total_jobs}
- Top Technologies: {', '.join(top_techs) if top_techs else 'None'}
- Top Programming Languages: {', '.join(top_langs) if top_langs else 'None'}
- Top Soft Skills: {', '.join(top_soft) if top_soft else 'None'}
- Top Technical Skills: {', '.join(top_hard) if top_hard else 'None'}

**YOUR TASK:**
Provide a concise, actionable market analysis (3-4 paragraphs) that:
1. Highlights the most important trends
2. Explains what these trends mean for job seekers
3. Offers specific, practical advice for career development
4. Identifies any emerging patterns or opportunities

Keep your response professional, encouraging, and data-driven. Write in a friendly but authoritative tone."""

        try:
            logger.info("🧠 Generating market insights with LLM...")
            response = self.model.generate_content(prompt)

            if response and response.text:
                logger.info("✅ Successfully generated market insights")
                return response.text.strip()
            else:
                logger.warning("Empty response from API for market insights")
                return "Market insights currently unavailable."

        except Exception as e:
            logger.error(f"❌ Error generating market insights: {str(e)}")
            return "Market insights currently unavailable."

    def _simulate_response(self, job_description: str) -> str:
        """
        Simulates a response when API is not available.
        """
        logger.info("⚠️ Simulating LLM response (API not configured)...")
        return f"""# TAILORED CV (SIMULATED OUTPUT)

⚠️ **Note**: This is a simulated response. Set GOOGLE_API_KEY environment variable to get AI-generated tailored CVs.

## Professional Summary
Highly motivated professional with skills matching the job requirements for: {job_description[:100]}...

## Experience
Your experience would be tailored here to match the job description.

## Skills
- Python
- Machine Learning
- Data Analysis
- API Development

## Education
Your education details would appear here.

---
**To enable real AI generation:**
1. Get a Google API key from: https://makersuite.google.com/app/apikey
2. Set it in your .env file: `GOOGLE_API_KEY=your_key_here`
3. Run the scraper again
"""
