import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  IconButton,
  Chip,
  TextField,
  MenuItem,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Clear as ClearIcon,
  Download as DownloadIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import io from 'socket.io-client';
import { apiService } from '../services/api';

const LiveLog = () => {
  const [logs, setLogs] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filterLevel, setFilterLevel] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const logContainerRef = useRef(null);
  const maxLogs = 1000; // Maximum number of logs to keep in memory

  useEffect(() => {
    // Initialize socket connection - use current host (nginx will proxy to backend)
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    const socketUrl = `${protocol}//${hostname}${port}`;
    
    console.log('Connecting to WebSocket at:', socketUrl);
    const newSocket = io(socketUrl, {
      path: '/socket.io/',
      transports: ['websocket', 'polling']
    });

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('Connected to log stream');
      setIsConnected(true);
      setError(null);
      
      // Subscribe to log stream
      newSocket.emit('subscribe_logs');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from log stream');
      setIsConnected(false);
    });

    newSocket.on('connect_error', (err) => {
      console.error('Connection error:', err);
      setError('Failed to connect to log stream');
      setIsConnected(false);
    });

    // Log event handlers
    newSocket.on('log_subscription_status', (data) => {
      console.log('Log subscription status:', data);
      if (data.status === 'error') {
        setError(data.message);
      }
    });

    newSocket.on('log_history', (data) => {
      console.log('Received log history:', data.count, 'logs');
      setLogs(data.logs || []);
    });

    newSocket.on('log_entry', (logEntry) => {
      if (!isPaused) {
        setLogs(prevLogs => {
          const newLogs = [...prevLogs, logEntry];
          // Keep only the last maxLogs entries
          if (newLogs.length > maxLogs) {
            return newLogs.slice(-maxLogs);
          }
          return newLogs;
        });
      }
    });

    // Load initial log stats
    loadLogStats();

    // Cleanup on unmount
    return () => {
      if (newSocket) {
        newSocket.emit('unsubscribe_logs');
        newSocket.disconnect();
      }
    };
  }, [isPaused]);

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const loadLogStats = async () => {
    try {
      const response = await apiService.getLogStats();
      setStats(response.data);
    } catch (err) {
      console.error('Error loading log stats:', err);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const downloadLogs = () => {
    const logText = filteredLogs.map(log => log.formatted).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pcap-replaya-logs-${new Date().toISOString().slice(0, 19)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'ERROR':
        return 'error';
      case 'WARNING':
        return 'warning';
      case 'INFO':
        return 'info';
      case 'DEBUG':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Filter logs based on level and search term
  const filteredLogs = logs.filter(log => {
    const levelMatch = filterLevel === 'ALL' || log.level === filterLevel;
    const searchMatch = !searchTerm || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.logger.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.filename.toLowerCase().includes(searchTerm.toLowerCase());
    
    return levelMatch && searchMatch;
  });

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Live Application Logs
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              size="small"
            />
            <Chip
              label={`${filteredLogs.length} logs`}
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 200 }}
            InputProps={{
              startAdornment: <FilterIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          
          <TextField
            select
            size="small"
            label="Level"
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            sx={{ minWidth: 100 }}
          >
            <MenuItem value="ALL">All</MenuItem>
            <MenuItem value="DEBUG">Debug</MenuItem>
            <MenuItem value="INFO">Info</MenuItem>
            <MenuItem value="WARNING">Warning</MenuItem>
            <MenuItem value="ERROR">Error</MenuItem>
          </TextField>

          <FormControlLabel
            control={
              <Switch
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                size="small"
              />
            }
            label="Auto-scroll"
          />

          <Tooltip title={isPaused ? "Resume log stream" : "Pause log stream"}>
            <IconButton onClick={togglePause} size="small">
              {isPaused ? <PlayIcon /> : <PauseIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Clear logs">
            <IconButton onClick={clearLogs} size="small">
              <ClearIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Download logs">
            <IconButton onClick={downloadLogs} size="small">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Pause Alert */}
        {isPaused && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Log stream is paused. Click the play button to resume.
          </Alert>
        )}

        {/* Log Container */}
        <Box
          ref={logContainerRef}
          sx={{
            height: 400,
            overflow: 'auto',
            bgcolor: 'grey.50',
            border: 1,
            borderColor: 'grey.300',
            borderRadius: 1,
            p: 1,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
          }}
        >
          {filteredLogs.length === 0 ? (
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Typography color="text.secondary">
                {logs.length === 0 ? 'No logs available' : 'No logs match current filters'}
              </Typography>
            </Box>
          ) : (
            filteredLogs.map((log, index) => (
              <Box
                key={`${log.timestamp}-${index}`}
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1,
                  py: 0.5,
                  borderBottom: '1px solid',
                  borderColor: 'grey.200',
                  '&:hover': {
                    bgcolor: 'grey.100',
                  },
                }}
              >
                <Typography
                  component="span"
                  sx={{
                    minWidth: 80,
                    fontSize: '0.75rem',
                    color: 'text.secondary',
                    fontFamily: 'monospace',
                  }}
                >
                  {formatTimestamp(log.timestamp)}
                </Typography>
                
                <Chip
                  label={log.level}
                  color={getLogLevelColor(log.level)}
                  size="small"
                  sx={{ minWidth: 70, fontSize: '0.7rem', height: 20 }}
                />
                
                <Typography
                  component="span"
                  sx={{
                    minWidth: 100,
                    fontSize: '0.75rem',
                    color: 'text.secondary',
                    fontFamily: 'monospace',
                  }}
                >
                  {log.logger}
                </Typography>
                
                <Typography
                  component="span"
                  sx={{
                    flex: 1,
                    fontSize: '0.875rem',
                    fontFamily: 'monospace',
                    wordBreak: 'break-word',
                  }}
                >
                  {log.message}
                </Typography>
                
                <Typography
                  component="span"
                  sx={{
                    fontSize: '0.7rem',
                    color: 'text.secondary',
                    fontFamily: 'monospace',
                  }}
                >
                  {log.filename}:{log.lineno}
                </Typography>
              </Box>
            ))
          )}
        </Box>

        {/* Footer Stats */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Showing {filteredLogs.length} of {logs.length} logs
            {searchTerm && ` (filtered by "${searchTerm}")`}
            {filterLevel !== 'ALL' && ` (${filterLevel} level)`}
          </Typography>
          
          {stats.connected_clients !== undefined && (
            <Typography variant="caption" color="text.secondary">
              {stats.connected_clients} client(s) connected
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default LiveLog;
