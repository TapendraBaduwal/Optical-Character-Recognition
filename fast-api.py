from typing import Optional
from fastapi import FastAPI, File, UploadFile
from pdf2image import convert_from_bytes
import numpy as np
import cv2
from pytesseract import image_to_string 
import re      #Rejex help to remove unnecessary  symbols
import logging

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: Optional[UploadFile] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        #return {"filename": file.filename}
        print("filename",file.filename)
        print("filename content type",file.content_type)
        print("filename file",file.file)
        pdf_file = await file.read()
        images = convert_from_bytes(
            pdf_file=pdf_file,
            thread_count=5,
            fmt="jpg",
            )
        numpy_image = np.array(images[0])

        imgray = cv2.cvtColor(numpy_image,cv2.COLOR_BGR2GRAY) # BGR to GRAY
        (thresh, blackAndWhiteImage) = cv2.threshold(imgray, 230, 255, cv2.THRESH_BINARY_INV) # Gray to black and white
        
        ### selecting min size as 25 pixels
        line_min_width = 25
        kernal_h = np.ones((1,line_min_width), np.uint8)
        kernal_v = np.ones((line_min_width,1), np.uint8)

        img_bin_h = cv2.morphologyEx(blackAndWhiteImage, cv2.MORPH_OPEN, kernal_h)
        img_bin_v = cv2.morphologyEx(blackAndWhiteImage, cv2.MORPH_OPEN, kernal_v)
        
        #logical OR to combine above two function
        img_bin_final=img_bin_h|img_bin_v 


        final_kernel=np.ones((3,3), np.uint8)
        img_bin_final=cv2.dilate(img_bin_final,final_kernel,iterations=1)

        _, labels, stats,_ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)     
        
        #Creat list of information from above image
        data ={          #Creat dictionary with key and value with above index
            'Rental location':73,
            'Requestor Phone number':82,
            'email Address':83,
            'Requestor Name':70,
            'GSA Customer Number':75,
            'Agency name':76,
            'Quantitys and Type of Vehicles':77,
            'Date needes':78, 
            'Previous request number':79,
            'Special instruction':80
        
            }
        dic = {}
        for key, value in data.items(): #For loop in dictionary with data.items function
            x,y,w,h,area = stats[value]
            c = numpy_image[y:y+h, x:x+w]
            txt = image_to_string(c, lang='eng')
            txt = re.sub("\n|\x0c|'|vY|Y|\W" ," ",txt) ##Rejex help to remove unnecessary  symbols
            dic[key] = txt
        return {"item_id": dic}



# if __name__=="__main__":
#     unicorn.run("fast-api:app",host='127.0.0.1',port="8000")
        

