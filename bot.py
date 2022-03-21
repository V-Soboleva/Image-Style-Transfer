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

bot = telebot.TeleBot(####);
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('english', 'russian')

@bot.message_handler(content_types=['text', 'photo'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Please, choose language./Пожалуйста, выберите язык.", reply_markup = keyboard1);
        bot.register_next_step_handler(message, choose_lang); #следующий шаг – функция get_content
    else:
        bot.send_message(message.from_user.id, 'Write/Напишите   /start');
        bot.register_next_step_handler(message, start);

def choose_lang(message):
    if message.text == 'russian':
        bot.send_message(message.from_user.id, "Вы выбрали русский! Пожалуйста, пришлите фотографию, которой вы бы хотели придать стиля!:)");
        bot.register_next_step_handler(message, get_content_russian);
    if message.text == 'english':
        bot.send_message(message.from_user.id, "You have chosen English! Please send a photo that you would like to style! :)");
        bot.register_next_step_handler(message, get_content_english);
    if message.text != 'russian' and message.text != 'english':
        bot.send_message(message.from_user.id, "You sent me something wrong ... Please, choose language./Пожалуйста, выберите язык.", reply_markup = keyboard1);
        bot.register_next_step_handler(message, choose_lang);




def get_content_russian(message): #получаем контент
    if message.photo == None:
        bot.send_message(message.from_user.id, "Вы прислали мне что-то не то... Пожалуйста, пришлите фотографию, которой вы бы хотели придать стиля!:)");
        bot.register_next_step_handler(message, get_content_russian);
    else:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        scr1 = 'content/'+ str(message.from_user.id) + '.png'
        with open(scr1, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Супер! Добавлено")
        bot.send_message(message.from_user.id, 'Теперь скинь фоточку стиля!');
        bot.register_next_step_handler(message, get_style_russian);
       


def get_content_english(message): #получаем контент

    if message.photo == None:
        bot.send_message(message.from_user.id, "You sent me something wrong ... Please send me a photo you would like to style! :)");
        bot.register_next_step_handler(message, get_content_english);
    else:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        scr1 = 'content/'+ str(message.from_user.id) + '.png'
        with open(scr1, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Great! Added")
        bot.send_message(message.from_user.id, 'Now send me a photo of the style!');
        bot.register_next_step_handler(message, get_style_english);



def get_style_russian(message): #получаем стиль
    global scr1, scr2
    if message.photo == None:
        bot.send_message(message.from_user.id, "Вы прислали мне что-то не то... Пожалуйста, пришлите фотографию стиля! ");
        bot.register_next_step_handler(message, get_style_russian);

    else:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        scr2 = 'style/' + str(message.from_user.id) + '.png'
        with open(scr2, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Отлично, и это добавлено")
        bot.send_message(message.from_user.id, "Теперь пожалуйста подождите где-то секунд 30")

        output_name = main_func('content/'+ str(message.from_user.id) + '.png', 'style/' + str(message.from_user.id) + '.png')
        bot.send_photo(message.from_user.id, open(output_name, 'rb'));

        bot.send_message(message.from_user.id, "Хочешь еще разок? Жми ---> /start");
        bot.register_next_step_handler(message, start);

def get_style_english(message): #получаем стиль
    global scr1, scr2
    if message.photo == None:
        bot.send_message(message.from_user.id, "You sent me something wrong ... Please send a photo of the style! ");
        bot.register_next_step_handler(message, get_style_english);

    else:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        scr2 = 'style/' + str(message.from_user.id) + '.png'
        with open(scr2, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message, "Great! Added")
        bot.send_message(message.from_user.id, "Now please wait about 30 seconds")

        output_name = main_func('content/'+ str(message.from_user.id) + '.png', 'style/' + str(message.from_user.id) + '.png')
        bot.send_photo(message.from_user.id, open(output_name, 'rb'));

        bot.send_message(message.from_user.id, "One more time? Press ---> /start");
        bot.register_next_step_handler(message, start);



bot.polling(none_stop=True, interval=0)
