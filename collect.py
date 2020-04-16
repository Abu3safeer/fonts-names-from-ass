import logging
from pathlib import Path
import pysubs2
import ass_tag_parser

# Start preparing the logger
logger = logging.getLogger('collector')  # Initialize new logger
logger.setLevel(1)  # Set the main logger level to the lowest, this will show all messages by default
logger_formatter = logging.Formatter('%(asctime)s: %(levelname)s : ~ %(message)s')  # Setup custom logger message
file_handler = logging.FileHandler('log.txt', encoding='utf-8')  # Setup file handler where logs will be stored
file_handler.setLevel(logging.DEBUG)  # Set file handler log level
file_handler.setFormatter(logger_formatter)  # Assign the custom format to warning file handler
warning_file_handler = logging.FileHandler('warnings.txt', encoding='utf-8')  # Setup warning file handler where logs will be stored
warning_file_handler.setLevel(logging.WARNING)  # Set warning file handler log level
warning_file_handler.setFormatter(logger_formatter)  # Assign the custom format to file handler
stream_handler = logging.StreamHandler()  # Setup Stream handler
stream_handler.setLevel(logging.INFO)  # Set stream handler log level
stream_handler.setFormatter(logger_formatter)  # Assign Custom format to stream handler
logger.addHandler(file_handler)  # Add file handler to the logger
logger.addHandler(warning_file_handler)  # Add file handler to the logger
logger.addHandler(stream_handler)  # Add stream handler to the logger
# End preparing the logger

# The collection variable is where organized data will be stored.
# The structure will be:
# { 'Fontname[-bold][-italic]' : {  # bold and italic depends on style state
#       'fontname': "FONT_NAME_GOES_HERE",
#       'bold': True or False,
#       'italic': True or False,
#       'characters': 'abcde...'
#    }
collection = {}

# This list will store data temporarily, and set for characters
collected_fonts_container = []
character_set = []

# Here all full path subtitles files will be stores
subtitles_full_path = []

# Get all ass files in directory and sub directories
subs = Path('.').rglob('*.ass')
for subtitle in subs:
    subtitles_full_path.append(str(subtitle.resolve()))

# Check if there any ass files found
if len(subtitles_full_path) > 0:
    logger.debug('Found {ASS_FILES_COUNT} ass files, They are {ASS_FILES_LIST}'.format_map({
        'ASS_FILES_COUNT': len(subtitles_full_path),
        'ASS_FILES_LIST': str(subtitles_full_path),
    }))
else:
    logger.warning('Cannot find any ass files.')
    exit()


