import requests
import json
import time
import telebot

API_TOKEN = '8176227619:AAGY_acwdNmXg8OGNWa1MomK9_NKm3VSuEA'
bot = telebot.TeleBot(API_TOKEN)


def transcrip(audio_file):
    base_url = "https://api.assemblyai.com/v2"
    headers = {"authorization": "9f5ddac36691496ba8af256d934dae8e"}
    data = {
        "audio_url": audio_file,
        "speaker_labels": True,
        "language_code": "ru"
    }
    response = requests.post(base_url + "/transcript", headers=headers, json=data)

    if response.status_code != 200:
        raise RuntimeError(f"Ошибка транскрипции: {response.status_code}, {response.text}")

    transcript_id = response.json()["id"]
    polling_endpoint = f"{base_url}/transcript/{transcript_id}"

    result = ""
    while True:
        transcript = requests.get(polling_endpoint, headers=headers).json()
        if transcript["status"] == "completed":
            for utterance in transcript.get("utterances", []):
                result += f"\nSpeaker {utterance['speaker']}: {utterance['text']}\n"
            return result
        elif transcript["status"] == "error":
            raise RuntimeError(f"Ошибка транскрипции: {transcript['error']}")
        time.sleep(3)


def send_messages(messages, bot_token):
    chat_id = "111111111"  # ваш chat_id
    api_url = f"https://us1.api.pro-talk.ru/api/v1.0/ask/{bot_token}"
    last_response = None

    for message in messages:
        try:
            payload = {
                "bot_id": 21384,
                "chat_id": chat_id,
                "message": message
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            last_response = response_json.get('done', "Ответ не содержит 'done'")
        except requests.exceptions.RequestException as e:
            last_response = f"Ошибка запроса: {e}"
            break

    return last_response


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        if message.audio.mime_type == 'audio/mpeg':
            file_info = bot.get_file(message.audio.file_id)
            download_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"

            bot_token = "eIrWl0kTi9P1gMJt4uQHR9Ej2T0v0XxM"
            messages = [transcrip(download_url)]
            messages = ["🏁"] + messages
            messages.append("вызови функцию 298, ссылка: “https://script.google.com/macros/s/AKfycbywcaFqTgQLawkVw1WpEtNVkNybRgBh4thWkEEu29vOvAUw51FBTzmBCH9uqRyV4QVh/exec” , с параметрами: analtext::Текст анализа разговора")
            result = send_messages(messages, bot_token)

            bot.reply_to(message, f"MP3 обработан!\n\n{result}")
        else:
            bot.reply_to(message, "Аудиофайл не является MP3.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке: {e}")


if __name__ == "__main__":
    print("Бот запущен и слушает MP3...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка в polling: {e}")
            time.sleep(10)
