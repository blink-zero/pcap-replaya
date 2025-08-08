import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormLabel,
  Alert,
  Chip,
  Grid,
  Checkbox,
} from '@mui/material';
import { apiService } from '../services/api';

const ReplayConfig = ({ config, setConfig, disabled = false }) => {
  const [interfaces, setInterfaces] = useState([]);
  const [loadingInterfaces, setLoadingInterfaces] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInterfaces();
  }, []);

  const loadInterfaces = async () => {
    try {
      setLoadingInterfaces(true);
      const response = await apiService.getInterfaces();
      setInterfaces(response.data.interfaces || []);
      setError(null);
    } catch (err) {
      setError('Failed to load network interfaces');
      console.error('Error loading interfaces:', err);
    } finally {
      setLoadingInterfaces(false);
    }
  };

  const handleSpeedChange = (event) => {
    const value = parseFloat(event.target.value);
    if (!isNaN(value) && value > 0) {
      setConfig(prev => ({ ...prev, speed: value }));
    }
  };

  const handleSpeedUnitChange = (event) => {
    setConfig(prev => ({ ...prev, speed_unit: event.target.value }));
  };

  const handleInterfaceChange = (event) => {
    setConfig(prev => ({ ...prev, interface: event.target.value }));
  };

  const handleContinuousReplayChange = (event) => {
    setConfig(prev => ({ ...prev, continuous: event.target.checked }));
  };

  const getSpeedLabel = () => {
    switch (config.speed_unit) {
      case 'pps':
        return 'Speed (PPS)';
      case 'multiplier':
      default:
        return 'Speed Multiplier';
    }
  };

  const getSpeedHelperText = () => {
    switch (config.speed_unit) {
      case 'pps':
        return 'Replay speed in packets per second';
      case 'multiplier':
      default:
        return 'Replay speed multiplier (1.0 = real-time, 2.0 = 2x speed)';
    }
  };

  const renderInterfaceInfo = (iface) => {
    const statusColor = iface.is_up ? 'success' : 'error';
    const statusText = iface.is_up ? 'UP' : 'DOWN';
    
    return (
      <Box key={iface.name} sx={{ mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            {iface.name}
          </Typography>
          <Chip
            label={statusText}
            size="small"
            color={statusColor}
            variant="outlined"
          />
        </Box>
        {iface.addresses && iface.addresses.length > 0 && (
          <Typography variant="caption" color="text.secondary">
            {iface.addresses.map(addr => addr.address).join(', ')}
          </Typography>
        )}
      </Box>
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Replay Configuration
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Network Interface</InputLabel>
              <Select
                value={config.interface || ''}
                onChange={handleInterfaceChange}
                disabled={disabled || loadingInterfaces}
                label="Network Interface"
              >
                {interfaces.map((iface) => (
                  <MenuItem
                    key={iface.name}
                    value={iface.name}
                    disabled={!iface.is_up}
                  >
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography>{iface.name}</Typography>
                        <Chip
                          label={iface.is_up ? 'UP' : 'DOWN'}
                          size="small"
                          color={iface.is_up ? 'success' : 'error'}
                          variant="outlined"
                        />
                      </Box>
                      {iface.addresses && iface.addresses.length > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          {iface.addresses[0]?.address}
                        </Typography>
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {loadingInterfaces && (
              <Typography variant="body2" color="text.secondary">
                Loading network interfaces...
              </Typography>
            )}
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl component="fieldset" margin="normal">
              <FormLabel component="legend">Speed Control</FormLabel>
              <RadioGroup
                value={config.speed_unit || 'multiplier'}
                onChange={handleSpeedUnitChange}
                row
              >
                <FormControlLabel
                  value="multiplier"
                  control={<Radio />}
                  label="Multiplier"
                  disabled={disabled}
                />
                <FormControlLabel
                  value="pps"
                  control={<Radio />}
                  label="PPS"
                  disabled={disabled}
                />
              </RadioGroup>
            </FormControl>

            <TextField
              fullWidth
              label={getSpeedLabel()}
              type="number"
              value={config.speed || ''}
              onChange={handleSpeedChange}
              disabled={disabled}
              helperText={getSpeedHelperText()}
              inputProps={{
                min: config.speed_unit === 'multiplier' ? 0.1 : 1,
                step: config.speed_unit === 'multiplier' ? 0.1 : 1,
              }}
              margin="normal"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl component="fieldset" margin="normal">
              <FormControlLabel
                control={
                  <Checkbox
                    checked={config.continuous || false}
                    onChange={handleContinuousReplayChange}
                    disabled={disabled}
                    color="primary"
                  />
                }
                label={
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        Continuous Replay
                      </Typography>
                      <Chip
                        label="BETA"
                        size="small"
                        color="warning"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem', height: '20px' }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Replay the PCAP file continuously until manually stopped
                    </Typography>
                  </Box>
                }
              />
            </FormControl>
          </Grid>
        </Grid>

        {interfaces.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Available Network Interfaces
            </Typography>
            <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
              {interfaces.map(renderInterfaceInfo)}
            </Box>
          </Box>
        )}

        {config.interface && config.speed && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Ready to replay on interface <strong>{config.interface}</strong> at{' '}
            <strong>
              {config.speed_unit === 'pps'
                ? `${config.speed} PPS`
                : `${config.speed}x speed`}
            </strong>
            {config.continuous && (
              <span>
                {' '}in <strong>continuous mode</strong> (will loop until stopped)
              </span>
            )}
          </Alert>
        )}

        {config.continuous && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            <strong>Continuous Mode:</strong> The PCAP will replay repeatedly until you manually stop it. 
            Make sure to monitor the replay and stop it when needed.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ReplayConfig;
