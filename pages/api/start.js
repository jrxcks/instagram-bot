import { bot } from '../../api/bot';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ status: 'error', message: 'Method not allowed' });
  }

  try {
    const { username, password, openaiKey } = req.body;

    if (!username || !password || !openaiKey) {
      return res.status(400).json({ 
        status: 'error', 
        message: 'Missing required credentials' 
      });
    }

    // Set the credentials for the bot
    bot.set_credentials(username, password, openaiKey);

    // Start the bot
    bot.start();
    
    res.status(200).json({ 
      status: 'success', 
      message: 'Bot started successfully' 
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      message: error.message 
    });
  }
} 