import markdown
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

def convert_md_to_pdf(md_path: str, pdf_path: str):
    try:
        with open(md_path, "r") as f:
            text = f.read()
            
        # Convert Markdown to HTML
        html_text = markdown.markdown(text, extensions=['extra', 'codehilite'])
        
        # Add some basic styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    font-size: 12pt;
                }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 20px; border-bottom: 1px solid #eee; }}
                h3 {{ color: #7f8c8d; }}
                code {{ background-color: #f9f9f9; padding: 2px 5px; border-radius: 3px; }}
                pre {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        HTML(string=styled_html).write_pdf(pdf_path)
        logger.info(f"Successfully converted {md_path} to {pdf_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting to PDF: {str(e)}")
        return False
