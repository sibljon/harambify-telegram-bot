#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cv2
import logging
import telebot

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Check for environment variable
if 'HARAMBIFY_TKN' not in os.environ:
    print >> sys.stderr, "Environment variable 'HARAMBIFY_TKN' not defined."
    exit(1)

# Initialize bot api with token from environment
bot = telebot.TeleBot(os.environ['HARAMBIFY_TKN'], skip_pending=True)

# harambify image and final image extension
img_harambe = cv2.imread('harambe.png', -1)
img_ext = '_harambify.png'
harambe_img_ratio = 0.7121661721 # width/height
harambe_scale_adjustment = 1.5 # > 1 means the width of Harambe's face will be larger than the width of the human face

# Cascade classifier parameters, can be tricky to adjust...
cc_scale_factor = 1.2
cc_min_neighbors = 5
cc_min_size = (20, 20)
cc_flags = cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_ROUGH_SEARCH


# harambify magic happens here
def harambify(img_file):
    # Initialize the classifier with the frontal face haar cascades (https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml)
    face_cc = cv2.CascadeClassifier(('cascade.xml'))

    # Read image
    img = cv2.imread(img_file)
    # Convert to grays
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Equalize histogram, for improving contrast (this helps detection)
    gray = cv2.equalizeHist(gray)

    # Perform detection
    faces = face_cc.detectMultiScale(gray,
                                     scaleFactor=cc_scale_factor,
                                     minNeighbors=cc_min_neighbors,
                                     minSize=cc_min_size,
                                     flags=cc_flags)

    # harambify all the faces!
    for (x, y, w, h) in faces:
        # Resize the harambe according to the face. Maintain harambe_img_ratio ratio of width:height
        harambe_height = int(round(w / harambe_img_ratio * harambe_scale_adjustment))
        harambe_y_offset = int(round((harambe_height - h) / 2))
        harambe_width = int(round(w * harambe_scale_adjustment))
        harambe_x_offset = int(round((harambe_width - w) / 2))
        harambe_res = cv2.resize(img_harambe, (harambe_width, harambe_height))

        # print("current_face.y: {}".format(y))
        # print("current_face.x: {}".format(x))
        # print("current_face.h: {}".format(h))
        # print("current_face.w: {}".format(w))

        (harambe_res_h, harambe_res_w) = harambe_res.shape[:2]
        # print("harambe_res.h: {}".format(harambe_res_h))
        # print("harambe_res.w: {}".format(harambe_res_w))

        (img_h, img_w) = img.shape[:2]
        # print("img.h: {}".format(img_h))
        # print("img.w: {}".format(img_w))

        # TODO: bound the Harambe replacement rectangle to the dimensions of the photo -- it's unclear what will happen if a face is detected at the edge of a photo, but likely the app will crash.

        # Copy the resided harambe over the face keeping the alpha channel
        for c in range(0, 3):
            harambe_y1 = y - harambe_y_offset
            harambe_y2 = harambe_y1 + harambe_height
            harambe_x1 = x - harambe_x_offset
            harambe_x2 = harambe_x1 + harambe_width

            harambe_clip_top = 0
            if harambe_y1 < 0:
              harambe_clip_top = abs(harambe_y1)
            harambe_clip_bottom = 0
            if harambe_y2 > img_h:
              harambe_clip_bottom = abs(harambe_y1 + harambe_height - img_h)
            harambe_clip_left = 0
            if harambe_x1 < 0:
              harambe_clip_left = abs(harambe_x1)
            harambe_clip_right = 0
            if harambe_x2 > img_w:
              harambe_clip_right = abs(harambe_x1 + harambe_width - img_w)

            harambe_y1 = max(harambe_y1, 0)
            harambe_y2 = min(harambe_y2, img_h)
            harambe_x1 = max(harambe_x1, 0)
            harambe_x2 = min(harambe_x2, img_w)

            # print("harambe_height: {}".format(harambe_height))
            # print("harambe_width: {}".format(harambe_width))
            # print("harambe_y_offset: {}".format(harambe_y_offset))
            # print("harambe_x_offset: {}".format(harambe_x_offset))
            # print("harambe_y1: {}".format(harambe_y1))
            # print("harambe_y2: {}".format(harambe_y2))
            # print("harambe_x1: {}".format(harambe_x1))
            # print("harambe_x2: {}".format(harambe_x2))

            img[harambe_y1:harambe_y2, harambe_x1:harambe_x2, c] = harambe_res[harambe_clip_top:harambe_height-harambe_clip_bottom, harambe_clip_left:harambe_width-harambe_clip_right, c] * \
                                   (harambe_res[harambe_clip_top:harambe_height-harambe_clip_bottom, harambe_clip_left:harambe_width-harambe_clip_right, 3] / 255.0) + \
                                   img[harambe_y1:harambe_y2, harambe_x1:harambe_x2, c] * \
                                   (1.0 - (harambe_res[harambe_clip_top:harambe_height-harambe_clip_bottom, harambe_clip_left:harambe_width-harambe_clip_right, 3] / 255.0))

    # Write the file if there is at least one face
    n_faces = len(faces)
    if n_faces > 0:
        cv2.imwrite(img_file+img_ext, img)

    return n_faces


