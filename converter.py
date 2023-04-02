import logging
import os
import pathlib
import shutil

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import roman
import zipfile
from patoolib import extract_archive

END, FILE, NICKNAME = range(-1, 2)
logger = logging.getLogger(__name__)

class Converter:
    def __init__(self, temp):
        self.filename = ''
        self.temp_path = temp
        self.zip_temp_folder = f'{self.temp_path}/temp_folder'

    async def help_command(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Use /convert to test this bot.")

    async def start(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Upload file",
        )
        return FILE

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            os.remove(os.path.join(self.temp_path, self.filename))
        except:
            pass
        logger.warning(context.error)
        await update.message.reply_text('Conversation ended. Please, try to start with /convert again')

        return ConversationHandler.END

    async def get_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file = await context.bot.getFile(update.message.document)
        self.filename = update.message.document.file_name
        with open(os.path.join(self.temp_path, self.filename), 'wb+') as f:
            await file.download_to_memory(out=f)

        await update.message.reply_text(
            "Enter your nickname",
        )

        return NICKNAME

    def extract_rar(self):
        if not os.path.exists(self.zip_temp_folder):
            pathlib.Path(self.zip_temp_folder).mkdir(parents=True, exist_ok=True)

        extract_archive(os.path.join(self.temp_path, self.filename), outdir=f'{self.temp_path}temp_folder')

    async def convert(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.message.text
        new_filenames = []
        self.extract_rar()
        os.remove(os.path.join(self.temp_path, self.filename))
        for root, dirs, files in os.walk(self.zip_temp_folder):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    data = f.read()
                    h2n_data = self.gg_to_h2n(data, username)
                    new_name = file.split('/')[-1].replace(' ', '-').replace('---', '-').replace('--', '-')
                    if not new_name:
                        continue
                    with open(os.path.join(self.temp_path, new_name), 'w+') as output:
                        output.write(h2n_data)
                    new_filenames.append(new_name)
        shutil.rmtree(self.zip_temp_folder)
        result_filename = os.path.join(self.temp_path, f'{self.filename.split(".")[0]}_h2n.{self.filename.split(".")[1]}')
        with zipfile.ZipFile(result_filename, "w") as f:
            for filename in new_filenames:
                f.write(os.path.join(self.temp_path, filename), arcname=filename)
        for filename in new_filenames:
            os.remove(os.path.join(self.temp_path, filename))
        await update.effective_chat.send_document(document=result_filename)
        os.remove(result_filename)

        return END

    @staticmethod
    def gg_to_h2n(data: str, username: str) -> str:
        data = '\n' + data
        start = 0
        while 'Level' in data[start:] and start < len(data):
            start_index = data[start:].find('Level') + len('Level')
            end_index = data[start + start_index:].find('(') + start_index
            number = data[start:][start_index:end_index]
            data = data[:start + start_index] + ' ' + roman.toRoman(int(number)) + ' ' + data[start + end_index:]
            start += end_index + len(str(roman.toRoman(int(number)))) - len(str(number))
        start = 0
        while 'Dealt to' in data[start:] and start < len(data):
            start_index = data[start:].find('Dealt to')
            end_index = data[start + start_index:].find('\n') + start_index + 1
            string = data[start:][start_index:end_index]
            delete_len = 0
            if not string.startswith('Dealt to Hero'):
                data = data[:start + start_index] + data[start + end_index:]
                delete_len = len(string)
            start += end_index - delete_len
        data = data.replace('and won', '###!!!').replace('won', 'collected').replace('###!!!', 'and won')
        data = data.replace('#TM', '#20').replace('Hero', username).replace('\n\n', '\n').replace('Poker Hand', 'PokerStars Hand')
        return data


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6268121226:AAHc70bDIUUj9c0FyW6SpabVsHUqCvuzhus").build()
    converter = Converter('./temp/')

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("convert", converter.start)],
        states={
            FILE: [MessageHandler(filters.ALL, converter.get_file)],
            NICKNAME: [MessageHandler(filters.ALL, converter.convert)],
        },
        fallbacks=[MessageHandler(filters.ALL, converter.stop)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", converter.help_command))
    application.add_error_handler(converter.stop)

    application.run_polling(timeout=1000)


if __name__ == '__main__':
    main()
