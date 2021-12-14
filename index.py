from cv2 import cv2
from pyclick import HumanClicker
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from src.date import dateFormatted
from captcha.solveCaptcha import solveCaptcha

import numpy as np
import mss
import pyautogui
import telegram
import time
import sys
import yaml
import random
import requests

btsversion = "1.2.4"

banner = """
=========================================================================
=========================== BombCrypto Bot ==============================
=========================================================================

 ███████████  ███████████  █████████   ████████   ████████ 
░░███░░░░░███░█░░░███░░░█ ███░░░░░███ ███░░░░███ ███░░░░███
 ░███    ░███░   ░███  ░ ░███    ░░░ ░░░    ░███░░░    ░███
 ░██████████     ░███    ░░█████████    ███████    ███████ 
 ░███░░░░░███    ░███     ░░░░░░░░███  ███░░░░    ███░░░░  
 ░███    ░███    ░███     ███    ░███ ███      █ ███      █
 ███████████     █████   ░░█████████ ░██████████░██████████
░░░░░░░░░░░     ░░░░░     ░░░░░░░░░  ░░░░░░░░░░ ░░░░░░░░░░ 
=========================================================================
================ Please consider buying me a coffee :) =================
=========================================================================
============== 0x7e665768270dF85A1D398498F9694C17e646Aa8C ===============
================================= PIX ===================================
================= 14c6beb5-a38a-46f1-b029-cf2e104712d0 ==================
=========================================================================

>>---> BTS-Key is optional and required for advanced resources.

>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be found in the config.yaml file.

"""

print(banner)


stream = open("config.yaml", 'r')
if stream is not None:
    c = yaml.safe_load(stream)
    ct = c['threshold']
    t = c['time_intervals']
    telegram_data = c['telegram']
    bts_data = c['bts-key']
    metamask_data = c['metamask']
    chest_data = c['value_chests']
    offsets = c['offsets']
    stream.close()
else:
    logger('Config file not found, exiting', emoji='😿')
    time.sleep(3)
    exit()

def logger(message, telegram=False, emoji=None):
    formatted_datetime = dateFormatted()
    console_message = "{} - {}".format(formatted_datetime, message)
    service_message = "⏰{}\n{} {}".format(formatted_datetime, emoji, message)
    if emoji is not None and c['emoji'] is True:
        console_message = "{} - {} {}".format(formatted_datetime, emoji, message)

    print(console_message)
    
    if telegram == True:
        sendTelegramMessage(service_message)

    if (c['save_log_to_file'] == True):
        logger_file = open("./logs/logger.log", "a", encoding='utf-8')
        logger_file.write(console_message + '\n')
        logger_file.close()
    return True


hc = HumanClicker()
pyautogui.PAUSE = c['time_intervals']['interval_between_movements']
pyautogui.FAILSAFE = False
general_check_time = 1
check_for_updates = 15

heroes_clicked = 0
heroes_clicked_total = 0
login_attempts = 0
next_refresh_heroes = t['send_heroes_for_work'][0]
next_refresh_heroes_positions = t['refresh_heroes_positions'][0]

go_work_img = cv2.imread('./images/targets/go-work.png')
home_img = cv2.imread('./images/targets/home.png')
arrow_img = cv2.imread('./images/targets/go-back-arrow.png')
full_screen_img = cv2.imread('./images/targets/full_screen.png')
hero_img = cv2.imread('./images/targets/hero-icon.png')
x_button_img = cv2.imread('./images/targets/x.png')
teasureHunt_icon_img = cv2.imread('./images/targets/treasure-hunt-icon.png')
ok_btn_img = cv2.imread('./images/targets/ok.png')
connect_wallet_btn_img = cv2.imread('./images/targets/connect-wallet.png')
sign_btn_img = cv2.imread('./images/targets/metamask_sign.png')
new_map_btn_img = cv2.imread('./images/targets/new-map.png')
green_bar = cv2.imread('./images/targets/green-bar.png')
full_stamina = cv2.imread('./images/targets/full-stamina.png')
character_indicator = cv2.imread('./images/targets/character_indicator.png')
error_img = cv2.imread('./images/targets/error.png')
metamask_unlock_img = cv2.imread('./images/targets/unlock_metamask.png')
metamask_cancel_button = cv2.imread('./images/targets/metamask_cancel_button.png')
puzzle_img = cv2.imread('./images/targets/puzzle.png')
piece = cv2.imread('./images/targets/piece.png')
robot = cv2.imread('./images/targets/robot.png')
slider = cv2.imread('./images/targets/slider.png')
chest_button = cv2.imread('./images/targets/treasure_chest.png')
coin_icon = cv2.imread('./images/targets/coin.png')
maintenance_popup = cv2.imread('./images/targets/maintenance.png')
chest1 = cv2.imread('./images/targets/chest1.png')
chest2 = cv2.imread('./images/targets/chest2.png')
chest3 = cv2.imread('./images/targets/chest3.png')
chest4 = cv2.imread('./images/targets/chest4.png')

