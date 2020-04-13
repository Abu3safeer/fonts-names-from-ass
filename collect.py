from pathlib import Path
import pysubs2
# subs = Path('.').rglob('*.ass')
#
# for sub in subs:
#     print(str(sub.resolve()))
#     subtitle = open(str(sub.resolve()), mode='r')
#     print(subtitle)

# Where all subtitles will be stored
# The structure will be like this
# { "Fontname[-bold][-italic]" : {  << bold and italic depends on style state
#       "fontname": "FONT_NAME_GOES_HERE",
#       "bold": True or False,
#       "italic": True or False,
#    }
collection = {}

fl = pysubs2.load('subs/Dragon Ball - 001 [SS].ass')
for style in fl.styles:
    fn = fl.styles[style].fontname
    if fl.styles[style].bold:
        fn += "-bold"
    if fl.styles[style].italic:
        fn += "-italic"

    collection.update({fn:{
        "fontname": fl.styles[style].fontname,
        "bold": fl.styles[style].bold,
        "italic": fl.styles[style].italic
    }})

print(collection)