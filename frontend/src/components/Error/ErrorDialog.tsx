import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Alert,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import { Error as ErrorIcon, CheckCircle, Lightbulb } from '@mui/icons-material';
import { AppError } from '../../utils/errorHandling';

interface ErrorDialogProps {
  open: boolean;
  onClose: () => void;
  error: AppError | null;
  onRetry?: () => void;
}

const ErrorDialog: React.FC<ErrorDialogProps> = ({ 
  open, 
  onClose, 
  error, 
  onRetry 
}) => {
  if (!error) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <ErrorIcon color="error" />
          <Typography variant="h6" component="div">
            {error.title}
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message}
        </Alert>
        
        {error.suggestions && error.suggestions.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Lightbulb fontSize="small" color="primary" />
              Here's what you can try:
            </Typography>
            <List dense>
              {error.suggestions.map((suggestion, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 30 }}>
                    <CheckCircle fontSize="small" color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={suggestion} 
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} color="inherit">
          Close
        </Button>
        {onRetry && error.actionable && (
          <Button 
            onClick={onRetry} 
            variant="contained" 
            color="primary"
            sx={{ ml: 1 }}
          >
            Try Again
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;