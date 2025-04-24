from sentence_transformers import SentenceTransformer
from datetime import datetime
from typing import Dict


class User:
    def __init__(self, data: Dict):
        self.id = data['email']
        self.bio = data['bio']
        self.passions = set(data['passions'])
        self.location = tuple(data['location'])
        self.birthdate = datetime.strptime(data['birthday'], "%Y-%m-%d").date()
        self._embeddings = {}

    @property
    def age(self):
        today = datetime.now().date()
        return today.year - self.birthdate.year - (
            (today.month, today.day) <
            (self.birthdate.month, self.birthdate.day)
        )

    @property
    def bio_embedding(self):
        if 'bio' not in self._embeddings:
            self._embeddings['bio'] = SentenceTransformer(
                'paraphrase-multilingual-MiniLM-L12-v2'
            ).encode(self.bio)
        return self._embeddings['bio']
