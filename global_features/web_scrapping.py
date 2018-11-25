import urllib
from xml.dom import minidom


def open_file_from_web(link):
    file_name, headers = urllib.request.urlretrieve(link)
    return file_name


def parse_xml(xml_file):
    dom = minidom.parse(xml_file)
    dom.normalize()

    dates_with_value = []

    nodeArray=dom.getElementsByTagName("Record")
    for node in nodeArray:
        date = (node.getAttribute('Date'))
        childList=node.childNodes
        for child in childList:
            value = child.childNodes[0].nodeValue.replace(',', '.')
            if float(value) != 1:
                dates_with_value.append([date, value])

    return dates_with_value