# For each subtitle file
for full_file_path in subtitles_full_path:

    # Logging the current file
    logger.debug('Working on file {FILE_NAME}'.format_map({'FILE_NAME': full_file_path}))

    try:
        # Load the subtitle file and parse it
        fl = pysubs2.load(full_file_path)
        logger.debug('Loaded the file successfully.')

        logger.debug('File "{FILE_NAME}" has "{STYLES_NUMBER}" styles, and there names are \n"{STYLES_LIST}"'.format_map({
            'FILE_NAME': full_file_path,
            'STYLES_NUMBER': len(fl.styles),
            'STYLES_LIST': list(fl.styles)
        }))

        # For each Dialogue in the subtitle file
        for event in fl.events:

            # Make sure the event is a Dialogue and check if the Dialogue is not empty
            if event.type == 'Dialogue' and len(event.text) > 0:

                logger.debug('Processing Dialogue: "{DIALOGUE}"'.format_map({
                    'DIALOGUE': str(event.text)
                }))

                # Prepare font properties
                current_font = {
                    'fontname': None,
                    'bold': False,
                    'italic': False
                }
                # Check if Style in Dialogue is in Styles list
                if event.style not in fl.styles.keys():

                    # If the style used in this Dialogue is not in styles, then show this warning
                    logger.warning('Style "{STYLE_NAME}" is not in \n"{STYLES_LIST}",\n'
                                   'This Style used in "{EVENT_TYPE}" '
                                   'with this content \n"{EVENT_CONTENT}",\n'
                                   'found in file with this name: "{FILE_NAME}"'.format_map(
                        {
                            'STYLE_NAME': event.style,
                            'STYLES_LIST': list(fl.styles.keys()),
                            'EVENT_TYPE': event.type,
                            'EVENT_CONTENT': event,
                            'FILE_NAME': full_file_path,
                        }))
                else:

                    # Prepare font date
                    current_font['fontname'] = fl.styles[event.style].fontname
                    current_font['bold'] = fl.styles[event.style].bold
                    current_font['italic'] = fl.styles[event.style].italic

                try:
                    # Parsing the Dialogue
                    ass_tags = ass_tag_parser.parse_ass(event.text)

                    # Paring each tag individually
                    for tag in ass_tags:

                        # Check if tag is AssTagResetStyle, this tag does one thing of two:
                        # 1 - Use the style of Dialogue.
                        # 2 - Assign a style from Style list in the ass file.
                        if type(tag) == ass_tag_parser.AssTagResetStyle:
                            # If style name is not present, then use the Dialogue style
                            if (tag.style is None) or (type(tag.style) == str and len(tag.style) < 1):
                                current_font['fontname'] = fl.styles[event.style].fontname
                                current_font['bold'] = fl.styles[event.style].bold
                                current_font['italic'] = fl.styles[event.style].italic

                            # If style name is present, use it.
                            elif type(tag.style) == str and len(tag.style) > 0:

                                # If the style name is not in style list
                                if tag.style not in fl.styles:
                                    logger.warning('The Dialogue \n"{DIALOGUE_TEXT}"\n has {RESET_TAG} tag, '
                                                   'This tag tried to set style to {R_TAG_STYLE_NAME}, '
                                                   'But {R_TAG_STYLE_NAME} is not is \n{STYLES_LIST},\n'
                                                   'in file {FILE_NAME}'
                                                   .format_map({
                                                        'DIALOGUE_TEXT': event.text,
                                                        'R_TAG': r'{\r}',
                                                        'R_TAG_STYLE_NAME': tag.style,
                                                        'STYLES_LIST': list(fl.styles),
                                                        'FILE_NAME': full_file_path,
                                                    }))
                                # Otherwise the style must be in the style list, then use it.
                                else:
                                    current_font['fontname'] = fl.styles[tag.style].fontname
                                    current_font['bold'] = fl.styles[tag.style].bold
                                    current_font['italic'] = fl.styles[tag.style].italic

                        if type(tag) == ass_tag_parser.AssTagBold:
                            current_font['bold'] = tag.enabled
                        elif type(tag) == ass_tag_parser.AssTagItalic:
                            current_font['italic'] = tag.enabled
                        elif type(tag) == ass_tag_parser.AssTagFontName:
                            current_font['fontname'] = tag.name
                        elif type(tag) == ass_tag_parser.AssText:
                            # Check if text is not empty
                            if len(tag.text) > 0:
                                # If no font name selected then style does not exists
                                # Note: if font name is not defined here, then the style itself
                                # does not exists! so it should just through the error.
                                if current_font['fontname'] is None:
                                    # If there is not style selected, Just additional check
                                    if event.style not in fl.styles:
                                        logger.warning('Dialogue with this text \n"{DIALOGUE_TEXT}"\n'
                                                       ' has a style named "{STYLE_NAME}"'
                                                       ', but "{STYLE_NAME}" does not exists in '
                                                       '\n{STYLES_LIST}\n in file "{FILE_NAME}"'
                                                       .format_map({
                                                            'DIALOGUE_TEXT': event.text,
                                                            'STYLE_NAME': event.style,
                                                            'STYLES_LIST': list(fl.styles),
                                                            'FILE_NAME': full_file_path,
                                                        }))
                                    else:
                                        # This assignment is not supposed to be here
                                        # Because We already have check font name in style list
                                        # But just in case i put this check here, though it is not logical.
                                        current_font['fontname'] = event.style

                                # If there is a font
                                else:

                                    font_name = current_font['fontname']
                                    if current_font['bold']:
                                        font_name += '-bold'
                                    if current_font['italic']:
                                        font_name += '-italic'

                                    # Make sure character set is empty before fill it
                                    character_set = []

                                    # This will get all used characters in this Dialogue
                                    for char in tag.text:
                                        character_set.append(char)

                                    collected_fonts_container.append([
                                        font_name,
                                        current_font['fontname'],
                                        current_font['bold'],
                                        current_font['italic'],
                                        set(character_set)
                                        ],
                                    )

                except (ass_tag_parser.BaseError, ass_tag_parser.ParseError,
                        ass_tag_parser.UnexpectedCurlyBrace, ass_tag_parser.UnknownTag,
                        ass_tag_parser.UnterminatedCurlyBrace, ass_tag_parser.BadAssTagArgument) as errrr:
                    logger.warning('Error occurred while parsing {DIALOGUE}\nin file {FILE_NAME}\n Error message is "{ERROR}"'.format_map({
                        'DIALOGUE': event.text,
                        'FILE_NAME': full_file_path,
                        'ERROR': errrr
                    }))

    except (pysubs2.FormatAutodetectionError, pysubs2.Pysubs2Error,
            pysubs2.UnknownFileExtensionError, pysubs2.UnknownFormatIdentifierError,
            pysubs2.UnknownFPSError) as errr:
        logger.warning('Error occurred while parsing file {FILE_NAME}\n Error message is "{ERROR}"'.format_map({
            'FILE_NAME': full_file_path,
            'ERROR': errr
        }))
    except (TypeError, ValueError, AttributeError) as errrrr:
        logger.warning('Error occurred while parsing file {FILE_NAME}\n Error message is "{ERROR}"'.format_map({
            'FILE_NAME': full_file_path,
            'ERROR': errrrr
        }))


logger.debug('Collected RAW data are:')

# for each style data
for tbd in collected_fonts_container:

    logger.debug(tbd)

    # Merge character set to a single string
    chars_to_str = ''
    for char in tbd[4]:
        chars_to_str += str(char)
    collection.update({
        tbd[0]: {
            'fontname': tbd[1],
            'bold': tbd[2],
            'italic': tbd[3],
            'characters': ''.join(sorted(chars_to_str))
        }
    })

# Log the collection of styles info
logger.debug(collection)

# Prepare the output ass file
output_ass = pysubs2.SSAFile()
output_ass.clear() # Clear the ass file from all pre-defined styles.

# Insert all styles and their proper text to one ass file object
for details in collection:
    style = pysubs2.SSAStyle()
    style.fontname = collection[details]['fontname']
    style.bold = collection[details]['bold']
    style.italic = collection[details]['italic']

    event = pysubs2.SSAEvent()
    event.text = collection[details]['characters']
    event.style = details

    output_ass.styles[details] = style
    output_ass.append(event)

# Finally save the data to one ass file
output_ass.save('output.ass', encoding='utf-8-sig')

