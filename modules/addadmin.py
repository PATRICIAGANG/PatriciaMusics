from pyrogram import Client, filters

from helpers.decorators import chat_allowed, admin_check, delayDelete, admin_mode_check, hasRequiredPermission, database_check
from utils.Logger import *
from utils.MongoClient import MongoDBClient

MongoDBClient = MongoDBClient()


@Client.on_message(filters.command(['refreshadmins', 'refreshadmins@vcplayerbot']) & ~filters.edited & ~filters.bot)
@database_check
@chat_allowed
@admin_mode_check
async def refreshAdmins(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"refreshadmins command in chat : {chat_id}")

        admins = await client.get_chat_members(chat_id, filter="administrators")
        admins = list(
            filter(lambda a:  a.user is not None and (a.user.id == config.get('BOT_ID') or a.user.is_bot is False), admins))
        admins = [{'chat_id': i.user.id, 'username': i.user.username if hasattr(
            i.user, 'username') else '', 'haspermission': hasRequiredPermission(i)} for i in admins]
        logInfo(f"refreshadmins in chat : {chat_id} , admins : {admins}")
        MongoDBClient.update_admins(chat_id, admins)
        m = await client.send_message(message.chat.id, f"**__Successfully refreshed admin list : {len(admins)} admins.__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in refreshAdmins: {ex}", True)
        m = await client.send_message(message.chat.id, f"**__Failed to refresh admin list : {ex}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return


@Client.on_message(filters.command(['auth', 'auth@vcplayerbot']) & ~filters.edited & ~filters.bot)
@database_check
@chat_allowed
@admin_check
async def addAdmins(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"auth command in chat : {chat_id}")

        user = None
        # check if the message is a reply
        if message.reply_to_message is not None:
            user = message.reply_to_message.from_user
        else:
            m = await client.send_message(message.chat.id, f"**Send this command in reply to a message.**")
            await delayDelete(m, 10)
            return

        if user is None or user.is_bot is True:
            m = await client.send_message(message.chat.id, f"**❎ Failed : Bots cannot be admins and the supergorup[anonymous admin] is by default admin.**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return
        if user.id in [c['chat_id'] for c in current_client['admins']]:
            m = await client.send_message(message.chat.id, f"**🧐 This user is already an admin.**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return
        newadmin = {'chat_id': user.id, 'username': user.username if hasattr(
            user, 'username') else ''}
        logInfo(
            f"making call to add the admin in chat : {chat_id} , admins : {newadmin}")

        MongoDBClient.update_admins(chat_id, newadmin)
        m = await client.send_message(message.chat.id, f"**__Successfully added the user to admin list : {newadmin['username'] if newadmin['username'] not in [''] else newadmin['chat_id']}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in addAdmins: {ex}", True)
        m = await client.send_message(message.chat.id, f"**__Failed to add the user to admin list : {ex}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return


@Client.on_message(filters.command(['unauth', 'unauth@vcplayerbot']) & ~filters.edited & ~filters.bot)
@database_check
@chat_allowed
@admin_check
async def removeAdmins(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"unauth command in chat : {chat_id}")

        user = None
        # check if the message is a reply
        if message.reply_to_message is not None:
            user = message.reply_to_message.from_user
        else:
            m = await client.send_message(message.chat.id, f"**Send this command in reply to a message.**")
            await delayDelete(m, 10)
            return

        if user is None or user.is_bot is True:
            m = await client.send_message(message.chat.id, f"**❎ Fᴀɪʟᴇᴅ : Bots cannot be added/removed as admins and the supergorup[anonymous admin] is by default admin.**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return
        if user.id not in [c['chat_id'] for c in current_client['admins']]:
            m = await client.send_message(message.chat.id, f"**🧐 Usᴇʀ Is Nᴏᴛ Aᴅᴍɪɴ Yᴇᴛ[ Tʜᴇʀᴇ Aᴅᴍɪɴ Aʀᴇ Nᴏᴛ Sᴀᴍᴇ As Gʀᴏᴜᴩ! ].**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return
        newadmin = {'chat_id': user.id, 'username': user.username if hasattr(
            user, 'username') else ''}
        logInfo(
            f"Mᴀᴋɪɴɢ Cᴀʟʟ Tᴏ Rᴇᴍᴏᴠᴇ Tʜᴇ Aᴅᴍɪɴ Iɴ Cʜᴀᴛ : {chat_id} , admins : {newadmin}")

        MongoDBClient.remove_admins(chat_id, newadmin)
        m = await client.send_message(message.chat.id, f"**__Sᴜᴄᴄᴇssғᴜʟʟʏ Rᴇᴍᴏᴠᴇᴅ Tʜᴇ Usᴇʀ : {newadmin['username'] if newadmin['username'] not in [''] else newadmin['chat_id']}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in removeAdmins: {ex}", True)
        m = await client.send_message(message.chat.id, f"**__Failed to remove the user from admin list : {ex}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return


@Client.on_message(filters.command(['listadmins', 'listadmins@vcplayerbot']) & ~filters.edited & ~filters.bot)
@database_check
@chat_allowed
@admin_check
async def listAdmins(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"listadmins command in chat : {chat_id}")

        if len(current_client['admins']) == 0:
            msg = "**__Nᴏ Mᴜsɪᴄ Pʟᴀʏᴇʀ Aᴅᴍɪɴ Hᴀs Bᴇᴇɴ Aᴅᴅᴇᴅ Yᴇᴛ.__**"
        else:
            msg = "**Current MusicPlayer Admins:**\n\n"
            for i in range(len(current_client['admins'])):
                msg = msg + \
                    f"**{i+1}.** __{current_client['admins'][i]['chat_id']} - {current_client['admins'][i]['username']}__\n"

        m = await client.send_message(message.chat.id, f"{msg}")
        await delayDelete(m, 10)
        return

    except Exception as ex:
        logException(f"Error in listAdmins: {ex}", True)
        m = await client.send_message(message.chat.id, f"**__Failed to list the admins : {ex}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return


@Client.on_message(filters.command(['adminmode', 'adminmode@Patricia_robot']) & ~filters.edited & ~filters.bot)
@database_check
@chat_allowed
@admin_check
async def adminModeToggle(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"adminModeToggle command in chat : {chat_id}")

        if len(message.command) > 1 and message.command[1].lower() in ['on', 'off']:
            new_status = True if message.command[1].lower() == 'on' else False
            if current_client.get('admin_mode') == new_status:
                msg = f"**🐶 Tʜᴇ Dᴇsɪʀᴇᴅ Sᴛᴀᴛᴜs Is Tʜᴇ Cᴜʀʀᴇɴᴛ Oɴᴇ  ,Hᴇɴᴄᴇ Nᴏᴛʜɪɴɢ Cʜᴀɴɢᴇᴅ!**"
            else:
                MongoDBClient.update_admin_mode(chat_id, new_status)
                msg = f"**✅ Cʜᴀɴɢᴇᴅ Tʜᴇ Aᴅᴍɪɴ Mᴏᴅᴇ : {new_status}.**"
                if new_status is True:
                    msg = msg + f"\n\n__Nᴏᴡ Oɴʟʏ Aᴅᴍɪɴ Wɪʟʟ Aʙʟᴇ Tᴏ Pᴇʀғᴏʀᴍ Tʜɪs Aᴄᴛɪᴏɴ.__"
                else:
                    msg = msg + f"\n\n__Nᴏᴡ Aɴʏ Usᴇʀ Cᴀɴ Pᴇʀғᴏʀᴍ Tʜɪs Aᴄᴛɪᴏɴ.__"

        else:
            msg = f"**😯Iɴᴄᴏʀʀᴇᴄᴛ Cᴏᴍᴍᴀɴᴅ, Cᴏʀʀᴇᴄᴛ Usᴀɢᴇ ⤵️ **\n__/adminmode on|off__"

        m = await client.send_message(message.chat.id, f"{msg}")
        await delayDelete(m, 10)
        return

    except Exception as ex:
        logException(f"Error in adminModeToggle: {ex}", True)
        m = await client.send_message(message.chat.id, f"**__Failed to toggle the admin mode : {ex}__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return
