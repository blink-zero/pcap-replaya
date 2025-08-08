import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional
import uuid


class ReplayHistoryService:
    """Service for managing replay history."""
    
    def __init__(self, history_file='replay_history.json'):
        self.history_file = history_file
        self.history = []
        self.load_history()
    
    def load_history(self):
        """Load history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                logging.info(
                    f"Loaded {len(self.history)} replay history entries"
                )
            else:
                self.history = []
                logging.info(
                    "No history file found, starting with empty history"
                )
        except Exception as e:
            logging.error(f"Error loading history: {e}")
            self.history = []
    
    def save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
            logging.debug(f"Saved {len(self.history)} replay history entries")
        except Exception as e:
            logging.error(f"Error saving history: {e}")
    
    def add_replay(self, replay_data: Dict) -> str:
        """Add a new replay to history."""
        try:
            history_entry = {
                'id': str(uuid.uuid4()),
                'filename': replay_data.get('filename', 'Unknown'),
                'file_id': replay_data.get('file_id'),
                'file_size': replay_data.get('file_size', 0),
                'config': {
                    'interface': replay_data.get('interface'),
                    'speed': replay_data.get('speed'),
                    'speed_unit': replay_data.get('speed_unit'),
                    'continuous': replay_data.get('continuous', False),
                    'loop': replay_data.get('loop', False),
                    'preload_pcap': replay_data.get('preload_pcap', False)
                },
                'status': 'running',
                'started_at': datetime.utcnow().isoformat(),
                'completed_at': None,
                'duration': None,
                'packets_sent': None,
                'error_message': None,
                'replay_id': replay_data.get('replay_id')
            }
            
            self.history.insert(0, history_entry)  # Add to beginning
            
            # Keep only last 100 entries
            if len(self.history) > 100:
                self.history = self.history[:100]
            
            self.save_history()
            logging.info(f"Added replay to history: {history_entry['id']}")
            return history_entry['id']
            
        except Exception as e:
            logging.error(f"Error adding replay to history: {e}")
            return None
    
    def update_replay_status(self, replay_id: str, status: str, **kwargs):
        """Update replay status and other fields."""
        try:
            for entry in self.history:
                if entry.get('replay_id') == replay_id:
                    entry['status'] = status
                    
                    if status in ['completed', 'failed', 'stopped']:
                        entry['completed_at'] = datetime.utcnow().isoformat()
                        
                        # Calculate duration
                        if entry.get('started_at'):
                            start_time = datetime.fromisoformat(
                                entry['started_at']
                            )
                            end_time = datetime.utcnow()
                            duration = (end_time - start_time).total_seconds()
                            entry['duration'] = duration
                    
                    # Update additional fields
                    for key, value in kwargs.items():
                        if key in ['packets_sent', 'error_message']:
                            entry[key] = value
                    
                    self.save_history()
                    logging.info(
                        f"Updated replay status: {replay_id} -> {status}"
                    )
                    return True
            
            logging.warning(f"Replay not found in history: {replay_id}")
            return False
            
        except Exception as e:
            logging.error(f"Error updating replay status: {e}")
            return False
    
    def get_history(self, limit: int = 50, offset: int = 0,
                    search: str = None, status: str = None) -> Dict:
        """Get replay history with pagination, search, and filtering."""
        try:
            # Start with all history
            filtered_history = self.history.copy()
            
            # Apply search filter
            if search and search.strip():
                search_term = search.strip().lower()
                filtered_history = [
                    entry for entry in filtered_history
                    if (search_term in entry.get('filename', '').lower() or
                        search_term in entry.get('config', {}).get(
                            'interface', '').lower())
                ]
            
            # Apply status filter
            if status and status.upper() != 'ALL':
                status_filter = status.lower()
                filtered_history = [
                    entry for entry in filtered_history
                    if entry.get('status', '').lower() == status_filter
                ]
            
            # Get total count after filtering
            total_count = len(filtered_history)
            
            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_history = filtered_history[start_idx:end_idx]
            
            return {
                'history': paginated_history,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': end_idx < total_count,
                'search': search,
                'status': status
            }
        except Exception as e:
            logging.error(f"Error getting history: {e}")
            return {
                'history': [],
                'total_count': 0,
                'limit': limit,
                'offset': offset,
                'has_more': False,
                'search': search,
                'status': status
            }
    
    def get_replay_by_id(self, history_id: str) -> Optional[Dict]:
        """Get a specific replay by history ID."""
        try:
            for entry in self.history:
                if entry.get('id') == history_id:
                    return entry
            return None
        except Exception as e:
            logging.error(f"Error getting replay by ID: {e}")
            return None
    
    def clear_history(self):
        """Clear all history."""
        try:
            self.history = []
            self.save_history()
            logging.info("Cleared replay history")
        except Exception as e:
            logging.error(f"Error clearing history: {e}")


# Global instance
_history_service = None


def get_history_service() -> ReplayHistoryService:
    """Get the global history service instance."""
    global _history_service
    if _history_service is None:
        _history_service = ReplayHistoryService()
    return _history_service
