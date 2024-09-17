import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot_states import WAITING_FOR_VIDEO_PROMPT
import config
from utils import call_luma_api


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /video command."""
    if context.args:
        # If a prompt was provided with the command, generate the video immediately
        prompt = ' '.join(context.args)
        await generate_video(update, context, prompt)
        return ConversationHandler.END
    else:
        # If no prompt was provided, ask for one
        await update.message.reply_text("Please provide a prompt for the video generation:")
        return WAITING_FOR_VIDEO_PROMPT


async def receive_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the received prompt and generate the video."""
    prompt = update.message.text
    await generate_video(update, context, prompt)
    return ConversationHandler.END


async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str) -> None:
    """Generate an video using LUMA API."""
    await update.message.reply_text(f"Generating video for prompt: {prompt}")

    try:
        task = asyncio.create_task(call_luma_api(prompt=prompt))
        countdown = config.WAIT_TIME
        message = await update.message.reply_text(f"Time remaining: {countdown} seconds.")
        for _ in range(config.WAIT_TIME):
            if task.done():
                message.delete()
                break
            else:
                await asyncio.sleep(10)
                countdown -= 10
                await message.edit_text(f"Time remaining: {countdown} seconds.")
        video, status = await asyncio.wait_for(task, timeout=config.WAIT_TIME)
        if status:
            await update.message.reply_video(video[0])
        else:
            await update.message.reply_text(f"We are unable to generate a video at this moment, please try after sometime.")
    except asyncio.TimeoutError:
        await update.message.reply_text("Video generation is taking longer than expected. Please try again later.")
    except Exception as e:
        await update.message.reply_text(f"We are unable to generate a video at this moment, please try after sometime.")
