# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from time import time, sleep

import multiprocessing
import colorsys
import shutil
import math
import uuid
import sys
import os

import merger
import styler


class Mandelbrot(object):

    logs = open("./logs/worker_logs.txt", "a")
    max_iteration = 0
    colors_max = 20000
    size = 0

    prev_r = 0
    prev_g = 0
    prev_b = 0

    # timers
    start_time = datetime.now()
    t0 = time()
    t1 = time()

    prev_percent = 0
    curr_precent = 0

    off_x = 0
    off_y = 0

    im = None

    doneInformation = ""

    def __init__(self):
        pass

    def done(self, id, completed_information):
        start = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        fmt = '%Y-%m-%d %H:%M:%S'
        d1 = datetime.strptime(start, fmt)
        d2 = datetime.strptime(end, fmt)

        daysDiff = (d2-d1).days

        # convert days to minutes
        minutesDiff = daysDiff * 24 * 60

        self.doneInformation = ''
        self.doneInformation += str(id) + ' Done. Lifetime: ' + str(minutesDiff) + ' minutes.'

        if completed_information is True:
            self.doneInformation += '\n'
            self.doneInformation += 'Started At: ' + str(start)
            self.doneInformation += '\n'
            self.doneInformation += 'Completed At: ' + str(end)
            self.doneInformation += '\n'

        print self.doneInformation

        fileObject = open("./logs/completed_threads.txt", "a")
        fileObject.write(self.doneInformation)

    def pre(self):
        print ''
        print 'Starting Process ID: {0}'.format(uuid.uuid1())

    def generate(self, x_start, x_end, y_start, y_end, id):

        for i in range(x_start, x_end):

            for j in range(y_start, y_end):

                x = (float(i) / float(100)) * (1.0 / self.zoom) + self.off_x
                y = (float(j) / float(100)) * (1.0 / self.zoom) + self.off_y

                a, b = (0.0, 0.0)
                iteration = 0

                while (a**2 + b**2 <= 4.0 and iteration < self.max_iteration):
                    a, b = a**2 - b**2 + x, 2*a*b + y
                    iteration += 1

                r = 0
                g = 0
                b = 0

                if iteration != self.max_iteration:

                    f = 1-abs((float(iteration+1)/self.colors_max-1)**45)
                    r, g, b = colorsys.hsv_to_rgb(.66+f/3, 1-f/2, .1+f) # 66

                    if r > 255:
                        r = self.prev_r
                    if g > 255:
                        g = self.prev_g
                    if b > 255:
                        b = self.prev_b
                    # less
                    if r < 0:
                        r = self.prev_r
                    if g < 0:
                        g = self.prev_g
                    if b < 0:
                        b = self.prev_b

                self.im.putpixel((i, j), (int(r*255), int(g*255), int(b*255)))

            if self.prev_percent <= i:
                update_time = time()
                update = str((update_time-self.t0)/60) + ' minutes'

                self.perc_done = 100 * float(i)/float(x_end)
                print 'Worker Thread ' + str(id) + ' ' + str(self.perc_done) + '% ' + 'complete.'
                self.logs.write('Worker Thread ' + str(id) + ' ' + str(self.perc_done) + '% ' + 'complete.' + '\n')

                self.prev_percent = i

        # fonts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
        #
        # font = ImageFont.truetype(os.path.join(fonts_path, 'Library/Fonts/Arial.ttf'), 8)
        # draw = ImageDraw.Draw(self.im)

        # draw.text((0, 0),"O[X]: " + str(self.off_x), (255,255,255),font=font)
        # draw.text((0, 10),"O[Y]: " + str(self.off_y), (255,255,255),font=font)
        # draw.text((0, 20),"Zoom: " + str(self.zoom), (255,255,255),font=font)
        # draw.text((0, 30),"Colors: " + str(self.colors_max), (255,255,255),font=font)
        # draw.text((0, 40),"Iterations: " + str(self.max_iteration), (255,255,255),font=font)
        # draw.text((0, 50),"ALU Cycles: " + str(self.t1-self.t0), (255,255,255),font=font)

        self.im.save("./images/" + str(id) + ".png", "PNG")
        self.done('Worker Thread ' + str(id), False)

    def clear(self, folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def start(self, off_x, off_y, zoom, size, block_size, iterations):

        # clear overall logs and images
        self.clear('./logs/')
        self.clear('./images/')

        # main file
        fileObject = open("./logs/rec.txt", "w")
        self.logs = open("./logs/worker_logs.txt", "a")

        self.pre()
        self.off_x = off_x
        self.off_y = off_y
        self.zoom = zoom
        process = None
        self.max_iteration = iterations
        thread_count = 0
        self.size = size
        self.im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        procs = []
        print ''

        for y in range(0, size, block_size):
            for x in range(0, size, block_size):
                process = multiprocessing.Process(target=self.generate, args=(x, x+block_size, y, y+block_size, str(thread_count)))
                procs.append(process)
                process.start()
                print 'Creating Thread: ' + str(thread_count)
                thread_count += 1

        print ''
        self.done('Thread Generation', True)

        merge_offset = size / block_size

        print 'Mandelbrot Size: ' + str(size) + 'px'
        print 'Thread Block Size: ' + str(block_size) + 'px'
        print 'Thread Count: ' + str(thread_count)
        print 'Merge Offset: ' + str(merge_offset) + ' blocks'
        print ''

        fileObject.write('Merge Offset: ' + str(merge_offset) + ' --- Image Count: ' + str(thread_count) + '\n')
        fileObject.write('off_x: ' + str(off_x) + '\n')
        fileObject.write('off_y: ' + str(off_y) + '\n')
        fileObject.write('zoom: ' + str(zoom) + '\n')
        fileObject.write('size: ' + str(size) + '\n')

        process_alive = True

        # wait for all worker processes to finish
        for p in procs:
            p.join()

        print ''
        self.done('Main Worker Process Pool', True)

        merger.merge(merge_offset, thread_count)
        print ''
        self.done('Merge Module', True)

        styler.style("merge_final")
        print ''
        self.done('Style Module', True)

        self.done('Main Thread', True)

# main
if __name__ == "__main__":

    # off_x = -1.2
    # off_y = -0.262
    off_x = -1.768977502791971147240883400847201056595206205552518056225326890392143996579015217439664376119973093588582949354023172297978192092823570966258499146719548846957213673181409910618147135950028450590566715
    off_y = 0.0019400495035209695647102872054426089298508762991118705637984149391509006042298931229502461586535581831240578702073505834331466206165329303974121146956914081239475447299603844106171592790364118096889349

    zoom = 80060.4
    iterations = 200

    size = 800
    block_size = 100

    man = Mandelbrot()
    man.start(off_x, off_y, zoom, size, block_size, iterations)
