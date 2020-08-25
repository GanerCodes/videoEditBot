from PIL import Image, ImageDraw, ImageFont, ImageOps
from math import ceil
import textwrap

def drawTextWithOutline(canvas, text, x, y, out, font, outline = True, inColor = (255, 255, 255), outColor = (0, 0, 0), **kwargs):
    out = int(out)
    if outline:
        for i in range(-out, out + 1):
            for o in range(-out, out + 1):
                if (i == 0) or (o == 0):
                    continue
                canvas.text((x + i, y + o), text, outColor, font = font, **kwargs)
    canvas.text((x, y), text, inColor, font = font, **kwargs)
    return

def drawText(img, text, pos, leftAlign = False, mode = "impact", **kwargs):
    canvas = ImageDraw.Draw(img)
    if mode == "impact":
        FS = int((img.width / 6) / (1 + (min(4, len(text) / 58))))
        font = ImageFont.truetype("impact.ttf", FS)
    elif mode == "cap":
        FS = int((img.width / (6 + (len(text) / 10))))
        font = ImageFont.truetype("Futura Condensed Extra Bold.otf", FS)
        kwargs['outline'] = False
        kwargs['inColor'] = (0, 0, 0)
    elif mode == "normalcap":
        FS = int(img.width / 15)
        font = ImageFont.truetype("arialbd.ttf", FS)
        kwargs['outline'] = False
        kwargs['inColor'] = (0, 0, 0)
    else:
        raise Exception("Mode not available!")

    text = textwrap.fill(text, int(2 * img.width / FS))

    for i in [r"\n", '^']:
        text = text.replace(i, ' ' * 100)

    w, h = canvas.textsize(text, font)
    lineCount = 1
    if w > img.width:
        lineCount = int(round((w / img.width) + 1))

    lines = []
    if lineCount > 1:

        lastCut = 0
        isLast = False
        for i in range(lineCount):
            if lastCut == 0:
                cut = (len(text) / lineCount) * i
            else:
                cut = lastCut

            if i < lineCount-1:
                nextCut = (len(text) / lineCount) * (i+1)
            else:
                nextCut = len(text)
                isLast = True

            if nextCut == len(text) or text[int(nextCut)] in [" ", "\n"]:
                pass
            else:
                while (int(nextCut) < len(text) and not text[int(nextCut)] in [" ", "\n"]):
                    nextCut += 1

            line = text[int(cut):int(nextCut)].strip()

            w, h = canvas.textsize(line, font)
            if not isLast and w > img.width:
                nextCut -= 1
                if len(text) > 0:
                    while text[min(int(nextCut), len(text) - 1)] != " ":
                        nextCut -= 1
                        if nextCut < 0:
                            break
            lastCut = nextCut
            lines.append(text[int(cut):int(nextCut)].strip())
    else:
        lines.append(text)

    lastY = -h
    if pos == "bottom":
        lastY = img.height - h * (lineCount+1)

    tmpX = lastY + h

    for i in range(0, lineCount):
        w, h = canvas.textsize(lines[i], font)
        h = h * 1.1
        if leftAlign:
            x = tmpX
        else:
            x = img.width/2 - w/2
        y = lastY + h
        if not leftAlign:
            kwargs["align"] = "center"
        drawTextWithOutline(canvas, lines[i], x, y - (FS / 4 if mode == "impact" else 0), max(2, FS / 25), font, **kwargs)
        lastY = y

def fixSize(i):
    if i.width % 2 == 1 or i.height % 2 == 1:
        return i.resize((2 * (i.width >> 1), 2 * (i.height >> 1)))
    return i

def cropWhite(i):
    return i.crop(ImageOps.invert(i.convert('L')).getbbox())

def pad(i, xPad, yPad, xOff = None, yOff = None, colorMode = "RGB", color = (0, 0, 0)):
    old_size = i.size
    new_size = (old_size[0] + xPad * 2, old_size[1] + yPad * 2)
    new_im = Image.new(colorMode, new_size, color)
    marg = (
        int((new_size[0] - old_size[0]) / 2) if xOff is None else int(xOff), 
        int((new_size[1] - old_size[1]) / 2) if yOff is None else int(yOff)
    )
    new_im.paste(i, marg)
    return new_im

def normalcaption(width, height, cap = None):
    img = Image.new('RGB', (width, height * 2), (255, 255, 255))
    drawText(img, cap, "top", mode = "normalcap", leftAlign = True)
    img = pad(crop:=pad(cropWhite(img), int(width / 60), int(height / 60), color = (255, 255, 255)), int((width - crop.size[0]) / 2), 0, xOff = 0, color = (255, 255, 255))
    return fixSize(img)

def impact(width, height, toptext = None, bottomtext = None):
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    if toptext:    
        invArgs = {}
        if toptext.startswith('^'):
            invArgs['inColor' ] = (0, 0, 0)
            invArgs['outColor'] = (255, 255, 255)
            toptext = toptext[1:]
        drawText(img, toptext   , "top", **invArgs)
    if bottomtext:
        invArgs = {}
        if bottomtext.startswith('^'):
            invArgs['inColor' ] = (0, 0, 0)
            invArgs['outColor'] = (255, 255, 255)
            bottomtext = bottomtext[1:]
        drawText(img, bottomtext, "bottom", **invArgs)
    return img

def poster(width, height, cap = None, bottomcap = None):
    if cap:
        cap = cap.replace('^', '\n')
    if bottomcap:
        bottomcap = bottomcap.replace('^', '\n')

    MP = min(width, height)

    ol = round(MP / 125)

    newSize = (int(width + MP / 10 + ol * 2), 2 * height)

    img = Image.new('RGB', newSize, (0, 0, 0))

    canvas = ImageDraw.Draw(img)

    bb = height + MP / 20 + 2 * ol

    canvas.rectangle([(1 + MP / 20, 1 + MP / 20), (width + MP / 20 + 2 * ol, bb + 1)], fill = "black", width = ol, outline = "white")
    
    bb += int(MP / 40)

    bottom = None
    if cap:
        font = ImageFont.truetype("times", int(MP / 10))
        w, h = canvas.textsize(cap, font = font)
        canvas.text(((newSize[0] - w) / 2, bb), cap, font = font, align = "center")
        bottom = bb + h
    if bottomcap:
        font = ImageFont.truetype("times", int(MP / 20))
        smallW, smallH = canvas.textsize(bottomcap, font = font)
        canvas.text(((newSize[0] - smallW) / 2, nb:=(bottom + 0.02 * MP if bottom else int(bb + MP / 9.5))), bottomcap, font = font, align = "center")
        bottom = nb + smallH

    if cap or bottomcap:
        img = img.crop((0, 0, img.width, bottom + MP / 25))

    return fixSize(img)

def cap(width, height, cap = None):
    img = Image.new('RGB', (width, height * 2), (255, 255, 255, 255))
    drawText(img, cap, "top", mode = "cap")
    crop = cropWhite(img)
    cropSize = crop.size
    img = pad(crop, int((width - cropSize[0]) / 2), int(0.1 * height), color = (255, 255, 255))
    return fixSize(img)