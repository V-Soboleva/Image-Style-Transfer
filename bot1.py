import telebot
from style_transfer import main_func
from PIL import Image
import io
import os

def image_to_byte_array(image:Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format=image.format)
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

bot = telebot.TeleBot('1200755615:AAHs_ArTkrn-NXJ7TJIVb94TRLPqjr3RRXU');


@bot.message_handler(content_types=['text', 'photo'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Скинь фоточку, которую хочешь застайлить!");
        bot.register_next_step_handler(message, get_content); #следующий шаг – функция get_content
    else:
        bot.send_message(message.from_user.id, 'Напиши /start');

def get_content(message): #получаем контент

    try:


        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        scr1 = 'content/'+ str(message.from_user.id) + '.png'
        with open(scr1, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Супер! Добавлено") 

    except Exception as e:
        bot.reply_to(message,e )
        
    bot.send_message(message.from_user.id, 'Теперь скинь фоточку стиля!');
    bot.register_next_step_handler(message, get_style);

def get_style(message): #получаем стиль
    global scr1, scr2
    try:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        scr2 = 'style/' + str(message.from_user.id) + '.png'
        with open(scr2, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Отлично, и это добавлено")
        bot.send_message(message.from_user.id, "Теперь жди где-то секунд 30 ок да")

    except Exception as e:
        bot.reply_to(message,e )
    print(scr2)
    output_name = main_func('content/'+ str(message.from_user.id) + '.png', 'style/' + str(message.from_user.id) + '.png')
    bot.send_photo(message.from_user.id, open(output_name, 'rb'));

    bot.send_message(message.from_user.id, "Хочешь еще разок? Жми ---> /start");



bot.polling(none_stop=True, interval=0)