import fitz #pip install PyMuPDF Pillow
import os
import io
from PIL import Image
import spacy
import re
import gensim # pip install "gensim==3.8.1"
from gensim.summarization import summarize
# !spacy download es_core_news_sm
import pdf2image
import pytesseract
from pytesseract import Output


class GET_IMAGES_AND_TEXT_:
    def __init__(self):
        
        self.In_path = input('Enter Input directory path: ')
        self.strt = int(input('Enter start year:'))
        self.end = int(input('Enter end year:'))
        self.Out_Dir = input('Enter Output directory path where data will store: ')
        if not os.path.exists(self.Out_Dir): 
            os.makedirs(self.Out_Dir)
        self.nlp = spacy.load("es_core_news_sm")

        self.main()
        
    def files_path(self, path, year):
        ''' path is the complete path to the dataset
            year is the starting year'''
        # initialize empty list to store links of each file in it
        lst = []
        # inter into dataset and add start year with path to inter into dataset by year
        pth_by_year = path + "\\" + str(year) + "\\"
        # show list of data within the years
        all_files = os.listdir(pth_by_year)
        # loop over the list of data to itterate
        for file in all_files:
            # if file name in years ends with .pdf
            if file.endswith('.pdf'):
                # then create full path to each file
                full_path = pth_by_year +'\\'+ file
                # and append all paths of the files to the empty list
                lst.append(full_path)
            else:
                pass
               
        return lst # it will return all the files paths 
        
    def image_extractor(self, file): 
        dir_ = self.Out_Dir + '\\' + 'Image_Data'
        if not os.path.exists(dir_): 
            os.makedirs(dir_)
        # open the file
        try:
           pdf_file = fitz.open(file)  
           # iterate over PDF pages
           for page_index in range(len(pdf_file)):
               # get the page itself
                page = pdf_file[page_index]
                image_list = page.getImageList()
                # printing number of images found in this page
                if image_list:
                    print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
                else:
                    print("[!] No images found on page", page_index)
                for image_index, img in enumerate(page.getImageList(), start=1):
                    # get the XREF of the image
                    xref = img[0]
                    # extract the image bytes
                    base_image = pdf_file.extractImage(xref)
                    image_bytes = base_image["image"]
                    # get the image extension
                    image_ext = base_image["ext"]
                    if image_ext != 'jpx':
                        # load it to PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        file_name = re.sub('\s', '', file)
                        file_name = file_name.split(os.sep)
                        img_name = file_name[-1]
                        img_name = re.sub('.pdf', '', img_name)
                        fold_name  = dir_ + '\\' + img_name
                        if not os.path.exists(fold_name):
                            os.makedirs(fold_name)
                        image_name = fold_name + '\\' + 'image'
                        # save it to local disk
                        image.save(open(f"{image_name}{page_index+1}_{image_index}.{image_ext}", "wb"))
        except:
            pass
                
    def text_extractor(self, file):
        dir_ = self.Out_Dir + '\\' + 'Text_Data'
        if not os.path.exists(dir_): 
            os.makedirs(dir_)
        Row_text = dir_ + '\\' + 'Row_Data'
        if not os.path.exists(Row_text): 
            os.makedirs(Row_text)
        Min_Clean_text = dir_ + '\\' + 'Min_Clean_Data'
        if not os.path.exists(Min_Clean_text): 
            os.makedirs(Min_Clean_text)
        Cleaned_text = dir_ + '\\' + 'Cleaned_Data'
        if not os.path.exists(Cleaned_text): 
            os.makedirs(Cleaned_text)
        
        try:
            with fitz.open(file) as doc:
                text = ""
                for e, page in enumerate(doc):
                    text += page.getText()
            file_name = file.replace('.pdf', ".txt")
            file_name = re.sub('\s', '', file_name)
            file_name = file_name.split(os.sep)
            if text != "":
                with open(Row_text + '\\' + file_name[-1], 'w') as f:
                    f.write(text)
                text = re.sub('\.\.+', ' ',text) 
                text = re.sub('\s+',' ', text)
                with open(Row_text + '\\' + file_name[-1], 'w') as f:
                    f.write(text)       
                doc = self.nlp(text)
                with open(Min_Clean_text + '\\' + file_name[-1], 'w') as f:
                    for sent in doc.sents:
                        if len(sent) > 5:
                            sent_ = sent.text
                            sent_ = sent_.replace('\n', '')
                            f.write(sent_+ '\n')
                summary = summarize(text)
                with open(Cleaned_text + '\\' + file_name[-1], 'w') as f:
                    f.write(summary)    
            else:
                with open(dir_ + '\\' + "OCRED_FILE_LIST.text", 'w') as f:
                    f.write(file + "\n")
                    
                    
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                text = ""
                images = pdf2image.convert_from_path(file, poppler_path=r'C:\Program Files\poppler-0.68.0_x86\poppler-0.68.0\bin')
                for e, i in enumerate(images):
                    pil_im = images[e] # assuming that we're interested in the first page only
                    ocr_dict = pytesseract.image_to_data(pil_im, lang='spa', output_type=Output.DICT)
                    # ocr_dict now holds all the OCR info including text and location on the image
                    text += " ".join(ocr_dict['text'])
                    
                    
                text = re.sub('\.\.+', ' ',text) 
                text = re.sub('\s+',' ', text)
                with open(Row_text + '\\' + file_name[-1], 'w') as f:
                    f.write(text)       
                doc = self.nlp(text)
                with open(Min_Clean_text + '\\' + file_name[-1], 'w') as f:
                    for sent in doc.sents:
                        if len(sent) > 5:
                            sent_ = sent.text
                            sent_ = sent_.replace('\n', '')
                            f.write(sent_+ '\n')
                summary = summarize(text)
                with open(Cleaned_text + '\\' + file_name[-1], 'w') as f:
                    f.write(summary)   
        except:
            pass
        
    def main(self):
        for year in range(self.strt, self.end+1):
            files_path_gen = self.files_path(self.In_path, year)
            for path in files_path_gen:
                self.image_extractor(path)
                self.text_extractor(path)
            
        
        
GET_IMAGES_AND_TEXT_()



