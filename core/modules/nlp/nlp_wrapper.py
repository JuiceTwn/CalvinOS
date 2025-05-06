import spacy

class NLP:
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise OSError(f"Run `python -m spacy download {model}` first")
        
    def interpret(self, text: str) -> dict:
        """
        Basic intent/entity extractor:
        - intent: root verb lemma
        - entities: list of (text, label)
        """
        doc = self.nlp(text)
        intent = ""
        for token in doc:
            if token.dep_ == "ROOT":
                intent = token.lemma_
                break

        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return {"intent": intent, "entities": entities}
