"""
Affiliation extraction script for hermes-arxiv-agent.

Extracts author affiliations from academic PDFs using PyMuPDF.
This approach reads raw first-page text and parses structured
author-affiliation blocks, which is more reliable than regex pattern matching.

Usage:
    python extract_affiliations.py <pdf_path>
    python extract_affiliations.py /Users/wangruifan/projects/hermes-arxiv-agent/papers/2607.21076.pdf
"""

import fitz  # PyMuPDF
import re
import sys


def extract_affiliations(pdf_path: str) -> str:
    """
    Extract author affiliations from the first page of an academic PDF.
    
    Returns:
        str: Semicolon-separated affiliations, or "未找到单位信息" if not found.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return f"未找到单位信息 (PDF读取失败: {e})"
    
    text = doc[0].get_text()
    doc.close()
    
    lines = text.split('\n')
    
    # Strategy 1: Look for email-institution pairs
    # Academic papers typically have: email@university.edu followed by University Name
    affiliations = []
    
    for i, line in enumerate(lines[:80]):
        line_clean = line.strip()
        
        # Check if line contains an email
        if '@' in line_clean:
            # Extract domain from email to identify institution
            email_match = re.search(r'@([\w.-]+)', line_clean)
            if email_match:
                domain = email_match.group(1)
                # Look for institution name in nearby lines
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    nearby = lines[j].strip()
                    # Check if this line looks like an institution
                    if _is_institution_line(nearby):
                        aff = _clean_affiliation(nearby)
                        if aff and aff not in affiliations:
                            affiliations.append(aff)
    
    if affiliations:
        return '; '.join(affiliations)
    
    # Strategy 2: Look for known institution patterns in first 50 lines
    known_patterns = [
        r'University\s+of\s+\w+',
        r'\w+\s+University',
        r'Institute\s+of\s+\w+',
        r'\w+\s+Institute',
        r'Google|Microsoft|Meta|Amazon|NVIDIA|Apple|OpenAI|DeepMind',
        r'KAIST|NUS|NTU|ETH|CMU|MIT|Stanford|Harvard',
        r'Alibaba|Tencent|Baidu|ByteDance|Huawei|Samsung',
        r'KU Leuven|Tsinghua|Peking|Zhejiang|Fudan|SJTU',
        r'Singapore\s+Institute',
        r'Information\s+Sciences\s+Institute',
        r'Indian\s+Institute',
        r'Politecnico|Technical\s+University',
        r'Carnegie\s+Mellon|Georgia\s+Tech',
    ]
    
    for i, line in enumerate(lines[:50]):
        line_clean = line.strip()
        for pat in known_patterns:
            if re.search(pat, line_clean, re.IGNORECASE):
                aff = _clean_affiliation(line_clean)
                if aff and len(aff) > 5 and aff not in affiliations:
                    affiliations.append(aff)
                break
    
    if affiliations:
        return '; '.join(affiliations)
    
    return "未找到单位信息"


def _is_institution_line(line: str) -> bool:
    """Check if a line looks like an institution name."""
    keywords = [
        'University', 'Institute', 'College', 'School',
        'Department', 'Laboratory', 'Center', 'Centre',
        'Research', 'Google', 'Microsoft', 'Meta', 'Amazon',
        'NVIDIA', 'Apple', 'OpenAI', 'DeepMind', 'Alibaba',
        'Tencent', 'Baidu', 'ByteDance', 'Huawei', 'Samsung',
        'KAIST', 'NUS', 'NTU', 'ETH', 'CMU', 'MIT', 'Stanford',
        'Harvard', 'Princeton', 'Berkeley', 'Yale', 'Columbia',
        'Cornell', 'UCLA', 'Georgia Tech', 'Carnegie Mellon',
    ]
    return any(kw.lower() in line.lower() for kw in keywords)


def _clean_affiliation(text: str) -> str:
    """Clean affiliation text."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # Remove footnote markers
    text = re.sub(r'[\*†‡§¶]', '', text)
    # Remove leading numbers/symbols
    text = re.sub(r'^[\d\s,]+', '', text)
    # Fix CamelCase
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip(' ,;.')
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_affiliations.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = extract_affiliations(pdf_path)
    print(f"Affiliations: {result}")
