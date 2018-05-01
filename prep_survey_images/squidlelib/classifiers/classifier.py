from squidleapi.mediadata import SQAPIMediaData

class BaseClassifier():
    # list of possible outputs of the classifier
    name = "MAGICBOT"
    tag_group_lookup = {}
    probability_threshold = 0.5

    def __init__(self, name, tag_scheme_list, probability_threshold=None):
        # initialise with name
        self.name = name

        # set probability threshold
        if probability_threshold is not None:
            self.probability_threshold = probability_threshold

        # create a lookup / hash of the different classifier labels and how they map to the tag_group_ids
        for tg in tag_scheme_list:
            for i in tg['info']:
                # build up a dictionary of short_codes that map to tag_group_ids
                # used to lookup id from classifier output
                if i['name'] == 'code_short':
                    self.tag_group_lookup[i['value'].strip()] = tg['id']

    def predict(self, media_path, points):
        raise NotImplemented
        # labeled_points = []
        # for p in points:
        #     classifier_code, prob = do_classification_for_point(p)
        #     labeled_point = self.get_labeled_point(p, classifier_code, prob)
        #     if labeled_point is not None:
        #         labeled_points.append()
        # return labeled_points

    def get_labeled_point(self, point, label, prob):
        if label in self.tag_group_lookup:
            # lookup tag_group_id from classification scheme
            tag_group_id = self.tag_group_lookup[label]
            # append to label list of dicts with random probability
            return {
                "tag_group_id": tag_group_id,
                "prob": prob,
                "media_annotation_id": point['id']
            }
        return None

    def submit_predictions(self, labeled_points, annotation_set_id, user_id, sqapi):
        j = 0
        for ma in labeled_points:
            # Create new annotation label
            if ma['prob'] > self.probability_threshold:  # if prob is greater than threshold make a new annotation label
                j += 1  # counter number of point labeled
                sqapi.new_annotation({
                    "annotation_set_id": annotation_set_id,
                    "tag_group_id": ma['tag_group_id'],  # the tag_group to use for this label
                    "data": {"probability": ma['prob']},
                    "media_annotation_id": ma['media_annotation_id'],
                    "user_id": user_id
                })
        print (" - Labelled {}/{} points".format(j, len(labeled_points)))
