import hashlib
import re
from io import BytesIO
from pathlib import Path


class DocumentProcessor:
    def process(self, file_path, doc_type=None, display_name=None, content_hash=None):
        path = Path(file_path)
        name = display_name or path.name
        digest = content_hash or hashlib.sha256(path.read_bytes()).hexdigest()
        if path.suffix.lower() == ".pdf":
            import fitz
            with fitz.open(stream=path.read_bytes(), filetype="pdf") as document:
                return [chunk for page, page_data in enumerate(document, 1) for chunk in self._chunks(page_data.get_text("text"), name, page, doc_type, digest)]
        if path.suffix.lower() == ".docx":
            from docx import Document
            document = Document(BytesIO(path.read_bytes()))
            return self._chunks(chr(10).join(paragraph.text for paragraph in document.paragraphs), name, 1, doc_type, digest)
        raise ValueError(f"Unsupported file type: {path.suffix}")

    def _chunks(self, text, name, page, doc_type, digest):
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]
        groups, current, size = [], [], 0
        for sentence in sentences:
            length = len(sentence.split())
            if current and size + length > 400:
                groups.append(" ".join(current)); current = current[-2:]; size = sum(len(item.split()) for item in current)
            current.append(sentence); size += length
        if current: groups.append(" ".join(current))
        section = next((line.strip() for line in text.splitlines()[:8] if line.strip() and len(line)<100 and (line.strip().isupper() or re.match(r"^\d+",line))), "General")
        return [{"text": group, "doc_name": name, "page": page, "section": section, "doc_type": doc_type or self._type(name), "chunk_id": f"{digest[:16]}_p{page}_c{index}"} for index,group in enumerate(groups) if len(group)>=50]

    def _type(self, name):
        value=name.lower()
        if "oisd" in value or "standard" in value:return "Safety Standard"
        if "work" in value:return "Maintenance Record"
        if "inspection" in value:return "Inspection Report"
        if "procedure" in value:return "Operating Procedure"
        if "incident" in value:return "Incident Report"
        return "General Document"
