import spacy

print("[NLP] Loading model...")
nlp = spacy.load("en_core_web_trf")  # Will auto-use GPU if set up


def process_text(text: str):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            print(f"Found GPE: {ent.text}")
