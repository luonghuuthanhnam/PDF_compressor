from tkinter import *
from pdf2image import convert_from_path
import glob
import cv2
from PIL import Image
import os
import img2pdf
import numpy as np
import shutil
from threading import *
from skimage import io
import sys
from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet
from PDFNetPython import *
import tkinter
from skimage.exposure import is_low_contrast
from tkinter import filedialog
  
# Function for opening the
# file explorer window
def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    return filename

import tkinter as tk
import tkinter.filedialog as fd


# list_pdfs = glob.glob("raw_pdf/*.pdf")
list_pdfs = []

shutil.rmtree('temp_files/resized_imgs')
os.makedirs('temp_files/resized_imgs')

shutil.rmtree('temp_files/temp_pdf')
os.makedirs('temp_files/temp_pdf')

def change_text_block(text_obj, content):
    text_obj.configure(state='normal')
    text_obj.insert('end', content + "\n")
    text_obj.see(tkinter.END)
    text_obj.configure(state='disabled')

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def process(txt_object, scale_percent):
    scale_percent = int(scale_percent)
    change_text_block(txt_object, f"\n**************************\n")
    change_text_block(txt_object, f"Reduce: {scale_percent}%")
    change_text_block(txt_object, f"Keep: {100-scale_percent}%")
    for pdf_name in list_pdfs:
        change_text_block(txt_object, f"Reducing: {pdf_name}")
        images = convert_from_path(pdf_name)
        # images[0].save('test.jpg', 'JPEG')
        # print(images[0].mode)
        for i in range(len(images)):
            name = f"temp_files/resized_imgs/resized_page_{i}.jpg"
            images[i].save(name, 'JPEG')
            img = cv2.imread(name)
            width = int(img.shape[1] * (100-scale_percent) / 100)
            height = int(img.shape[0] * (100-scale_percent) / 100)
            dim = (width, height)
            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            resized = resized[:, :, ::-1].copy()

            # cv2.imwrite( name, resized)
            io.imsave(name, resized)
        list_reized_img = glob.glob("temp_files/resized_imgs/*.jpg")
        sorted_resized_imgs = []
        for i in range(len(list_reized_img)):
            sorted_resized_imgs.append(f"temp_files/resized_imgs/resized_page_{i}.jpg")
        
        pdf_file_name = pdf_name.split("\\")[-1]
        save_pdf = "temp_files\\temp_pdf\\" + pdf_file_name
        with open(save_pdf, "wb") as f:
            f.write(img2pdf.convert(sorted_resized_imgs))

        _output_path = save_pdf.replace("temp_files\\temp_pdf\\", "output\\")
        saved_path = pdf_compressor(save_pdf,_output_path)


        ori_size = os.path.getsize(pdf_name)
        compressed_size = os.path.getsize(saved_path)
        ratio = 1 - (compressed_size / ori_size)

        ori_size = get_size_format(ori_size)
        compressed_size = get_size_format(compressed_size)
        ratio = "{0:.3%}.".format(ratio)
        summary_compression = f"Compress from: {ori_size} to {compressed_size} {[ratio]}"
        change_text_block(txt_object, summary_compression)
        change_text_block(txt_object, f"Saving to: {saved_path}")

        shutil.rmtree('temp_files/resized_imgs')
        os.makedirs('temp_files/resized_imgs')

        shutil.rmtree('temp_files/temp_pdf')
        os.makedirs('temp_files/temp_pdf')

    change_text_block(txt_object, f"***********************")
    change_text_block(txt_object, f"************DONE***********")

        

def pdf_compressor(input_file, output_file):
    file_name = input_file.split("\\")[-1]
    file_name = ".".join(file_name.split(".")[:-1])
    doc = PDFDoc(input_file)
    doc.InitSecurityHandler()
    image_settings = ImageSettings()

    # low quality jpeg compression
    image_settings.SetCompressionMode(ImageSettings.e_jpeg)
    image_settings.SetQuality(4)

    image_settings.ForceRecompression(True)
    opt_settings = OptimizerSettings()
    opt_settings.SetColorImageSettings(image_settings)
    opt_settings.SetGrayscaleImageSettings(image_settings)

    # use the same settings for both color and grayscale images
    Optimizer.Optimize(doc, opt_settings)
    full_save_path = "output\\" + file_name + "_compressed.pdf"
    doc.Save(full_save_path, SDFDoc.e_linearized)
    doc.Close()
    return full_save_path
    

window = Tk()

window.title("Resize pdf")

window.geometry('500x500')

lbl = Label(window, text="Reduce Percentage(%):")

lbl.grid(column=0, row=1)

txt = Entry(window,width=10)
txt.insert(END, "40")

txt.grid(column=1, row=1)

def clicked():
    global Output
    lbl_status.configure(text="Processing...")
    btn.configure(state='disabled')
    scale_percent = txt.get()
    process(Output, scale_percent)
    btn.configure(state='normal')
    lbl_status.configure(text="Ready")

def threading():
    # Call work function
    t1=Thread(target=clicked)
    t1.start()


btn = Button(window, text="Resize", command=threading)

def check_pdf_source():
    global btn
    if len(list_pdfs) == 0:
        change_text_block(Output, "No PDF file(s) selected!")
        btn.configure(state='disabled')
    else:
        change_text_block(Output, "Existing PDF file:")
        btn.configure(state='normal')
    for p in list_pdfs:
        change_text_block(Output, p)
def open_select_file():
    global list_pdfs
    list_pdfs = list(fd.askopenfilenames(parent=window, title='Choose a file'))
    list_pdfs = [p.replace("/","\\") for p in list_pdfs]
    check_pdf_source()
    return list_pdfs

btn_open = Button(window, text="Open", command=open_select_file)

lbl_status = Label(window, text="Hello TraMy")
lbl_status.grid(column=3, row=1)
btn.grid(column=2, row=1)
btn_open.grid(column=0, row=0)

Output = tkinter.Text(window, width=50, state='disabled')
Output.grid(row=2, columnspan=4)
change_text_block(Output, "Hello Tra My\nThis program written by your poor lover")
change_text_block(Output, "************************")

check_pdf_source()

window.mainloop()


