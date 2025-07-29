import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  TextField,
  MenuItem,
  Pagination,
  Stack,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { apiService, formatFileSize, formatDuration, formatSpeed } from '../services/api';

const ReplayHistory = ({ onReplayStart }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReplay, setSelectedReplay] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [confirmReplayOpen, setConfirmReplayOpen] = useState(false);
  const [replayingId, setReplayingId] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const itemsPerPage = 20;

  useEffect(() => {
    loadHistory();
  }, [currentPage]);

  useEffect(() => {
    // Reset to first page when filters change
    if (currentPage !== 1) {
      setCurrentPage(1);
    } else {
      loadHistory();
    }
  }, [filterStatus, searchTerm]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const offset = (currentPage - 1) * itemsPerPage;
      const response = await apiService.getReplayHistory(itemsPerPage, offset);
      
      setHistory(response.data.history || []);
      setTotalCount(response.data.total_count || 0);
      setHasMore(response.data.has_more || false);
    } catch (err) {
      console.error('Error loading replay history:', err);
      setError('Failed to load replay history');
    } finally {
      setLoading(false);
    }
  };

  const handleReplayAgain = async (historyItem) => {
    try {
      setReplayingId(historyItem.id);
      
      // Prepare replay config from history
      const replayConfig = {
        file_id: historyItem.file_id,
        interface: historyItem.config.interface,
        speed: historyItem.config.speed,
        speed_unit: historyItem.config.speed_unit,
        loop: historyItem.config.loop || false,
        preload_pcap: historyItem.config.preload_pcap || false,
      };

      const response = await apiService.startReplay(replayConfig);
      
      if (response.data.success) {
        // Notify parent component about replay start
        if (onReplayStart) {
          onReplayStart({
            ...historyItem,
            replay_id: response.data.replay_id,
            status: 'running'
          });
        }
        
        // Refresh history to show updated status
        await loadHistory();
        setConfirmReplayOpen(false);
      } else {
        setError(response.data.error || 'Failed to start replay');
      }
    } catch (err) {
      console.error('Error starting replay:', err);
      setError(err.response?.data?.error || 'Failed to start replay');
    } finally {
      setReplayingId(null);
    }
  };

  const showDetails = (historyItem) => {
    setSelectedReplay(historyItem);
    setDetailsOpen(true);
  };

  const confirmReplay = (historyItem) => {
    setSelectedReplay(historyItem);
    setConfirmReplayOpen(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'stopped':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  // Filter history based on status and search term
  const filteredHistory = history.filter(item => {
    const statusMatch = filterStatus === 'ALL' || item.status === filterStatus;
    const searchMatch = !searchTerm || 
      item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.config.interface.toLowerCase().includes(searchTerm.toLowerCase());
    
    return statusMatch && searchMatch;
  });

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Loading replay history...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Replay History
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={`${totalCount} total replays`}
              size="small"
              variant="outlined"
            />
            <Tooltip title="Refresh history">
              <IconButton onClick={loadHistory} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search by filename or interface..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 250 }}
            InputProps={{
              startAdornment: <FilterIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          
          <TextField
            select
            size="small"
            label="Status"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            sx={{ minWidth: 120 }}
          >
            <MenuItem value="ALL">All</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="running">Running</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="stopped">Stopped</MenuItem>
          </TextField>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* History Table */}
        {filteredHistory.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              {history.length === 0 ? 'No replay history available' : 'No replays match current filters'}
            </Typography>
          </Box>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Filename</TableCell>
                  <TableCell>Interface</TableCell>
                  <TableCell>Speed</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredHistory.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {item.filename}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatFileSize(item.file_size)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {item.config.interface}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatSpeed(item.config.speed, item.config.speed_unit)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={item.status}
                        color={getStatusColor(item.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatTimestamp(item.started_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {item.duration ? formatDuration(item.duration) : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View details">
                          <IconButton
                            size="small"
                            onClick={() => showDetails(item)}
                          >
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Replay again">
                          <IconButton
                            size="small"
                            onClick={() => confirmReplay(item)}
                            disabled={replayingId === item.id}
                            color="primary"
                          >
                            {replayingId === item.id ? (
                              <CircularProgress size={16} />
                            ) : (
                              <PlayIcon />
                            )}
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Pagination */}
        {totalCount > itemsPerPage && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Stack spacing={2}>
              <Pagination
                count={Math.ceil(totalCount / itemsPerPage)}
                page={currentPage}
                onChange={(event, page) => setCurrentPage(page)}
                color="primary"
                showFirstButton
                showLastButton
              />
              <Typography variant="caption" color="text.secondary" textAlign="center">
                Showing {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} replays
              </Typography>
            </Stack>
          </Box>
        )}

        {/* Details Dialog */}
        <Dialog
          open={detailsOpen}
          onClose={() => setDetailsOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Replay Details</DialogTitle>
          <DialogContent>
            {selectedReplay && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="h6" gutterBottom>
                  File Information
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography><strong>Filename:</strong> {selectedReplay.filename}</Typography>
                  <Typography><strong>File Size:</strong> {formatFileSize(selectedReplay.file_size)}</Typography>
                  <Typography><strong>File ID:</strong> {selectedReplay.file_id}</Typography>
                </Box>

                <Typography variant="h6" gutterBottom>
                  Replay Configuration
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography><strong>Interface:</strong> {selectedReplay.config.interface}</Typography>
                  <Typography><strong>Speed:</strong> {formatSpeed(selectedReplay.config.speed, selectedReplay.config.speed_unit)}</Typography>
                  <Typography><strong>Loop:</strong> {selectedReplay.config.loop ? 'Yes' : 'No'}</Typography>
                  <Typography><strong>Preload PCAP:</strong> {selectedReplay.config.preload_pcap ? 'Yes' : 'No'}</Typography>
                </Box>

                <Typography variant="h6" gutterBottom>
                  Execution Details
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography><strong>Status:</strong> 
                    <Chip
                      label={selectedReplay.status}
                      color={getStatusColor(selectedReplay.status)}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography><strong>Started:</strong> {formatTimestamp(selectedReplay.started_at)}</Typography>
                  {selectedReplay.completed_at && (
                    <Typography><strong>Completed:</strong> {formatTimestamp(selectedReplay.completed_at)}</Typography>
                  )}
                  {selectedReplay.duration && (
                    <Typography><strong>Duration:</strong> {formatDuration(selectedReplay.duration)}</Typography>
                  )}
                  {selectedReplay.packets_sent && (
                    <Typography><strong>Packets Sent:</strong> {selectedReplay.packets_sent.toLocaleString()}</Typography>
                  )}
                  {selectedReplay.error_message && (
                    <Typography color="error"><strong>Error:</strong> {selectedReplay.error_message}</Typography>
                  )}
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Confirm Replay Dialog */}
        <Dialog
          open={confirmReplayOpen}
          onClose={() => setConfirmReplayOpen(false)}
        >
          <DialogTitle>Confirm Replay</DialogTitle>
          <DialogContent>
            {selectedReplay && (
              <Box sx={{ mt: 1 }}>
                <Typography gutterBottom>
                  Are you sure you want to replay this PCAP file again?
                </Typography>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography><strong>File:</strong> {selectedReplay.filename}</Typography>
                  <Typography><strong>Interface:</strong> {selectedReplay.config.interface}</Typography>
                  <Typography><strong>Speed:</strong> {formatSpeed(selectedReplay.config.speed, selectedReplay.config.speed_unit)}</Typography>
                </Box>
                <Alert severity="info" sx={{ mt: 2 }}>
                  This will start a new replay with the same configuration as the previous run.
                </Alert>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setConfirmReplayOpen(false)}>Cancel</Button>
            <Button
              onClick={() => handleReplayAgain(selectedReplay)}
              variant="contained"
              disabled={replayingId !== null}
            >
              {replayingId ? 'Starting...' : 'Start Replay'}
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default ReplayHistory;
