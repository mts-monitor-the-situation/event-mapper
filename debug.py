import spacy  # Load SpaCy transformer model

nlp = spacy.load("en_core_web_trf")

text = "no br fuck"

doc = nlp(text)


for ent in doc.ents:
    if ent.label_ in {"GPE", "LOC", "FAC"}:
        loc = ent.text.strip()
        print(f"Found {ent.label_}: {loc}")
