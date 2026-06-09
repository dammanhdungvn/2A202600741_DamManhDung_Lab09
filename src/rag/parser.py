from __future__ import annotations

def parse_policy_markdown(markdown_text: str) -> list[dict]:
    lines = markdown_text.split('\n')
    chunks = []
    
    current_h2 = ""
    current_h3 = ""
    current_content = []
    
    def save_chunk():
        if current_h2 and current_content:
            content_str = "\n".join(current_content).strip()
            if content_str:
                if current_h3:
                    rendered_text = f"{current_h2}\n{current_h3}\n{content_str}"
                    citation = f"{current_h2.strip('# ')} > {current_h3.strip('# ')}"
                else:
                    rendered_text = f"{current_h2}\n{content_str}"
                    citation = f"{current_h2.strip('# ')}"
                
                chunks.append({
                    "section_h2": current_h2.strip("# "),
                    "section_h3": current_h3.strip("# ") if current_h3 else "",
                    "citation": citation,
                    "rendered_text": rendered_text
                })
    
    for line in lines:
        if line.startswith("## "):
            save_chunk()
            current_h2 = line.strip()
            current_h3 = ""
            current_content = []
        elif line.startswith("### "):
            save_chunk()
            current_h3 = line.strip()
            current_content = []
        else:
            if current_h2:
                current_content.append(line)
                
    save_chunk()
    return chunks
