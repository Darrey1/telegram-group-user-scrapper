from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
import asyncio

api_id = ""
api_hash = ""
phone_number = "+234+++"

client = TelegramClient('session_name', api_id, api_hash)



async def get_usernames_and_add_to_group(source_group, target_group):
    await client.start()

    try:
        source_entity = await client.get_entity(source_group)
        participants = await client.get_participants(source_entity)
        # usernames = [user.username for user in participants if user.username]
        usernames = [user.id for user in participants if user.id]
        print(f"Usernames to add: {usernames}")
        for username in usernames:
            try:
                user = await client.get_entity(username)
                username = user.username
                if username.lower().endswith("bot") or username is None:
                    print(f"user with {username} is a bot, skipping...")
                    continue
                print(f"{username} is adding to the new group")
                await add_user_to_group(target_group, username)
                await asyncio.sleep(20) 
            except Exception as e:
                continue
    except Exception as e:
        print(f"Failed to get usernames or add users: {str(e)}")
        await asyncio.sleep(20) 
        
        
        

async def add_user_to_group(group_username, user_username):
    try:
        group = await client.get_entity(group_username)
        user = await client.get_entity(user_username)
        await client(InviteToChannelRequest(group, [user]))
        print(f"Successfully added @{user_username} to {group_username}")
    
    except Exception as e:
        print(f"Failed to add user: {str(e)}")

# Run the script
copy_username_name_group = input("enter the group username to get all the user from:")
add_username_to_group = input("enter the username of the group to add the users to:")
with client:
    # client.loop.run_until_complete(get_usernames_and_add_to_group('tech_like_pro', 'ddriveraiupdate'))
    client.loop.run_until_complete(get_usernames_and_add_to_group(copy_username_name_group, add_username_to_group))



# piteasio
# trade_shape