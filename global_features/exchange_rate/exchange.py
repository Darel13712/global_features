#%%
from datetime import datetime
from functools import reduce

import pandas as pd

from global_features.base_feature import BaseFeature
from global_features.web_scrapping import open_file_from_web, parse_xml

class Exchange(BaseFeature):
    def __init__(self, date_from=None, date_to=None):
        super(Exchange, self).__init__(date_from, date_to)
        self.currency_code = {'usd': 'R01235', 'euro': 'R01239'}

    def create(self, currencies_list=None):
        if currencies_list is None:
            currencies_list = self.currency_code.keys()
        curr = [self.get_exchange_rate(currency) for currency in currencies_list]
        exchange_rate = reduce(lambda left,right: pd.merge(left,right,on='date'), curr)
        return exchange_rate


    def get_exchange_rate(self, currency):
        '''кодировки от ЦБ:
            http://www.cbr.ru/scripts/XML_val.asp?d=0'''
        code = self.currency_code[currency]
        date = datetime.now().strftime("%d/%m/%Y")
        raw_link = 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=02/03/2001&date_req2='+date+'&VAL_NM_RQ='+code
        xml_file = open_file_from_web(raw_link)
        dates_with_value = parse_xml(xml_file)

        return self.__compile_rate(dates_with_value, currency)


    def __compile_rate(self, dates_with_value, currency):
        rate_col = currency + '_exchange_rate'
        res = pd.DataFrame(dates_with_value, columns=['date', rate_col])
        res[rate_col] = res[rate_col].astype(float)
        res['date'] = pd.to_datetime(res['date'], format='%d.%m.%Y')

        days = pd.date_range(res['date'].min(), datetime.now())
        res = pd.DataFrame(data={'date': days}).merge(res, on='date', how='left')
        res.fillna(method='ffill', inplace=True)
        return res
