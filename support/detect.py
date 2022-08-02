import magic, csv, json, xml, string
import xml.etree.ElementTree as ET

'''

Module detects what type of file is fed into the fuzzer
Depends on input file in given as the arguments with the script

'''
def detect(file):

    # Try for JPG
    mime_type = magic.from_file(file, mime=True)
    result = mime_type.split('/')[-1]
    if result == "jpeg":
        return result

    # Try for JSON
    try:
        with open(file) as jsonfile:
            data = json.loads(jsonfile.read())
            return "json"
    except:
        pass

    # Try for XML
    try:
        with open(file) as xmlfile:
            xmlfile.seek(0)
            xmlObj = ET.parse(file)
            return "xml"
    except:
        pass
    
    # Try for CSV
    try:
        with open(file, newline='') as csvfile:
            start = csvfile.read(4096)
            if not all([p in string.printable or p.isprintable() for p in start]):
                pass
            else:
                dialect = csv.Sniffer().sniff(start)
                return "csv"
    except csv.Error:
        pass

    
    # Else return plain
    return "plain"

if __name__ == '__main__':
    print(detect('../tests/inputs/csv1.txt'))
    print(detect('../tests/inputs/csv2.txt'))
    print(detect('../tests/inputs/jpg1.txt'))
    print(detect('../tests/inputs/json1.txt'))
    print(detect('../tests/inputs/json2.txt'))
    print(detect('../tests/inputs/plaintext1.txt'))
    print(detect('../tests/inputs/plaintext2.txt'))
    print(detect('../tests/inputs/plaintext3.txt'))
    print(detect('../tests/inputs/xml1.txt'))
    print(detect('../tests/inputs/xml2.txt'))
    print(detect('../tests/inputs/xml3.txt'))