import os
import glob
import markdown
from weasyprint import HTML, CSS

def build_ebook():
    print("Gathering markdown files...")
    # Find all numbered markdown files
    md_files = sorted(glob.glob("[0-9][0-9]-*.md"))
    if not md_files:
        print("No markdown files found!")
        return

    full_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>From Vibe to Value</title>
        <style>
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                page-break-before: always;
                color: #2c3e50;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
                margin-top: 0;
            }
            h1:first-of-type {
                page-break-before: avoid;
            }
            h2 {
                color: #34495e;
                margin-top: 1.5em;
            }
            h3 {
                color: #7f8c8d;
            }
            p {
                margin: 1em 0;
            }
            pre {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 1em;
                border-radius: 4px;
                overflow-x: a;
                font-family: 'Courier New', Courier, monospace;
            }
            code {
                background-color: #f8f9fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Courier New', Courier, monospace;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5em 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            blockquote {
                border-left: 4px solid #3498db;
                margin: 1.5em 0;
                padding: 0.5em 1em;
                background-color: #fdfdfd;
                color: #555;
            }
            /* Add cover page styling */
            .cover-page {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
                page-break-after: always;
            }
            .cover-title {
                font-size: 3em;
                color: #2c3e50;
                margin-bottom: 0.2em;
                page-break-before: avoid;
                border: none;
            }
            .cover-subtitle {
                font-size: 1.5em;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <div class="cover-page">
            <h1 class="cover-title">From Vibe to Value</h1>
            <p class="cover-subtitle">A Guide to Agentic Capabilities</p>
        </div>
    """

    for file_path in md_files:
        print(f"Processing {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            html_content = markdown.markdown(
                md_content, 
                extensions=['fenced_code', 'tables']
            )
            full_html += f"\\n<div class='chapter'>\\n{html_content}\\n</div>\\n"

    full_html += """
    </body>
    </html>
    """
    
    # Save the intermediate HTML for debugging
    with open('ebook.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    print("Generating PDF with WeasyPrint...")
    html = HTML(string=full_html, base_url=os.getcwd())
    html.write_pdf('ebook.pdf')
    print("Done! PDF saved to ebook.pdf")
    
    print("Opening PDF in Document Viewer...")
    import subprocess
    subprocess.Popen(["evince", "ebook.pdf"])

if __name__ == "__main__":
    build_ebook()
