# Instagram DM Bot

An automated Instagram DM responder that handles both regular and hidden messages using natural language processing.

## Features
- Automated responses to Instagram DMs
- Support for hidden messages inbox
- Natural language processing for human-like responses
- Secure credential management
- Configurable response templates

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
```

3. Run the bot:
```bash
python insta_bot.py
```

## Security Notes
- Never commit your `.env` file
- Use 2FA when possible
- Regularly rotate your credentials
- Monitor bot activity for unusual patterns

## Configuration
Edit `config.py` to customize:
- Response templates
- Message handling rules
- Processing intervals
- Language settings 