import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Input } from './input';

const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
};

const TagSelect = ({ onTagsSelected }) => {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef();
  const debouncedSearch = useDebounce(search, 300);
  const loadingRef = useRef(false);
  const abortControllerRef = useRef(null);

  const loadTags = useCallback(async (pageNum, searchTerm, append = false) => {
    try {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      setLoading(true);
      loadingRef.current = true;

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/tags/available?search=${searchTerm}&page=${pageNum}&per_page=100`,
        { signal: abortControllerRef.current.signal }
      );

      const data = await response.json();
      
      setTags(prevTags => {
        if (append) {
          return [...prevTags, ...data.tags];
        }
        return data.tags;
      });

      setHasMore(pageNum * 100 < data.total);
      
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error loading tags:', error);
      }
    } finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }, []);

  // Reset when search changes
  useEffect(() => {
    setTags([]);
    setPage(1);
    setHasMore(true);
    loadTags(1, debouncedSearch, false);
  }, [debouncedSearch, loadTags]);

  // Intersection Observer for infinite scrolling
  const lastTagRef = useCallback(node => {
    if (loading) return;
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);
      }
    });

    if (node) observerRef.current.observe(node);
  }, [loading, hasMore]);

  // Load more when page changes
  useEffect(() => {
    if (page > 1) {
      loadTags(page, debouncedSearch, true);
    }
  }, [page, debouncedSearch, loadTags]);

  return (
    <div className="w-full">
      <div className="space-y-4">
        <Input
          type="text"
          placeholder="Search tags..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full"
        />
        <div className="border rounded-md h-96 overflow-y-auto">
          {loading && tags.length === 0 ? (
            <div className="p-4 text-center text-gray-500">Loading tags...</div>
          ) : (
            <ul className="divide-y">
              {tags.map((tag, index) => (
                <li
                  key={`${tag}-${index}`}
                  ref={index === tags.length - 1 ? lastTagRef : null}
                  className="p-2 hover:bg-gray-50 cursor-pointer truncate"
                  onClick={() => onTagsSelected(tag)}
                >
                  {tag}
                </li>
              ))}
            </ul>
          )}
          {loading && tags.length > 0 && (
            <div className="p-2 text-center text-sm text-gray-500">
              Loading more tags...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TagSelect;