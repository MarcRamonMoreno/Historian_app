import React, { useState, useEffect, useCallback } from 'react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Alert, AlertDescription } from './components/ui/alert';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

const ConfigManager = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [cachedTags, setCachedTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [configurations, setConfigurations] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState('');
  const [newConfigName, setNewConfigName] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadTags = useCallback(async (reset = false) => {
    if (isLoading || (!hasMore && !reset)) return;
    
    try {
      setIsLoading(true);
      const currentPage = reset ? 1 : page;
      const response = await fetch(
        `${API_URL}/tags/available?search=${encodeURIComponent(searchTerm)}&page=${currentPage}&per_page=100`
      );
      const data = await response.json();
      
      if (response.ok) {
        const newTags = data.tags || [];
        setCachedTags(prev => reset ? newTags : [...prev, ...newTags]);
        setHasMore(currentPage * data.per_page < data.total);
        setPage(currentPage + 1);
      }
    } catch (err) {
      setError(`Error loading tags: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, page, hasMore, isLoading]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
      setHasMore(true);
      loadTags(true);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, loadTags]);

  useEffect(() => {
    loadTags();
  }, [loadTags]);

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    try {
      const response = await fetch(`${API_URL}/configurations`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch configurations');
      }
      
      setConfigurations(data.configurations || []);
      setError('');
    } catch (err) {
      setError(`Error fetching configurations: ${err.message}`);
    }
  };

  const handleConfigSelect = async (configName) => {
    setSelectedConfig(configName);
    if (configName) {
      try {
        const response = await fetch(`${API_URL}/configurations/${configName}/tags`);
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch configuration tags');
        }
        setSelectedTags(data.tags || []);
      } catch (err) {
        setError(`Error loading configuration: ${err.message}`);
      }
    } else {
      setSelectedTags([]);
    }
  };

  const handleAddTag = (tag) => {
    if (!selectedTags.includes(tag)) {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const handleRemoveTag = (tag) => {
    setSelectedTags(selectedTags.filter(t => t !== tag));
  };

  const handleSaveConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/configurations/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: selectedConfig,
          tags: selectedTags,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Configuration saved successfully');
        fetchConfigurations();
      } else {
        throw new Error(data.error || 'Failed to save configuration');
      }
    } catch (err) {
      setError(`Error saving configuration: ${err.message}`);
    }
  };

  const handleCreateConfig = async () => {
    if (!newConfigName) {
      setError('Please enter a configuration name');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/configurations/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newConfigName,
          tags: selectedTags,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Configuration created successfully');
        fetchConfigurations();
        setNewConfigName('');
        setSelectedTags([]);
      } else {
        throw new Error(data.error || 'Failed to create configuration');
      }
    } catch (err) {
      setError(`Error creating configuration: ${err.message}`);
    }
  };

  const handleDeleteConfig = async () => {
    if (!selectedConfig) {
      setError('Please select a configuration to delete');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/configurations/delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: selectedConfig,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Configuration deleted successfully');
        fetchConfigurations();
        setSelectedConfig('');
        setSelectedTags([]);
      } else {
        throw new Error(data.error || 'Failed to delete configuration');
      }
    } catch (err) {
      setError(`Error deleting configuration: ${err.message}`);
    }
  };

  const observer = useCallback((node) => {
    if (!node) return;
    const intersectionObserver = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !isLoading) {
        loadTags();
      }
    });
    intersectionObserver.observe(node);
    return () => intersectionObserver.disconnect();
  }, [hasMore, isLoading, loadTags]);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Configuration Manager</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-lg font-semibold mb-4">Available Tags:</h2>
            <Input
              type="text"
              placeholder="Search tags..."
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mb-4"
            />
            <div className="border rounded-lg p-4 h-96 overflow-y-auto">
              <div className="space-y-2">
                {cachedTags.map((tag, index) => (
                  <div 
                    key={tag} 
                    className="flex items-center justify-between py-1 hover:bg-gray-50"
                    ref={index === cachedTags.length - 1 ? observer : null}
                  >
                    <span className="text-sm">{tag}</span>
                    <Button
                      onClick={() => handleAddTag(tag)}
                      className="px-2 py-1 text-xs"
                      disabled={selectedTags.includes(tag)}
                    >
                      Add
                    </Button>
                  </div>
                ))}
                {isLoading && <div className="text-center py-2">Loading...</div>}
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-semibold mb-4">Selected Tags:</h2>
            <div className="border rounded-lg p-4 h-96 overflow-y-auto">
              <div className="space-y-2">
                {selectedTags.map((tag) => (
                  <div key={tag} className="flex items-center justify-between">
                    <span className="text-sm">{tag}</span>
                    <Button
                      onClick={() => handleRemoveTag(tag)}
                      className="px-2 py-1 text-xs bg-red-500 hover:bg-red-600"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <div className="flex items-center space-x-4">
            <select
              value={selectedConfig}
              onChange={(e) => handleConfigSelect(e.target.value)}
              className="flex-1 p-2 border rounded"
            >
              <option value="">Select Configuration</option>
              {configurations.map((config) => (
                <option key={config} value={config}>
                  {config}
                </option>
              ))}
            </select>
            <Button onClick={handleSaveConfig}>Save</Button>
            <Button
              onClick={handleDeleteConfig}
              className="bg-red-500 hover:bg-red-600"
            >
              Delete
            </Button>
          </div>

          <div className="flex items-center space-x-4">
            <Input
              type="text"
              value={newConfigName}
              onChange={(e) => setNewConfigName(e.target.value)}
              placeholder="New Configuration Name"
              className="flex-1"
            />
            <Button onClick={handleCreateConfig}>Create New</Button>
          </div>
        </div>

        {message && (
          <Alert className="mt-4 bg-green-50 border-green-200">
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="mt-4 bg-red-50 border-red-200 text-red-800">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
};

export default ConfigManager;