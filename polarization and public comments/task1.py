#%%
import pandas as pd

df = pd.read_csv('org.csv')
# %%
df.head()
# %%
df.columns
# %%
df1 = df[['documentId','title']]
# %%
df1.head()
# %%
df1['org'] = df1['title']
# %%
df1
# %%
df1['org'] = df1['org'].str[21:]
#%%
for x in df1.org:
    for y in len(x):
        print(max(y))
# %%
max1 = [max(len(x)) for x in df1['org']]
# %%
new = df1['org'].str.split(",", n = 3, expand = True)
#%%
new
# %%
