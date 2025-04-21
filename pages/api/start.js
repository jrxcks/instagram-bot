import { bot } from '../../api/bot';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ status: 'error', message: 'Method not allowed' });
  }

  try {
    if (bot.is_running) {
      return res.status(400).json({ status: 'error', message: 'Bot is already running' });
    }

    bot.start();
    res.status(200).json({ status: 'success', message: 'Bot started successfully' });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
} 