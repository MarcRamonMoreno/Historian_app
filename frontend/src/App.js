import React, { useState } from 'react';
import DataProcessor from './DataProcessor';
import ConfigManager from './ConfigManager';
import { Button } from './components/ui/button';

function App() {
  const [currentView, setCurrentView] = useState('processor'); // 'processor' or 'config'

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold">Historian Data Tool</h1>
              </div>
              <div className="ml-6 flex space-x-4">
                <Button
                  onClick={() => setCurrentView('processor')}
                  className={currentView === 'processor' ? 'bg-blue-700' : 'bg-blue-500'}
                >
                  Data Processor
                </Button>
                <Button
                  onClick={() => setCurrentView('config')}
                  className={currentView === 'config' ? 'bg-blue-700' : 'bg-blue-500'}
                >
                  Configuration Manager
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <main className="py-6">
        {currentView === 'processor' ? <DataProcessor /> : <ConfigManager />}
      </main>
    </div>
  );
}

export default App;