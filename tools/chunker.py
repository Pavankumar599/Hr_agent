"""
tools/chunker.py  —  Header-based DOCX chunker (reused from RAG project).
"""

import re
from dataclasses import dataclass
from typing import List, Optional
from docx import Document


@dataclass
class PolicyChunk:
    chunk_id:   str
    section:    str
    subsection: Optional[str]
    content:    str


def _slugify(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")


def load_and_chunk(docx_path: str) -> List[PolicyChunk]:
    doc = Document(docx_path)
    lines = []
    for para in doc.paragraphs:
        style = para.style.name
        text  = para.text
        if style == "Heading 1":
            lines.append(f"# {text}")
        elif style == "Heading 2":
            lines.append(f"## {text}")
        else:
            for line in text.split("\n"):
                lines.append(line)

    chunks, current_h1, current_h2, buf = [], None, None, []

    def flush():
        if not buf or not current_h1:
            return
        content = "\n".join(l for l in buf if l.strip())
        if not content:
            return
        cid = (f"{_slugify(current_h1)}__{_slugify(current_h2)}"
               if current_h2 else _slugify(current_h1))
        chunks.append(PolicyChunk(chunk_id=cid, section=current_h1,
                                  subsection=current_h2, content=content))
        buf.clear()

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if re.match(r"^# (?!#)", s):
            flush(); current_h1 = s[2:].strip(); current_h2 = None
        elif re.match(r"^## ", s):
            flush(); current_h2 = s[3:].strip()
        else:
            buf.append(s)

    flush()
    return chunks
