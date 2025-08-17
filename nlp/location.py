from typing import List, Set
import spacy

# Load SpaCy transformer model
nlp = spacy.load("en_core_web_trf")


def process_text(text: str) -> List[str]:
    """
    Extracts unique location entities (GPE, LOC, FAC) using spaCy.
    Returns a list of dicts with location names and placeholder coordinates.
    """
    doc = nlp(text)
    results: List[str] = []
    seen: Set[str] = set()

    for ent in doc.ents:
        if ent.label_ in {"GPE", "LOC", "FAC"}:
            loc = ent.text.strip()

            # Case-insensitive deduplication
            key = loc.lower()
            if key in seen:
                continue
            seen.add(key)

            # print(f"Found {ent.label_}: {loc}")
            results.append(loc)

    return results
