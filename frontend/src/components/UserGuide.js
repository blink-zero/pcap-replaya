import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Settings as ConfigIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const UserGuide = ({ currentStep = 0, uploadedFile, replayConfig }) => {
  const steps = [
    {
      label: 'Upload PCAP File',
      icon: <UploadIcon />,
      description: 'Select and upload your PCAP file for replay',
      details: [
        'Click "Choose File" or drag and drop your PCAP file',
        'Supported formats: .pcap, .pcapng, .cap',
        'Maximum file size: 1GB',
        'File will be analyzed automatically after upload'
      ],
      completed: !!uploadedFile
    },
    {
      label: 'Configure Replay Settings',
      icon: <ConfigIcon />,
      description: 'Set up network interface and speed parameters',
      details: [
        'Select a network interface from the dropdown',
        'Choose speed control method:',
        '  • Multiplier: Speed relative to original timing (e.g., 2x = twice as fast)',
        '  • PPS: Exact packets per second rate (e.g., 5000 PPS)',
        'Ensure the selected interface is UP and accessible'
      ],
      completed: !!(replayConfig.interface && replayConfig.speed)
    },
    {
      label: 'Start Replay',
      icon: <PlayIcon />,
      description: 'Begin packet replay with your configured settings',
      details: [
        'Click "Start Replay" to begin transmission',
        'Monitor status updates in real-time',
        'Use "Stop" button to halt replay if needed',
        'View completion status and statistics'
      ],
      completed: false // This will be determined by replay status
    }
  ];

  const getStepStatus = (stepIndex) => {
    if (steps[stepIndex].completed) {
      return 'completed';
    } else if (stepIndex === currentStep) {
      return 'active';
    } else {
      return 'pending';
    }
  };

  const getStepColor = (stepIndex) => {
    const status = getStepStatus(stepIndex);
    switch (status) {
      case 'completed':
        return 'success';
      case 'active':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <InfoIcon color="primary" />
          Quick Start Guide
        </Typography>

        <Alert severity="info" sx={{ mb: 3 }}>
          Follow these steps to replay your PCAP file. Each step must be completed before proceeding to the next.
        </Alert>

        <Stepper orientation="vertical" activeStep={currentStep}>
          {steps.map((step, index) => (
            <Step key={index} completed={step.completed}>
              <StepLabel
                StepIconComponent={() => (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      bgcolor: step.completed ? 'success.main' : 
                              index === currentStep ? 'primary.main' : 'grey.300',
                      color: step.completed || index === currentStep ? 'white' : 'grey.600'
                    }}
                  >
                    {step.completed ? <CheckIcon /> : step.icon}
                  </Box>
                )}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="h6">
                    Step {index + 1}: {step.label}
                  </Typography>
                  <Chip
                    label={step.completed ? 'Complete' : index === currentStep ? 'Current' : 'Pending'}
                    color={getStepColor(index)}
                    size="small"
                    variant={step.completed ? 'filled' : 'outlined'}
                  />
                </Box>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {step.description}
                </Typography>
                <List dense>
                  {step.details.map((detail, detailIndex) => (
                    <ListItem key={detailIndex} sx={{ py: 0.5, pl: detail.startsWith('  ') ? 4 : 2 }}>
                      <ListItemIcon sx={{ minWidth: 20 }}>
                        <Box
                          sx={{
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            bgcolor: 'primary.main'
                          }}
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary={detail.replace(/^  /, '')}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            💡 Pro Tips:
          </Typography>
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            <Typography component="li" variant="body2" color="text.secondary">
              Use <strong>Multiplier mode</strong> to speed up/slow down based on original timing
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Use <strong>PPS mode</strong> for precise packet rate control regardless of original timing
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Higher PPS values will replay faster but may be limited by network interface capabilities
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Large files (&gt;100k packets) will have limited analysis display but full replay capability
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Monitor the auto-refreshing status for real-time updates during replay
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default UserGuide;
