import glob
import re

AI_SMELLS = [
    "delve", "tapestry", "testament", "symphony", "crucial", "landscape", 
    "moreover", "in conclusion", "important to note", "it's worth noting", 
    "at the end of the day", "game changer", "multifaceted", "paradigm shift", 
    "unlocking", "embrace", "foster", "meticulous",
    "it’s important to note", "it’s worth mentioning", "it should be noted", 
    "this demonstrates", "furthermore", "additionally", "in addition", 
    "however", "particularly", "specifically", "incredibly", "absolutely", 
    "tremendously", "individuals", "utilize", "facilitate", "fascinating", 
    "remarkable", "incredible", "demonstrate", "this can sometimes help with", 
    "in many cases", "often", "tends to", "may", "might", "could potentially", 
    "it seems that", "appears to be"
]

def scan_files():
    print("Scanning markdown files for AI smells...")
    md_files = sorted(glob.glob("[0-9][0-9]-*.md"))
    
    total_found = 0
    smell_pattern = re.compile(r'\b(' + '|'.join(AI_SMELLS) + r')\b', re.IGNORECASE)
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        file_matches = 0
        for i, line in enumerate(lines):
            matches = smell_pattern.findall(line)
            if matches:
                # Deduplicate matches on the same line if needed
                for match in set(matches):
                    print(f"[{file_path}:{i+1}] Found smell: '{match}' -> {line.strip()[:60]}...")
                    file_matches += 1
                    total_found += 1
                    
        if file_matches > 0:
            print(f"--- {file_matches} smells in {file_path} ---\\n")

    print(f"\\nScan complete. Total AI smells found: {total_found}")

if __name__ == "__main__":
    scan_files()
