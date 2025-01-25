import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

function DataProcessor() {
  const [selectedConfig, setSelectedConfig] = useState('');
  const [configurations, setConfigurations] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('');
  const [status, setStatus] = useState('');
  const [exportFile, setExportFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConfigurations = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/configurations`);
        if (!response.ok) throw new Error('Failed to fetch configurations');
        const data = await response.json();
        setConfigurations(data.configurations.map(config => config.replace('.txt', '')) || []);
      } catch (error) {
        setError(error.message);
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchConfigurations();
  }, []);
  
  // Update the handleSubmit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Processing...');
    setExportFile(null);
  
    try {
      const startDateTime = `${startDate} ${startTime}`;
      const endDateTime = `${endDate} ${endTime}`;
  
      const response = await fetch(`${API_URL}/process`, {  // Changed from /export to /process
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          configuration: `${selectedConfig}.txt`,  // Add .txt extension back
          startDate: startDateTime,
          endDate: endDateTime,
        }),
      });
  
      const data = await response.json();
      
      if (response.ok) {
        setStatus('Data processed successfully!');
        setExportFile(data.processed_files?.[0]);
      } else {
        throw new Error(data.error || 'Processing failed');
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`);
      setExportFile(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Historian Data Processor</h1>
        
        {loading && (
          <Alert className="mb-4">
            <AlertDescription>Loading configurations...</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="mb-4 bg-red-50 border-red-200 text-red-800">
            <AlertDescription>Error: {error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Configuration</label>
            <select
              value={selectedConfig}
              onChange={(e) => setSelectedConfig(e.target.value)}
              className="w-full p-2 border rounded"
              required
            >
              <option value="">Select configuration</option>
              {configurations.map((config) => (
                <option key={config} value={config}>{config.replace('.txt', '')}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Start Date and Time</label>
            <div className="flex space-x-2">
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
                className="flex-1"
              />
              <Input
                type="time"
                step="1"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
                className="flex-1"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">End Date and Time</label>
            <div className="flex space-x-2">
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
                className="flex-1"
              />
              <Input
                type="time"
                step="1"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
                className="flex-1"
              />
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full"
            disabled={!selectedConfig || loading}
          >
            Process Data
          </Button>
        </form>

        {status && (
          <Alert className={`mt-4 ${status.includes('Error') ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
            <AlertDescription>{status}</AlertDescription>
          </Alert>
        )}

        {exportFile && (
          <div className="mt-4 p-4 border rounded-lg">
            <h3 className="font-medium mb-2">Download Export:</h3>
            <a
              href={`${API_URL}/download/${exportFile}`}
              download
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {exportFile}
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default DataProcessor;