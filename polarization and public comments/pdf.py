#%%
import urllib.request
import PyPDF2
import io

#%%
id = ['EPA-HQ-OAR-2009-0234-19623', 'EPA-HQ-OAR-2011-0044-3761' ,'EPA-HQ-OAR-2011-0044-3817','EPA-HQ-OAR-2011-0081-0094','EPA-HQ-OAR-2011-0081-0095']

#%%
for i in id:
    url = 'https://downloads.regulations.gov/'+i+'/attachment_1.pdf'
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
    remote_file = urllib.request.urlopen(req).read()
    remote_file_bytes = io.BytesIO(remote_file)
    pdfdoc_remote = PyPDF2.PdfFileReader(remote_file_bytes)
    all_text = ''
    for pdf_page in pdfdoc_remote.pages:
           #all_text = ''
           single_page_text = pdf_page.extract_text()
    
           print(single_page_text)
           all_text += '\n' + single_page_text
    
           print(all_text)
           text_file = open(i, "w")
           text_file.write(all_text)
           text_file.close()
#%%
URL = 'https://downloads.regulations.gov/attachment_1.pdf'
req = urllib.request.Request(URL, headers={'User-Agent' : "Magic Browser"})
remote_file = urllib.request.urlopen(req).read()
remote_file_bytes = io.BytesIO(remote_file)
pdfdoc_remote = PyPDF2.PdfFileReader(remote_file_bytes)
# %%
pdfdoc_remote.numPages
# # %%
# print(pdfdoc_remote)
# %%
for i in range(pdfdoc_remote.numPages):
    current_page = pdfdoc_remote.getPage(i)
    print("===================")
    print("Content on page:" + str(i + 1))
    print("===================")
    print(current_page.extractText())
   
    # text_file = open("Output.txt", "w")
    # text_file.write(current_page.extractText())
    # text_file.close()

#############################################


# %%
pageObj = pdfdoc_remote.getPage(0)
print(pageObj.extract_text())

# %%
pdfdoc_remote.pages
# %%
all_text = ''
for pdf_page in pdfdoc_remote.pages:
    single_page_text = pdf_page.extract_text()
    
    print(single_page_text)
    all_text += '\n' + single_page_text
    
    print(all_text)
    text_file = open("New.txt", "w")
    text_file.write(all_text)
    text_file.close()

# %%
# for pdf_page in pdfdoc_remote.pages:
#     single_page_text = pdf_page.extract_text()
    
#     print(single_page_text)
#     #all_text += '\n' + single_page_text
    
#     #print(all_text)
#     text_file = open("New1.txt", "w")
#     text_file.write(single_page_text)
#     text_file.close()

# %%
