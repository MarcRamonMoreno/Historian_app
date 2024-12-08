import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

function DataProcessor() {
  const [configurations, setConfigurations] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState('');
  const [tags, setTags] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('');
  const [frequency, setFrequency] = useState('00:10:00');
  const [status, setStatus] = useState('');
  const [processedFiles, setProcessedFiles] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    try {
      const response = await fetch(`${API_URL}/configurations`);
      const data = await response.json();
      setConfigurations(data.configurations);
    } catch (err) {
      setError('Failed to fetch configurations');
    }
  };

  const fetchTags = async (configName) => {
    try {
      const response = await fetch(`${API_URL}/configurations/${configName}/tags`);
      const data = await response.json();
      setTags(data.tags);
    } catch (err) {
      setError('Failed to fetch tags');
    }
  };

  const handleConfigChange = (e) => {
    const value = e.target.value;
    setSelectedConfig(value);
    if (value) {
      fetchTags(value);
    } else {
      setTags([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Processing...');
    setError('');
    setProcessedFiles([]);

    try {
      const startDateTime = `${startDate} ${startTime}`;
      const endDateTime = `${endDate} ${endTime}`;

      const response = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          configuration: selectedConfig,
          startDate: startDateTime,
          endDate: endDateTime,
          frequency,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setStatus('Data processed successfully!');
        setProcessedFiles(data.processed_files || []);
      } else {
        setError(data.error || 'Processing failed');
      }
    } catch (err) {
      setError('Failed to process data');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Historian Data Processor</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Configuration</label>
            <select
              value={selectedConfig}
              onChange={handleConfigChange}
              className="w-full p-2 border rounded"
            >
              <option value="">Select configuration</option>
              {configurations.map((config) => (
                <option key={config} value={config}>
                  {config}
                </option>
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

          <div className="space-y-2">
            <label className="block text-sm font-medium">Frequency (HH:MM:SS)</label>
            <Input
              type="text"
              pattern="[0-9]{2}:[0-9]{2}:[0-9]{2}"
              placeholder="00:10:00"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              required
            />
          </div>

          {selectedConfig && tags.length > 0 && (
            <div className="space-y-2">
              <label className="block text-sm font-medium">Selected Tags:</label>
              <div className="text-sm text-gray-600 max-h-40 overflow-y-auto p-2 border rounded">
                {tags.map((tag) => (
                  <div key={tag} className="py-1">
                    {tag}
                  </div>
                ))}
              </div>
            </div>
          )}

          <Button type="submit" className="w-full">
            Process Data
          </Button>
        </form>

        {status && (
          <div>
            <Alert className="mt-4 bg-green-50 border-green-200">
              <AlertDescription>{status}</AlertDescription>
            </Alert>
            {processedFiles.length > 0 && (
              <div className="mt-4 p-4 border rounded-lg">
                <h3 className="font-medium mb-2">Download Processed Files:</h3>
                <div className="space-y-2">
                  {processedFiles.map((file) => (
                    <div key={file} className="flex items-center">
                      <a
                        href={`${API_URL}/download/${file}`}
                        download
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        {file}
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <Alert className="mt-4 bg-red-50 border-red-200 text-red-800">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}

export default DataProcessor;