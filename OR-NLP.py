import spacy

# Charger le modèle de langue en français (ou anglais)
nlp = spacy.load("fr_core_news_sm")

def parse_instruction(instruction):
    doc = nlp(instruction)
    
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
        print(ent.text, ent.label_)
    
    return entities

# Exemple d'utilisation
instruction = "Déplace la pause de Bob à 14h"
entities = parse_instruction(instruction)
print(entities)
