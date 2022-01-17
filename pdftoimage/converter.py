import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from PySide6 import QtCore as qtc


def resource_path(relative_path):
    """ 
    Get absolute path to resource, works for dev and for PyInstaller
    Credits to Jonathon Reinhart: https://stackoverflow.com/a/44352931
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Converter(qtc.QObject):

    progress_update = qtc.Signal()

    def __init__(self, input_type, output_type, inputs, output_fdr):
        super().__init__()
        self.input_type = input_type
        self.output_type = output_type
        self.inputs = inputs
        self.output_fdr = output_fdr
        self.poppler_path = resource_path("poppler-bin")

    def pdf2img(self, inputs, output, format):
        for input in inputs:
            convert_from_path(input, output_folder=output, fmt=format, poppler_path=self.poppler_path)
            self.progress_update.emit()

    def im2pdf(self, paths, output):
        imglist = []
        for path in paths:
            with Image.open(path) as im:
                im = im.convert("RGB")
                imglist.append(im)
            self.progress_update.emit()
        img1 = imglist.pop(0)
        img1.save(rf"{output}\converted.pdf", save_all=True, append_images=imglist)

    def run(self):
        if self.input_type == 0: # PDF
            if self.output_type == "jpeg":
                self.pdf2img(self.inputs, self.output_fdr, self.output_type)
        elif self.input_type == 1: # Image
            self.im2pdf(self.inputs, self.output_fdr)
