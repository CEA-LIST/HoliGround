import json
import os
import pickle


class IndexedJSONL:
    def __init__(self, file_path: str, primary_key='id', index_file=None, force_rebuild=False):
        """
        Args:
            file_path (str): Path to the .jsonl file.
            primary_key (str): The key in the JSON objects that holds the unique ID.
            index_file (str): Optional path for the index file. Defaults to file_path + '.idx'.
            force_rebuild (bool): If True, ignores existing index and rebuilds it.
        """
        self.file_path = file_path
        self.primary_key = primary_key
        self.index_path = index_file if index_file else f"{file_path}.idx"
        self.offset_map = self._load_or_build_index(force_rebuild)

        print(f"Total entries indexed: {len(self)}")

    def _load_or_build_index(self, force_rebuild):
        """Internal method to manage the index lifecycle."""
        if os.path.exists(self.index_path) and not force_rebuild:
            print(f"Loading index from ./{os.path.relpath(self.index_path)}")
            try:
                with open(self.index_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Failed to load index ({e}). Rebuilding...")
        
        return self._build_index()

    def _build_index(self):
        """Scans the file and creates a {id: byte_offset} map."""
        print(f"Building index for {self.file_path} (this may take a while)...")
        mapping = {}
        
        processed_bytes = 0
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            while True:
                offset = f.tell()
                line = f.readline()
                if not line:
                    break
                
                # Progress tracking (optional, helpful for big files)
                processed_bytes += len(line.encode('utf-8')) # approx
                
                try:
                    # We parse the line to extract the ID
                    # Note: If lines are massive, a regex extraction is faster here
                    entry = json.loads(line)
                    key = entry.get(self.primary_key)
                    
                    if key is not None:
                        mapping[key] = offset
                except json.JSONDecodeError:
                    continue # Skip malformed lines

        # Save to disk
        print(f"Saving index to {self.index_path}...")
        with open(self.index_path, 'wb') as f:
            pickle.dump(mapping, f)
            
        print("Index built successfully.")
        return mapping

    def get(self, entry_id):
        """
        Retrieves a single entry by ID.
        Returns the dictionary or None if not found.
        """
        offset = self.offset_map.get(entry_id)
        
        if offset is None:
            return None

        with open(self.file_path, 'r', encoding='utf-8') as f:
            f.seek(offset)
            line = f.readline()
            return json.loads(line)

    def __len__(self):
        return len(self.offset_map)
    
    def __contains__(self, item):
        return item in self.offset_map
    
    def __iter__(self):
        """Iterates over IDs (Keys), acting like a standard dict."""
        for key in self.offset_map:
            yield key

    def keys(self):
        """Returns an iterator over the IDs."""
        return self.offset_map.keys()

    def values(self):
        """
        Iterates over the actual JSON entries.
        Efficiently keeps the file open during iteration.
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            # We iterate based on the index to ensure we only yield valid/indexed entries
            for offset in self.offset_map.values():
                f.seek(offset)
                line = f.readline().strip()
                if line:
                    yield json.loads(line)

    def items(self):
        """Iterates over (ID, Entry) tuples."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for key, offset in self.offset_map.items():
                f.seek(offset)
                line = f.readline().strip()
                if line:
                    yield key, json.loads(line)