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
            current_cv: The current CV content

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

**CURRENT CV:**
{current_cv}

**YOUR TASK:**
Rewrite the current CV to be perfectly tailored for the job description above. Follow these guidelines:

1. **ATS Optimization**: Extract key skills, technologies, and keywords from the job description and naturally incorporate them throughout the CV
2. **Relevance**: Highlight and expand on experiences and skills that directly relate to the job requirements
3. **Truthfulness**: Maintain complete honesty - only reframe existing experiences, never fabricate
4. **Impact**: Use action-oriented language and quantify achievements where possible
5. **Structure**: Keep the same general structure but optimize content for this specific role
6. **Professional Tone**: Use professional, confident language that showcases expertise
7. **Format**: Output in clean Markdown format with proper headers and bullet points

**IMPORTANT NOTES:**
- Keep the candidate's name and contact information unchanged
- Focus on making existing experiences more relevant to the target role
- If the current CV lacks certain required skills, don't add them - instead emphasize transferable skills
- Maintain the same level of seniority - don't inflate or deflate the candidate's position

Generate the tailored CV now in Markdown format:"""

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
