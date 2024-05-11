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
from .functions import functions, run_function

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
  initial_response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                                    messages=messages,
                                                    tools=functions)
  initial_response_message = initial_response.choices[0].message
  messages.append(initial_response_message)
  final_response = None
  tool_calls = initial_response_message.tool_calls
  if tool_calls:
    for tool_call in tool_calls:
      name = tool_call.function.name
      args = json.loads(tool_call.function.arguments)
      response = run_function(name, args)
      print(tool_calls)
      messages.append({
          "tool_call_id": tool_call.id,
          "role": "tool",
          "name": name,
          "content": str(response),
      })
      if name == 'svg_to_png_bytes':
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=response)
      if name == 'generate_image':
        await image(update, context)
      # Generate the final response
      final_response = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=messages,
      )
      final_answer = final_response.choices[0].message

      # Send the final response if it exists
      if (final_answer):
        messages.append(final_answer)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=final_answer.content)
      else:
        # Send an error message if something went wrong
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='something wrong happened, please try again')
  #no functions were execute
  else:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=initial_response_message.content)      

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
