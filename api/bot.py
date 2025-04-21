try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Flask is not installed. Installing now...")
    import subprocess
    subprocess.check_call(["pip", "install", "flask==2.0.1"])
    from flask import Flask, request, jsonify

import threading
import time
import os
import sys

# Add the parent directory to the path so we can import the bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from insta_bot import InstagramBot

app = Flask(__name__)

# Global variable to store the bot instance
bot_instance = None
bot_thread = None
bot_running = False

@app.route('/api/start', methods=['POST'])
def start_bot():
    global bot_instance, bot_thread, bot_running
    
    if bot_running:
        return jsonify({"status": "error", "message": "Bot is already running"}), 400
    
    try:
        # Create a new bot instance
        bot_instance = InstagramBot()
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        bot_running = True
        return jsonify({"status": "success", "message": "Bot started successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    global bot_instance, bot_thread, bot_running
    
    if not bot_running:
        return jsonify({"status": "error", "message": "Bot is not running"}), 400
    
    try:
        # Set a flag to stop the bot
        if bot_instance:
            bot_instance.running = False
        
        # Wait for the thread to finish
        if bot_thread:
            bot_thread.join(timeout=5)
        
        bot_running = False
        return jsonify({"status": "success", "message": "Bot stopped successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def bot_status():
    global bot_running
    
    return jsonify({
        "status": "running" if bot_running else "stopped",
        "message": "Bot is currently running" if bot_running else "Bot is not running"
    }), 200

def run_bot():
    """Run the bot in a separate thread"""
    global bot_instance
    
    if bot_instance:
        # Set a flag to control the bot loop
        bot_instance.running = True
        
        # Run the bot
        bot_instance.run()
        
        # Reset the flag when done
        bot_instance.running = False

if __name__ == '__main__':
    app.run(debug=True) 