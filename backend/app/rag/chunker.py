import re
from typing import List

class Chunker:
    def __init__(self, target_chunk_size: int = 600, overlap: int = 90):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits text into chunks respecting markdown headers, paragraphs, and sentence boundaries.
        Target size is in estimated token count (~4 characters per token).
        """
        clean_text = re.sub(r'\r\n', '\n', text).strip()
        if not clean_text:
            return []

        # Split on markdown headings first
        sections = re.split(r'(\n(?=#{1,4}\s))', clean_text)
        raw_blocks: List[str] = []
        current_block = ""

        for part in sections:
            if not part.strip():
                continue
            if part.startswith('\n#'):
                if current_block.strip():
                    raw_blocks.append(current_block.strip())
                current_block = part.strip()
            else:
                current_block += "\n\n" + part.strip()

        if current_block.strip():
            raw_blocks.append(current_block.strip())

        # Subdivide blocks into target chunk sizes
        char_limit = self.target_chunk_size * 4
        char_overlap = self.overlap * 4
        chunks: List[str] = []

        for block in raw_blocks:
            if len(block) <= char_limit:
                chunks.append(block)
            else:
                # Split by paragraphs
                paragraphs = block.split('\n\n')
                current_chunk = ""
                for p in paragraphs:
                    p = p.strip()
                    if not p:
                        continue
                    if len(current_chunk) + len(p) + 2 <= char_limit:
                        current_chunk = f"{current_chunk}\n\n{p}".strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            # Keep overlap
                            current_chunk = current_chunk[-char_overlap:] + "\n\n" + p
                        else:
                            # Long single paragraph, split by sentences
                            sentences = re.split(r'(?<=[.!?])\s+', p)
                            for s in sentences:
                                if len(current_chunk) + len(s) + 1 <= char_limit:
                                    current_chunk = f"{current_chunk} {s}".strip()
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk)
                                        current_chunk = current_chunk[-char_overlap:] + " " + s
                                    else:
                                        # Force split hard chunk
                                        chunks.append(s[:char_limit])
                                        current_chunk = s[char_limit - char_overlap:]

                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

        return chunks

chunker = Chunker()
