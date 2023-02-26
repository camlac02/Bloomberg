def bds_v2(self, strTicker, strFields, startdate, enddate, strOverrideField='', strOverrideValue=''):
    # Créer une requête pour les prix de clôture de l'indice S&P 500
    request = self.refDataSvc.createRequest('HistoricalDataRequest')
    # request.getElement("securities").appendValue("SPX Index")
    request.getElement("securities").appendValue(strTicker)
    request.getElement("fields").appendValue(strFields)
    start_date = startdate
    end_date = enddate
    request.set("startDate", start_date.strftime("%Y%m%d"))
    request.set("endDate", end_date.strftime("%Y%m%d"))

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
        list_msg.append(msg.getElement(SECURITY_DATA))

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
            ticker_name = msg.getValue(i).getElement(SECURITY).getValue()
            # recup la security
            field_data = msg.getValue(i).getElement(FIELD_DATA)

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