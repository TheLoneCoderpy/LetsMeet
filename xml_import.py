def get_xml_data() -> dict:
    import xml.etree.ElementTree as ET

    tree = ET.parse("Lets_Meet_Hobbies.xml")
    root = tree.getroot()

    xml_data = {}

    def get_attrib(e, name: str):
        try:
            return e.find(name).text
        except:
            return "<<Empty>>"

    for e in root.findall("user"):
        email = get_attrib(e, "email")
        name = get_attrib(e, "name")
        hobbies = [h.text for h in e.find("hobbies")]
        xml_data[email] = {"name": name, "hobbies": hobbies} # 'heinz.heinrichs@gmaiil.te': {'name': 'Heinrichs, Heinz', 'hobbies': ['Schreiben', 'Musik', 'Bowling']}

    return xml_data