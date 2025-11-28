import markdown
from weasyprint import HTML, CSS
import logging
from pypdf import PdfReader
import io

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""


def convert_md_to_pdf(md_path: str, pdf_path: str):
    try:
        with open(md_path, "r") as f:
            text = f.read()

        # Convert Markdown to HTML
        html_text = markdown.markdown(text, extensions=["extra", "codehilite"])

        # LaTeX-like CSS styling
        css = CSS(
            string="""
            @page {
                size: A4;
                margin: 2.5cm;
                @bottom-center {
                    content: counter(page);
                    font-family: "Latin Modern Roman", serif;
                    font-size: 10pt;
                }
            }
            body {
                font-family: "Latin Modern Roman", "Times New Roman", serif;
                line-height: 1.4;
                font-size: 11pt;
                color: #000;
                text-align: justify;
            }
            h1 {
                font-size: 24pt;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
                border-bottom: 1px solid #000;
                padding-bottom: 10px;
            }
            h2 {
                font-size: 14pt;
                font-weight: bold;
                margin-top: 15px;
                margin-bottom: 10px;
                border-bottom: 1px solid #000;
                padding-bottom: 3px;
                text-transform: uppercase;
            }
            h3 {
                font-size: 12pt;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            p {
                margin-bottom: 10px;
            }
            ul {
                margin-top: 5px;
                margin-bottom: 10px;
                padding-left: 20px;
            }
            li {
                margin-bottom: 2px;
            }
            code {
                font-family: "Latin Modern Mono", "Courier New", monospace;
                background-color: #f5f5f5;
                padding: 2px 4px;
                font-size: 0.9em;
            }
            strong {
                font-weight: bold;
            }
            em {
                font-style: italic;
            }
            a {
                color: #000;
                text-decoration: none;
            }
        """
        )

        # Wrap in HTML structure
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """

        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
        logger.info(f"Successfully converted {md_path} to {pdf_path}")
        return True

    except Exception as e:
        logger.error(f"Error converting to PDF: {str(e)}")
        return False
