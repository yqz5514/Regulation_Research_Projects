#%%
import pandas as pd
import matplotlib.pyplot as plt

#%%
df = pd.read_excel('FR2022.xlsx')
# %%
df.head()
# %%
df
#%%
df.dtypes
# %%
df = pd.read_csv('TotalPagesFederalRegister_10272022.csv')
# %%
df.head()
# %%
df.head(50)
#%%
df.columns
#%%
df.iloc[5:91,8:9].values
# data type are different 

#%%
new = pd.DataFrame({'year':df.iloc[5:91,0:1].values.tolist(), 'Pages':df.iloc[5:91,8:9].values.tolist()})
#%%
new.
# %%
import matplotlib.pyplot as plt
#%%
plt.figure()
plt.bar(new['year'].values, new['Pages'].values)
plt.ylabel('score')
plt.xlabel('languages')
plt.title('simple bar plot')
plt.show()
# %%
