import pandas as pd
class BaseFeature():
    def __init__(self, date_from=None, date_to=None):
        self.date_from = self._handle_date(date_from)
        self.date_to = self._handle_date(date_to)

    def _handle_date(self, date):
        if type(date) == str:
            return pd.to_datetime(date, format='%y.%m.%d')

        return date