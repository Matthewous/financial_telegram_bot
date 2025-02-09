from aiogram.types import BufferedInputFile


def send_graph_func(message, file):
    from common.bot_config import bot
    bot.send_photo(message.chat.id, BufferedInputFile(file, filename="portfolio_performance.png"))
    return 200