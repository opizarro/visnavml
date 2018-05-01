import random
from .classifier import BaseClassifier

class RandomSampleClassifier(BaseClassifier):
    def __init__(self, name, tag_scheme_list, probability_threshold=0.5, possible_codes=frozenset(["MALCB", "BIOTA", "P"])):
        # NB: possible_codes is an additional argument that is only relevant for this model
        self.possible_codes = possible_codes
        BaseClassifier.__init__(self, name, tag_scheme_list, probability_threshold=probability_threshold)

    def predict(self, media_path, points):
        print(" - Working on: {}".format(media_path))
        # Do something with the media file
        labeled_points = []
        for p in points:
            classifier_code = random.sample(self.possible_codes, 1)[0]
            prob = round(random.random(), 2)
            labeled_point = self.get_labeled_point(p, classifier_code, prob)
            if labeled_point is not None:
                labeled_points.append(labeled_point)
        return labeled_points

