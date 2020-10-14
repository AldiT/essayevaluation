from bs4 import BeautifulSoup as BS

import numpy as nps
import sys

xml_path = None
levels = ["a1", "a2", "b1", "b2", "c1"]

operation = sys.argv[2] #avg word num -> avg_w, avg len -> avg_l, avg sentence num -> avg_sent_num


if sys.argv[1] == "all":
    xml_path = []
    for level in levels:
        xml_path.append("level_" + level + ".xml")
    
else:
    xml_path = sys.argv[1]

print(xml_path)

def get_essays(xml_path):
    """
    Params:
    xml_path(string or list): could be a list of paths or a single string path

    Returns:
    list: all essays in a list of strings
    """
    pass


def get_average_words(essays):
    """
    Params:
    essays(list): a list of strings representing a group of essays

    Returns:
    int: the average number of words on this group of essays that was passed as a parameter
    """
    pass

def get_average_sentence_number(essays):
    """
    Params:
    essays(list): a list of essays as strings

    Returns
    int: average number of sentence length
    """
    pass



if __name__ == "__main__":
    print(xml_path)

