import pandas as pd
import blpapi
import datetime as dt
import numpy as np


class BLP():
    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def __init__(self, date, security, security_data, field_data):
        """
            Improve this
            BLP object initialization
            Synchronus event handling


            ref:
                https://data.bloomberglp.com/labs/sites/2/2013/12/blpapi-developers-guide-1.38.pdf
                https://data.bloomberglp.com/professional/sites/10/2017/03/BLPAPI-Core-Developer-Guide.pdf
                https://bloomberg.github.io/blpapi-docs/python/3.13/index.html
        """
        self.DATE = date
        self.SECURITY = security
        self.SECURITY_DATA = security_data
        self.FIELD_DATA = field_data
        # Create Session object
        self.session = blpapi.Session()

        # Exit if can't start the Session
        if not self.session.start():
            print("Failed to start session.")
            return

        # Open & Get RefData Service or exit if impossible
        if not self.session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            return

        self.session.openService('//BLP/refdata')
        self.refDataSvc = self.session.getService('//BLP/refdata')

        print('Session open')

    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def bdp(self, strSecurity, strFields, strOverrideField='', strOverrideValue=''):

        """
            Summary:
                Reference Data Request ; Real-time if entitled, else delayed values
                Only supports 1 override


            Input:
                strSecurity
                strFields
                strOverrideField
                strOverrideValue

            Output:
               Dict
        """

        # -----------------------------------------------------------------------
        # Create request
        # -----------------------------------------------------------------------

        # Create request
        request = self.refDataSvc.createRequest('ReferenceDataRequest')

        # Put field and securities in list is single field passed
        if type(strFields) == str:
            strFields = [strFields]

        if type(strSecurity) == str:
            strSecurity = [strSecurity]

        # Append list of fields
        for strD in strFields:
            request.append('fields', strD)

        # Append list of securities
        for strS in strSecurity:
            request.append('securities', strS)

        # Add override
        if strOverrideField != '':
            o = request.getElement('overrides').appendElement()
            o.setElement('fieldId', strOverrideField)
            o.setElement('value', strOverrideValue)

        # -----------------------------------------------------------------------
        # Send request
        # -----------------------------------------------------------------------

        requestID = self.session.sendRequest(request)
        print("Sending request")

        # -----------------------------------------------------------------------
        # Receive request
        # -----------------------------------------------------------------------

        list_msg = []

        while True:
            event = self.session.nextEvent()

            # Ignores anything that's not partial or final
            if (event.eventType() != blpapi.event.Event.RESPONSE) & (
                    event.eventType() != blpapi.event.Event.PARTIAL_RESPONSE):
                continue

            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__()
            list_msg.append(msg.getElement(self.SECURITY_DATA))

            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break

                # -----------------------------------------------------------------------
        # Extract the data
        # -----------------------------------------------------------------------
        # creer le disct le plus global
        # create as many empty  dictionaries as field
        for field in strFields:
            globals()['dict_' + field] = {}

        for msg in list_msg:

            for i in range(0, msg.numValues()):
                ticker_name = msg.getValue(i).getElement(self.SECURITY).getValue()
                # recup la security
                field_data = msg.getValue(i).getElement(self.FIELD_DATA)

                for field in strFields:
                    globals()['dict_' + field][ticker_name] = {}

                for j in range(0, field_data.numElements()):
                    field_name = str(field_data.getElement(j).name())
                    field_value = field_data.getElement(j).getValue()

                    globals()['dict_' + field_name][ticker_name] = field_value

        dict_Security_Fields = {}
        for field in strFields:
            dict_Security_Fields[field] = pd.DataFrame.from_dict(globals()['dict_' + field], orient="index",
                                                                 columns=[field])

        return dict_Security_Fields if len(strFields) > 1 else dict_Security_Fields[field]

    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def bdh(self, strSecurity, strFields, startdate, enddate, per='DAILY', perAdj='CALENDAR',
            days='NON_TRADING_WEEKDAYS', fill='PREVIOUS_VALUE', curr='EUR'):
        """
            Summary:
                HistoricalDataRequest ;

                Gets historical data for a set of securities and fields

            Inputs:
                strSecurity: list of str : list of tickers
                strFields: list of str : list of fields, must be static fields (e.g. px_last instead of last_price)
                startdate: date
                enddate
                per: periodicitySelection; daily, monthly, quarterly, semiannually or annually
                perAdj: periodicityAdjustment: ACTUAL, CALENDAR, FISCAL
                curr: string, else default currency is used
                Days: nonTradingDayFillOption : NON_TRADING_WEEKDAYS*, ALL_CALENDAR_DAYS or ACTIVE_DAYS_ONLY
                fill: nonTradingDayFillMethod :  PREVIOUS_VALUE, NIL_VALUE

                Options can be selected these are outlined in “Reference Services and Schemas Guide.”

            Output:
                A list containing as many dataframes as requested fields
            # Partial response : 6
            # Response : 5

        """

        # -----------------------------------------------------------------------
        # Create request
        # -----------------------------------------------------------------------

        # Create request slide 22
        request = self.refDataSvc.createRequest('HistoricalDataRequest')

        # Put field and securities in list is single value is passed
        if type(strFields) == str:
            strFields = [strFields]

        if type(strSecurity) == str:
            strSecurity = [strSecurity]

        # Append list of securities
        for strF in strFields:
            request.append('fields', strF)

        for strS in strSecurity:
            request.append('securities', strS)

        # Set other parameters
        request.set('startDate', startdate.strftime('%Y%m%d'))
        request.set('endDate', enddate.strftime('%Y%m%d'))
        request.set('periodicitySelection', per)
        request.set('currency', curr)
        request.set('nonTradingDayFillMethod', fill)
        request.set('nonTradingDayFillOption', days)
        request.set('periodicityAdjustment', perAdj)

        # -----------------------------------------------------------------------
        # Send request
        # -----------------------------------------------------------------------

        requestID = self.session.sendRequest(request)
        print("Sending request")

        # -----------------------------------------------------------------------
        # Receive request
        # -----------------------------------------------------------------------

        list_msg = []

        while True:
            event = self.session.nextEvent()

            # Ignores anything that's not partial or final
            if (event.eventType() != blpapi.event.Event.RESPONSE) & (
                    event.eventType() != blpapi.event.Event.PARTIAL_RESPONSE):
                continue

            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__()
            # print(msg)
            list_msg.append(msg)

            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break

                # -----------------------------------------------------------------------
        # Exploit data
        # -----------------------------------------------------------------------

        # creer le disct le plus global
        # create as many empty  dictionaries as field
        for field in strFields:
            globals()['dict_' + field] = {}

        for msg in list_msg:

            # recupere partie en bleu cf slides le ticker
            ticker_name = msg.getElement(self.SECURITY_DATA).getElement(self.SECURITY).getValue()
            # renvoie la securities
            field_data = msg.getElement(self.SECURITY_DATA).getElement(self.FIELD_DATA)

            for field in strFields:
                globals()['dict_' + field][ticker_name] = {}

            for i in range(0, field_data.numValues()):

                # recup date et faire une boucle de 1 a nb d'element
                fields = field_data.getValue(i)
                # avoir la date
                dt_date = fields.getElement(self.DATE).getValue()

                for j in range(1, fields.numElements()):
                    # avoir le name du fill
                    field_name = str(fields.getElement(j).name())
                    # avoir la value du fill
                    field_value = fields.getElement(j).getValue()

                    globals()['dict_' + field_name][ticker_name][dt_date] = field_value

        dict_Security_Fields = {}
        for field in strFields:
            dict_Security_Fields[field] = pd.DataFrame(globals()['dict_' + field])

        return dict_Security_Fields if len(strFields) > 1 else dict_Security_Fields[field]

    def bds(self, strSecurity, strFields, strOverrideField='', strOverrideValue='', strEndDate=''):

        """
            Summary:
                Reference Data Request ; Real-time if entitled, else delayed values
                Only supports 1 override


            Input:
                strSecurity
                strFields
                strOverrideField
                strOverrideValue

            Output:
               Dict
        """

        # -----------------------------------------------------------------------
        # Create request
        # -----------------------------------------------------------------------

        # Create request
        request = self.refDataSvc.createRequest('ReferenceDataRequest')

        # Put field and securities in list is single field passed
        if type(strFields) == str:
            strFields = [strFields]

        if type(strSecurity) == str:
            strSecurity = [strSecurity]

        # Append list of fields
        for strD in strFields:
            request.append('fields', strD)

        # Append list of securities
        for strS in strSecurity:
            request.append('securities', strS)

        # Add override
        if strOverrideField != '':
            o = request.getElement('overrides').appendElement()
            o.setElement('fieldId', strOverrideField)
            o.setElement('value', strOverrideValue)


        # -----------------------------------------------------------------------
        # Send request
        # -----------------------------------------------------------------------

        requestID = self.session.sendRequest(request)
        print("Sending request")

        # -----------------------------------------------------------------------
        # Receive request
        # -----------------------------------------------------------------------

        list_msg = []

        while True:
            event = self.session.nextEvent()

            # Ignores anything that's not partial or final
            if (event.eventType() != blpapi.event.Event.RESPONSE) & (
                    event.eventType() != blpapi.event.Event.PARTIAL_RESPONSE):
                continue

            # Extract the response message
            msg = blpapi.event.MessageIterator(event).__next__()
            list_msg.append(msg.getElement(self.SECURITY_DATA))

            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break

                # -----------------------------------------------------------------------
        # Extract the data
        # -----------------------------------------------------------------------
        # creer le disct le plus global
        # create as many empty  dictionaries as field
        for field in strFields:
            globals()['dict_' + field] = {}

        list_index = []
        for msg in list_msg:

            for i in range(0, msg.numValues()):
                ticker_name = msg.getValue(i).getElement(self.SECURITY).getValue()
                # recup la security
                field_data = msg.getValue(i).getElement(self.FIELD_DATA)

                for field in strFields:
                    globals()['dict_' + field][ticker_name] = {}

                for j in range(0, field_data.numElements()):
                    numbers = field_data.getElement(j).numValues()
                    field_name = str(field_data.getElement(j).name())
                    if numbers == 1:
                        field_value = field_data.getElement(j).getValue()
                    else:
                        field_value = [field_data.getElement(j).getValue(num).getElement(0).getValue() for num in range(0, numbers)]

                    globals()['dict_' + field_name][ticker_name] = field_value
                    # if field_data.getElement(j).numValues() > 1:
                    # qi = [field_value.getValue(num) for num in range(0, field_data.getElement(j).numValues())]


        dict_Security_Fields = {}
        for field in strFields:
            dict_Security_Fields[field] = globals()['dict_' + field]# pd.DataFrame.from_dict(globals()['dict_' + field], orient="index")

        return dict_Security_Fields if len(strFields) > 1 else dict_Security_Fields[field]

    def compo_per_date_old(self, strSecurity, strFields, strOverrideField='', strOverrideValue='', strEndDate='', rebal_index=52):
        dico_compo = {}
        start = strOverrideValue
        for security in strSecurity:
            strOverrideValue = start
            while strOverrideValue < strEndDate:
                date_ts = dt.datetime.strftime(strOverrideValue, "%Y%m%d")
                dico_compo[(strOverrideValue, security)] = [self.bds(strSecurity, strFields, strOverrideField=strOverrideField,
                                              strOverrideValue=date_ts, strEndDate=strEndDate)[strFields[-1]][security]]
                strOverrideValue += dt.timedelta(weeks=rebal_index)
        return dico_compo

    def compo_per_date(self, strSecurity, strFields, strOverrideField='', strOverrideValue='', strEndDate='',
                           rebal_index=52):
        list_compo = np.array(self.bds(strSecurity, strFields, strOverrideField=strOverrideField, strOverrideValue=dt.datetime.strftime(strOverrideValue, "%Y%m%d"), strEndDate=strEndDate)[strFields[-1]][
                strSecurity[0]])
        while strOverrideValue < strEndDate:
            strOverrideValue += dt.timedelta(weeks=rebal_index)
            date_ts = dt.datetime.strftime(strOverrideValue, "%Y%m%d")
            list_compo.loc[date_ts] = self.bds(strSecurity, strFields, strOverrideField=strOverrideField,
                                                    strOverrideValue=date_ts, strEndDate=strEndDate)[strFields[-1]][
                strSecurity[0]]


        return list_compo
        """
        dict_Security_Fields = {}
        for field in strFields:
            if type(globals()['dict_' + field][ticker_name]) is float:
                dict_Security_Fields[field] = globals()['dict_' + field][ticker_name]
            else:
                for length in range(len(globals()['dict_' + field][ticker_name])):
                    dict_Security_Fields[field + str(length)] = globals()['dict_' + field][ticker_name][length]
        

        return dict_Security_Fields"""


    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------

    def closeSession(self):
        print("Session closed")
        self.session.stop()

    # blp.bds('RIY Index', "INDX_MWEIGHT", END_DATE_OVERRIDE="20210101")