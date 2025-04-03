just fix this code except the funny triggers it will react with 👻😭 on every message 

 - import os
import random
import aiohttp
import asyncio

class UniversalSelfReactBot:
    def __init__(self):
        # Get token directly from GitHub Secrets
        self.token = os.environ.get('DISCORD_TOKEN')
        if not self.token:
            raise ValueError(
                "No DISCORD_TOKEN found in environment variables!\n"
                "Please add your token to GitHub Secrets:\n"
                "1. Go to Repository Settings → Secrets → Actions\n"
                "2. Add new secret named 'DISCORD_TOKEN'\n"
                "3. Paste your bot token"
            )
            
        self.base_emojis = ['😭', '👻']
        self.funny_emojis = ['😭', '☠️', '⁉️']
        self.funny_triggers = ['lol', 'lmao', 'lmfao', 'funny', 'haha', '😂', '😹', '💀', '..']
        self.session = None
        self.semaphore = asyncio.Semaphore(5)
        self.last_messages = set()

    async def start(self):
        self.session = aiohttp.ClientSession()
        print("🟢 Bot started (Token from GitHub Secrets)")
        await self.listen_to_messages()

    async def close(self):
        if self.session:
            await self.session.close()

    def is_funny(self, content):
        content_lower = content.lower()
        return any(trigger in content_lower for trigger in self.funny_triggers)

    async def react_to_self_message(self, channel_id, message_id, is_funny):
        emojis = self.funny_emojis if is_funny else self.base_emojis
        
        async with self.semaphore:
            for emoji in emojis:
                try:
                    react_url = f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
                    async with self.session.put(
                        react_url, 
                        headers={'Authorization': self.token}
                    ) as resp:
                        if resp.status == 429:
                            retry_after = (await resp.json()).get('retry_after', 0.5)
                            await asyncio.sleep(retry_after)
                            continue
                        await asyncio.sleep(random.uniform(0.1, 0.25))
                except Exception:
                    await asyncio.sleep(0.5)
                    continue

    async def get_self_user_id(self):
        async with self.session.get(
            'https://discord.com/api/v9/users/@me',
            headers={'Authorization': self.token}
        ) as resp:
            data = await resp.json()
            return data['id']

    async def listen_to_messages(self):
        self.user_id = await self.get_self_user_id()
        gateway_url = 'wss://gateway.discord.gg/?v=9&encoding=json'
        
        async with self.session.ws_connect(gateway_url) as ws:
            await ws.send_json({
                "op": 2,
                "d": {
                    "token": self.token,
                    "intents": 512,
                    "properties": {
                        "$os": "linux",
                        "$browser": "my_library",
                        "$device": "my_library"
                    }
                }
            })

            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT:
                    continue

                data = msg.json()
                if data.get('t') == 'MESSAGE_CREATE':
                    message = data['d']
                    if (message['author']['id'] != self.user_id or 
                        message['id'] in self.last_messages):
                        continue
                    
                    self.last_messages.add(message['id'])
                    asyncio.create_task(self._clean_message_cache(message['id']))
                    
                    is_funny = self.is_funny(message['content'])
                    asyncio.create_task(
                        self.react_to_self_message(
                            message['channel_id'],
                            message['id'],
                            is_funny
                        )
                    )

    async def _clean_message_cache(self, message_id):
        await asyncio.sleep(30)
        self.last_messages.discard(message_id)

async def main():
    try:
        print("🔵 Starting Bot (GitHub Secrets Version)...")
        bot = UniversalSelfReactBot()
        await bot.start()
    except ValueError as e:
        print(f"🔴 Error: {e}")
    except KeyboardInterrupt:
        print("\n🟠 Bot stopped by user")
    except Exception as e:
        print(f"🔴 Unexpected error: {type(e).__name__}")
    finally:
        if 'bot' in locals():
            await bot.close()
        print("🔴 Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
