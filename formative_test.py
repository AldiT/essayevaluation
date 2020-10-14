from essay_evaluation.pipeline import FeatureCollector
from essay_evaluation.lexical_sophistication import LexicalSophisticationFeatures
from essay_evaluation.lexical_variation import LexicalVariationFeatures
from bs4 import BeautifulSoup as BS
import numpy as np
import spacy
import os
import argparse, sys

parser = argparse.ArgumentParser()

"""
Feature name list on --> feature_names
"""


features_lv = ['LV_W', 'LV_WT', 'LV_WT1', 'LV_TTR', 'LV_CTTR', 'LV_RTTR', 'LV_HDD', 'LV_DUGA', 'LV_MAAS', 'LV_SUMM',
                         'LV_YULEK','LV_MTLD','LV_MSTTR','LV_MATTR']

#14 features
features_ls = ["LS_FPC_NG", "LS_FPC_NA", "LS_FPC_TC", "LS_FPC_BS", "LS_FPC_CA", "LS_FPC_CT", "LS_FPC_CGA1",
            "LS_FPC_CGA2", "LS_FPC_CGA3", "LS_FOMN_NG", "LS_FOMN_NA", "LS_FOMN_TC", "LS_FOMN_BS", "LS_FOMN_CA"]
#3 features
features_la = ["LA_ER", "LA_COL_ERR_R"]
#6 features
features_ca = ["CA_BIN1_R", "CA_BIN2_R", "CA_BIN3_R"]
#2 features
features_ld = ["LD_LXUR", "LD_GRUR"]

feature_names = features_lv + features_ls + features_la + features_ca + features_ld
feature_names = np.array(feature_names)
binning_indicies = [6, 18, 19, 20, 21, 22, 28, 29, 30, 31, 32, 33]
feature_names[binning_indicies]

#########################################################################################

class FormativeFeedbackEvaluator(object):

    #Not needed till now
    def __init__(self, bin_file_path=None):
        """
        Constructor -> Needs the path to the file where the bins are stored
        """
        self.bin_file_path = bin_file_path

    
    def __call__(self, feature_matrix, level):
        """
        Let's make this object callable
        """
    

        self.level = level
        if self.bin_file_path == None:
            self.bin_file_path = os.path.join(os.path.dirname(__file__), "../bin_values_level_{}.xml".format(self.level))
        
        self.feature_matrix = feature_matrix
        self.read_bin_values()

        return self.get_feedback()

    #Done
    def read_bin_values(self):
        """
        Gets the bin values from the specified file path
        """
        f = open(self.bin_file_path, "r")
        bs4 = BS(f, "lxml")

        features = bs4.find_all("feature")
        self.bin_data = []

        for feature in features:
            self.bin_data.append({
                "index" : int(feature.find("feature_index").text),
                "mean"  : float(feature.find("mean").text),
                "std"   : float(feature.find("std").text)
            })

    #TODO: Return a matrix with a numerical code if there should be feedback or not
    def get_feedback(self):
        indicies = [element["index"] for element in self.bin_data]
        indicies = np.array(indicies)
        binning_features = self.feature_matrix[:, indicies][0]

        #1 for positive feedback, -1 for negative feedback, 0 for no feedback
        result = []
        for index in range(len(self.bin_data)):
            #print(binning_features[index])
            if binning_features[index] >= self.bin_data[index]["mean"] + self.bin_data[index]["std"]:
                result.append(1)
            elif binning_features[index] <= self.bin_data[index]["mean"] - self.bin_data[index]["std"]:
                result.append(-1)
            else:
                result.append(0)

            if feature_names[self.bin_data[index]["index"]] == "LA_ER" or feature_names[self.bin_data[index]["index"]] == "LA_COL_ERR_R" or feature_names[self.bin_data[index]["index"]] == "CA_BIN1_R":
                result[-1] = result[-1] * -1 #reverse the feedback for these values.

        return result



    
        
