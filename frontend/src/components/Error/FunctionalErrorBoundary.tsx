import React, { ReactNode } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { Alert, AlertTitle, Box, Button, Typography, Paper } from '@mui/material';
import { Refresh, BugReport, Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

function ErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/dashboard');
    resetErrorBoundary();
  };

  const handleReload = () => {
    window.location.reload();
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        p: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 600,
          width: '100%',
          textAlign: 'center',
        }}
      >
        <BugReport 
          sx={{ 
            fontSize: 64, 
            color: 'error.main', 
            mb: 2 
          }} 
        />
        
        <Typography variant="h4" gutterBottom color="error">
          Oops! Something went wrong
        </Typography>
        
        <Typography variant="body1" color="textSecondary" paragraph>
          We're sorry, but something unexpected happened. Please try one of the options below or contact support if the problem persists.
        </Typography>

        {process.env.NODE_ENV === 'development' && (
          <Alert severity="error" sx={{ mt: 2, mb: 2, textAlign: 'left' }}>
            <AlertTitle>Error Details (Development Mode)</AlertTitle>
            <Typography variant="body2" component="div">
              <strong>Error:</strong> {error.message}
            </Typography>
            {error.stack && (
              <Box
                component="pre"
                sx={{
                  mt: 1,
                  fontSize: '0.75rem',
                  overflow: 'auto',
                  maxHeight: 200,
                  bgcolor: 'grey.100',
                  p: 1,
                  borderRadius: 1,
                }}
              >
                {error.stack}
              </Box>
            )}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={resetErrorBoundary}
            color="primary"
          >
            Try Again
          </Button>
          <Button
            variant="outlined"
            startIcon={<Home />}
            onClick={handleGoHome}
            color="secondary"
          >
            Go to Dashboard
          </Button>
          <Button
            variant="outlined"
            onClick={handleReload}
            color="secondary"
          >
            Reload Page
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

interface FunctionalErrorBoundaryProps {
  children: ReactNode;
  onError?: (error: Error, errorInfo: { componentStack: string }) => void;
}

function FunctionalErrorBoundary({ children, onError }: FunctionalErrorBoundaryProps) {
  const handleError = (error: Error, errorInfo: { componentStack: string }) => {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Call custom error handler if provided
    if (onError) {
      onError(error, errorInfo);
    }

    // In production, send error to monitoring service
    if (process.env.NODE_ENV === 'production') {
      logErrorToService(error, errorInfo);
    }
  };

  const logErrorToService = (error: Error, errorInfo: { componentStack: string }) => {
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };
    
    console.error('Error report:', errorReport);
    
    // In production, you would send this to your error tracking service:
    // fetch('/api/errors', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(errorReport),
    // }).catch(console.error);
  };

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={handleError}
      onReset={() => {
        // Reset any global state if needed
        // This function is called when resetErrorBoundary is called
      }}
    >
      {children}
    </ErrorBoundary>
  );
}

export default FunctionalErrorBoundary;