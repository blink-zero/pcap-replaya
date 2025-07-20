import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';
import io from 'socket.io-client';

const ProgressMonitor = ({ uploadedFile, replayConfig, onReplayComplete }) => {
  const [replayStatus, setReplayStatus] = useState(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [replayStats, setReplayStats] = useState({
    packets_sent: 0,
    bytes_sent: 0,
    elapsed_time: 0,
  });
  const [autoRefreshInterval, setAutoRefreshInterval] = useState(null);

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

    // Listen for replay status updates
    newSocket.on('replay_status', (data) => {
      console.log('Replay status update:', data);
      setReplayStatus(data);
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
        setIsReplaying(false);
        // Stop auto-refresh when replay completes
        stopAutoRefresh();
        if (onReplayComplete) {
          onReplayComplete(data);
        }
      }
    });

    // Listen for progress updates
    newSocket.on('replay_progress', (data) => {
      console.log('Replay progress update:', data);
      setProgress(data.progress || 0);
      setReplayStats({
        packets_sent: data.packets_sent || 0,
        bytes_sent: data.bytes_sent || 0,
        elapsed_time: data.elapsed_time || 0,
      });
    });

    // Cleanup on unmount
    return () => {
      newSocket.disconnect();
    };
  }, [onReplayComplete, stopAutoRefresh]);

  useEffect(() => {
    // Check initial replay status
    checkReplayStatus();
  }, []);

  useEffect(() => {
    // Cleanup auto-refresh interval on unmount
    return () => {
      if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
      }
    };
  }, [autoRefreshInterval]);

  const startAutoRefresh = () => {
    // Clear any existing interval
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
    }

    // Start new auto-refresh interval (every 2 seconds)
    const interval = setInterval(() => {
      checkReplayStatus();
    }, 2000);

    setAutoRefreshInterval(interval);
  };

  const stopAutoRefresh = () => {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      setAutoRefreshInterval(null);
    }
  };

  const checkReplayStatus = async () => {
    try {
      const response = await apiService.getReplayStatus();
      const status = response.data;
      setReplayStatus(status);
      setIsReplaying(status.status === 'running' || status.status === 'starting');
      if (status.progress_percent) {
        setProgress(status.progress_percent);
      }
    } catch (err) {
      console.error('Error checking replay status:', err);
    }
  };

  const startReplay = async () => {
    if (!uploadedFile || !replayConfig.interface || !replayConfig.speed) {
      setError('Please upload a file and configure replay settings');
      return;
    }

    try {
      setError(null);
      setIsReplaying(true);
      setProgress(0);
      setReplayStats({ packets_sent: 0, bytes_sent: 0, elapsed_time: 0 });

      const config = {
        file_id: uploadedFile.file_id,
        interface: replayConfig.interface,
        speed: replayConfig.speed,
        speed_unit: replayConfig.speed_unit || 'multiplier',
      };

      const response = await apiService.startReplay(config);
      setReplayStatus(response.data);
      
      // Start auto-refresh when replay begins
      startAutoRefresh();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start replay');
      setIsReplaying(false);
    }
  };

  const stopReplay = async () => {
    try {
      setError(null);
      await apiService.stopReplay();
      setIsReplaying(false);
      // Stop auto-refresh when manually stopping replay
      stopAutoRefresh();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to stop replay');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
      case 'error':
        return 'error';
      case 'stopped':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'starting':
        return 'Starting...';
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
      case 'error':
        return 'Failed';
      case 'stopped':
        return 'Stopped';
      default:
        return 'Idle';
    }
  };

  const canStartReplay = () => {
    return (
      uploadedFile &&
      replayConfig.interface &&
      replayConfig.speed &&
      !isReplaying
    );
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Replay Monitor
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<PlayIcon />}
              onClick={startReplay}
              disabled={!canStartReplay()}
              color="primary"
            >
              Start Replay
            </Button>
            <Button
              variant="outlined"
              startIcon={<StopIcon />}
              onClick={stopReplay}
              disabled={!isReplaying}
              color="error"
            >
              Stop
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={checkReplayStatus}
              size="small"
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {replayStatus && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="subtitle1">Status:</Typography>
              <Chip
                label={getStatusText(replayStatus.status)}
                color={getStatusColor(replayStatus.status)}
                size="small"
              />
              {isReplaying && (
                <CircularProgress size={16} />
              )}
            </Box>

            {replayStatus.replay_id && (
              <Typography variant="body2" color="text.secondary">
                Replay ID: {replayStatus.replay_id}
              </Typography>
            )}
          </Box>
        )}


        {replayStatus && replayStatus.interface && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Configuration
            </Typography>
            <Typography variant="body2">
              <strong>Interface:</strong> {replayStatus.interface}
            </Typography>
            <Typography variant="body2">
              <strong>Speed:</strong> {replayStatus.speed_unit === 'pps' 
                ? `${replayStatus.speed} PPS` 
                : `${replayStatus.speed}x`}
            </Typography>
            {replayStatus.file_path && (
              <Typography variant="body2">
                <strong>File:</strong> {replayStatus.file_path.split('/').pop()}
              </Typography>
            )}
          </Box>
        )}

        {replayStatus && replayStatus.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <strong>Replay Error:</strong> {replayStatus.error}
          </Alert>
        )}

        {!uploadedFile && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Please upload a PCAP file to begin replay.
          </Alert>
        )}

        {uploadedFile && (!replayConfig.interface || !replayConfig.speed) && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Please configure replay settings (interface and speed) to start replay.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressMonitor;
