import os
from calendar import monthrange

from sklearn.externals import joblib


from global_features.base_feature import BaseFeature
import json

#%%
from global_features.util import PACKAGE_ROOT


class Weather(BaseFeature):
    def __init__(self, date_from=None, date_to=None):
        super(Weather, self).__init__(date_from, date_to)
        with open(PACKAGE_ROOT + '/weather/historical_mean.json', 'r') as f:
            self.historical_mean = json.load(f)
        self.weather = joblib.load(PACKAGE_ROOT + '/weather/weather.jbl')
        self.weather.reset_index(inplace=True)

    #http://www.pogodaiklimat.ru/climate/27612.htm



    def add_weather_mean_feature(self, date, weather_mean_feature):
        return weather_mean_feature[(date.month-1)]

    def create(self):
        weather = self.weather.copy()
        weather['mean_month_t'] = weather['date'].apply(lambda x: self.add_weather_mean_feature(x, self.historical_mean['Moscow']['temperature']))
        weather['mean_month_percipation'] = weather['date'].apply(lambda x: self.add_weather_mean_feature(x, self.historical_mean['Moscow']['percipation']) / monthrange(x.year, x.month)[1])
        weather['mean_month_snow_depth'] = weather['date'].apply(lambda x: self.add_weather_mean_feature(x, self.historical_mean['Moscow']['snow_depth']))
        weather['mean_month_humidity'] = weather['date'].apply(lambda x: self.add_weather_mean_feature(x, self.historical_mean['Moscow']['humidity']))
        weather['pressure_difference'] = weather['pressure'].apply(lambda x: x - 760)
        weather['pressure_shift'] = weather['pressure'] - weather['pressure'].shift().fillna(760)
        weather['t_diff_during_day'] = weather['t_max'] - weather['t_min']
        return weather