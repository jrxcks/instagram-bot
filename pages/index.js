import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [botStatus, setBotStatus] = useState('stopped');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    openaiKey: ''
  });

  useEffect(() => {
    // Check bot status on page load
    checkBotStatus();
  }, []);

  const checkBotStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setBotStatus(data.status);
    } catch (err) {
      setError('Failed to check bot status');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const startBot = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });
      const data = await response.json();
      if (data.status === 'success') {
        setBotStatus('running');
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to start bot');
    }
    setLoading(false);
  };

  const stopBot = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/stop', {
        method: 'POST',
      });
      const data = await response.json();
      if (data.status === 'success') {
        setBotStatus('stopped');
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to stop bot');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <Head>
        <title>Instagram Bot Dashboard</title>
        <meta name="description" content="Control your Instagram bot" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-3xl font-bold text-center mb-8">Instagram Bot Dashboard</h1>
                
                <div className="text-center mb-8">
                  <p className="text-lg">Bot Status: 
                    <span className={`ml-2 font-semibold ${botStatus === 'running' ? 'text-green-600' : 'text-red-600'}`}>
                      {botStatus.toUpperCase()}
                    </span>
                  </p>
                </div>

                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <span className="block sm:inline">{error}</span>
                  </div>
                )}

                <div className="space-y-4 mb-8">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Instagram Username</label>
                    <input
                      type="text"
                      name="username"
                      value={credentials.username}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Instagram Password</label>
                    <input
                      type="password"
                      name="password"
                      value={credentials.password}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
                    <input
                      type="password"
                      name="openaiKey"
                      value={credentials.openaiKey}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
                    />
                  </div>
                </div>

                <div className="flex justify-center space-x-4">
                  <button
                    onClick={startBot}
                    disabled={loading || botStatus === 'running' || !credentials.username || !credentials.password || !credentials.openaiKey}
                    className={`px-4 py-2 rounded-md text-white font-medium ${
                      loading || botStatus === 'running' || !credentials.username || !credentials.password || !credentials.openaiKey
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-green-500 hover:bg-green-600'
                    }`}
                  >
                    {loading ? 'Processing...' : 'Start Bot'}
                  </button>

                  <button
                    onClick={stopBot}
                    disabled={loading || botStatus === 'stopped'}
                    className={`px-4 py-2 rounded-md text-white font-medium ${
                      loading || botStatus === 'stopped'
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-red-500 hover:bg-red-600'
                    }`}
                  >
                    {loading ? 'Processing...' : 'Stop Bot'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 