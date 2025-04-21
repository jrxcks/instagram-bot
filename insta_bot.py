import time
import random
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import os

import openai
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self):
        self.client = Client()
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.response_count = 0
        self.last_reset = datetime.now()
        self.last_health_check = datetime.now()
        self.processed_messages = set()  # Track processed message IDs
        
    def load_session(self):
        """Load saved session if available"""
        if config.SAVE_SESSION and os.path.exists(config.SESSION_FILE):
            try:
                with open(config.SESSION_FILE, 'r') as f:
                    session_data = json.load(f)
                self.client.load_settings(session_data)
                logger.info("Loaded saved session")
                return True
            except Exception as e:
                logger.error(f"Failed to load session: {str(e)}")
                # If session loading fails, delete the corrupted session file
                try:
                    os.remove(config.SESSION_FILE)
                    logger.info("Deleted corrupted session file")
                except:
                    pass
        return False

    def save_session(self):
        """Save current session"""
        if config.SAVE_SESSION:
            try:
                session_data = self.client.get_settings()
                with open(config.SESSION_FILE, 'w') as f:
                    json.dump(session_data, f)
                logger.info("Saved session")
            except Exception as e:
                logger.error(f"Failed to save session: {str(e)}")

    def login(self):
        """Login to Instagram"""
        try:
            # Try to use saved session first
            if self.load_session():
                try:
                    self.client.get_timeline_feed()  # Test if session is valid
                    logger.info("Successfully logged in using saved session")
                    return
                except LoginRequired:
                    logger.info("Saved session expired, logging in with credentials")
            
            # If no session or expired, login with credentials
            self.client.delay_range = [2, 5]  # Add random delay between actions
            self.client.login(
                config.INSTAGRAM_USERNAME,
                config.INSTAGRAM_PASSWORD,
                verification_code=None  # Let the library handle 2FA if needed
            )
            self.save_session()
            logger.info("Successfully logged in to Instagram")
        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            # If login fails, wait a bit before retrying
            time.sleep(30)
            raise

    def get_natural_response(self, message: str) -> str:
        """Generate a natural response using OpenAI"""
        try:
            # Check if message is about the club
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in config.CLUB_KEYWORDS):
                logger.info("Club-related question detected, sending club information")
                return config.CLUB_INFO

            # For other messages, use OpenAI
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful Instagram assistant. Keep responses casual and friendly, but professional. Keep responses under 100 words."},
                    {"role": "user", "content": message}
                ],
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return random.choice(list(config.DEFAULT_RESPONSES.values())[0])

    def should_respond(self) -> bool:
        """Check if we should respond based on rate limits"""
        now = datetime.now()
        if now - self.last_reset > timedelta(hours=1):
            self.response_count = 0
            self.last_reset = now
        
        return self.response_count < config.MAX_RESPONSES_PER_HOUR

    def is_new_message(self, message) -> bool:
        """Check if message is new and hasn't been processed before"""
        # Check if message ID is in processed set
        if message.id in self.processed_messages:
            logger.info(f"Message {message.id} already processed")
            return False
            
        # Check if message is recent (within last 5 minutes)
        try:
            # Try different timestamp attributes
            message_time = None
            if hasattr(message, 'taken_at'):
                if isinstance(message.taken_at, (int, float)):
                    message_time = datetime.fromtimestamp(message.taken_at, tz=timezone.utc)
                else:
                    message_time = message.taken_at.replace(tzinfo=timezone.utc)
            elif hasattr(message, 'timestamp'):
                if isinstance(message.timestamp, (int, float)):
                    message_time = datetime.fromtimestamp(message.timestamp, tz=timezone.utc)
                else:
                    message_time = message.timestamp.replace(tzinfo=timezone.utc)
            elif hasattr(message, 'created_at'):
                if isinstance(message.created_at, (int, float)):
                    message_time = datetime.fromtimestamp(message.created_at, tz=timezone.utc)
                else:
                    message_time = message.created_at.replace(tzinfo=timezone.utc)
            
            if message_time is None:
                logger.info(f"Message {message.id} has no timestamp, treating as new")
                return True
                
            # Make sure current time is also timezone-aware
            now = datetime.now(timezone.utc)
            if now - message_time > timedelta(minutes=5):
                logger.info(f"Message {message.id} too old (from {message_time})")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking message timestamp: {str(e)}")
            # If we can't determine the timestamp, treat the message as new
            return True

    def process_message(self, message: Dict) -> Optional[str]:
        """Process a single message and generate a response"""
        if not self.should_respond():
            logger.warning("Rate limit reached, skipping response")
            return None

        try:
            # Double-check that this isn't our own message
            if message['user_id'] == self.bot_user_id:
                logger.warning(f"Skipping response to our own message {message['id']}")
                return None
                
            # Add random delay to seem more human-like
            time.sleep(random.uniform(*config.RESPONSE_DELAY))
            
            # Generate response
            response = self.get_natural_response(message['text'])
            
            # Send response
            self.client.direct_send(response, [message['user_id']])
            
            # Mark message as processed
            self.processed_messages.add(message['id'])
            logger.info(f"Marked message {message['id']} as processed")
            
            self.response_count += 1
            logger.info(f"Responded to message from user {message['user_id']} with: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    def check_messages(self):
        """Check for new messages and respond"""
        try:
            logger.info("Checking for new messages...")
            
            # Get the bot's user ID if we don't have it yet
            if not hasattr(self, 'bot_user_id'):
                self.bot_user_id = self.client.user_id
                logger.info(f"Bot user ID: {self.bot_user_id}")
            
            # Get regular messages
            threads = self.client.direct_threads()
            logger.info(f"Found {len(threads)} message threads")
            
            # Get hidden messages if enabled
            if config.PROCESS_HIDDEN_MESSAGES:
                hidden_threads = self.client.direct_threads(selected_filter="unread")
                logger.info(f"Found {len(hidden_threads)} hidden message threads")
                threads.extend(hidden_threads)
            
            new_messages_count = 0
            for thread in threads:
                try:
                    messages = self.client.direct_messages(thread.id)
                    logger.info(f"Thread {thread.id} has {len(messages)} messages")
                    
                    # Process messages in reverse order (newest first)
                    for message in reversed(messages):
                        # Skip messages from the bot itself
                        if message.user_id == self.bot_user_id:
                            logger.info(f"Skipping message {message.id} from bot's own account (user_id: {message.user_id})")
                            continue
                            
                        if message.id in self.processed_messages:
                            logger.info(f"Message {message.id} already processed, skipping")
                            continue
                            
                        logger.info(f"Checking message from user {message.user_id}: {message.text[:50]}... (ID: {message.id})")
                        if self.is_new_message(message):
                            new_messages_count += 1
                            logger.info(f"Processing new message from user {message.user_id}: {message.text[:50]}...")
                            self.process_message({
                                'text': message.text,
                                'user_id': message.user_id,
                                'id': message.id
                            })
                except Exception as e:
                    logger.error(f"Error processing thread {thread.id}: {str(e)}")
                    continue
            
            logger.info(f"Processed {new_messages_count} new messages")
                        
        except LoginRequired:
            logger.error("Login required, attempting to relogin")
            self.login()
        except Exception as e:
            logger.error(f"Error checking messages: {str(e)}")

    def health_check(self):
        """Perform health check"""
        if not config.ENABLE_HEALTH_CHECK:
            return True

        now = datetime.now()
        if now - self.last_health_check > timedelta(seconds=config.HEALTH_CHECK_INTERVAL):
            try:
                self.client.get_timeline_feed()  # Test if session is valid
                self.last_health_check = now
                logger.info("Health check passed")
                return True
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                return False
        return True

    def check_follow_requests(self):
        """Check for and accept follow requests"""
        try:
            logger.info("Checking for follow requests...")
            
            # Get pending follow requests using the correct method
            pending_requests = self.client.friendships_pending()
            logger.info(f"Found {len(pending_requests)} pending follow requests")
            
            # Accept each follow request
            for user in pending_requests:
                try:
                    user_id = user.pk if hasattr(user, 'pk') else user
                    logger.info(f"Accepting follow request from user {user_id}")
                    self.client.friendships_approve(user_id)
                    logger.info(f"Successfully accepted follow request from user {user_id}")
                except Exception as e:
                    logger.error(f"Error accepting follow request from user {user_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error checking follow requests: {str(e)}")

    def run(self):
        """Main bot loop"""
        logger.info("Starting Instagram Bot")
        retry_count = 0
        
        while True:
            try:
                if retry_count >= config.MAX_RETRIES:
                    logger.error("Max retries reached, exiting")
                    break

                self.login()
                retry_count = 0  # Reset retry count on successful login
                
                while True:
                    if not self.health_check():
                        break
                        
                    # Check for follow requests first
                    self.check_follow_requests()
                    
                    # Then check for messages
                    self.check_messages()
                    
                    time.sleep(config.CHECK_INTERVAL)
                    
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                retry_count += 1
                time.sleep(config.RETRY_DELAY)

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run() 