#Done
class BinCalculator(object):

    #Done
    def __init__(self, binning_features, feature_matrix, level):
        """
        Gets the index of the features on which to calculate the binning values
        Params
        binning_features:list(int) -> a list of ints indicating the indecies on the feature matrix of the features to bin on
        feature_matrix:numpy matrix -> the feature matrix used to calculate the actual binning values
        """
        self.binning_features = binning_features
        self.feature_matrix = feature_matrix
        self.level = level

    #Done
    def calculate_binning_values(self):
        """
        Calculates the binning values
        Params:
        feature_matrix: a matrix of which each row contains the feature of each text
        Returns:
        numpy array(3) -> binning values
        """
        #self.feature_matrix = self.get_feature_matrix()

        self.avgs = self.calc_avg(self.feature_matrix[:, self.binning_features])
        self.stdevs = self.calc_std_deviation(self.feature_matrix[:, self.binning_features])
        
        return self.avgs, self.stdevs

    #Done
    def get_binning_values(self):
        """
        Returns a vector with binning thresh holds: mean-std < mean < mean+std <
        """
        self.calculate_binning_values()
        return self.avgs, self.stdevs

    #Done
    def save_binning_values(self, folder="."):
        """
        Saves the binning values on a file with name format: bin_values_level{level}.xml
        """
        filename = "bin_values_level_{}.xml".format(self.level)
    
        self.calculate_binning_values()
        
        if self.binning_features == None or self.avgs.all() == None or self.stdevs.all() == None:
            return

        with open(os.path.join(os.path.dirname(folder), filename), "w") as f:
            f.write("<bin_values level={}>\n".format(self.level))
            f.write("<features>\n")

            for index, value in enumerate(self.binning_features):
                f.write("\t<feature>\n")
                f.write("\t\t<feature_index>\n")
                f.write("\t\t\t{}\n".format(value))
                f.write("\t\t</feature_index>\n")
                f.write("\t\t<mean>\n")
                f.write("\t\t\t{}\n".format(self.avgs[index]))
                f.write("\t\t</mean>\n")
                f.write("\t\t<std>\n")
                f.write("\t\t\t{}\n".format(self.stdevs[index]))
                f.write("\t\t</std>\n")
                f.write("\t</feature>\n")

            f.write("</features>\n")
            f.write("</bin_values>")

    #Done
    def calc_avg(self, feature_matrix):
        return np.mean(feature_matrix.T, axis=1)

    #Done
    def calc_std_deviation(self, feature_matrix):
        return np.std(feature_matrix.T, axis=1)
    
    #Done
    def get_feature_matrix(self):
            return np.load(os.path.join(os.path.dirname(__file__), "../feature_matrices/level_{}_fm.npy".format(self.level)))


"""
if __name__ == "__main__":

    text = open(os.path.join(os.path.dirname(__file__), "../{}".format(sys.argv[1])), "r").read()
    #print(os.path.join(os.path.dirname(__file__), "../{}".format(sys.argv[1])))
    print(text)

    nlp = spacy.load("en_core_web_sm")
    lvf = LexicalVariationFeatures()
    lsf = LexicalSophisticationFeatures()
    feature_collector = FeatureCollector()

    nlp.add_pipe(lvf, name=lvf.name, last=True)
    nlp.add_pipe(lsf, name=lsf.name, last=True)
    nlp.add_pipe(feature_collector, name=feature_collector.name, last=True)

    nlp.remove_pipe('ner')
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')

    doc = nlp(text)

    feature_matrix = feature_collector.get_feature_matrix()
    feature_matrix = np.array(feature_matrix)
    print("Shape of the array: ", feature_matrix.shape)
    #bin_calc = BinCalculator([9, 16], feature_matrix, sys.argv[2])

    #print(bin_calc.get_binning_values())
    #bin_calc.save_binning_values()

    ffe = FormativeFeedbackEvaluator()
    feedback = ffe(feature_matrix, "a1")

    print(feedback)
"""
"""
if __name__ == "__main__":
    features_picked_by_klara = [6, 18, 19, 20, 21, 22, 28, 29, 30, 31, 32, 33]

    level = sys.argv[2]

    feature_matrix = np.load("all_features_1000/feature_matrix_"+level+"_fm.npy")
    print("Shape of matrix:", feature_matrix.shape)
    grades = np.load("all_features_1000/feature_matrix_"+level+"_grades.npy")

    bin_calc = BinCalculator(features_picked_by_klara, feature_matrix, sys.argv[2])

    print(bin_calc.get_binning_values())
    bin_calc.save_binning_values()
    
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", help="Choose mode between: train and debug.Train creates the bins, debug classifies a text.")
    parser.add_argument("--file", help="Pass the text file where the text you want to classify resides.")
    parser.add_argument("--wbs",  help="Use this argument to specify the folder where to store the bins.")
    parser.add_argument("--fms",  help="Specify the path where to find the feature matrices here.")
    parser.add_argument("--level", help="Specify the proficiency level.")
    parser.add_argument("--save_to", help="Specify the folder where to save the bins at.")
    
    #TODO: Specify the feature indices by a parameter. This little shit needs to be passed as string.
    #parser.add_argument("--feature_indices", help="Pass the indicies on which to bin on, e.g. [1, 2, 3, 4].")

    args = parser.parse_args()

    try:
        if args.mode == "train":
            feature_matrix = np.load(args.fms)
            bin_calc = BinCalculator([6, 18, 19, 20, 21, 22, 28, 29, 30, 31, 32, 33], feature_matrix, args.level)
            print(bin_calc.get_binning_values())
            bin_calc.save_binning_values(folder=args.save_to)
        elif args.mode == "debug":
            ffe = FormativeFeedbackEvaluator()
            feature_matrix = np.load(args.fms)
            print(ffe(feature_matrix, args.level))

    except Exception as ve:
        print("One of the mandatory arguments: --fms, --level, --save_to was not provided. Press --help for more info.")
        print(ve)
