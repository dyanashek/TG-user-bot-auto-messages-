import asyncio
import uvloop
from pyrogram import Client, filters, types


import functions
import db_functions
from config import API_HASH, API_ID
from settings import STAGES, STOP_WORDS, ALIVE, FINISHED, DEAD


uvloop.install()
app = Client(name = 'acc', api_id = API_ID, api_hash = API_HASH)


async def start_app() -> None:
    await app.start()


@app.on_message(filters.private & filters.incoming)
async def handle_incoming(client: Client, message: types.Message) -> None:
    user_id = message.from_user.id
    await app.read_chat_history(message.chat.id)

    user = await db_functions.get_user(user_id)

    if not user:
        await db_functions.add_user(user_id)
    else:
        if user.stage == 0:
            await db_functions.update_status(user.id, ALIVE)


@app.on_message(filters.private & filters.outgoing)
async def handle_incoming(client: Client, message: types.Message) -> None:
    user_id = message.chat.id
    user = await db_functions.get_user(user_id)

    if not user:
        await db_functions.add_user(user_id, 0)


async def check_triggers(user: db_functions.User) -> bool:
    last_message_id = user.last_message
    triggers_found = False
    stage = STAGES.get(user.stage)

    async for message in app.get_chat_history(user.id, offset_id=user.last_message, reverse= True):
        last_message_id = message.id
 
        if not triggers_found:
            if message.outgoing:
                try:
                    message_text = message.text.lower()
                except:
                    message_text = False

                if message_text:
                    for stop_word in STOP_WORDS:
                        if stop_word in message_text:
                            await db_functions.update_status(user.id, FINISHED, last_message_id)
                            return True
                    
                    for trigger in stage.triggers:
                        if trigger in message_text:
                            triggers_found = True
                            break
    
    if triggers_found:
        status = await functions.set_status(user.stage)
        await db_functions.update_status(user.id, status, last_message_id)
    else:
        await db_functions.update_last_message(user.id, last_message_id)


    return triggers_found


async def send_message(user_id: int, text: str) -> None:
    await app.send_message(chat_id = user_id,
                     text = text,
                     )


async def send_messages() -> None:
    users = await functions.get_users_for_messages()
    for user in users:
        try:
            triggers = await check_triggers(user)
        except:
            await db_functions.update_status(user.id, DEAD)
            triggers = True

        if not triggers:
            try:
                await send_message(user.id, STAGES.get(user.stage).message)
                status = await functions.set_status(user.stage)
            except:
                status = DEAD
            finally:
                await db_functions.update_status(user.id, status)


async def main() -> None:
    await db_functions.create_database()
    while True:
        try:
            await send_messages()
        except:
            pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_app())
    loop.create_task(main())
    loop.run_forever()