# Initialize telegram
if telegram_data['telegram_mode'] == True:
    logger('Initializing Telegram...', emoji='📱')
    updater = Updater(telegram_data["telegram_bot_key"])

    try:
        TBot = telegram.Bot(token=telegram_data["telegram_bot_key"])

        def send_print(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' % telegram_data["format_of_images"], screenshot)
            update.message.reply_photo(photo=open('./logs/print-report.%s' % telegram_data["format_of_images"], 'rb'))

        def send_id(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(f'🆔 Your id is: {update.effective_user.id}')

        def send_map(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendMapReport() is None:
                update.message.reply_text('😿 An error has occurred')

        def send_bcoin(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendBCoinReport() is None:
                update.message.reply_text('😿 An error has occurred')

        commands = [
            ['print', send_print],
            ['id', send_id],
            ['map', send_map],
            ['bcoin', send_bcoin]
        ]

        for command in commands:
            updater.dispatcher.add_handler(CommandHandler(command[0], command[1]))

        updater.start_polling()
        # updater.idle()
    except:
        logger('Bot not initialized, see configuration file', emoji='🤖')

def sendTelegramMessage(message):
    if telegram_data['telegram_mode'] == False:
        return
    try:
        if(len(telegram_data["telegram_chat_id"]) > 0):
            for chat_id in telegram_data["telegram_chat_id"]:
                TBot.send_message(text=message, chat_id=chat_id)
    except:
        logger('Error to send telegram message. See configuration file', emoji='📄')

def sendTelegramPrint():
    if telegram_data['telegram_mode'] == False:
        return
    try:
        if(len(telegram_data["telegram_chat_id"]) > 0):
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' % telegram_data["format_of_images"], screenshot)
            for chat_id in telegram_data["telegram_chat_id"]:
                TBot.send_photo(chat_id=chat_id, photo=open('./logs/print-report.%s' % telegram_data["format_of_images"], 'rb'))
    except:
        logger('Error to send telegram message. See configuration file', emoji='📄')

def sendPossibleAmountReport(baseImage):
    if telegram_data['telegram_mode'] == False:
        return
    c1 = len(positions(chest1, ct['chest'], baseImage, True))
    c2 = len(positions(chest2, ct['chest'], baseImage, True))
    c3 = len(positions(chest3, ct['chest'], baseImage, True))
    c4 = len(positions(chest4, ct['chest'], baseImage, True))
    
    value1 = c1 * chest_data["value_chest1"]
    value2 = c2 * chest_data["value_chest2"]
    value3 = c3 * chest_data["value_chest3"]
    value4 = c4 * chest_data["value_chest4"]

    total = value1 + value2 + value3 + value4

    report = """
Possible quantity chest per type:
🟤 - """+str(c1)+"""
🟣 - """+str(c2)+"""
🟡 - """+str(c3)+"""
🔵 - """+str(c4)+"""

🤑 Possible amount: """+f'{total:.3f} BCoin'+"""
"""
    logger(report, telegram=True)

def sendBCoinReport():
    if telegram_data['telegram_mode'] == False:
        return
    if(len(telegram_data["telegram_chat_id"]) <= 0 or telegram_data["enable_coin_report"] is False):
        return

    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
            if clickButton(teasureHunt_icon_img):
                time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return
        
    clickButton(chest_button)

    sleep(5, 15)

    coin = positions(coin_icon, return_0=True)
    if len(coin) > 0:
        x, y, w, h = coin[0]

        with mss.mss() as sct:
            sct_img = np.array(sct.grab(sct.monitors[c['monitor_to_use']]))
            crop_img = sct_img[y:y+h, x:x+w]
            cv2.imwrite('./logs/bcoin-report.%s' % telegram_data["format_of_images"], crop_img)
            time.sleep(1)
            try:
                for chat_id in telegram_data["telegram_chat_id"]:
                    # TBot.send_document(chat_id=chat_id, document=open('bcoin-report.png', 'rb'))
                    TBot.send_photo(chat_id=chat_id, photo=open('./logs/bcoin-report.%s' % telegram_data["format_of_images"], 'rb'))
            except:
                logger('Telegram offline', emoji='😿')
    clickButton(x_button_img)
    logger('BCoin report sent', telegram=True, emoji='📄')
    return True

def sendMapReport():
    if telegram_data['telegram_mode'] == False:
        return
    if(len(telegram_data["telegram_chat_id"]) <= 0 or telegram_data["enable_map_report"] is False):
        return

    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
            if clickButton(teasureHunt_icon_img):
                time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return

    back = positions(arrow_img, return_0=True)
    full_screen = positions(full_screen_img, return_0=True)
    if len(back) <= 0 or len(full_screen) <= 0:
        return
    x, y, _, _ = back[0]
    x1, y1, w, h = full_screen[0]
    newY0 = y
    newY1 = y1
    newX0 = x
    newX1 = x1 + w

    with mss.mss() as sct:
        sct_img = np.array(sct.grab(sct.monitors[c['monitor_to_use']]))
        crop_img = sct_img[newY0:newY1, newX0:newX1]
        # resized = cv2.resize(crop_img, (500, 250))

        cv2.imwrite('./logs/map-report.%s' % telegram_data["format_of_images"], crop_img)
        time.sleep(1)
        try:
            for chat_id in telegram_data["telegram_chat_id"]:
                # TBot.send_document(chat_id=chat_id, document=open('map-report.png', 'rb'))
                TBot.send_photo(chat_id=chat_id, photo=open('./logs/map-report.%s' % telegram_data["format_of_images"], 'rb'))
        except:
            logger('Telegram offline', emoji='😿')

        try:
            sendPossibleAmountReport(sct_img[:,:,:3])
        except:
            logger('Error finding chests', telegram=True, emoji='😿')

    clickButton(x_button_img)
    logger('Map report sent', telegram=True, emoji='📄')
    return True

def clickButton(img,name=None, timeout=3, threshold = ct['default']):
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(matches is False):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        # pyautogui.moveTo(int(random.uniform(x, x+w)),int(random.uniform(y, y+h)),1)
        hc.move((int(random.uniform(x, x+w)), int(random.uniform(y, y+h))),1)
        pyautogui.click()
        return True

def printScreen():
    with mss.mss() as sct:
        # The screen part to capture
        # Grab the data
        sct_img = np.array(sct.grab(sct.monitors[c['monitor_to_use']]))
        return sct_img[:,:,:3]

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'], base_img=None, return_0=False):
    if base_img is None:
        img = printScreen()
    else:
        img = base_img

    w = target.shape[1]
    h = target.shape[0]

    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if return_0 is False:
        if len(rectangles) > 0:
            # sys.stdout.write("\nGet_coords. " + str(rectangles) + " " + str(weights) + " " + str(w) + " " + str(h) + " ")
            return rectangles
        else:
            return False
    else:
        return rectangles

def findPuzzlePieces(result, piece_img, threshold=0.5):
    piece_w = piece_img.shape[1]
    piece_h = piece_img.shape[0]
    yloc, xloc = np.where(result >= threshold)


    r= []
    for (piece_x, piece_y) in zip(xloc, yloc):
        r.append([int(piece_x), int(piece_y), int(piece_w), int(piece_h)])
        r.append([int(piece_x), int(piece_y), int(piece_w), int(piece_h)])


    r, weights = cv2.groupRectangles(r, 1, 0.2)

    if len(r) < 2:
        # print('threshold = %.3f' % threshold)
        return findPuzzlePieces(result, piece_img,threshold-0.01)

    if len(r) == 2:
        # print('match')
        return r

    if len(r) > 2:
        # logger('🧩 Overshoot by %d attempts' % len(r))

        return r

def getRightPiece(puzzle_pieces):
    if puzzle_pieces is False:
        return False

    xs = [row[0] for row in puzzle_pieces]
    index_of_right_rectangle = xs.index(max(xs))

    right_piece = puzzle_pieces[index_of_right_rectangle]
    return right_piece

def getLeftPiece(puzzle_pieces):
    if puzzle_pieces is False:
        return False

    xs = [row[0] for row in puzzle_pieces]
    index_of_left_rectangle = xs.index(min(xs))

    left_piece = puzzle_pieces[index_of_left_rectangle]
    return left_piece

def show(rectangles = None, img = None):

    if img is None:
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[c['monitor_to_use']]))

    if rectangles is not None:
        for (x, y, w, h) in rectangles:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)



def checkCaptcha():
    puzzle_pos = positions(robot)
    if puzzle_pos is not False:
        logger('Captcha detected.', telegram=True, emoji='🧩')
        #r = requests.get('http://api.btscenter.net/telegram/call.php?user=@XXXXXXXXXXX&text=Verifique+o+sistema+anti+bot&lang=pt-BR-Wavenet-B')
        solveCaptcha()
    else:
        return True

def scroll():
    offset = offsets['character_indicator']
    offset_random = random.uniform(offset[0], offset[1])
    
    # width, height = pyautogui.size()
    # pyautogui.moveTo(width/2-200, height/2,1)
    character_indicator_pos = positions(character_indicator)
    if character_indicator_pos is False:
        return

    x, y, w, h = character_indicator_pos[0]
    hc.move((int(x+(w/2)),int(y+h+offset_random)), np.random.randint(1,2))

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.click()
        pyautogui.scroll(-c['scroll_size'])
    else:
        # pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')
        pyautogui.mouseDown(button='left')
        hc.move((int(x),int(y+(-c['click_and_drag_amount']))), np.random.randint(1,2))
        pyautogui.mouseUp(button='left')

def clickButtons():
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])
    offset = offsets['work_button_all']

    if buttons is False:
        return

    if c['debug'] is not False:
        logger('%d buttons detected' % len(buttons), emoji='✔️')

    for (x, y, w, h) in buttons:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random),int(y+(h/2))), np.random.randint(1,2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold', telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    logger('Clicking in %d heroes detected.' % len(buttons), telegram=False, emoji='👆')
    return len(buttons)

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    offset = offsets['work_button']
    green_bars = positions(green_bar, threshold=ct['green_bar'])
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])

    if green_bars is False or buttons is False:
        return

    if c['debug'] is not False:
        logger('%d green bars detected' % len(green_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('Clicking in %d heroes with green bar detected.' % len(not_working_green_bars), telegram=False, emoji='👆')

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # isWorking(y, buttons)
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)),int(y+(h/2))), np.random.randint(1,2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold', telegram=True, emoji='⚠️')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        sleep(1, 3)
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = offsets['work_button_full']
    full_bars = positions(full_stamina, threshold=ct['full_bar'])
    buttons = positions(go_work_img, threshold=ct['go_to_work_btn'])

    if full_bars is False or buttons is False:
        return

    if c['debug'] is not False:
        logger('%d FULL bars detected' % len(full_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('Clicking in %d heroes with FULL bar detected.' % len(not_working_full_bars), telegram=True, emoji='👆')

    for (x, y, w, h) in not_working_full_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)),int(y+(h/2))), np.random.randint(1,2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold', telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    return len(not_working_full_bars)

def currentScreen():
    if positions(arrow_img) is not False:
        # sys.stdout.write("\nThunt. ")
        return "thunt"
    elif positions(teasureHunt_icon_img) is not False:
        # sys.stdout.write("\nmain. ")
        return "main"
    elif positions(connect_wallet_btn_img) is not False:
        # sys.stdout.write("\nlogin. ")
        return "login"
    elif positions(character_indicator) is not False:
        # sys.stdout.write("\ncharacter. ")
        return "character"
    else:
        # sys.stdout.write("\nUnknown. ")
        return "unknown"

def goToHeroes():
    if currentScreen() == "thunt":
        if clickButton(arrow_img):
            sleep(1, 3)
            if clickButton(hero_img):
                sleep(1, 3)
                checkCaptcha()
                waitForImage(home_img)
    if currentScreen() == "main":
        if clickButton(hero_img):
            sleep(1, 3)
            checkCaptcha()
            waitForImage(home_img)
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()

def goToTreasureHunt():
    if currentScreen() == "main":
        clickButton(teasureHunt_icon_img)
    if currentScreen() == "character":
        if clickButton(x_button_img):
            sleep(1, 3)
            clickButton(teasureHunt_icon_img)
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()

def refreshHeroesPositions():
    logger('Refreshing heroes positions', emoji='🔃')
    global next_refresh_heroes_positions
    next_refresh_heroes_positions = random.uniform(t['refresh_heroes_positions'][0], t['refresh_heroes_positions'][1])
    if currentScreen() == "thunt":
        if clickButton(arrow_img):
            time.sleep(5)
    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            return True
        else:
            return False
    else:
        return False

def login():
    global login_attempts

    randomMouseMovement()

    if clickButton(connect_wallet_btn_img):
        logger('Connect wallet button detected, logging in!', emoji='🎉')
        time.sleep(2)
        #solveCaptcha() mexendo
        checkCaptcha()


        waitForImage((sign_btn_img, metamask_unlock_img), multiple=True)

    metamask_unlock_coord = positions(metamask_unlock_img)
    if metamask_unlock_coord is not False:
        if(metamask_data["enable_login_metamask"] is False):
            logger('Metamask locked! But login with password is disabled, exiting', emoji='🔒')
            exit()
        logger('Found unlock button. Waiting for password', emoji='🔓')
        password = metamask_data["password"]
        pyautogui.typewrite(password, interval=0.1)
        sleep(1, 3)
        if clickButton(metamask_unlock_img):
            logger('Unlock button clicked', emoji='🔓')

    if clickButton(sign_btn_img):
        logger('Found sign button. Waiting to check if logged in', emoji='✔️')
        time.sleep(5)
        if clickButton(sign_btn_img): ## twice because metamask glitch
            logger('Found glitched sign button. Waiting to check if logged in', emoji='✔️')
        # time.sleep(25)
        waitForImage(teasureHunt_icon_img, timeout=60)

    if currentScreen() == "main":
        logger('Logged in', telegram=True, emoji='🎉')
        return True
    else:
        logger('Login failed, trying again', emoji='😿')
        login_attempts += 1

        if (login_attempts > 3):
            sendTelegramPrint()
            logger('+3 login attempts, retrying', telegram=True, emoji='🔃')
            # pyautogui.hotkey('ctrl', 'f5')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            login_attempts = 0

            if clickButton(metamask_cancel_button):
                logger('Metamask is glitched, fixing', emoji='🙀')
            
            waitForImage(connect_wallet_btn_img)

        login()

    handleError()

def handleError():
    if positions(error_img, ct['error']) is not False:
        sendTelegramPrint()
        logger('Error detected, trying to resolve', telegram=True, emoji='💥')
        clickButton(ok_btn_img)
        logger('Refreshing page', telegram=True, emoji='🔃')
        # pyautogui.hotkey('ctrl', 'f5')
        pyautogui.hotkey('ctrl', 'shift', 'r')
        waitForImage(connect_wallet_btn_img)
        login()
    else:
        return False

def getMoreHeroes():
    global next_refresh_heroes
    global heroes_clicked

    logger('Search for heroes to work', emoji='🏢')

    goToHeroes()

    if c['select_heroes_mode'] == "full":
        logger('Sending heroes with full stamina bar to work!', emoji='⚒️')
    elif c['select_heroes_mode'] == "green":
        logger('Sending heroes with green stamina bar to work!', emoji='⚒️')
    else:
        logger('Sending all heroes to work!', emoji='⚒️')

    buttonsClicked = 0
    heroes_clicked = 0
    empty_scrolls_attempts = c['scroll_attempts']
    next_refresh_heroes = random.uniform(t['send_heroes_for_work'][0], t['send_heroes_for_work'][1])

    while(empty_scrolls_attempts > 0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked
        else:
            buttonsClicked = clickButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked

        if buttonsClicked == 0 or buttonsClicked is None:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
            scroll()
        sleep(1, 3)
    logger('{} total heroes sent since the bot started'.format(heroes_clicked_total), telegram=True, emoji='🦸')
    goToTreasureHunt()

def checkLogout():
    if currentScreen() == "unknown" or currentScreen() == "login":
        if positions(connect_wallet_btn_img) is not False:
            sendTelegramPrint()
            logger('Logout detected', telegram=True, emoji='😿')
            logger('Refreshing page', telegram=True, emoji='🔃')
            # pyautogui.hotkey('ctrl', 'f5')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            waitForImage(connect_wallet_btn_img)
            login()
        elif positions(sign_btn_img):
            logger('Sing button detected', telegram=True, emoji='✔️')
            if clickButton(metamask_cancel_button):
                logger('Metamask is glitched, fixing', telegram=True, emoji='🙀')
        else:
            return False
            
    else:
        return False

def waitForImage(imgs, timeout=30, threshold=0.5, multiple=False):
    start = time.time()
    while True:
        if multiple is not False:
            for img in imgs:
                matches = positions(img, threshold=threshold)
                if matches is False:
                    hast_timed_out = time.time()-start > timeout
                    if hast_timed_out is not False:
                        return False
                    continue
                return True
        else:
            matches = positions(imgs, threshold=threshold)
            if matches is False:
                hast_timed_out = time.time()-start > timeout
                if hast_timed_out is not False:
                    return False
                continue
            return True

def sleep(min, max):
	sleep = random.uniform(min,max)
	randomMouseMovement()
	return time.sleep(sleep)

def randomMouseMovement():
    x, y = pyautogui.size()
    x = np.random.randint(0, x)
    y = np.random.randint(0, y)
    hc.move((int(x), int(y)), np.random.randint(1,3))

def checkUpdates():
    data = requests.get('https://raw.githubusercontent.com/bts22/bombcrypto-bot/main/version.yaml')

    if data is not None:
        v = yaml.safe_load(data.text)
        version = v['version']
        data.close()
    else:
        logger('Version not found, exiting', emoji='💥')
        #time.sleep(3)
        #exit()

    print('Git Version: ' + version)
    print('Version installed: ' + btsversion)
    if version > btsversion:
        logger('New version available, please update', telegram=True, emoji='🎉')


def main():

    checkUpdates()
    input('Press Enter to start the bot...')
    logger('Starting bot...', telegram=True, emoji='🤖')

    last = {
        "login" : 0,
        "heroes" : 0,
        "new_map" : 0,
        "refresh_heroes" : 0,
        "check_updates" : 0
    }

    while True:
        if currentScreen() == "login":
            login()
        
        handleError()

        checkCaptcha()

        now = time.time()

        if now - last["heroes"] > next_refresh_heroes * 60:
            last["heroes"] = now
            last["refresh_heroes"] = now
            getMoreHeroes()

        if currentScreen() == "main":
            if clickButton(teasureHunt_icon_img):
                logger('Entering treasure hunt', emoji='▶️')
                last["refresh_heroes"] = now

        if currentScreen() == "thunt":
            if clickButton(new_map_btn_img):
                logger('New map', emoji='🗺️')
                last["new_map"] = now
                sleep(1, 2)
                checkCaptcha()
                sleep(2, 3)
                sendMapReport()
                sleep(3, 5)
                sendBCoinReport()
                
        if currentScreen() == "character":
            clickButton(x_button_img)
            sleep(1, 3)

        if now - last["refresh_heroes"] > next_refresh_heroes_positions * 60:
            last["refresh_heroes"] = now
            refreshHeroesPositions()

        if now - last["check_updates"] > check_for_updates * 60:
            last["check_updates"] = now
            checkUpdates()

        checkLogout()
        sys.stdout.flush()
        time.sleep(general_check_time)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger('Shutting down the bot', telegram=True, emoji='😓')
        updater.stop()
        exit()