import data
import random
from copy import deepcopy

import tkinter
import tkinter.ttk as ttk
import time

class MyDisplay(ttk.Frame):
    def __init__(self, name='leftRow'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=tkinter.Y, fill=tkinter.BOTH)
        self.master.title('leftRow')

        self.panel = ttk.Frame(self, name='leftRow')
        self.panel.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.Y)
        self.nb = ttk.Notebook(self.panel, name='notebook')
        self.nb.enable_traversal()
        self.nb.pack(fill=tkinter.BOTH, expand=tkinter.Y, padx=2, pady=3)

        #container for images
        self.images=[]
        self.save_to_file=False
        
        #hide for now
        self._root().iconify()
        self._root().withdraw()
        
    def add_tab(self,P,tab_name="def"):
        img=self._create_image(P)
        self.images.append(tuple([img,tab_name]))

        if self.save_to_file:
            #writes image to file
            img.write(tab_name+time.strftime("%y-%m-%d_%H-%M-%S")+'.gif', format='gif')

        self._root().withdraw()
        
    def _prepare(self,_P):
        P=deepcopy(_P)
        for y in range(len(P)):
            for x in range(len(P[0])):
                piksel = P[y][x]*255
                P[y][x] = (piksel,piksel,piksel)
        return P

    def _create_image(self,matrix):
        matrix=self._prepare(matrix)
        
        width = len(matrix[0])
        height = len(matrix)

        pixel_pattern = "#%02x%02x%02x"

        str_rows = []
        for row in matrix:
            if len(row) != width:
                raise AssertionError("All rows must be of same length")
            
            str_pixels = []
            for pixel in row:
                str_pixels.append("#%02x%02x%02x" % pixel)
            str_rows.append("{" + " ".join(str_pixels) + "}")

        img = tkinter.PhotoImage(width=width, height=height)
        img.put(" ".join(str_rows))

        return img

    #blocks
    def show(self):
        self._create_tab_content()
        self._root().deiconify()
        self._root().mainloop()

    def _create_tab_content(self):
        for img,tab_name in self.images:
            if len(tab_name)==0:
                tab_name="tab"
            frame = ttk.Frame(self.nb)
            self.nb.add(frame, text=tab_name)
            label = tkinter.Label(frame,image=img)
            label.pack()
            self.nb.pack()
        

if __name__ == '__main__':
    d=MyDisplay()

    pilt=data.read_instance_from_file('evil-2.img')
    d.add_tab(pilt,"pic1")
    for y in range(len(pilt)):
        for x in range(len(pilt[0])):
            piksel = pilt[y][x]*0.5
            pilt[y][x] = piksel
    d.add_tab(pilt,"pic2")
    d.show()
    
