import React, { useState } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { useMemoizedFetch } from './hooks/useAPI';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

function DataProcessor() {
  const [selectedConfig, setSelectedConfig] = useState('');
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('');
  const [frequency, setFrequency] = useState('00:10:00');
  const [status, setStatus] = useState('');
  const [processedFiles, setProcessedFiles] = useState([]);

  const { 
    data: configurationsData,
    loading: configsLoading,
    error: configsError,
  } = useMemoizedFetch('/configurations');

  const {
    data: configTagsData,
    loading: tagsLoading,
    error: tagsError,
  } = useMemoizedFetch(
    selectedConfig ? `/configurations/${selectedConfig}/tags` : null,
    [selectedConfig]
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedConfig) return;

    setStatus('Processing...');
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
        throw new Error(data.error || 'Processing failed');
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`);
      setProcessedFiles([]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Historian Data Processor</h1>
        
        {configsLoading && (
          <Alert className="mb-4">
            <AlertDescription>Loading configurations...</AlertDescription>
          </Alert>
        )}

        {configsError && (
          <Alert className="mb-4 bg-red-50 border-red-200 text-red-800">
            <AlertDescription>Error loading configurations: {configsError}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Configuration</label>
            <select
              value={selectedConfig}
              onChange={(e) => setSelectedConfig(e.target.value)}
              className="w-full p-2 border rounded"
              disabled={configsLoading}
            >
              <option value="">Select configuration</option>
              {configurationsData?.configurations?.map((config) => (
                <option key={config} value={config}>
                  {config}
                </option>
              ))}
            </select>
          </div>

          {selectedConfig && (
            <div className="space-y-2">
              <label className="block text-sm font-medium">Configuration Tags:</label>
              {tagsLoading ? (
                <Alert>
                  <AlertDescription>Loading tags...</AlertDescription>
                </Alert>
              ) : tagsError ? (
                <Alert className="bg-red-50 border-red-200 text-red-800">
                  <AlertDescription>Error loading tags: {tagsError}</AlertDescription>
                </Alert>
              ) : (
                <div className="text-sm text-gray-600 max-h-40 overflow-y-auto p-2 border rounded">
                  {configTagsData?.tags?.map((tag) => (
                    <div key={tag} className="py-1">
                      {tag}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

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

          <Button 
            type="submit" 
            className="w-full"
            disabled={!selectedConfig || configsLoading || tagsLoading}
          >
            Process Data
          </Button>
        </form>

        {status && (
          <div>
            <Alert className={`mt-4 ${status.includes('Error') ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
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
      </div>
    </div>
  );
}

export default DataProcessor;