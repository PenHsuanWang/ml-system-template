import pickle

from ml_system.controller.data_acq_controller import DataAcquisitorController
from ml_system.tools.data_loader import CsvDataLoader

from ml_system.tools.model import XGBoostClassifier, SklearnRandonForest, RFAdaptiveHoeffdingClassifier
from ml_system.tools.model_performance_tester import OnlineMLTestRunner

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class MachineLearningServer:

    """
    Machine Learning System implements AI/ML Solutions as software system
    Which is consisted by following functionalities
    1. Data Ingress
    2. AI/ML Model Training
    3. AI/ML Model Serving
    4. Model performance inspection
    5. Controlling various pipeline w.r.t. Model action.

    MachineLearningServer is designed as main process which holding on various controller and servicer.
    The controller is responsible for coordinating object, i.e. the interface between server and various objects.
    including 1. Model; 2. Data Acquisitor.
    The servicer is responsible for maintain the core parts of AI/ML services.
    including 1. Data Acquisition services; 2. Model Training services; 3. Model Inference Serving; 4. Performance Monitor.



    """

    def __init__(self):

        # Controller
        self.__data_acq_controller = DataAcquisitorController.get_instance()
        self.__data_acq_servicer = None
        self.__model_controller = None
        self.__model_serving = None

        #TODO temporary experiment model object, should be removed in the future and using model_controller
        self._model = None
        # Servicer


        # repository
        self.__handling_data_acq = {}
        self.__handling_model_list = {}

        #init object needed
        # self._init_data_daq()
        self._init_model(
            n_estimators=10,
            max_depth=5,
            verbose=1
        )




    def _init_model(self, *args, **kwargs):
        # self._model = SklearnRandonForest(*args, **kwargs)
        self._model = RFAdaptiveHoeffdingClassifier(
            max_depth=5,
            split_criterion='gini',
            split_confidence=1e-2,
            grace_period=1000,
            seed=0
        )
        # self._model = XGBoostClassifier(
        #     verbosity=3,
        #     n_estimators=10,
        #     max_depth=5
        # )


    def _init_data_daq(self):

        # preparing data acquisitor here
        self.__data_acq_controller.create_data_acq(
            data_source_type='kafka',
            data_acq_name='kafka_1',
            bootstrap_server='localhost:9092',
            topic='testTopic'
        )


    def run(self):

        # start the servicer by controller
        # self.__data_acq_controller.run_data_acq_by_servicer('kafka_1', auto_retry_times=1)

        csv_data_loader = CsvDataLoader(data_path='../../data/hospital/aggregate_data_training_202001_to_202006.csv')
        training_df = csv_data_loader.get_df(do_label_encoder=True)
        training_y = training_df.pop('SEPSIS')

        # x_train, x_test, y_train, y_test = train_test_split(df, y, test_size=0.3, random_state=0)

        self._model.fit(training_df, training_y)

        out_file_name = '../../model_persist/hospital_hoeffding_tree_classifier.pickle'
        with open(out_file_name, 'wb') as out_file:
            try:
                pickle.dump(self._model, out_file)
            except Exception as e:
                e.with_traceback()
                print("model persisting error, can not save model into file {}. Please check!".format(out_file_name))

        data_path_list = [
            '../../data/hospital/aggregate_data_testing_202007_to_202008.csv',
            '../../data/hospital/aggregate_data_testing_202008_to_202009.csv',
            '../../data/hospital/aggregate_data_testing_202009_to_202010.csv',
            '../../data/hospital/aggregate_data_testing_202010_to_202011.csv',
            '../../data/hospital/aggregate_data_testing_202011_to_202012.csv',
            '../../data/hospital/aggregate_data_testing_202012_to_202201.csv'
        ]

        model_tester = OnlineMLTestRunner()

        model_tester\
            .set_model(self._model)\
            .set_testing_dataset(data_path_list)\
            .set_label('SEPSIS')

        model_tester.run_model_tester()

        # csv_data_loader = CsvDataLoader(data_path='../../data/hospital/aggregate_data_testing_202007_to_202008.csv')
        # testing_df = csv_data_loader.get_df(do_label_encoder=True)
        # testing_y = testing_df.pop('SEPSIS')
        # predict_result = self._model.predict(testing_df)
        #
        # acc = accuracy_score(testing_y, predict_result)
        # print("Accuracy: {}".format(acc))

        # # data_acq_services = threading.Thread(target=data_acq.run)
        # # data_acq_services.start()
        # data_fetcher = self.__data_acq_controller.get_data_acq('kafka_1').get_data_fetcher()
        # data_accumulator = []
        # while True:
        #     try:
        #         data_accumulator.extend(next(data_fetcher))
        #         if len(data_accumulator) >= 2000:
        #             df = pd.DataFrame(data_accumulator)
        #             print(df)
        #             x = df
        #             y = df.pop('Y')
        #             # going to do model fitting
        #             self._model.fit(x, y)
        #         else:
        #             print('current data rows:{} keep accumulating until: 2000'.format(len(data_accumulator)))
        #
        #
        #     except StopIteration:
        #         print('Stop data acq')

if __name__ == '__main__':

    mls = MachineLearningServer()
    mls.run()



    # #TODO: implement model
    # def _start_training_model(self):
    #
    #     self._model = None
    #
    #     data = self._data_fetcher.get_data()
    #     self._model.fit(data)

