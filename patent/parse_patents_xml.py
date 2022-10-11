import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import zipfile
import xml.etree.ElementTree as et
from lxml import etree
import time
from lxml.etree import fromstring
import pathlib
import textwrap
import io
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from tqdm import tqdm

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
# Download and extract patent files
files_failed=[]
for year in range(1976, 2021):
    folder_path='Data/Patent Data/Raw Data/'+str(year)
    if not os.path.exists(folder_path):
        # Create a new directory if it does not exist
        os.makedirs(folder_path)
    folder_url = 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/'+str(year)
    page = requests.get(folder_url)
    html = page.content.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')

    files=[]
    trs = soup.find_all('tr')
    for row in trs:
        for link in row.find_all('a'):
            file_name=link['href']
            if file_name.endswith('zip'):
                files.append(file_name)
    print(files)

    for file in files:
        try:
            file_path = 'Data/Patent Data/Raw Data/'+str(year)+'/'+file
            if not os.path.exists(file_path):
                file_url = 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/'+str(year)+'/'+file
                r = requests.get(file_url, allow_redirects=True)
                open(file_path, 'wb').write(r.content)
                print(file+' has been downloaded')
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
        except:
            print('Failed: '+file)
            files_failed.append(file)
print('# of files failed',len(files_failed))

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
# Parse a single patent (Version 4.x)
file='Patent Data/test_xml3.xml'

xmlp=et.XMLParser(encoding='UTF-8')
parsed_xml=et.parse(file, parser=xmlp)
root=parsed_xml.getroot()

print(root.tag,root.attrib)
print(root[0].tag)
for x in root[0]:
    print(x.tag, x.attrib)

# Patent section name
print(parsed_xml.getroot().attrib['file'])

# ID and publication date
for child in root.findall('us-bibliographic-data-grant'):
    id=child.find('publication-reference').find('document-id').find('doc-number').text
    date=child.find('publication-reference').find('document-id').find('date').text
    print(id,date)

# Description of drawings
for p in parsed_xml.findall('.//description/description-of-drawings/p'):
    # Get all inner text
    description="".join(t for t in p.itertext())
    print(textwrap.fill(description, 100))

# Description
for p in parsed_xml.findall('.//description/p'):
    # Get all inner text
    description="".join(t for t in p.itertext())
    print(textwrap.fill(description, 150))

# Claim text
for child in root.find('claims').findall('claim'):
    claim=child.find('claim-text').text
    print(claim)

#-----------------------------------------------------------------------------------------------------------------------
# Parse all patents in a XML file (Version 4.x)
def parse(data):
    id=""
    date=""
    abstract=""
    drawing=""
    description={}
    parsed_xml = et.ElementTree(et.fromstring(data))
    # ID and publication date
    for child in parsed_xml.findall('.//us-bibliographic-data-grant'):
        id = child.find('publication-reference').find('document-id').find('doc-number').text
        date = child.find('publication-reference').find('document-id').find('date').text

    if id!="":
        # Abstract
        for p in parsed_xml.findall('.//abstract/p'):
            abstract=abstract+" "+"".join(t for t in p.itertext())

        # # Description of drawings
        # for p in parsed_xml.findall('.//description/description-of-drawings/p'):
        #     # Get all inner text
        #     drawing=drawing+" "+"".join(t for t in p.itertext())
        #
        # # Description text
        # output_lst = []
        # for child in parsed_xml.find('.//description'):
        #     output_lst.append(et.tostring(child, encoding="unicode"))
        # output_text = ''.join(output_lst)
        # # Remove <description-of-drawings> section
        # if drawing!="":
        #     output_text = re.sub('<description-of-drawings>.*?</description-of-drawings>', '', output_text, flags=re.DOTALL)
        # # Parse description text by section/heading
        # soup = BeautifulSoup(output_text)
        # for header in soup.find_all('heading'):
        #     heading = str(header.contents[0])
        #     content = ""
        #     nextNode = header
        #     while True:
        #         nextNode = nextNode.nextSibling
        #         if nextNode is None:
        #             break
        #         if isinstance(nextNode, NavigableString):
        #             content = content + " " + nextNode.strip()
        #         if isinstance(nextNode, Tag):
        #             if nextNode.name == "heading":
        #                 break
        #             content = content + " " + nextNode.get_text(strip=True).strip()
        #     description[heading] = content

        # return (id, date, abstract, drawing, description)
        return (id, date, abstract)

results=[]
xml_section = ""
i=0
with open('Data/Patent Data/Raw Data/2021/ipg210105.xml',encoding='utf-8') as temp:
    while True:
        line = temp.readline()
        if line:
            if line.startswith('<?xml'):
                if xml_section:
                    results.append(parse(xml_section))
                    i=i+1
                    print(i)
                xml_section = line.strip()
            else:
                xml_section=xml_section+line.strip()
        else:
            results.append(parse(xml_section))
            i=i+1
            print(i)
            break
