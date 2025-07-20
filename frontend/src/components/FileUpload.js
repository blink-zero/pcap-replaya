import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { apiService, formatFileSize } from '../services/api';

const FileUpload = ({ onFileUploaded, uploadedFile, setUploadedFile }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setError(null);
    setUploading(true);
    setAnalyzing(false);
    setUploadProgress(0);

    try {
      const response = await apiService.uploadFile(file, (progress) => {
        setUploadProgress(progress);
        // When upload reaches 100%, switch to analysis mode
        if (progress === 100) {
          setUploading(false);
          setAnalyzing(true);
        }
      });

      const uploadData = response.data;
      setUploadedFile(uploadData);
      onFileUploaded(uploadData);
      setUploading(false);
      setAnalyzing(false);
    } catch (err) {
      // Handle timeout errors specifically
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        setError('Upload timed out during analysis. Large files may take several minutes to process. Please try again or check the server logs.');
      } else {
        setError(err.response?.data?.error || err.message || 'Upload failed');
      }
      setUploading(false);
      setAnalyzing(false);
      setUploadProgress(0);
    }
  }, [onFileUploaded, setUploadedFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.tcpdump.pcap': ['.pcap'],
      'application/octet-stream': ['.pcapng', '.cap'],
    },
    maxFiles: 1,
    maxSize: 1024 * 1024 * 1024, // 1GB
  });

  const formatProtocols = (protocols) => {
    if (!protocols || protocols.length === 0) return 'None detected';
    return protocols.join(', ');
  };

  const handleReplaceFile = () => {
    setUploadedFile(null);
    setError(null);
    setUploadProgress(0);
    onFileUploaded(null);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Upload PCAP File
      </Typography>

      {!uploadedFile && (
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover',
            },
          }}
        >
          <input {...getInputProps()} />
          <UploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive
              ? 'Drop the PCAP file here'
              : 'Drag & drop a PCAP file here, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: .pcap, .pcapng, .cap (max 1GB)
          </Typography>
        </Paper>
      )}

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            Uploading... {uploadProgress}%
          </Typography>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      {analyzing && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            Analyzing PCAP file... This may take a few minutes for large files.
          </Typography>
          <LinearProgress variant="indeterminate" />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Large files (&gt;100k packets) will have limited analysis but full replay capability.
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }} icon={<ErrorIcon />}>
          {error}
          {error.includes('timeout') && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                <strong>Note:</strong> The file may have been uploaded successfully despite the timeout. 
                Check the server logs or try refreshing the page to see if your file appears in the replay history.
              </Typography>
            </Box>
          )}
        </Alert>
      )}

      {uploadedFile && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6">File Uploaded Successfully</Typography>
              </Box>
              <Tooltip title="Upload a different file">
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={handleReplaceFile}
                  color="primary"
                >
                  Replace File
                </Button>
              </Tooltip>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  File Information
                </Typography>
                <Typography variant="body2">
                  <strong>Name:</strong> {uploadedFile.filename}
                </Typography>
                <Typography variant="body2">
                  <strong>Size:</strong> {formatFileSize(uploadedFile.file_size)}
                </Typography>
                <Typography variant="body2">
                  <strong>Upload Time:</strong>{' '}
                  {new Date(uploadedFile.upload_time).toLocaleString()}
                </Typography>
              </Grid>

              {uploadedFile.pcap_info && (
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    PCAP Analysis
                  </Typography>
                  <Typography variant="body2">
                    <strong>Format:</strong> {uploadedFile.pcap_info.file_format || 'Unknown'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Packets:</strong> {uploadedFile.pcap_info.packet_count || 'Unknown'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Duration:</strong> {uploadedFile.pcap_info.duration ? `${uploadedFile.pcap_info.duration.toFixed(2)}s` : 'Unknown'}
                  </Typography>
                  {uploadedFile.pcap_info.protocols && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" gutterBottom>
                        <strong>Protocols:</strong>
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {uploadedFile.pcap_info.protocols.map((protocol) => (
                          <Chip
                            key={protocol}
                            label={protocol}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Grid>
              )}
            </Grid>

            {uploadedFile.pcap_info?.error && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Analysis Warning: {uploadedFile.pcap_info.error}
              </Alert>
            )}

            {uploadedFile.pcap_info?.analysis_limited && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  <strong>Large File Notice:</strong>
                </Typography>
                <Typography variant="body2">
                  {uploadedFile.pcap_info.analysis_limit_reason}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  The displayed packet count and analysis are limited for performance, but the entire file will be replayed when you start the replay process.
                </Typography>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default FileUpload;
