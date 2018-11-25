from datetime import datetime

import pandas as pd
from sklearn.externals import joblib


from global_features.base_feature import BaseFeature
from global_features.util import PACKAGE_ROOT
from global_features.web_scrapping import open_file_from_web


class Holidays(BaseFeature):
    def __init__(self, date_from=None, date_to=None):
        super(Holidays, self).__init__(date_from, date_to)
        self.holidays = joblib.load(PACKAGE_ROOT + '/holidays/holidays.jbl')
        self.translate = {'Пасха': 'Easter',
             'Ураза Байрам': 'UrazaBayram',
             'Курбан Байрам': 'KurbanBayram',
             '8 Марта': 'march8',
             'День Защитника отечества': 'february23',
             'Масленница': 'PancakeWeek',
             'Великий Пост': 'GreatFasting',
             'Рамадан': 'Ramadan',
             'Весенние школьные каникулы': 'SchoolSpringHolidays',
             'Осенние школьные каникулы': 'SchoolAutumnHolidays',
             'Летние школьные каникулы': 'SchoolSummerHolidays',
             'Зимние школьные каникулы': 'SchoolWinterHolidays'}

        self.before_list = ['Пасха', 'Ураза Байрам', 'Курбан Байрам', '8 Марта',
                            'День Защитника отечества', 'Масленница']
        self.period_list = ['Масленница', 'Ураза Байрам', 'Курбан Байрам',
               'Великий Пост', 'Рамадан', 'Весенние школьные каникулы',
               'Осенние школьные каникулы', 'Летние школьные каникулы',
               'Зимние школьные каникулы']

    def create(self):
        days = pd.date_range(datetime(year=2015, month=1, day=1), datetime.now())

        df = pd.DataFrame(data={'date': days})
        df['weekday'] = df['date'].apply(lambda x: x.weekday() + 1)
        df['month'] = df['date'].apply(lambda x: x.month)
        df['weekend'] = 0
        df.loc[df['date'].isin(self.__get_gov_holidays()), 'weekend'] = 1

        df['CristmasFasting'] = self.__apply_on_date(df, self.__CristmasFasting)
        df['days_before_NewYear'] = self.__apply_on_date(df, self.__days_before_NewYear)

        for holiday in self.before_list:
            df['days_before_' + self.translate[holiday]] = self.__calc_feature(df, holiday, self.__days_before_holidays)

        for holiday in self.period_list:
            df[self.translate[holiday]] = self.__calc_feature(df, holiday, self.__holiday_period, True)

        # todo: this mustn't even had been needed to be fixed here in the first place
        df.loc[df['PancakeWeek'] == 1, 'days_before_PancakeWeek'] = 0
        df.loc[df['UrazaBayram'] == 1, 'days_before_UrazaBayram'] = 0
        df.loc[df['KurbanBayram'] == 1, 'days_before_KurbanBayram'] = 0

        return df

    def __get_gov_holidays(self):
        '''Производственный календарь с сайта открытых данных.'''

        link_to_weekends = 'https://data.gov.ru/sites/default/files/proizv_calendar_1999-2025_10.04.18.xlsx'
        file_name = open_file_from_web(link_to_weekends)
        weekends = pd.read_excel(file_name)
        weekends = weekends[weekends.columns[:13]]

        columns = ['year', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        weekends.columns = columns
        weekends_dict = weekends.set_index('year').to_dict()

        weekend_list = []
        for month_key, year_and_days in weekends_dict.items():
            for year_key, days in year_and_days.items():
                all_weekend = days.replace('*', '').split(',')
                for day in all_weekend:
                    weekend_list.append(datetime(year=int(year_key), month=int(month_key),
                                                 day=int(day.replace('+', ''))))
        return weekend_list

    def __get_dates(self, holiday, continuous=False):
        if continuous:
            return self.holidays[self.holidays.title == holiday][['start', 'end']].values
        else:
            return self.holidays[self.holidays.title == holiday].set_index('start').index

    def __apply_on_date(self, df, func, arg=None):
        if arg is None:
            return df['date'].apply(lambda x: func(x))
        else:
            return df['date'].apply(lambda x: func(x, arg))

    def __calc_feature(self, df, name, func, with_end=False):
        return self.__apply_on_date(df, func, self.__get_dates(name, with_end))

    def __days_before_NewYear(self, date):
        next_NewYear = datetime(year=date.year, month=12, day=31)
        days_before_NewYear = (next_NewYear-date).days
        return days_before_NewYear


    def __CristmasFasting(self, date):
        if date >= datetime(year=date.year, month=11, day=28):
            return 1
        if date <= datetime(year=date.year, month=1, day=6):
                return 1
        return 0


    def __get_this_year(self, date, holidays_days):
        that_year_date = holidays_days[holidays_days.year==date.year][0]
        if date <= that_year_date:
            return that_year_date
        if date >= that_year_date:
            return holidays_days[holidays_days.year==(date.year+1)][0]


    def __days_before_holidays(self, date, holidays_days):
        easter_date = self.__get_this_year(date, holidays_days)
        days_before_Easter = (easter_date-date).days
        return days_before_Easter


    def __holiday_period(self, date, weeks):
        for week in weeks:
            if date in pd.date_range(week[0], week[1]):
                return 1
        return 0