import re
from pathlib import Path


class DocumentProcessor:
    def process(self, file_path, doc_type=None):
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            import fitz

            with fitz.open(path) as doc:
                return [
                    chunk
                    for page, page_data in enumerate(doc, 1)
                    for chunk in self._chunks(page_data.get_text("text"), path, page, doc_type)
                ]
        if path.suffix.lower() == ".docx":
            from docx import Document

            doc = Document(path)
            return self._chunks(
                chr(10).join(paragraph.text for paragraph in doc.paragraphs),
                path,
                1,
                doc_type,
            )
        raise ValueError(f"Unsupported file type: {path.suffix}")

    def _chunks(self, text, path, page, doc_type):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        groups, current, size = [], [], 0
        for sentence in sentences:
            length = len(sentence.split())
            if current and size + length > 400:
                groups.append(" ".join(current))
                current = current[-2:]
                size = sum(len(item.split()) for item in current)
            current.append(sentence)
            size += length
        if current:
            groups.append(" ".join(current))
        section = next(
            (
                line.strip()
                for line in text.splitlines()[:8]
                if line.strip()
                and len(line) < 100
                and (line.strip().isupper() or re.match(r"^\d+", line))
            ),
            "General",
        )
        return [
            {
                "text": group,
                "doc_name": path.name,
                "page": page,
                "section": section,
                "doc_type": doc_type or self._type(path.name),
                "chunk_id": f"{path.stem}_p{page}_c{index}",
            }
            for index, group in enumerate(groups)
            if len(group) >= 50
        ]

    def _type(self, name):
        value = name.lower()
        if "oisd" in value or "standard" in value:
            return "Safety Standard"
        if "work" in value:
            return "Maintenance Record"
        if "inspection" in value:
            return "Inspection Report"
        if "procedure" in value:
            return "Operating Procedure"
        if "incident" in value:
            return "Incident Report"
        return "General Document"

