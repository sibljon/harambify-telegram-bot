Harambify Telegram Bot
---------

A Telegram Bot to remember Harambe through replacing faces with his own.

# Setup

## Creating a new bot in Telegram

You do this by messaging @BotFather

_TODO: add more details_

## Deploying to AWS Lambda

### Creating your bot's AWS Lambda function

_TODO: add more details_

### Deploying the app

1. Zip all of the contents of this repo (READ: the contents, not a single directory containing the contents).
1. Choose `Upload a .ZIP file` in the `Code` tab
1. Set your Telegram bot token as an environment variable

![](https://cl.ly/1D1g2M0A3X41/Screen_Shot_2016-11-21_at_10_50_53_PM.png)

### Register your webhook with Telegram

1. Once your Lambda function is running on AWS, switch to the `Triggers` tab and copy your API Gateway URL. Paste it into the following command to register it as the webhook URL to which Telegram should post:

`curl -XPOST https://api.telegram.org/botYOURTOKEN/setWebhook\?url\=YOURAPIGATEWAYURL`

![](https://cl.ly/2N0L3f0x0N17/Lambda_Management_Console.png)

## Running Locally

### macOS

_TODO: add instructions to run as a simple Flask app to poll as [Dogefy Telegram Bot](https://github.com/skgsergio/dogefy-tg-bot) does_

## Content

| File/Directory     | Character |
| ---      | ---       |
| `harambe.png` | Faces are replaced with this image, and alpha layers are preserved. |
| `cascade.xml` | The OpenCV algorithm by which human faces are detected. This algorithm is hosted [here](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_alt_tree.xml). |
| `lambda.py` | This is where the logic happens. `lambda_handler()` is the function that the AWS Lambda function executes when telegram POSTs to the AWS API Gateway's webhook URL. |
| `cv2/` | [OpenCV wrapped in Python](https://github.com/skvark/opencv-python). Since OpenCV is native code, it is necessary to do `pip install opencv-python` on the environment in which it will run. The `cv2` directory contained in this repo has been built by running `[ip install opencv-python` on an EC2 instance running Amazon Linux AMI, which is what AWS Lamba also runs. In other words, if you are running Harambify locally, you'll need to rebuild OpenCV on your machine. |
| `telebot/` | [pyTelegramBotAPI], a Telegram Bot SDK for Python. `pip install pyTelegramBotAPI`. |
| `requests/` | A dependency of `pyTelegramBotAPI`. |


## TODO

* Scriptify the AWS Lambda deployment
* Add instructions for running locally on other platforms
* Pluralize the "1 people have honored Harambe" and perhaps pepper in some wit and rotate messages
* Fix a bug preventing multi-face detection

## Credits

The face-swap code is essentially a fork of the [Dogefy Telegram Bot](https://github.com/skgsergio/dogefy-tg-bot).
