#%%
import urllib.request
import PyPDF2
import io

#%%
URL = 'https://downloads.regulations.gov/EPA-HQ-OAR-2009-0234-19576/attachment_1.pdf'
req = urllib.request.Request(URL, headers={'User-Agent' : "Magic Browser"})
remote_file = urllib.request.urlopen(req).read()
remote_file_bytes = io.BytesIO(remote_file)
pdfdoc_remote = PyPDF2.PdfFileReader(remote_file_bytes)
# %%
pdfdoc_remote.numPages
# %%
print(pdfdoc_remote)
# %%
for i in range(pdfdoc_remote.numPages):
    current_page = pdfdoc_remote.getPage(i)
    #print("===================")
    #print("Content on page:" + str(i + 1))
    #print("===================")
    #print(current_page.extractText())
    text_file = open("Output.txt", "w")
    text_file.write(current_page.extractText())
    text_file.close()

#############################################

