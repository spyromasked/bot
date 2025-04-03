import os
import random
import aiohttp
import asyncio

class UniversalSelfReactBot:
    def __init__(self):
        # Get token from environment variables
        self.token = os.environ.get('DISCORD_TOKEN')
        if not self.token:
            raise ValueError(
                "No DISCORD_TOKEN found in environment variables!\n"
                "Please add your token to GitHub Secrets:\n"
                "1. Go to Repository Settings → Secrets → Actions\n"
                "2. Add new secret named 'DISCORD_TOKEN'\n"
                "3. Paste your bot token"
            )
            
        # Reaction configuration
        self.base_emojis = ['😭', '👻']  # Default reactions
        self.funny_emojis = ['😭', '☠️', '⁉️']  # Reactions for funny messages
        self.funny_triggers = ['lol', 'lmao', 'lmfao', 'funny', 'haha', '😂', '😹', '💀', '..']
        
        # Rate limiting and session management
        self.session = None
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent reactions
        self.last_messages = set()  # Prevent duplicate reactions
        self.user_id = None

    async def start(self):
        """Initialize the bot connection"""
        self.session = aiohttp.ClientSession()
        print("🟢 Bot started successfully")
        await self.listen_to_messages()

    async def close(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            print("🔴 Session closed properly")

    def is_funny(self, content):
        """Check if message contains funny triggers"""
        content_lower = content.lower()
        return any(trigger in content_lower for trigger in self.funny_triggers)

    async def react_to_self_message(self, channel_id, message_id, is_funny):
        """Add reactions to a message"""
        emojis = self.funny_emojis if is_funny else self.base_emojis
        
        async with self.semaphore:
            for emoji in emojis:
                try:
                    react_url = f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
                    
                    async with self.session.put(
                        react_url,
                        headers={'Authorization': self.token},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        # Handle rate limits
                        if resp.status == 429:
                            retry_data = await resp.json()
                            await asyncio.sleep(retry_data.get('retry_after', 1))
                            continue
                        elif resp.status not in (200, 204):
                            print(f"⚠️ Failed to react: {resp.status}")
                        
                        await asyncio.sleep(random.uniform(0.15, 0.3))  # Natural delay
                        
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"⚠️ Reaction error: {type(e).__name__}")
                    await asyncio.sleep(1)
                    continue

    async def get_self_user_id(self):
        """Fetch the bot's user ID"""
        try:
            async with self.session.get(
                'https://discord.com/api/v9/users/@me',
                headers={'Authorization': self.token},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['id']
                raise Exception(f"Failed to get user ID: {resp.status}")
        except Exception as e:
            print(f"🔴 Critical error fetching user ID: {e}")
            raise

    async def listen_to_messages(self):
        """Main WebSocket listener"""
        self.user_id = await self.get_self_user_id()
        print(f"🤖 Bot User ID: {self.user_id}")
        
        while True:
            try:
                async with self.session.ws_connect(
                    'wss://gateway.discord.gg/?v=9&encoding=json',
                    timeout=30,
                    heartbeat=30
                ) as ws:
                    # Identify with Discord
                    await ws.send_json({
                        "op": 2,
                        "d": {
                            "token": self.token,
                            "intents": 512,  # Message content intent
                            "properties": {
                                "$os": "linux",
                                "$browser": "aiohttp",
                                "$device": "aiohttp"
                            }
                        }
                    })

                    async for msg in ws:
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            continue

                        data = msg.json()
                        if data.get('t') == 'MESSAGE_CREATE':
                            message = data['d']
                            
                            # Only react to our own messages
                            if message['author']['id'] != self.user_id:
                                continue
                                
                            # Prevent duplicate reactions
                            if message['id'] in self.last_messages:
                                continue
                                
                            self.last_messages.add(message['id'])
                            asyncio.create_task(self._clean_message_cache(message['id']))
                            
                            # Determine reaction set
                            is_funny = self.is_funny(message.get('content', ''))
                            asyncio.create_task(
                                self.react_to_self_message(
                                    message['channel_id'],
                                    message['id'],
                                    is_funny
                                )
                            )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"🔴 Connection error: {type(e).__name__}, reconnecting in 5s...")
                await asyncio.sleep(5)
                continue
            except Exception as e:
                print(f"🔴 Unexpected error: {type(e).__name__}: {e}")
                await asyncio.sleep(10)
                continue

    async def _clean_message_cache(self, message_id):
        """Remove message ID from cache after delay"""
        await asyncio.sleep(30)  # Keep in cache for 30 seconds
        self.last_messages.discard(message_id)

async def main():
    bot = None
    try:
        print("🔵 Starting Discord bot...")
        bot = UniversalSelfReactBot()
        await bot.start()
    except ValueError as e:
        print(f"🔴 Configuration error: {e}")
    except KeyboardInterrupt:
        print("\n🟠 Bot stopped by user")
    except Exception as e:
        print(f"🔴 Fatal error: {type(e).__name__}: {e}")
    finally:
        if bot:
            await bot.close()
        print("🔴 Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
