from functools import reduce

import pandas as pd

from global_features.base_feature import BaseFeature
from global_features.exchange_rate import Exchange
from global_features.weather import Weather
from global_features.holidays import Holidays


#%%
class GlobalFeatures(BaseFeature):
    def __init__(self, date_from=None, date_to=None):
        super(GlobalFeatures, self).__init__(date_from, date_to)

    def create(self, feature_list=None):
        available_features = ['weather',
                              'exchange',
                              'holidays']
        if feature_list is None:
            feature_list = available_features

        res = []
        for feature in feature_list:
            res.append(self.__create(feature))
        if len(res) > 1:
            res = reduce(lambda left, right: pd.merge(left, right,on='date', how='outer'), res)
        else:
            res = res[0]
        return res


    def __create(self, feature):
        if feature == 'weather':
            f = Weather(self.date_from, self.date_to).create()
        elif feature == 'holidays':
            f = Holidays(self.date_from, self.date_to).create()
        elif feature == 'exchange':
            f = Exchange(self.date_from, self.date_to).create()
        return f




