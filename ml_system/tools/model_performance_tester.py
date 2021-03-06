
from abc import ABC
import pandas as pd
import os
from tqdm import tqdm
import pickle

import numpy as np

from ml_system.tools.model import RFAdaptiveHoeffdingClassifier
from ml_system.tools.data_loader import CsvDataLoader

from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score


class ModelTester(ABC):
    """
    ModelTester, an abstraction class for tester pipeline and architecture and corresponding api.
    provided api `set_model`to put desired model to be tested, `set_testing_dataset` to set test data. `set_label` provided label column name
    """

    def __init__(self):
        self._model = None
        self._testing_data_path_list = []
        self._label = ''

    def set_model(self, model: object):
        self._model = model
        return self

    def set_testing_dataset(self, testing_data_path: list):
        for f in testing_data_path:
            if os.path.isfile(f):
                pass
            else:
                raise FileNotFoundError('The file {} in the provided list not found!, please check'.format(f))
        self._testing_data_path_list = testing_data_path
        return self

    def set_label(self, label: str):
        self._label = label




class OnlineMLPredictor(ModelTester):

    def __init__(self):
        super(OnlineMLPredictor).__init__()

    def run_predict_true_class(self, predict_proba_cut_point=0.5):

        for f in self._testing_data_path_list:
            print(f)

            csv_data_loader = CsvDataLoader(data_path=f)
            df = csv_data_loader.get_df(do_label_encoder=True)
            y = df.pop(self._label)

            # if isinstance(self._model, RFAdaptiveHoeffdingClassifier):
            predict_is_true = self._model.predict(df, pred_proba_cut_point=predict_proba_cut_point)
            # else:
            #     predict_is_true = []
            #
            #     for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            #
            #
            #         predict_result = self._model.predict_proba_one(row)
            #         if isinstance(predict_result, dict):
            #             if predict_result.get(1) > predict_proba_cut_point:
            #                 predict_is_true.append(1)
            #             else:
            #                 predict_is_true.append(0)

            yield predict_is_true, y

    def run_predict_proba_distribution_checker(self, fig_save_path='./temp_prediction_proba_distribution.png'):

        for f in self._testing_data_path_list:

            csv_data_loader = CsvDataLoader(data_path=f)
            df = csv_data_loader.get_df(do_label_encoder=True)
            y = df.pop(self._label)

            predict_proba = self._model.predict_proba(df)

            # print(predict_proba)
            fig = self.draw_analyze_proba_distribution(np.array(predict_proba), y)
            fig.savefig(fig_save_path)

    @staticmethod
    def draw_analyze_proba_distribution(pred_proba: np.array, is_target_list: pd.Series):

        from matplotlib import pyplot as plt

        pred_proba_result_true_class = pred_proba[is_target_list == 1]
        pred_proba_result_false_class = pred_proba[is_target_list == 0]

        fig = plt.figure(figsize=(14, 4))
        fig.suptitle('{}pred_proba_distribution'.format(''))
        plt.subplot(131)
        plt.hist(pred_proba_result_true_class, bins=50, alpha=0.5, label='Y True')
        plt.hist(pred_proba_result_false_class, bins=50, alpha=0.5, label='Y False')
        plt.yscale('log')
        plt.title('stacking prediction proba in both class')
        plt.xlabel('pred proba')
        plt.ylabel('statistics')
        plt.grid()
        plt.legend()
        plt.subplot(132)
        plt.hist(pred_proba_result_true_class, bins=50)
        plt.yscale('log')
        plt.title('Y True class prediction proba. dist.')
        plt.xlabel('pred proba')
        plt.ylabel('statistics')
        plt.grid()
        plt.subplot(133)
        plt.hist(pred_proba_result_false_class, bins=50)
        plt.yscale('log')
        plt.title('Y False class prediction proba. dist.')
        plt.xlabel('pred proba')
        plt.ylabel('statistics')
        plt.grid()
        return fig



class OnlineMLTestRunner(OnlineMLPredictor):

    def __init__(self):
        super(OnlineMLTestRunner).__init__()


    def run_model_tester(self):

        for pred_list, y in self.run_predict_true_class():
            acc = accuracy_score(y, pred_list)
            recall = recall_score(y, pred_list)
            precision = precision_score(y, pred_list)
            f1 = f1_score(y, pred_list)

            print("accuracy: {} \nrecall: {} \nprecision: {}\nf1: {}".format(acc, recall, precision, f1))


if __name__ == '__main__':
    data_path_list = [
        '../../data/hospital/aggregate_data_testing_202007_to_202008.csv'
    ]
    with open('../../model_persist/hospital_hoeffding_tree_classifier.pickle', 'rb') as f:
        model = pickle.load(f)



    model_tester = OnlineMLTestRunner()

    model_tester\
        .set_model(model)\
        .set_testing_dataset(data_path_list)\
        .set_label('SEPSIS')

    model_tester.run_model_tester()
    # model_tester.run_predict_proba_distribution_checker()