print(len(results))
# print(results[0][0],results[0][1])
# print(textwrap.fill(results[1][3], 150))
# print(results[1][4].keys())
# print(textwrap.fill(results[1][4]['SUMMARY'], 150))

df_results=pd.DataFrame(results,columns=['id', 'date', 'abstract', 'drawing', 'description'])
print(df_results.info())

print(df_results.iloc[7482]['description'].keys())
print(textwrap.fill(df_results.iloc[7482]['description']['CROSS-REFERENCE TO RELATED APPLICATION'], 150))

df_results=df_results[df_results['id'].notnull()].reset_index(drop=True)
df_results.to_pickle('Data/Patent Data/Raw Data/2021/ipg210105.pkl')

#-----------------------------------------------------------------------------------------------------------------------
# Parse all XML files in a folder (Version 4.x)
# assign directory
for year in range(2005,2021):
    directory = 'Data/Patent Data/Raw Data/'+str(year)

    # iterate over files in that directory
    for filename in tqdm(os.listdir(directory)):
        if filename.lower().endswith('.xml'):
            file = os.path.join(directory, filename)

            results = []
            xml_section = ""
            with open(file, encoding='utf-8') as temp:
                while True:
                    line = temp.readline()
                    if line:
                        if line.startswith('<?xml'):
                            if xml_section:
                                results.append(parse(xml_section))
                            xml_section = line.strip()
                        else:
                            xml_section = xml_section + line.strip()
                    else:
                        results.append(parse(xml_section))
                        break

            df_results = pd.DataFrame(results, columns=['id', 'date', 'abstract'])
            df_results=df_results[df_results['id'].notnull()].reset_index(drop=True)

            df_results.to_pickle(directory+'/'+filename.replace('.xml','.pkl'))

# Review
df_temp=pd.read_pickle('Data/Patent Data/Raw Data/2021/ipg210302.pkl')
print(df_temp.info())
print(textwrap.fill(df_temp.iloc[1195]['abstract'], 100))


#-----------------------------------------------------------------------------------------------------------------------
# Parse all patents in a XML file (Version 2.x)
def parse2(data):
    id=""
    date=""
    abstract=""
    soup = BeautifulSoup(data)
    # ID and publication date
    id = soup.find('sdobi').find('b100').find('b110').find('dnum').find('pdat').text
    date = soup.find('sdobi').find('b100').find('b140').find('date').find('pdat').text

    if id!="":
        # Abstract
        try:
            abstract = soup.find('sdoab').get_text()
        except:
            pass
        return (id, date, abstract)

results=[]
xml_section = ""
i=0
with open('Data/Patent Data/Raw Data/2001/pg010306.sgm',encoding='utf-8') as temp:
    while True:
        line = temp.readline()
        if line:
            if line.startswith('<!DOCTYPE'):
                if xml_section:
                    results.append(parse2(xml_section))
                    i=i+1
                    print(i)
                xml_section = line.strip()
            else:
                xml_section=xml_section+line.strip()
        else:
            results.append(parse2(xml_section))
            i=i+1
            print(i)
            break
print(len(results))
print(results[0][0],results[0][1])
print(textwrap.fill(results[946][2], 100))

df_results=pd.DataFrame(results,columns=['id', 'date', 'abstract'])
df_results=df_results[df_results['id'].notnull()].reset_index(drop=True)
print(df_results.info())

#-----------------------------------------------------------------------------------------------------------------------
# Parse all XML files in a folder (Version 2.x)
for year in range(2002,2005):
    # assign directory
    directory = 'Data/Patent Data/Raw Data/'+str(year)

    # iterate over files in that directory
    for filename in tqdm(os.listdir(directory)):
        if filename.lower().endswith('.xml'):
            file = os.path.join(directory, filename)
            output_file=os.path.join(directory,re.sub('.xml','.pkl',filename,flags=re.IGNORECASE))

            if not os.path.exists(output_file):
                results = []
                xml_section = ""
                with open(file, encoding='utf-8', errors='ignore') as temp:
                    while True:
                        line = temp.readline()
                        if line:
                            if line.startswith('<?xml'):
                                if xml_section:
                                    results.append(parse2(xml_section))
                                xml_section = line.strip()
                            else:
                                xml_section = xml_section + line.strip()
                        else:
                            results.append(parse2(xml_section))
                            break

                df_results = pd.DataFrame(results, columns=['id', 'date', 'abstract'])
                df_results=df_results[df_results['id'].notnull()].reset_index(drop=True)

                df_results.to_pickle(output_file)

