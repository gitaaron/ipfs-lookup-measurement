from pickled.model_publication import Publication

class Run:
    def __init__(self, publication: Publication):
        self.first_publication = publication

    def add_publication(self, pub: Publication):
        if pub.get_providers_ended_at < self.first_publication.get_providers_ended_at:
            self.first_publication = pub