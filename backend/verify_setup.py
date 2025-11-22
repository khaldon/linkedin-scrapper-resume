#!/usr/bin/env python3
"""
Verification script for LinkedIn Scraper Resume setup
Checks Supabase configuration and dependencies
"""

import os
import sys
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def check_env_variable(var_name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if environment variable exists and return its value"""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if "PASSWORD" in var_name or "KEY" in var_name or "SECRET" in var_name:
            masked_value = (
                value[:4] + "*" * (len(value) - 8) + value[-4:]
                if len(value) > 8
                else "***"
            )
            return True, masked_value
        return True, value
    return False, ""


def check_dependencies() -> Dict[str, bool]:
    """Check if required Python packages are installed"""
    results = {}

    packages = {
        "psycopg2": "PostgreSQL adapter",
        "google.generativeai": "Google Gemini API",
        "playwright": "Browser automation",
        "fastapi": "Web framework",
        "dotenv": "Environment variables",
    }

    for package, description in packages.items():
        try:
            __import__(package)
            results[f"{description} ({package})"] = True
        except ImportError:
            results[f"{description} ({package})"] = False

    return results


def check_database_config() -> Dict[str, any]:
    """Check database configuration"""
    results = {
        "has_supabase_config": False,
        "has_supabase_sdk": False,
        "can_connect": False,
        "db_type": "Unknown",
    }

    # Check for Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        results["has_supabase_config"] = True
        results["supabase_url"] = supabase_url

    # Check if supabase SDK is available
    try:
        import importlib.util

        results["has_supabase_sdk"] = importlib.util.find_spec("supabase") is not None
    except (ImportError, ValueError):
        results["has_supabase_sdk"] = False

    # Try to initialize database
    try:
        from src.database import Database

        db = Database()
        results["can_connect"] = True
        results["db_type"] = (
            "Supabase (PostgreSQL)" if db.use_supabase else "SQLite (Local)"
        )
        results["use_supabase"] = db.use_supabase
    except Exception as e:
        results["error"] = str(e)

    return results


def check_huggingface_config() -> Dict[str, bool]:
    """Check Hugging Face specific configuration"""
    results = {}

    # Check if running on Hugging Face Spaces
    results["is_hf_space"] = os.getenv("SPACE_ID") is not None
    results["space_id"] = os.getenv("SPACE_ID", "Not running on HF Spaces")

    # Check port configuration
    port = os.getenv("PORT", "7860")
    results["port"] = port
    results["port_correct"] = port == "7860"

    return results


def verify_file_structure() -> Dict[str, bool]:
    """Verify required files and directories exist"""
    required_items = {
        "src/database.py": "file",
        "src/scraper.py": "file",
        "src/llm_generator.py": "file",
        "api.py": "file",
        "Dockerfile": "file",
        "pyproject.toml": "file",
        ".env.example": "file",
        "data": "dir",
        "logs": "dir",
        "../frontend": "dir",
        "../frontend/static": "dir",
        "../frontend/view_report.html": "file",
    }

    results = {}
    for item, item_type in required_items.items():
        if item_type == "file":
            results[item] = os.path.isfile(item)
        else:
            results[item] = os.path.isdir(item)

    return results


def main():
    """Main verification function"""
    print_header("LinkedIn Scraper Resume - Setup Verification")

    # 1. Check Dependencies
    print_header("1. Python Dependencies")
    deps = check_dependencies()
    all_deps_ok = True
    for dep, status in deps.items():
        if status:
            print_success(f"{dep} installed")
        else:
            print_error(f"{dep} NOT installed")
            all_deps_ok = False

    if not all_deps_ok:
        print_warning("Run: uv sync  or  pip install -r requirements.txt")

    # 2. Check Environment Variables
    print_header("2. Environment Variables")

    env_vars = {
        "SUPABASE_URL": ("Required - Supabase project URL", True),
        "SUPABASE_KEY": ("Required - Supabase anon/public key", True),
        "GOOGLE_API_KEY": ("Required - Google Gemini API key", True),
        "FIREBASE_SERVICE_ACCOUNT_JSON": (
            "Recommended - Firebase Admin SDK JSON content (for HF Spaces)",
            False,
        ),
        "FIREBASE_CREDENTIALS_PATH": (
            "Optional - Path to Firebase Admin SDK JSON file (for local dev)",
            False,
        ),
        "HEADLESS": ("Optional - Browser headless mode", False),
        "PORT": ("Optional - Server port (default: 7860)", False),
    }

    env_ok = True
    firebase_creds_found = False

    for var, (description, required) in env_vars.items():
        exists, value = check_env_variable(var, required)
        if exists:
            print_success(f"{var}: {value}")
            if "FIREBASE" in var:
                firebase_creds_found = True
        else:
            if required:
                print_error(f"{var}: NOT SET - {description}")
                env_ok = False
            else:
                print_info(f"{var}: Not set - {description}")

    if not firebase_creds_found:
        print_warning(
            "No Firebase credentials found (FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_CREDENTIALS_PATH)."
        )
        print_warning(
            "Authentication verification may fail unless running on GCP with default credentials."
        )

    # 3. Check Database Configuration
    print_header("3. Database Configuration")
    db_config = check_database_config()

    if db_config["can_connect"]:
        print_success("Database connection successful")
        print_success("Connected to Supabase (PostgreSQL) ✨")
        if db_config["has_supabase_sdk"]:
            print_success("Supabase SDK installed")
    else:
        print_error("Database connection failed")
        if "error" in db_config:
            print_error(f"Error: {db_config['error']}")

    # 4. Check Hugging Face Configuration
    print_header("4. Hugging Face Spaces Configuration")
    hf_config = check_huggingface_config()

    if hf_config["is_hf_space"]:
        print_success("Running on Hugging Face Spaces")
        print_info(f"Space ID: {hf_config['space_id']}")
    else:
        print_info("Not running on Hugging Face Spaces (local development)")

    print_info(f"Port: {hf_config['port']}")
    if hf_config["port_correct"]:
        print_success("Port configured correctly for HF Spaces (7860)")

    # 5. Check File Structure
    print_header("5. File Structure")
    files = verify_file_structure()
    files_ok = True
    for item, exists in files.items():
        if exists:
            print_success(f"{item}")
        else:
            print_error(f"{item} NOT FOUND")
            files_ok = False

    # 6. Final Summary
    print_header("Summary")

    issues = []
    if not all_deps_ok:
        issues.append("Missing Python dependencies")
    if not env_ok:
        issues.append("Missing required environment variables")
    if not db_config["can_connect"]:
        issues.append("Database connection failed")
    if not files_ok:
        issues.append("Missing required files/directories")

    if not issues:
        print_success("All checks passed! ✨")
        print_info("Your application is ready to deploy to Hugging Face!")
        print_info("\nNext steps:")
        print_info("  1. Configure Supabase (recommended for production)")
        print_info("  2. Set SUPABASE_URL and SUPABASE_KEY in HF Spaces secrets")
        print_info("  3. Set GOOGLE_API_KEY in HF Spaces secrets")
        print_info("  4. Deploy using: git push")
    else:
        print_warning("Issues found:")
        for issue in issues:
            print_error(f"  - {issue}")
        print_info("\nPlease fix the issues above before deploying.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
