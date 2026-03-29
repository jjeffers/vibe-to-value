import glob
import re
import os

SMELL_REMEDIATIONS = {
    "delve": "explore, examine, or dig into",
    "tapestry": "complex web, mixture, or combination",
    "testament": "proof, evidence, or demonstration",
    "symphony": "coordinated effort, harmony, or arrangement",
    "crucial": "essential, important, or key",
    "landscape": "environment, context, or field",
    "moreover": "in addition, also, or simply start a new sentence",
    "in conclusion": "to sum up, finally, or simply end the text naturally",
    "important to note": "consider deleting; just state the fact directly",
    "it's worth noting": "consider deleting; just state the fact directly",
    "at the end of the day": "ultimately, eventually, or when all is said and done",
    "game changer": "major breakthrough, significant advancement, or innovation",
    "multifaceted": "complex, varied, or multi-dimensional",
    "paradigm shift": "fundamental change, major shift, or transformation",
    "unlocking": "enabling, releasing, or discovering",
    "embrace": "adopt, welcome, or accept",
    "foster": "encourage, promote, or support",
    "meticulous": "careful, precise, or thorough",
    "it’s important to note": "consider deleting; just state the fact directly",
    "it’s worth mentioning": "consider deleting; just state the fact directly",
    "it should be noted": "consider deleting; just state the fact directly",
    "this demonstrates": "this shows, this proves, or this indicates",
    "furthermore": "also, besides, or simply start a new sentence",
    "additionally": "also, besides, or simply start a new sentence",
    "in addition": "also, besides, or simply start a new sentence",
    "however": "but, yet, or nevertheless",
    "particularly": "especially, notably, or specifically (use sparingly)",
    "specifically": "in particular, explicitly, or precisely (use sparingly)",
    "incredibly": "very, extremely, or highly (use sparingly)",
    "absolutely": "completely, entirely, or definitely (use sparingly)",
    "tremendously": "enormously, greatly, or significantly (use sparingly)",
    "individuals": "people, persons, or users",
    "utilize": "use, employ, or apply",
    "facilitate": "help, ease, or make possible",
    "fascinating": "interesting, captivating, or engaging",
    "remarkable": "notable, extraordinary, or impressive",
    "incredible": "unbelievable, amazing, or astounding",
    "demonstrate": "show, prove, or exhibit",
    "this can sometimes help with": "this can help with, or this assists in",
    "in many cases": "often, frequently, or generally",
    "often": "frequently, regularly, or commonly (use sparingly)",
    "tends to": "usually, generally, or is likely to",
    "may": "might, could, or can (use sparingly to avoid weak statements)",
    "might": "may, could, or can (use sparingly to avoid weak statements)",
    "could potentially": "could, might, or may (redundant 'potentially')",
    "it seems that": "it appears that, or state directly if true",
    "appears to be": "seems to be, or state directly if true"
}

def scan_files():
    print("Scanning markdown files for AI smells...")
    md_files = sorted(glob.glob("[0-9][0-9]-*.md"))
    
    total_found = 0
    # Escape the keys just in case
    keys_regex = '|'.join(re.escape(k) for k in SMELL_REMEDIATIONS.keys())
    smell_pattern = re.compile(r'\b(' + keys_regex + r')\b', re.IGNORECASE)
    
    report_lines = ["# AI Smell Detection Report\n\n"]
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        file_matches = []
        for i, line in enumerate(lines):
            matches = smell_pattern.findall(line)
            if matches:
                # Deduplicate matches on the same line if needed
                for match in set(matches):
                    suggestion = SMELL_REMEDIATIONS.get(match.lower(), "Consider rephrasing to sound more natural")
                    context = line.strip().replace('|', '&#124;') # escape pipes for markdown table
                    if len(context) > 80:
                        context = context[:77] + "..."
                    file_matches.append((i+1, match, context, suggestion))
                    total_found += 1
                    
        if file_matches:
            report_lines.append(f"## {file_path}\n\n")
            report_lines.append("| Line | Smell | Context | Suggested Remediation |\n")
            report_lines.append("|---|---|---|---|\n")
            for (line_num, match, context, suggestion) in file_matches:
                report_lines.append(f"| {line_num} | **{match}** | `{context}` | {suggestion} |\n")
            report_lines.append("\n")

    report_lines.append(f"**Total AI smells found:** {total_found}\n")
    
    report_path = "ai_smells_report.md"
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.writelines(report_lines)
        
    print(f"Scan complete. Total AI smells found: {total_found}")
    print(f"Detailed report generated at: {report_path}")

if __name__ == "__main__":
    scan_files()
