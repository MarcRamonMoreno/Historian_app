import { useState, useCallback, useEffect, useRef } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://100.97.52.112:5002/api';

export const useAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (endpoint) => {
    if (!endpoint) return null;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}${endpoint}`);
      if (!response.ok) throw new Error('API request failed');
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchData, loading, error };
};

export const useMemoizedFetch = (endpoint, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  // Memoize dependencies to avoid unnecessary re-renders
  const deps = useRef(dependencies);
  deps.current = dependencies;

  const fetchMemoizedData = useCallback(async () => {
    if (!endpoint) return;
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        signal: abortControllerRef.current.signal
      });
      
      if (!response.ok) throw new Error('API request failed');
      const result = await response.json();
      setData(result);
    } catch (err) {
      if (err.name === 'AbortError') return;
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchMemoizedData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchMemoizedData, endpoint]);

  return {
    data,
    loading,
    error,
    fetchMemoizedData
  };
};

export default useAPI;