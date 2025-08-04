import React, { useState, useEffect } from 'react';
import {
  Card, CardContent, Typography, Grid, TextField,
  Button, Accordion, AccordionSummary, AccordionDetails,
  Chip, Box, Alert, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper,
  IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, FormControl, InputLabel, Select,
  MenuItem, Tooltip, CircularProgress, Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Delete as DeleteIcon,
  Preview as PreviewIcon,
  PlayArrow as PlayIcon,
  Info as InfoIcon,
  Add as AddIcon
} from '@mui/icons-material';
import apiService from '../services/api';

const PacketManipulation = ({ uploadedFile, onManipulationComplete }) => {
  const [manipulationRules, setManipulationRules] = useState({
    ip_mapping: {},
    mac_mapping: {},
    port_mapping: {},
    vlan_operations: {}
  });
  
  const [analysis, setAnalysis] = useState(null);
  const [preview, setPreview] = useState(null);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState(null);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  
  // Form state for adding new mappings
  const [newIpMapping, setNewIpMapping] = useState({ source: '', target: '' });
  const [newMacMapping, setNewMacMapping] = useState({ source: '', target: '' });
  const [newPortMapping, setNewPortMapping] = useState({ source: '', target: '' });
  const [vlanOperation, setVlanOperation] = useState({ type: '', value: '' });

  useEffect(() => {
    if (uploadedFile) {
      loadAnalysis();
      loadTemplates();
    }
  }, [uploadedFile]);

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      const response = await apiService.analyzeForManipulation({
        file_id: uploadedFile.file_id,
        analysis_limit: 1000
      });
      setAnalysis(response.data.analysis);
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Failed to analyze PCAP file for manipulation opportunities');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await apiService.getManipulationTemplates();
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const addIpMapping = () => {
    if (newIpMapping.source && newIpMapping.target) {
      setManipulationRules(prev => ({
        ...prev,
        ip_mapping: {
          ...prev.ip_mapping,
          [newIpMapping.source]: newIpMapping.target
        }
      }));
      setNewIpMapping({ source: '', target: '' });
    }
  };

  const addMacMapping = () => {
    if (newMacMapping.source && newMacMapping.target) {
      setManipulationRules(prev => ({
        ...prev,
        mac_mapping: {
          ...prev.mac_mapping,
          [newMacMapping.source]: newMacMapping.target
        }
      }));
      setNewMacMapping({ source: '', target: '' });
    }
  };

  const addPortMapping = () => {
    if (newPortMapping.source && newPortMapping.target) {
      const sourcePort = parseInt(newPortMapping.source);
      const targetPort = parseInt(newPortMapping.target);
      if (sourcePort >= 1 && sourcePort <= 65535 && targetPort >= 1 && targetPort <= 65535) {
        setManipulationRules(prev => ({
          ...prev,
          port_mapping: {
            ...prev.port_mapping,
            [sourcePort]: targetPort
          }
        }));
        setNewPortMapping({ source: '', target: '' });
      }
    }
  };

  const addVlanOperation = () => {
    if (vlanOperation.type && vlanOperation.value) {
      setManipulationRules(prev => ({
        ...prev,
        vlan_operations: {
          [vlanOperation.type]: parseInt(vlanOperation.value)
        }
      }));
      setVlanOperation({ type: '', value: '' });
    }
  };

  const removeMapping = (category, key) => {
    setManipulationRules(prev => {
      const newMapping = { ...prev[category] };
      delete newMapping[key];
      return { ...prev, [category]: newMapping };
    });
  };

  const previewManipulation = async () => {
    try {
      setPreviewLoading(true);
      setError(null);
      const response = await apiService.previewManipulation({
        file_id: uploadedFile.file_id,
        manipulation_rules: manipulationRules,
        sample_size: 10
      });
      setPreview(response.data.preview);
    } catch (error) {
      console.error('Preview failed:', error);
      setError('Failed to preview packet manipulation');
    } finally {
      setPreviewLoading(false);
    }
  };

  const applyTemplate = (templateKey) => {
    const template = templates[templateKey];
    if (template && template.example_rules) {
      setManipulationRules(prev => ({
        ...prev,
        ...template.example_rules
      }));
      setTemplateDialogOpen(false);
    }
  };

  const hasRules = () => {
    return Object.values(manipulationRules).some(rules => 
      Object.keys(rules).length > 0
    );
  };

  const getRulesSummary = () => {
    const summary = [];
    if (Object.keys(manipulationRules.ip_mapping).length > 0) {
      summary.push(`${Object.keys(manipulationRules.ip_mapping).length} IP mappings`);
    }
    if (Object.keys(manipulationRules.mac_mapping).length > 0) {
      summary.push(`${Object.keys(manipulationRules.mac_mapping).length} MAC mappings`);
    }
    if (Object.keys(manipulationRules.port_mapping).length > 0) {
      summary.push(`${Object.keys(manipulationRules.port_mapping).length} port mappings`);
    }
    if (Object.keys(manipulationRules.vlan_operations).length > 0) {
      summary.push('VLAN operations');
    }
    return summary.join(', ');
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={3}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Analyzing PCAP file for manipulation opportunities...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6">
            Advanced Packet Manipulation
          </Typography>
          <Button
            variant="outlined"
            startIcon={<InfoIcon />}
            onClick={() => setTemplateDialogOpen(true)}
          >
            Templates
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {analysis && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Analysis Results:</strong> Found {analysis.unique_ips.length} unique IPs, {' '}
              {analysis.unique_macs.length} unique MACs, {analysis.unique_ports.length} unique ports, {' '}
              and {analysis.protocols.length} protocols in {analysis.packet_count} packets.
            </Typography>
          </Alert>
        )}

        {/* IP Address Mapping */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>
              IP Address Mapping ({Object.keys(manipulationRules.ip_mapping).length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={4}>
                <TextField
                  label="Original IP"
                  placeholder="192.168.1.100"
                  value={newIpMapping.source}
                  onChange={(e) => setNewIpMapping(prev => ({ ...prev, source: e.target.value }))}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="New IP"
                  placeholder="10.0.0.100"
                  value={newIpMapping.target}
                  onChange={(e) => setNewIpMapping(prev => ({ ...prev, target: e.target.value }))}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <Button
                  onClick={addIpMapping}
                  variant="contained"
                  startIcon={<AddIcon />}
                  disabled={!newIpMapping.source || !newIpMapping.target}
                  fullWidth
                >
                  Add
                </Button>
              </Grid>
            </Grid>
            
            {analysis && analysis.unique_ips.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Available IPs in file:
                </Typography>
                <Box sx={{ maxHeight: 100, overflow: 'auto' }}>
                  {analysis.unique_ips.slice(0, 10).map(ip => (
                    <Chip
                      key={ip}
                      label={ip}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                      onClick={() => setNewIpMapping(prev => ({ ...prev, source: ip }))}
                    />
                  ))}
                  {analysis.unique_ips.length > 10 && (
                    <Typography variant="caption" color="textSecondary">
                      ... and {analysis.unique_ips.length - 10} more
                    </Typography>
                  )}
                </Box>
              </Box>
            )}
            
            <Box sx={{ mt: 2 }}>
              {Object.entries(manipulationRules.ip_mapping).map(([src, dst]) => (
                <Chip
                  key={src}
                  label={`${src} → ${dst}`}
                  onDelete={() => removeMapping('ip_mapping', src)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* MAC Address Mapping */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>
              MAC Address Mapping ({Object.keys(manipulationRules.mac_mapping).length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={4}>
                <TextField
                  label="Original MAC"
                  placeholder="00:11:22:33:44:55"
                  value={newMacMapping.source}
                  onChange={(e) => setNewMacMapping(prev => ({ ...prev, source: e.target.value }))}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="New MAC"
                  placeholder="AA:BB:CC:DD:EE:FF"
                  value={newMacMapping.target}
                  onChange={(e) => setNewMacMapping(prev => ({ ...prev, target: e.target.value }))}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <Button
                  onClick={addMacMapping}
                  variant="contained"
                  startIcon={<AddIcon />}
                  disabled={!newMacMapping.source || !newMacMapping.target}
                  fullWidth
                >
                  Add
                </Button>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2 }}>
              {Object.entries(manipulationRules.mac_mapping).map(([src, dst]) => (
                <Chip
                  key={src}
                  label={`${src} → ${dst}`}
                  onDelete={() => removeMapping('mac_mapping', src)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Port Mapping */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>
              Port Mapping ({Object.keys(manipulationRules.port_mapping).length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={4}>
                <TextField
                  label="Original Port"
                  placeholder="8080"
                  type="number"
                  value={newPortMapping.source}
                  onChange={(e) => setNewPortMapping(prev => ({ ...prev, source: e.target.value }))}
                  fullWidth
                  size="small"
                  inputProps={{ min: 1, max: 65535 }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="New Port"
                  placeholder="80"
                  type="number"
                  value={newPortMapping.target}
                  onChange={(e) => setNewPortMapping(prev => ({ ...prev, target: e.target.value }))}
                  fullWidth
                  size="small"
                  inputProps={{ min: 1, max: 65535 }}
                />
              </Grid>
              <Grid item xs={4}>
                <Button
                  onClick={addPortMapping}
                  variant="contained"
                  startIcon={<AddIcon />}
                  disabled={!newPortMapping.source || !newPortMapping.target}
                  fullWidth
                >
                  Add
                </Button>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2 }}>
              {Object.entries(manipulationRules.port_mapping).map(([src, dst]) => (
                <Chip
                  key={src}
                  label={`${src} → ${dst}`}
                  onDelete={() => removeMapping('port_mapping', src)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* VLAN Operations */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>
              VLAN Operations ({Object.keys(manipulationRules.vlan_operations).length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Operation</InputLabel>
                  <Select
                    value={vlanOperation.type}
                    onChange={(e) => setVlanOperation(prev => ({ ...prev, type: e.target.value }))}
                    label="Operation"
                  >
                    <MenuItem value="add_vlan">Add VLAN Tag</MenuItem>
                    <MenuItem value="remove_vlan">Remove VLAN Tag</MenuItem>
                    <MenuItem value="modify_vlan">Modify VLAN ID</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="VLAN ID"
                  placeholder="100"
                  type="number"
                  value={vlanOperation.value}
                  onChange={(e) => setVlanOperation(prev => ({ ...prev, value: e.target.value }))}
                  fullWidth
                  size="small"
                  inputProps={{ min: 1, max: 4094 }}
                  disabled={vlanOperation.type === 'remove_vlan'}
                />
              </Grid>
              <Grid item xs={4}>
                <Button
                  onClick={addVlanOperation}
                  variant="contained"
                  startIcon={<AddIcon />}
                  disabled={!vlanOperation.type || (!vlanOperation.value && vlanOperation.type !== 'remove_vlan')}
                  fullWidth
                >
                  Add
                </Button>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2 }}>
              {Object.entries(manipulationRules.vlan_operations).map(([operation, value]) => (
                <Chip
                  key={operation}
                  label={`${operation.replace('_', ' ')}: ${value}`}
                  onDelete={() => removeMapping('vlan_operations', operation)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>

        <Divider sx={{ my: 3 }} />

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            startIcon={previewLoading ? <CircularProgress size={20} /> : <PreviewIcon />}
            onClick={previewManipulation}
            disabled={!hasRules() || previewLoading}
          >
            Preview Changes
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={() => onManipulationComplete(manipulationRules)}
            disabled={!hasRules()}
          >
            Apply & Continue to Replay
          </Button>
        </Box>

        {hasRules() && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Rules Summary:</strong> {getRulesSummary()}
            </Typography>
          </Alert>
        )}

        {/* Preview Results */}
        {preview && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Preview Results
            </Typography>
            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Packet #</TableCell>
                    <TableCell>Original</TableCell>
                    <TableCell>Modified</TableCell>
                    <TableCell>Changed</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {preview.samples.map((sample, index) => (
                    <TableRow key={index}>
                      <TableCell>{sample.packet_number}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {sample.original_summary}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {sample.modified_summary}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={sample.was_modified ? 'Yes' : 'No'}
                          color={sample.was_modified ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Templates Dialog */}
        <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Manipulation Templates</DialogTitle>
          <DialogContent>
            <Grid container spacing={2}>
              {Object.entries(templates).map(([key, template]) => (
                <Grid item xs={12} sm={6} key={key}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {template.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" paragraph>
                        {template.description}
                      </Typography>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => applyTemplate(key)}
                      >
                        Apply Template
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTemplateDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default PacketManipulation;
