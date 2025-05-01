#import cv2
from tkinter import filedialog
from tkinter import *
from PIL import Image,ImageTk,ImageDraw
import math
from statistics import *

def select_image():
    global panelA, baseimage, linecanvas, canvas_image, previewcanvas

    path = filedialog.askopenfilename()

    if len(path) > 0:
        #Load original image
        #image = cv2.imread(path)
        #imagergb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #baseimage = Image.fromarray(imagergb).convert('RGBA')
        baseimage = Image.open(path).convert('RGBA')

        #Transparent layer for lines
        linecanvas = Image.new("RGBA", baseimage.size, (0,0,0,0)) #permanent
        previewcanvas = Image.new("RGBA", baseimage.size, (0,0,0,0)) #temp
        
        panelA.tk_image = ImageTk.PhotoImage(baseimage)

        canvas_image = panelA.create_image(0,0,anchor="nw",image=panelA.tk_image)
        panelA.bind('<B1-Button>', clickdown_image)
        panelA.bind('<B1-ButtonRelease>', clickrelease_image)
        panelA.bind('<B1-Motion>', mousemove_image)
        #panelA.bind('<B2-ButtonRelease>', click_zoom)

        update_image()
        #else:
        #    panelA.configure(image=imagetk)
        #    panelA.image = imagetk


def update_image(downpoint=None, lines=None):
    global panelA, baseimage, linecanvas, previewcanvas, canvas_image
    
    merged = Image.alpha_composite(baseimage, linecanvas)
    merged = Image.alpha_composite(merged, previewcanvas)
    panelA.tk_image = ImageTk.PhotoImage(merged)
    panelA.itemconfig(canvas_image, image=panelA.tk_image)
    #panelA.image=tk_image

def draw_temporary_point(x, y):
    global previewcanvas
    previewcanvas = Image.new("RGBA", baseimage.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(previewcanvas)
    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(0, 255, 0, 255))

def clickdown_image(event):
    global mousedown, downpoint
    mousedown=True
    draw_temporary_point(event.x, event.y)
    update_image()
    #update_image(downpoint=downpoint)
    #print("Label clicked", event)
    return

def mousemove_image(event):
    global downpoint, mousedown, draw
    
    if mousedown:
        draw_temporary_point(event.x, event.y)
        update_image()

def clickrelease_image(event):
    global mousedown, linecanvas, linepoints
    mousedown=False

    if event.x < 0 or event.x > panelA.winfo_width() or \
        event.y < 0 or event.y > panelA.winfo_height():
        return
    
    draw = ImageDraw.Draw(linecanvas)
    draw.ellipse((event.x-5, event.y-5, event.x+5, event.y+5), fill=(255,0,0,255))
    linepoints.append((event.x, event.y))
    if len(linepoints) > 0 and len(linepoints) % 3 == 0:
        lines = linepoints[-3:]
        draw.line([lines[0], lines[1]], width=3, fill=(255,0,0,255))
        draw.line([lines[2], lines[1]], width=3, fill=(255,0,0,255))
        
        get_angle(lines)
        #print("Angle between lines: ", get_angle(lines))

    previewcanvas.paste((0,0,0,0),
                        [0,0, previewcanvas.size[0], previewcanvas.size[1]])
    update_image()

def get_angle(lines):
    global angles, summary
    v1 = (lines[1][0] - lines[0][0], lines[1][1]-lines[0][1])
    v2 = (lines[2][0] - lines[1][0], lines[2][1]-lines[1][1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(*v1)
    mag2 = math.hypot(*v2)
    
    if mag1 == 0 or mag2 == 0:
        return None

    cos_theta = dot/(mag1*mag2)
    cos_theta = max(-1.0, min(1.0, cos_theta))

    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    
    table.insert(END, f"{angle_deg:.1f} degrees \n")
    
    angles.append(angle_deg)
    summary.delete("1.0", END)
    summary.insert(END, f"Average: {mean(angles):.2f} \n")
    if len(angles) >= 2: 
        summary.insert(END, f"StDev: {stdev(angles):.2f} \n")
    summary.insert(END, f"Median: {median(angles):.2f} \n")

    return angle_deg

root = Tk()
panelA = None
baseimage = None
imagemask = None
linecanvas = None
mousedown = False
downpoint = None
linepoints = []
angles = []

btn = Button(root, text="Select an image", command=select_image)
btn.pack(side="bottom", fill="both", expand="yes", padx="10", pady="10")
panelA = Canvas(root, width=1600, height=900)
panelA.pack(side="right", padx="10", pady="10", expand=True)

table = Text(root, width=30, height=10)
table.pack()

summary = Text(root, width=30, height=3)
summary.pack()


root.mainloop()
