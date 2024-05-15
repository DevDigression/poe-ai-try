import os
import json
import logging
import requests
import replicate
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
from functions import functions, run_function
from replicate import Client

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

replicate_token = os.getenv('REPLICATE_API_TOKEN')

client = Client(api_token=replicate_token)
model = client.models.get("meta/llama-2-70b-chat")
version = model.versions.get("2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1")

def generate_prompt(messages):
  return "\n".join(f"[INST] {message['text']} [/INST]"
                   if message['isUser'] else message['text']
                   for message in messages)

message_history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message_history.append({"isUser": True, "text": update.message.text})

  prompt = generate_prompt(message_history)

  prediction = client.predictions.create(version=version,
                                         input={"prompt": prompt})
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Let me think...")
  prediction.wait()

  human_readable_output = ''.join(prediction.output).strip()

  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=human_readable_output)

  message_history.append({"isUser": False, "text": human_readable_output})  

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  response = openai.images.generate(prompt=update.message.text,
                                    model="dall-e-3",
                                    n=1,
                                    size="1024x1024")
  image_url = response.data[0].url
  image_response = requests.get(image_url)
  await context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=image_response.content)

async def sdxl(update: Update, context: ContextTypes.DEFAULT_TYPE):
  input = {
      "width": 768,
      "height": 768,
      "prompt": update.message.text,
      "refine": "expert_ensemble_refiner",
      "apply_watermark": False,
      "num_inference_steps": 25
  }

  response = replicate.run(
      "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
      input=input
  )
  print(response[0])
  image_url = response[0]
  image_response = requests.get(image_url)
  await context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=image_response.content)
  
if __name__ == '__main__':
  application = ApplicationBuilder().token(tg_bot_token).build()

  start_handler = CommandHandler('start', start)
  chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
  image_handler = CommandHandler('image', image)
  sdxl_handler = CommandHandler('sdxl', sdxl)

  application.add_handler(start_handler)
  application.add_handler(chat_handler)
  application.add_handler(image_handler)
  application.add_handler(sdxl_handler)

  application.run_polling()