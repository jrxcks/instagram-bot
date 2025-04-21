import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# OpenAI API key for natural language processing
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Bot settings
CHECK_INTERVAL = 30  # Check for new messages every 30 seconds
MAX_RESPONSES_PER_HOUR = 50  # Rate limiting
RESPONSE_DELAY = (2, 5)  # Random delay between 2-5 seconds before responding

# Message processing settings
PROCESS_HIDDEN_MESSAGES = True
MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 10

# Session handling
SESSION_FILE = 'instagram_session.json'
SAVE_SESSION = True  # Save session to avoid frequent logins

# Club information
CLUB_INFO = """📍 Address: General Prim 71 Hospitalet (Barcelona, Spain)

⏰ Opening times: everyday 10am - 11pm

🚪 Entering the club: Walk under the shutters and ring the doorbell (on the left)

🔒 30€ Membership: To become a member, you must arrive at DOE BCN with your ID, please.

💭 Any other information can be found at the club 

We hope to see you soon 🫡💨

@DOEBCN 🇪🇸 @GrowWithDoe 🌱 @DankOfEngland 👑"""

# Keywords to identify club-related questions
CLUB_KEYWORDS = [
    'join', 'membership', 'member', 'club', 'doe', 'bcn', 'barcelona',
    'social club', 'how to join', 'where', 'address', 'location',
    'opening', 'hours', 'time', 'price', 'cost', 'fee', 'id',
    'entrance', 'enter', 'door', 'doorbell', 'test'
]

# Response templates (will be enhanced by OpenAI)
DEFAULT_RESPONSES = {
    'greeting': [
        "Hey! Thanks for your message. I'll get back to you soon!",
        "Hi there! Thanks for reaching out. I'll respond shortly!",
    ],
    'question': [
        "That's a great question! Let me look into that for you.",
        "I'll check that out and get back to you right away.",
    ],
    'urgent': [
        "I understand this is urgent. I'll prioritize your request.",
        "Thanks for letting me know about the urgency. I'll handle this ASAP.",
    ]
}

# OpenAI settings
OPENAI_MODEL = "gpt-4o-mini"  # Using the most cost-effective model
MAX_TOKENS = 100  # Reduced token limit for cost savings
TEMPERATURE = 0.7  # Controls response creativity (0.0 = deterministic, 1.0 = creative)

# Cloud deployment settings
ENABLE_HEALTH_CHECK = True
HEALTH_CHECK_INTERVAL = 3600  # Check health every hour
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds 