import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

interface SidecarStatus {
  status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
  port: number;
  pid: number | null;
  uptime_seconds: number;
  message: string;
}

function App() {
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>({
    status: 'Stopped',
    port: 62601,
    pid: null,
    uptime_seconds: 0,
    message: '',
  });

  useEffect(() => {
    // 监听 sidecar 状态变化
    const unlisten = invoke('listen', { event: 'sidecar-status' })
      .then((unlisten: any) => {
        const listener = (event: any) => {
          setSidecarStatus(event.payload);
        };
        return unlisten;
      })
      .catch(console.error);

    return () => {
      unlisten.then((fn: any) => fn?.());
    };
  }, []);

  const handleStart = async () => {
    try {
      await invoke('start_sidecar');
    } catch (error) {
      console.error('Failed to start sidecar:', error);
    }
  };

  const handleStop = async () => {
    try {
      await invoke('stop_sidecar');
    } catch (error) {
      console.error('Failed to stop sidecar:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8">AnyClaw Desktop</h1>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Backend Status</h2>

          <div className="space-y-4">
            <div>
              <span className="text-gray-400">Status:</span>
              <span className={`ml-2 font-semibold ${
                sidecarStatus.status === 'Running' ? 'text-green-400' :
                sidecarStatus.status === 'Error' ? 'text-red-400' :
                'text-yellow-400'
              }`}>
                {sidecarStatus.status}
              </span>
            </div>

            <div>
              <span className="text-gray-400">Port:</span>
              <span className="ml-2">{sidecarStatus.port}</span>
            </div>

            <div>
              <span className="text-gray-400">PID:</span>
              <span className="ml-2">{sidecarStatus.pid || 'N/A'}</span>
            </div>

            <div>
              <span className="text-gray-400">Uptime:</span>
              <span className="ml-2">{sidecarStatus.uptime_seconds}s</span>
            </div>

            <div>
              <span className="text-gray-400">Message:</span>
              <span className="ml-2">{sidecarStatus.message}</span>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleStart}
              disabled={sidecarStatus.status === 'Running'}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Backend
            </button>
            <button
              onClick={handleStop}
              disabled={sidecarStatus.status !== 'Running'}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Stop Backend
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
