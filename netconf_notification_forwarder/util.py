def to_message(data):
    """
    :param data: xml-string
    :return: netconf-message formatted string
    """

    return f"{data}]]>]]>"