for year in range(2001,2002):
    # assign directory
    directory = 'Data/Patent Data/Raw Data/'+str(year)

    # iterate over files in that directory
    for filename in tqdm(os.listdir(directory)):
        if filename.lower().endswith(('.sgm', '.sgml')):
            file = os.path.join(directory, filename)
            output_file=os.path.join(directory,filename.split('.')[0]+'.pkl')

            #if not os.path.exists(output_file):
            results = []
            xml_section = ""
            with open(file, encoding='utf-8', errors='ignore') as temp:
                while True:
                    line = temp.readline()
                    if line:
                        if line.startswith('<!DOCTYPE'):
                            if xml_section:
                                results.append(parse2(xml_section))
                            xml_section = line.strip()
                        else:
                            xml_section = xml_section + line.strip()
                    else:
                        results.append(parse2(xml_section))
                        break

            df_results = pd.DataFrame(results, columns=['id', 'date', 'abstract'])
            df_results=df_results[df_results['id'].notnull()].reset_index(drop=True)

            df_results.to_pickle(output_file)

# Review
df_temp=pd.read_pickle('Data/Patent Data/Raw Data/2001/pg010508.pkl')
print(df_temp.info())
print(textwrap.fill(df_temp.iloc[1195]['abstract'], 100))

#-----------------------------------------------------------------------------------------------------------------------
# Test Test Test (Version 4.x)
xml_section2 = ""
with open('Data/Patent Data/test_xml_none.xml') as temp:
    while True:
        line = temp.readline()
        if line:
            xml_section2=xml_section2+line.strip()
        else:
            break

id=""
date=""
abstract=""
description=""
parsed_xml = et.ElementTree(et.fromstring(xml_section2))

# Patent section name
print(parsed_xml.getroot().attrib)
print(parsed_xml.getroot().attrib['file'])

# ID and publication date
for child in parsed_xml.findall('.//us-bibliographic-data-grant'):
    id = child.find('publication-reference').find('document-id').find('doc-number').text
    date = child.find('publication-reference').find('document-id').find('date').text

# Description of drawings
for p in parsed_xml.findall('.//description/description-of-drawings/p'):
    # Get all inner text
    drawing="".join(t for t in p.itertext())
    print(textwrap.fill(drawing, 100))

# Description
for p in parsed_xml.findall('.//description/p'):
    # Get all inner text
    description="".join(t for t in p.itertext())
    print(textwrap.fill(description, 150))

# Description text
output_lst = []
for child in parsed_xml.find('.//description'):
    output_lst.append(et.tostring(child, encoding="unicode"))
output_text = ''.join(output_lst)
print(textwrap.fill(output_text, 150))

# Remove description of drawings
output_text=re.sub('<description-of-drawings>.*?</description-of-drawings>', '', output_text, flags=re.DOTALL)
print(textwrap.fill(output_text, 150))

# Parse description text by section
print('* with beautiful soup:')
soup = BeautifulSoup(output_text)
tmp = soup.find_all('heading')
for val in tmp:
    print(val.contents[0])

soup = BeautifulSoup(output_text)
parsed_content={}
for header in soup.find_all('heading'):
    heading=str(header.contents[0])
    content=""
    nextNode = header
    while True:
        nextNode = nextNode.nextSibling
        if nextNode is None:
            break
        if isinstance(nextNode, NavigableString):
            content=content+" "+nextNode.strip()
        if isinstance(nextNode, Tag):
            if nextNode.name == "heading":
                break
            content=content+" "+nextNode.get_text(strip=True).strip()
    parsed_content[heading]=content
print(type(heading), type(content))
print(len(parsed_content), parsed_content.keys())
print(textwrap.fill(parsed_content['Technical Field'], 150))

#-----------------------------------------------------------------------------------------------------------------------
# Test Test Test (Version 2.x)
file='Data/Patent Data/DTDS/test_xml2.xml'
xml_section2 = ""
with open(file, encoding='utf-8') as temp:
    while True:
        line = temp.readline()
        if line:
            xml_section2=xml_section2+line.strip()
        else:
            break

print(parse2(xml_section2))

# Use lxml
parser = etree.XMLParser(load_dtd=True,
                         no_network=False,
                         recover=True)
tree = etree.fromstring(xml_section2.encode('utf-8'), parser=parser)
id = tree.find('SDOBI').find('B100').find('B110').find('DNUM').find('PDAT').text
date = tree.find('SDOBI').find('B100').find('B140').find('DATE').find('PDAT').text
print(id,date)
for p in tree.findall('.//SDOAB/BTEXT/PARA/PTEXT/PDAT'):
    # Get all inner text
    abstract="".join(t for t in p.itertext())
    abstract=re.sub(r'\&\w+;','',abstract)
print(textwrap.fill(abstract, 100))

# Use beatifulsoup
soup = BeautifulSoup(xml_section2)
id=soup.find('sdobi').find('b100').find('b110').find('dnum').find('pdat').text
print(id)
date=soup.find('sdobi').find('b100').find('b140').find('date').find('pdat').text
print(date)
abstract = soup.find('sdoab').get_text()
print(textwrap.fill(abstract, 100))
