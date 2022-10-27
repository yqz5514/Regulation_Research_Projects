#%%
import xml.etree.ElementTree as ET
# %%
with open('pg020101.xml','r') as f:
    text = f.read()
# %%
tree = ET.parse(text)
root = tree.getroot()
# %%
root1 = ET.fromstring()