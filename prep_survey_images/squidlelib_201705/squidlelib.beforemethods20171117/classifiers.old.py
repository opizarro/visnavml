import random
#from slim_classify_squidle_image_points import *
from keras_classify_squidle_image_points import *

class RandomSampleClassifier():

    # list of possible outputs of the classifier
    possible_codes = ["MALCB", "BIOTA", "P"]

    def __init__(self, tag_scheme_list):
        # create a lookup / hash of the different classifier labels and how they map to the tag_group_ids
        self.tag_group_lookup = {}
        for tg in tag_scheme_list:
            for i in tg['info']:
                # build up a dictionary of short_codes that map to tag_group_ids
                # used to lookup id from classifier output
                if i['name'] == 'code_short':
                    self.tag_group_lookup[i['value'].strip()] = tg['id']

    def predict(self, media_path, annotations):
        print " - Working on:", media_path
        labeled_annotations = []
        for a in annotations:
            # Get label
            # NOTE: KELP CLASSIFIER WOULD ONLY USE ONE LABEL.
            # In this example, the classifier picks one of the "possible_codes" at random.
            classifier_code = random.sample(self.possible_codes, 1)[0]
            if classifier_code in self.tag_group_lookup:
                # lookup tag_group_id from classification scheme
                tag_group_id = self.tag_group_lookup[classifier_code]
                # append to label list of dicts with random probability
                labeled_annotations.append({
                    "tag_group_id": tag_group_id,
                    "prob": round(random.random(), 2),
                    "media_annotation_id": a['id']
                })

        return labeled_annotations


class KelpClassifier():
    # list of possible outputs of the classifier
    possible_codes = ["MALC"]

    def __init__(self, tag_scheme_list):
        # create a lookup / hash of the different classifier labels and how they map to the tag_group_ids
        self.tag_group_lookup = {}
        for tg in tag_scheme_list:
            for i in tg['info']:
                # build up a dictionary of short_codes that map to tag_group_ids
                # used to lookup id from classifier output
                if i['name'] == 'code_short':
                    self.tag_group_lookup[i['value'].strip()] = tg['id']

    def predict(self, media_path, annotations):
        print " - Working on:", media_path
        labeled_annotations = []
        # lookup tag_group_id from classification scheme
        tag_group_id = self.tag_group_lookup["MALC"] # hardcoded
        annotations_that_are_kelp, prob_class = classify_patches(media_path, annotations)
        k = 0
        for a in annotations_that_are_kelp:
            # Get label
            # NOTE: KELP CLASSIFIER WOULD ONLY USE ONE LABEL.
            # In this example, the classifier picks one of the "possible_codes" at random.
            #classifier_code = random.sample(self.possible_codes, 1)[0]

            # append to label list of dicts with random probability
            labeled_annotations.append({
                    "tag_group_id": tag_group_id,
                    "prob": round(prob_class[k],3),
                    "media_annotation_id": a['id']
                })
            k=k+1
        return labeled_annotations


class KerasKelpClassifier():
    # list of possible outputs of the classifier
    #possible_codes = ["MALC","S"]

    def __init__(self, tag_scheme_list):
        # create a lookup / hash of the different classifier labels and how they map to the tag_group_ids
        self.tag_group_lookup = {}
        for tg in tag_scheme_list:
            for i in tg['info']:
                # build up a dictionary of short_codes that map to tag_group_ids
                # used to lookup id from classifier output
                if i['name'] == 'code_short':
                    self.tag_group_lookup[i['value'].strip()] = tg['id']

    def predict(self, media_path, annotations):
        print " - Working on:", media_path
        labeled_annotations = []
        # lookup tag_group_id from classification scheme
        #tag_group_id = self.tag_group_lookup["MALC"] # hardcoded
        classifier_codes, prob_classes = classify_patches(media_path, annotations)

        for i in range(0, len(annotations)):
            if classifier_codes[i] in self.tag_group_lookup:
                # lookup tag_group_id from classification scheme
                tag_group_id = self.tag_group_lookup[classifier_codes[i]]
                prob = prob_classes[i]
                # append to label list of dicts with random probability
                labeled_annotations.append({
                    "tag_group_id": tag_group_id,
                    "prob": prob,
                    "media_annotation_id": annotations[i]['id']
                })
        return labeled_annotations
