import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import filters
from tkinter import filedialog as fd

original = Image.open("lenacolor.tif")
image = original

def open_file():
    global original, result, image
    filetypes = (
        ('Tif images', '*.tif'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilename(
        title='Open a file',
        initialdir='/home/ognjen/workingDir/IIP',
        filetypes=filetypes)

    original = Image.open(filenames)
    image = original
    result = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_id,image = result)
 
def plot_histogram():
    global image
    figure = Figure(figsize=(5, 5),
                    dpi=100,
                    facecolor='#282828',
                    edgecolor='w')
    histogram = figure.add_subplot(111, facecolor='#282828')
    graph = filters._histogram(image)

    for side in ['bottom', 'top', 'left', 'right']:
        histogram.spines[side].set_color('white')

    histogram.tick_params(axis='x', colors='white')
    histogram.tick_params(axis='y', colors='white')

    if len(graph) <= 3:
        histogram.plot(graph[0], c='r')
        histogram.plot(graph[1], c='g')
        histogram.plot(graph[2], c='b')
    else:
        histogram.plot(graph, c='white')

    canvas_histogram = FigureCanvasTkAgg(figure, master=canvas)
    canvas_histogram.draw()
    canvas_histogram.get_tk_widget().place(x=712, y=24, height=656, width=656)
  

def apply_brightness():
    global image, result
    brightness_value = slider_brightness.get()
    if brightness_value != 0:
        image = filters.brightness(image, brightness_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_brightness.set(0)

def apply_rotation():
    global image, result
    alpha = slider_alpha.get()
    if alpha != 0:
        image = filters.rotate(image, alpha)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_alpha.set(0)

def apply_median():
    global image, result
    if median_check.get() == 1:
        image = filters.median_filter(image)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        median_check.set(0)

def apply_contrast():
    global image, result
    contrast_value = slider_contrast.get()
    if contrast_value != 0:
        image = filters.contrast(image, contrast_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_contrast.set(0)

def apply_zoom():
    global image, result
    zoom_value = slider_zoom.get()
    if zoom_value != 1:
        image = filters.zoom_in(image, zoom_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_zoom.set(1)

def apply_tilt_shift():
    global image, result, tilt_shift_check
    if tilt_shift_check.get() == '2':
        image = filters.linear_tilt_shift(image)
    elif tilt_shift_check.get() == '3':
        image = filters.radial_tilt_shift(image)
    result = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_id, image=result)
    tilt_shift_check.set('1')

def apply_shadows():
    global image, result
    shadows_value = slider_shadows.get()
    threshold = 100
    if shadows_value != 0:
        image = filters.shadows_highlights(image, shadows_value, threshold)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_shadows.set(0)

def apply_highlights():
    global image, result
    highlights_value = slider_highlights.get()
    threshold = 155
    if highlights_value != 0:
        image = filters.shadows_highlights(image, highlights_value, threshold)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_highlights.set(0)

def apply_vignette():
    global image, result
    if vignette_check.get() == 1:
        image = filters.vignette(image)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        vignette_check.set(0)

def apply_warmth():
    global image, result
    warmth_value = slider_warmth.get()
    if warmth_value != 0:
        image = filters.warmth(image, warmth_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_warmth.set(0)

def apply_saturation():
    global image, result
    saturation_value = slider_saturation.get()
    if saturation_value != 0:
        image = filters.saturation(image, saturation_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_saturation.set(0)

def apply_fade_washed():
    global image, result
    fade_washed_value = slider_fade_washed.get()
    if fade_washed_value != 0:
        image = filters.fade_washed(image, fade_washed_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_fade_washed.set(0)

def apply_fade_white():
    global image, result
    fade_white_value = slider_fade_white.get()
    if fade_white_value != 0:
        image = filters.fade_white(image, fade_white_value)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        slider_fade_white.set(0)

def apply_sharpen():
    global image, result
    if sharpen_check.get() == 1:
        image = filters.sharpen(image)
        result = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_id, image=result)
        sharpen_check.set(0)

def reset():
    global original, result, image
    image = original
    result = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_id, image=result)

# Tkinter window
window = tk.Tk()
window.title("Slide and click Apply!")
window.geometry("1440x1024")
canvas_image = ImageTk.PhotoImage(original)

# Canvas
canvas = tk.Canvas(window, height=700, width=1920, bg='#282828')
canvas.pack()

# Open button
open_button = tk.Button(window, padx = 52, pady = 15, text = 'Open image', command =lambda: [open_file(),plot_histogram()])
open_button.place(x = 1200, y = 730)

# Apply button
apply_btn = tk.Button(window,
                      padx=70,
                      pady=15,
                      text='Apply',
                      command=lambda: [apply_rotation(),
                                       apply_brightness(),
                                       apply_contrast(),
                                       apply_zoom(),
                                       apply_tilt_shift(),
                                       apply_shadows(),
                                       apply_highlights(),
                                       apply_median(),
                                       apply_vignette(),
                                       apply_warmth(),
                                       apply_saturation(),
                                       apply_fade_washed(),
                                       apply_fade_white(),
                                       apply_sharpen(),
                                       plot_histogram()])
apply_btn.place(x = 730, y = 930)

# Brightness slider
slider_brightness = tk.Scale(window,
                             orient='horizontal',
                             label='Brightness',
                             length=300,
                             from_=-100,
                             to=100)
slider_brightness.place(x=20, y=830)

# Rotation slider
slider_alpha = tk.Scale(window,
                        orient='horizontal',
                        label='Angle',
                        length=300,
                        from_=-90,
                        to=90)
slider_alpha.place(x=20, y=710)

# Contrast slider
slider_contrast = tk.Scale(window,
                           orient='horizontal',
                           label='Contrast',
                           length=300,
                           from_=-100,
                           to=100)
slider_contrast.place(x=370, y=950)

# Zoom slider
slider_zoom = tk.Scale(window,
                       orient='horizontal',
                       label='Zoom',
                       length=300,
                       from_=1,
                       to=10)
slider_zoom.place(x=20, y=770)

# Shadows slider
slider_shadows = tk.Scale(window,
                          orient='horizontal',
                          label='Shadows',
                          length=300,
                          from_=-30,
                          to=30)
slider_shadows.place(x=370, y=890)

# Highlights slider
slider_highlights = tk.Scale(window,
                             orient='horizontal',
                             label='Highlights',
                             length=300,
                             from_=-30,
                             to=30)
slider_highlights.place(x=370, y=830)

# Warmth slider
slider_warmth = tk.Scale(window,
                         orient='horizontal',
                         label='Warmth',
                         length=300,
                         from_=-100,
                         to=100)
slider_warmth.place(x=20, y=890)

# Saturation slider
slider_saturation = tk.Scale(window,
                         orient='horizontal',
                         label='Saturation',
                         length=300,
                         from_=-100,
                         to=100)
slider_saturation.place(x=20, y=950)

# Fade (washed out)
slider_fade_washed = tk.Scale(window,
                         orient='horizontal',
                         label='Fade (washed out)',
                         length=300,
                         from_=0,
                         to=100)
slider_fade_washed.place(x=370, y=710)

# Fade (white)
slider_fade_white = tk.Scale(window,
                         orient='horizontal',
                         label='Fade (white)',
                         length=300,
                         from_=0,
                         to=100)
slider_fade_white.place(x=370, y=770)

# Median filter checkbox
median_check = tk.IntVar(window, 0)
check_median_filter = tk.Checkbutton(window,
                                     text='Median filter',
                                     variable=median_check)
check_median_filter.place(x=1000, y=730)

# Vignette checkbox
vignette_check = tk.IntVar(window, 0)
check_vignette = tk.Checkbutton(window,
                                text='Vignette',
                                variable=vignette_check)
check_vignette.place(x=1000, y=790)

# Sharpen checkbox
sharpen_check = tk.IntVar(window, 0)
check_sharpen = tk.Checkbutton(window,
                               text='Sharpen',
                               variable=sharpen_check)
check_sharpen.place(x=1000, y=850)

# Reset button
reset_btn = tk.Button(window,
                      padx=70,
                      pady=15,
                      text='Reset',
                      command=lambda: [reset(), plot_histogram()])
reset_btn.place(x=1200, y=830)

# Tilt shift combo box
tilt_shift_check = tk.StringVar(window, '1')
radio_no_tilt = tk.Radiobutton(window,
                               text='No tilt shift',
                               variable=tilt_shift_check,
                               value='1',
                               font=('arial', 10))
radio_no_tilt.place(x=730, y=730)
radio_linear_tilt = tk.Radiobutton(window,
                                   text='Linear tilt shift',
                                   variable=tilt_shift_check,
                                   value='2',
                                   font=('arial', 10))
radio_linear_tilt.place(x=730, y=790)
radio_radial_tilt = tk.Radiobutton(window,
                                   text='Radial tilt shift',
                                   variable=tilt_shift_check,
                                   value='3',
                                   font=('arial', 10))
radio_radial_tilt.place(x=730, y=850)

# Quit button
quit_btn = tk.Button(window,
                     padx=72,
                     pady=15,
                     text='Quit',
                     command=quit)
quit_btn.place(x=1200, y=930)

image_id = canvas.create_image(356, 356, image=canvas_image)
plot_histogram()
window.mainloop()

