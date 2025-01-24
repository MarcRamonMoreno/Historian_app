import React, { useState } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { useMemoizedFetch } from './hooks/useAPI';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

function ConfigManager() {
  const [selectedConfig, setSelectedConfig] = useState('');
  const [newConfigName, setNewConfigName] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTag, setSearchTag] = useState('');
  
  const {
    data: configurationsData,
    loading: configsLoading,
    error: configsError,
    fetchMemoizedData: fetchConfigurations
  } = useMemoizedFetch('/configurations');

  const {
    data: configTagsData,
    loading: configTagsLoading,
    error: configTagsError,
    fetchMemoizedData: fetchConfigTags
  } = useMemoizedFetch(
    selectedConfig ? `/configurations/${selectedConfig}/tags` : null,
    [selectedConfig]
  );

  const {
    data: availableTagsData,
    loading: tagsLoading,
    error: tagsError
  } = useMemoizedFetch('/tags');

  const createConfiguration = async () => {
    try {
      if (!newConfigName) return;

      const response = await fetch(`${API_URL}/configurations/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newConfigName,
          tags: []
        }),
      });

      if (!response.ok) throw new Error('Failed to create configuration');
      
      setSuccess('Configuration created successfully');
      setNewConfigName('');
      fetchConfigurations();
    } catch (err) {
      setSuccess('');
    }
  };

  const addTagToConfig = async (tag) => {
    try {
      if (!selectedConfig) return;
      if (configTagsData?.tags?.includes(tag)) return;

      const tags = [...(configTagsData?.tags || []), tag];
      
      const response = await fetch(`${API_URL}/configurations/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedConfig,
          tags
        }),
      });

      if (!response.ok) throw new Error('Failed to add tag');
      
      setSuccess('Tag added successfully');
      fetchConfigTags();
    } catch (err) {
      setSuccess('');
    }
  };

  const removeTag = async (tag) => {
    try {
      const tags = configTagsData?.tags?.filter(t => t !== tag) || [];
      
      const response = await fetch(`${API_URL}/configurations/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedConfig,
          tags
        }),
      });

      if (!response.ok) throw new Error('Failed to remove tag');
      
      setSuccess('Tag removed successfully');
      fetchConfigTags();
    } catch (err) {
      setSuccess('');
    }
  };

  const deleteConfiguration = async () => {
    try {
      if (!selectedConfig) return;

      const response = await fetch(`${API_URL}/configurations/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedConfig
        }),
      });

      if (!response.ok) throw new Error('Failed to delete configuration');
      
      setSuccess('Configuration deleted successfully');
      setSelectedConfig('');
      fetchConfigurations();
    } catch (err) {
      setSuccess('');
    }
  };

  const filteredTags = availableTagsData?.tags?.filter(tag => 
    tag.toLowerCase().includes(searchTag.toLowerCase()) &&
    !configTagsData?.tags?.includes(tag)
  ) || [];

  return (
    <div className="max-w-7xl mx-auto px-4">
      {(configsLoading || tagsLoading) && (
        <Alert className="mb-4">
          <AlertDescription>Loading...</AlertDescription>
        </Alert>
      )}

      {(configsError || tagsError) && (
        <Alert className="mb-4 bg-red-50 border-red-200 text-red-800">
          <AlertDescription>
            {configsError || tagsError}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Create New Configuration</h2>
            <div className="flex gap-4 mb-4">
              <Input
                type="text"
                placeholder="Configuration name"
                value={newConfigName}
                onChange={(e) => setNewConfigName(e.target.value)}
                className="flex-1"
                disabled={configsLoading}
              />
              <Button 
                onClick={createConfiguration}
                disabled={configsLoading || !newConfigName}
              >
                Create Configuration
              </Button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Manage Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Configuration</label>
                <select
                  value={selectedConfig}
                  onChange={(e) => setSelectedConfig(e.target.value)}
                  className="w-full p-2 border rounded"
                  disabled={configsLoading}
                >
                  <option value="">Select configuration</option>
                  {configurationsData?.configurations?.map((config) => (
                    <option key={config} value={config}>{config}</option>
                  ))}
                </select>
              </div>

              {selectedConfig && (
                <>
                  <div className="flex gap-4 items-center">
                    <Button 
                      onClick={deleteConfiguration}
                      className="bg-red-600 hover:bg-red-700"
                      disabled={configsLoading}
                    >
                      Delete Configuration
                    </Button>
                  </div>

                  {configTagsLoading ? (
                    <Alert>
                      <AlertDescription>Loading configuration tags...</AlertDescription>
                    </Alert>
                  ) : configTagsError ? (
                    <Alert className="bg-red-50 border-red-200 text-red-800">
                      <AlertDescription>Error loading configuration tags: {configTagsError}</AlertDescription>
                    </Alert>
                  ) : configTagsData?.tags?.length > 0 && (
                    <div>
                      <h3 className="font-medium mb-2">Configuration Tags</h3>
                      <div className="border rounded p-4 space-y-2 max-h-96 overflow-y-auto">
                        {configTagsData.tags.map((tag) => (
                          <div key={tag} className="flex justify-between items-center">
                            <span>{tag}</span>
                            <Button
                              onClick={() => removeTag(tag)}
                              className="text-red-600 hover:text-red-700"
                              disabled={configTagsLoading}
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Available Tags</h2>
          {selectedConfig ? (
            <>
              <Input
                type="text"
                placeholder="Search tags..."
                value={searchTag}
                onChange={(e) => setSearchTag(e.target.value)}
                className="mb-4"
                disabled={tagsLoading}
              />
              {tagsLoading ? (
                <Alert>
                  <AlertDescription>Loading available tags...</AlertDescription>
                </Alert>
              ) : tagsError ? (
                <Alert className="bg-red-50 border-red-200 text-red-800">
                  <AlertDescription>Error loading tags: {tagsError}</AlertDescription>
                </Alert>
              ) : (
                <div className="border rounded p-4 max-h-[calc(100vh-300px)] overflow-y-auto">
                  {filteredTags.map((tag) => (
                    <div key={tag} className="flex justify-between items-center py-2">
                      <span>{tag}</span>
                      <Button
                        onClick={() => addTagToConfig(tag)}
                        disabled={configTagsLoading}
                      >
                        Add to Config
                      </Button>
                    </div>
                  ))}
                  {filteredTags.length === 0 && (
                    <p className="text-gray-500 text-center py-4">
                      No additional tags available
                    </p>
                  )}
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500 text-center py-4">
              Select a configuration to manage tags
            </p>
          )}
        </div>
      </div>

      {success && (
        <Alert className="mt-4 bg-green-50 border-green-200">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}

export default ConfigManager;