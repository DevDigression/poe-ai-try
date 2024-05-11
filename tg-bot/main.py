import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tg_bot_token = os.getenv("TG_BOT_TOKEN")


messages = [{
  "role": "system",
  "content": "You are a helpful assistant that answers questions."
}]

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  messages.append({"role": "user", "content": update.message.text})
  completion = openai.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=messages)
  completion_answer = completion.choices[0].message
  messages.append(completion_answer)

  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=completion_answer.content)

async def transcribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  voice_id = update.message.voice.file_id
  if voice_id:
        file = await context.bot.get_file(voice_id)
        await file.download_to_drive(f"voice_note_{voice_id}.ogg")
        await update.message.reply_text("Voice note downloaded, transcribing now")
        audio_file = open(f"voice_note_{voice_id}.ogg", "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        await update.message.reply_text(
            f"Transcript finished:\n {transcript.text}"
        )

  if __name__ == '__main__':
      application = ApplicationBuilder().token(tg_bot_token).build()

      start_handler = CommandHandler('start', start)
      chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
      voice_handler = MessageHandler(filters.VOICE, transcribe_message)

      application.add_handler(start_handler)
      application.add_handler(chat_handler)
      application.add_handler(voice_handler)

      application.run_polling()
