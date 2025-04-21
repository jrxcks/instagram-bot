import { bot } from '../../api/bot';

export default function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ status: 'error', message: 'Method not allowed' });
  }

  try {
    res.status(200).json({
      status: 'success',
      data: {
        is_running: bot.is_running,
        last_message: bot.last_message,
        last_response: bot.last_response,
        processed_messages: bot.processed_messages
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
} 