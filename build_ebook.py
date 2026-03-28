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
                margin: 2.5cm 2cm;
                @top-center {
                    content: "VIBE-TO-VALUE GUIDE · jjeffers.net";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #999;
                    border-bottom: 1px solid #eeeeee;
                    padding-bottom: 10px;
                }
                @top-right {
                    content: "PAGE " counter(page);
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #999;
                    border-bottom: 1px solid #eeeeee;
                    padding-bottom: 10px;
                }
                @bottom-left {
                    content: "© jjeffers.net · Not for redistribution without permission";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #999;
                    border-top: 1px solid #eeeeee;
                    padding-top: 10px;
                    width: 100%;
                }
            }
            @page :first {
                margin: 0;
                @top-center { content: none; border: none; }
                @top-right { content: none; border: none; }
                @bottom-left { content: none; border: none; }
            }
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.7;
                color: #222;
            }
            .chapter {
                page-break-before: always;
            }
            h1 {
                color: #111;
                border-bottom: 2px solid #de4a22;
                padding-bottom: 15px;
                margin-top: 1em;
                font-size: 2.2em;
            }
            h2 {
                color: #222;
                margin-top: 1.8em;
                font-size: 1.4em;
            }
            h3 {
                color: #de4a22;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            p {
                margin: 1.2em 0;
            }
            pre {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 1.5em;
                border-radius: 4px;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: 'Courier New', Courier, monospace;
            }
            code {
                background-color: #f8f9fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                word-wrap: break-word;
                font-family: 'Courier New', Courier, monospace;
                color: #e83e8c;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5em 0;
            }
            th, td {
                border-bottom: 1px solid #ddd;
                padding: 12px 8px;
                text-align: left;
            }
            th {
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
            }
            blockquote {
                border-right: 4px solid #de4a22;
                margin: 2em 0;
                padding: 1.5em;
                background-color: #fcf7f4;
                color: #444;
            }
            /* Add cover page styling */
            .cover-page {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: flex-start;
                height: 100vh;
                background-color: #151b26;
                border-left: 20px solid #de4a22;
                padding-left: 50px;
                text-align: left;
                page-break-after: always;
                color: #ffffff;
            }
            .cover-page p {
                color: #999;
                font-size: 1.2em;
            }
            .cover-title {
                font-size: 4em;
                color: #ffffff;
                margin-bottom: 0.1em;
                page-break-before: avoid;
                border: none;
                line-height: 1.1;
                font-weight: 800;
            }
            .cover-subtitle {
                font-size: 1.5em;
                color: #999;
                margin-top: 1em;
            }
            /* Table of Contents */
            .toc-page {
                page-break-after: always;
                padding: 40px;
            }
            .toc-page h1 {
                border-bottom: 2px solid #de4a22;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            .toc-list {
                list-style: none;
                padding: 0;
            }
            .toc-list li {
                margin-bottom: 12px;
                font-size: 1.1em;
            }
            .toc-list a {
                color: #333;
                text-decoration: none;
                display: flex;
            }
            .toc-title {
                margin-right: -4px;
            }
            .toc-leader {
                flex-grow: 1;
                border-bottom: 1px dotted #ccc;
                margin: 0 8px;
                position: relative;
                top: -6px;
            }
            .toc-page-num::after {
                content: target-counter(attr(href), page);
            }
        </style>
    </head>
    <body>
        <div class="cover-page">
            <h1 class="cover-title">From Vibe to Value</h1>
            <p class="cover-subtitle">A Guide to Agentic Capabilities</p>
        </div>
    """

    toc_entries = []
    chapters_html = ""

    for i, file_path in enumerate(md_files):
        print(f"Processing {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Extract title for TOC
            title = file_path
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
                    
            chapter_id = f"chap-{i}"
            toc_entries.append((title, chapter_id))
            
            md_content = "".join(lines)
            html_content = markdown.markdown(
                md_content, 
                extensions=['fenced_code', 'tables']
            )
            # Inject anchor ID into chapter wrapper
            chapters_html += f"\n<div class='chapter' id='{chapter_id}'>\n{html_content}\n</div>\n"

    # Build the TOC HTML
    toc_html = "<div class='toc-page'>\n<h1>Table of Contents</h1>\n<ul class='toc-list'>\n"
    for title, chapter_id in toc_entries:
        # Weasyprint target-counter needs href to an id
        toc_html += f"  <li><a href='#{chapter_id}'><span class='toc-title'>{title}</span><span class='toc-leader'></span><span class='toc-page-num' href='#{chapter_id}'></span></a></li>\n"
    toc_html += "</ul>\n</div>\n"

    # Assemble full HTML
    full_html += toc_html + chapters_html

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
