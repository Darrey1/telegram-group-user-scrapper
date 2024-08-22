from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import SendMessageRequest,ExportChatInviteRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, UserAlreadyParticipantError
import asyncio


api_id = ""
api_hash = ""
phone_number = ""

client = TelegramClient('session_name', api_id, api_hash)



async def get_usernames_and_add_to_group(source_group, target_group):
    await client.start()

    try:
        source_entity = await client.get_entity(source_group)
        participants = await client.get_participants(source_entity)
        usernames = [user.username for user in participants if user.username]
        # usernames = [user.id for user in participants if user.id]
        print(f"Usernames to add: {usernames}")
        for username in usernames:
            try:
                # user = await client.get_entity(username)
                # username = user.username
                if username.lower().endswith("bot") or username is None:
                    print(f"user with {username} is a bot, skipping...")
                    continue
                print(f"{username} is adding to the new group")
                await add_user_to_group(target_group, username)
                await asyncio.sleep(10) 
            except Exception as e:
                continue
    except Exception as e:
        print(f"Failed to get usernames or add users: {str(e)}")
        await asyncio.sleep(20) 
        


async def send_invite_link_to_user(group_id, user_id):
    try:
        # Get the invite link
        invite_link_response = await client(ExportChatInviteRequest(group_id))
        invite_link = invite_link_response.link

        # Send the invite link to the user
        await client(SendMessageRequest(
            peer=user_id,
            message=f"Join the group using this invite link: {invite_link}"
        ))

    except Exception as e:
        print(f"Failed to send invite link: {e}")   
        await asyncio.sleep(30)      
        

async def add_user_to_group(group_username, user_username):
    try:
        group = await client.get_entity(group_username)
        participants = await client.get_participants(group)
        usernames = [user.username for user in participants if user.username]
        user = await client.get_entity(user_username)
        if user_username in usernames:
            print("user already exist, skipping....")
            return

        await client(InviteToChannelRequest(group, [user]))
        
        print(f"Successfully added @{user_username} to {group_username}")
    except FloodWaitError as e:
            print(f"Rate limited. Sleeping for {e.seconds} seconds...")
            await send_invite_link_to_user(group.id,user.id)
            print(f"but i have send an invite link to the {user.username} to join manually")
            await asyncio.sleep(e.seconds)
    except UserPrivacyRestrictedError:
            print(f"Failed to add {user}: The user's privacy settings do not allow adding to groups.")
            await send_invite_link_to_user(group.id,user.id)
            print(f"but i have send an invite link to the {user.username} to join manually")
    except UserAlreadyParticipantError:
            print(f"Failed to add {user}: The user is already a participant of the group.")
            await send_invite_link_to_user(group.id,user.id)
            print(f"but i have send an invite link to the {user.username} to join manually")
    
    except Exception as e:
        print(f"Failed to add user: {str(e)}")
        await send_invite_link_to_user(group.id,user.id)
        print(f"but i have send an invite link to the {user.username} to join manually")
        await asyncio.sleep(30) 
        
        

copy_username_name_group = input("enter the group username to get all the user from:")
add_username_to_group = input("enter the username of the group to add the users to:")
with client:
    # client.loop.run_until_complete(get_usernames_and_add_to_group('tech_like_pro', 'ddriveraiupdate'))
    client.loop.run_until_complete(get_usernames_and_add_to_group(copy_username_name_group, add_username_to_group))
#iPlay999b

# AirdropFamGroup
# piteasio
# https://t.me/tradesphe
