import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  AppBar,
  Toolbar,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Drawer,
  IconButton,
  Fab,
} from '@mui/material';
import {
  NetworkCheck as NetworkIcon,
  Help as HelpIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

import FileUpload from './components/FileUpload';
import ReplayConfig from './components/ReplayConfig';
import ProgressMonitor from './components/ProgressMonitor';
import LiveLog from './components/LiveLog';
import ReplayHistory from './components/ReplayHistory';
import UserGuide from './components/UserGuide';
import { apiService } from './services/api';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [replayConfig, setReplayConfig] = useState({
    interface: '',
    speed: 1.0,
    speed_unit: 'multiplier',
  });
  const [guideOpen, setGuideOpen] = useState(false);
  const [versionInfo, setVersionInfo] = useState(null);

  // Fetch version information on component mount
  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const response = await apiService.getVersion();
        setVersionInfo(response.data);
      } catch (error) {
        console.error('Failed to fetch version information:', error);
        // Set fallback version info
        setVersionInfo({
          version: '1.1.0',
          name: 'PCAP Replaya',
          description: 'Network Packet Replay Tool'
        });
      }
    };

    fetchVersion();
  }, []);

  const handleFileUploaded = (fileData) => {
    console.log('File uploaded:', fileData);
    setUploadedFile(fileData);
  };

  const handleReplayComplete = (replayData) => {
    console.log('Replay completed:', replayData);
    
    // Auto-reset the upload after replay completes
    if (replayData.status === 'completed' || replayData.status === 'failed' || replayData.status === 'stopped') {
      // Clear the uploaded file to allow new upload
      setUploadedFile(null);
      
      // Reset replay config to defaults
      setReplayConfig({
        interface: '',
        speed: 1.0,
        speed_unit: 'multiplier',
      });
    }
  };

  const handleReplayFromHistory = (replayData) => {
    console.log('Replay started from history:', replayData);
    // You could add notifications or other actions when replay starts from history
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <NetworkIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              PCAP Replaya
              {versionInfo && (
                <Typography component="span" variant="caption" sx={{ ml: 1, opacity: 0.7 }}>
                  v{versionInfo.version}
                </Typography>
              )}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Network Packet Replay Tool
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" gutterBottom align="center" sx={{ mb: 4 }}>
            PCAP Replay Dashboard
          </Typography>
          
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
            Upload PCAP files, configure replay settings, and monitor real-time progress
          </Typography>

          <Grid container spacing={4}>
            {/* File Upload Section */}
            <Grid item xs={12}>
              <FileUpload
                onFileUploaded={handleFileUploaded}
                uploadedFile={uploadedFile}
                setUploadedFile={setUploadedFile}
              />
            </Grid>

            {/* Replay Configuration Section */}
            <Grid item xs={12}>
              <ReplayConfig
                config={replayConfig}
                setConfig={setReplayConfig}
                disabled={!uploadedFile}
              />
            </Grid>

            {/* Progress Monitor Section */}
            <Grid item xs={12}>
              <ProgressMonitor
                uploadedFile={uploadedFile}
                replayConfig={replayConfig}
                onReplayComplete={handleReplayComplete}
              />
            </Grid>

            {/* Replay History Section */}
            <Grid item xs={12}>
              <ReplayHistory onReplayStart={handleReplayFromHistory} />
            </Grid>

            {/* Live Log Section */}
            <Grid item xs={12}>
              <LiveLog />
            </Grid>
          </Grid>

          {/* Footer */}
          <Box sx={{ mt: 6, pt: 3, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body2" color="text.secondary" align="center">
              {versionInfo ? `${versionInfo.name} v${versionInfo.version}` : 'PCAP Replaya'} - Built with React, Flask, and tcpreplay
            </Typography>
            <Typography variant="caption" color="text.secondary" align="center" display="block">
              Supports PCAP, PCAPNG, and CAP file formats up to 1GB
            </Typography>
            {versionInfo && (
              <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 0.5 }}>
                {versionInfo.description}
              </Typography>
            )}
          </Box>
        </Container>

        {/* Floating Action Button for Quick Start Guide */}
        <Fab
          color="primary"
          aria-label="help"
          onClick={() => setGuideOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
          }}
        >
          <HelpIcon />
        </Fab>

        {/* Sidebar Drawer for Quick Start Guide */}
        <Drawer
          anchor="right"
          open={guideOpen}
          onClose={() => setGuideOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: { xs: '100%', sm: 400, md: 500 },
              maxWidth: '90vw',
            },
          }}
        >
          <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Quick Start Guide</Typography>
              <IconButton onClick={() => setGuideOpen(false)} size="small">
                <CloseIcon />
              </IconButton>
            </Box>
            <Box sx={{ flex: 1, overflow: 'auto' }}>
              <UserGuide
                currentStep={!uploadedFile ? 0 : (!replayConfig.interface || !replayConfig.speed) ? 1 : 2}
                uploadedFile={uploadedFile}
                replayConfig={replayConfig}
              />
            </Box>
          </Box>
        </Drawer>
      </Box>
    </ThemeProvider>
  );
}

export default App;
