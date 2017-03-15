from PIL import Image, ImageOps

def style(final):

    print 'Styling Image.'
    orig = Image.open('./images/' + final + '.png')

    img = Image.open('./images/' + final + '.png').convert('LA')
    img.save('./images/greyscale.png')
    print 'Grey Scale Styling Done.'

    if orig.mode == 'RGBA':
        r, g, b, a = orig.split()
        rgb_image = Image.merge('RGB', (r,g,b))

        inverted_image = ImageOps.invert(rgb_image)

        r2, g2, b2 = inverted_image.split()

        final_transparent_image = Image.merge('RGBA', (r2, g2, b2, a))

        final_transparent_image.save('./images/inverted_image.png')

    else:

        inverted_image = ImageOps.invert(image)
        inverted_image.save('./images/inverted_image.png')

    print 'Invert Styling Done.'

    img = Image.open('./images/inverted_image.png').convert('LA')
    img.save('images/greyscale_inverted.png')
    print 'Greyscale Inverting Styling Done.'

    imin = Image.open('./images/inverted_image.png')
    imout = Image.new('RGBA', imin.size)

    imout.putdata(map(lambda pixel: (0, 0, 0) if pixel == (255, 255, 255) else pixel, imin.getdata()))

    imout.save('./images/invert_black.png')
    print 'Inverted Black Override Styling Done.'
