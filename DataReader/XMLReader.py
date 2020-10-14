import csv
import glob

from bs4 import BeautifulSoup as BS
import re
import html

class DataInstance:
    """
    This would be the result object to carry all the neccessary information
    from the xml file for one data instance
    """

    def __init__(self):
        self.topic = None
        self.grade = None
        self.text = None
        self.nationality = None

    def get_topic(self):
        return self.topic

    def get_grade(self):
        return self.grade

    def get_text(self):
        return self.text

    def get_nat(self):
        return self.nationality

    def set_topic(self, topic_):
        self.topic = topic_

    def set_grade(self, grade_):
        self.grade = grade_

    def set_text(self, text_):
        self.text = text_

    def set_nat(self, nationality_):
        self.nationality = nationality_


class XMLReader:

    def __init__(self, path_to_xml=''):
        if path_to_xml == "":
            raise ValueError("Please provide a path to the xml file.")
        else:
            self.content = open(path_to_xml)
            self.soup = BS(self.content, "lxml")

    def get_tree_object(self):
        """
        Returns the tree object created from a XML file.
        """
        return self.soup

    def get_essay_list(self, num_essays=None):
        essays = []
        writings = self.soup.find_all("writing")
        if num_essays is None:
            num_essays = len(writings)
        for index, writing in enumerate(writings):
            if index >= num_essays:
                break

            essays.append(writing.find("text").text)

        return essays

    def pass_through_spacy_pipeline(self, text):
        """
        Passes the text through the spacy pipeline to perform all tokenization lemmatization etc.
        --text: the essay text (or any text that needs to go through the prompt)
        """
        pass

    def add_data_instance(self, topic, grade, text, l1_nat, dataset_name):
        """
        Adds a new instance to the data list of this object
        Question: What if the data is bigger than RAM? -->Shift to batches
        --topic:        The prompt of the this data instance
        --grader:       The grade given by the human grader
        --text:         The free-form response to the prompt
        --l1_nat:       Represents either the l1 background, or nationality(which might not be the same)
        --dataset_name: Dataset name specified for analysis purposes
        """
        pass

    def remove_xml_tags_from_writings(self):
        writings = self.soup.find_all("writing")

        for writing in writings:
            writing.text = re.sub('<[^>]+>', '', writing.text)


class FeatureExtractor:
    def __init__(self):
        pass

    def get_lexical_sophistication_features(self):
        pass

    def get_lexical_diversity_features(self):
        pass

    def get_discourse_features(self):
        pass


def get_essays(xml_path):
    """
    copied from essay_evaluation.LexicalDiversity get_feature_matrix
    but just reading the essays without feature extraction etc.
    :param xml_path:
    :param num_essays:
    :return:
    """
    reader = XMLReader(xml_path)
    tree = reader.get_tree_object()
    writings = tree.find_all("writing")

    grades = []
    essays = []
    for index, writing in enumerate(writings):
        grades.append(int(writing.find('grade').text))
        essays.append(html.unescape(writing.find("text").text))
    return essays, grades


def get_bawe_texts(folder_path):
    re_remove_tags = re.compile('<.*?>.*?<.*?>', re.MULTILINE)
    texts = []
    for file in glob.glob(folder_path + "/*.txt"):
        with open(file, 'r') as fh:
            text_raw = fh.read()

        text = re_remove_tags.sub("", text_raw)
        text = text.replace('URL','')
        text = text.replace('FORMULA', '')

        texts.append(text)

    return texts

def get_flip_texts(filepath):
    texts = []
    with open(filepath) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            texts.append(row['Essay'].replace('\n', ' '))
    return texts

if __name__ == "__main__":
    texts = get_flip_texts("/home/simon/Downloads/flip.csv")
    print("done")