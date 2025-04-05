import requests
import json
import time
import telebot
import os

# Убедитесь, что указали свой токен
API_TOKEN = '7100666490:AAGm2BJ3bzwgL8eQX5FbgkLEWs1EdT8djJM'
bot = telebot.TeleBot(API_TOKEN)


def transcrip(audio_file):

    base_url = "https://api.assemblyai.com/v2"
    headers = { "authorization": "9f5ddac36691496ba8af256d934dae8e"}
    data = {"audio_url": audio_file,
            "speaker_labels": True,
            "language_code": "ru"}
    response = requests.post(base_url + "/transcript", headers=headers, json=data)

    if response.status_code != 200:
        print(f"Error: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

    transcript_json = response.json() 
    transcript_id = transcript_json["id"]
    polling_endpoint = f"{base_url}/transcript/{transcript_id}"

    a = ''
    while True:
        transcript = requests.get(polling_endpoint, headers=headers).json()
        if transcript["status"] == "completed":
            for utterance in transcript["utterances"]:
                a += f"\nSpeaker {utterance["speaker"]}: {utterance["text"]}\n"
            return a
            break
        elif transcript["status"] == "error":
            raise RuntimeError(f"Transcription failed: {transcript['error']}")
        else:
            time.sleep(3)


def send_messages(messages, bot_token):  # Переименовали аргумент
    """
    Отправляет список сообщений на API.

    Args:
        messages: Список сообщений для отправки.
        bot_token: Токен бота.

    Returns:
        Последний ответ API или сообщение об ошибке.
    """
    
    chat_id = "111111111"  # Жестко заданный chat_id
    api_url = f"https://us1.api.pro-talk.ru/api/v1.0/ask/{bot_token}"
    last_response = None

    for message in messages:
        try:
            payload = {
                "bot_id": 21760,
                "chat_id": chat_id,
                "message": message
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=payload, headers=headers)  # Исправлено
            response.raise_for_status()  

            try:
                response_json = response.json()
                last_response = response_json.get('done', "Ответ не содержит 'done'")
            except json.JSONDecodeError:
                last_response = f"Ошибка: некорректный JSON-ответ: {response.text}"
                print(last_response)
                break

        except requests.exceptions.RequestException as e:
            last_response = f"Ошибка запроса: {e}"
            print(last_response)
            break

    return last_response

# Пример использования




# Обработчик для аудиофайлов (отправленных как "Музыка/Аудио")
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        # Проверим, действительно ли это MP3 (хотя content_type='audio' уже хороший признак)
        if message.audio.mime_type == 'audio/mpeg':
            file_id = message.audio.file_id
            print(f"Получен MP3 (как аудио). File ID: {file_id}")

            # Получаем информацию о файле для генерации ссылки
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

            # Формируем временную ссылку для скачивания
            # ВАЖНО: Эта ссылка действительна ограниченное время (мин. 1 час)!
            download_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

            print(f"Временная ссылка для скачивания: {download_url}")
            
            bot_token = "0v0giWvreW2ddp1MKzJexH0uGeeZRAPW"
            audi = download_url
            messages = [transcrip(audi)]
            messages = ["🏁##"] + messages
            result = send_messages(messages, bot_token)
            print(result)

            
            bot.reply_to(message, f"Получил MP3 файл!\n\n"
                                  f"{result}")
# Если нужно скачать файл:
            # downloaded_file_bytes = bot.download_file(file_path)
            # file_name = message.audio.file_name or f"audio_{message.message_id}.mp3"
            # with open(file_name, 'wb') as new_file:
            #     new_file.write(downloaded_file_bytes)
            # print(f"Файл сохранен как {file_name}")

        else:
            bot.reply_to(message, f"Получил аудиофайл, но это не MP3 (MIME-тип: {message.audio.mime_type}).")

    except Exception as e:
        print(f"Ошибка при обработке аудио: {e}")
        bot.reply_to(message, "Не удалось обработать аудиофайл.")

print("Бот запущен и ожидает MP3 файлы...")
bot.polling(none_stop=True)