# Bot photo handler
# @bot.message_handler(content_types=['photo'])
def handle_photo(m):
    logger.info("Processing message")

    # Chat id, for sending actions and file
    cid = m.chat.id

    # Search the biggest photo (avoid thumbnails)
    f_id = None
    b_size = 0
    if m.photo is not None:
      for p in m.photo:
          t_size = p.height * p.width
          if t_size > b_size:
              b_size = t_size
              f_id = p.file_id
    else:
      logger.info("No photos in message.")
      return

    if f_id == None:
        logger.info("No f_id -- that's odd!")
        return

    logger.info("Photo(s) found in message: party time?")

    # Download and write the file
    f_info = bot.get_file(f_id)
    f_download = bot.download_file(f_info.file_path)

    filepath = "/tmp/" + f_id

    # We only have permission to write to /tmp on AWS Lambda
    with open(filepath, 'wb') as f:
        f.write(f_download)

    # harambify all the faces!!
    n_faces = harambify(filepath)
    if n_faces > 0:
        logger.info("%i. Group message.", n_faces)

        # Send "uploading photo" action since can take a few seconds
        bot.send_chat_action(cid, 'upload_photo')

        # Upload the photo and do it as a reply
        bot.send_photo(cid,
                       open(filepath+img_ext, 'rb'),
                       caption='%i people have honored Harambe' % n_faces)

        try:
            os.unlink(filepath+img_ext)
        except:  # You shouldn't do this never but... *effort*
            pass

    # If there is no faces and is not a group tell the user
    elif cid > 0:
        bot.send_chat_action(cid, 'typing')
        bot.send_message(cid, 'No faces found. Harambe\'s face wasn\'t even given a chance to be found.')
        logger.info("No faces found in a group message.")
    else:
        logger.info("No faces found in an individual message.")

    try:
        os.unlink(filepath)
    except:  # You shouldn't do this never but... *effort*
        pass


# Help/Start handler
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(m):
    logger.info("Processing start/help")
    bot.send_chat_action(m.chat.id, 'typing')
    bot.send_message(m.chat.id,
                     ("RIP"),
                     disable_web_page_preview=True,
                     parse_mode="Markdown")

# # Start the polling
# bot.polling(none_stop=True)

def lambda_handler(event, context):

  logger.info("lambda_handler triggered")

  if "body" in event:
    logger.info(event["body"])
    update = telebot.types.Update.de_json(event["body"])
    handle_photo(update.message)
  else:
    logger.error("No body key")

  return {
    "statusCode": 200,
    "headers": { },
    "body": ""
  }

def dumpclean(obj):
  if type(obj) == dict:
    for k, v in obj.items():
        if hasattr(v, '__iter__'):
          print k
          dumpclean(v)
        else:
          print '%s : %s' % (k, v)
  elif type(obj) == list:
    for v in obj:
        if hasattr(v, '__iter__'):
          dumpclean(v)
        else:
          print v
  else:
    print obj

  # logger.info("context: %s" + context)
