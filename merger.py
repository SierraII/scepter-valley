import sys
from PIL import Image

def merge(merge_offset, threads):
    print 'Merging Generated Images.'
    background = Image.open('./images/0.png')

    for x in range(0, threads - 1, merge_offset):
        for y in range(x, x+merge_offset):
            print 'Gathering Thread ' + str(y) + ' Image.'
            foreground = Image.open('./images/' + str(y) + '.png')
            background.paste(foreground, (0, 0), foreground)

    background.save('images/merge_final.png')
