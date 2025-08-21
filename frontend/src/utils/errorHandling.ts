export interface AppError {
  title: string;
  message: string;
  actionable?: boolean;
  suggestions?: string[];
}

export const parseApiError = (error: any): AppError => {
  // If it's already an AppError, return it
  if (error.title && error.message) {
    return error;
  }

  // Default error structure
  let appError: AppError = {
    title: 'Something went wrong',
    message: 'Please try again in a moment',
    actionable: false
  };

  // Handle different error types
  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    // Common API error patterns
    if (detail.includes('OpenAI API key')) {
      appError = {
        title: 'API Key Issue',
        message: 'Your OpenAI API key is invalid or has insufficient credits.',
        actionable: true,
        suggestions: [
          'Check your OpenAI API key in Settings',
          'Ensure your OpenAI account has sufficient credits',
          'Verify the API key has the correct permissions'
        ]
      };
    } else if (detail.includes('Shopify')) {
      appError = {
        title: 'Shopify Connection Error',
        message: 'Unable to connect to your Shopify store.',
        actionable: true,
        suggestions: [
          'Check your Shopify store URL and access token',
          'Ensure the access token has blog management permissions',
          'Verify your store is accessible'
        ]
      };
    } else if (detail.includes('rate limit') || detail.includes('too many requests')) {
      appError = {
        title: 'Rate Limit Exceeded',
        message: 'Too many requests. Please wait a moment before trying again.',
        actionable: true,
        suggestions: [
          'Wait a few minutes before retrying',
          'Consider generating fewer blogs at once',
          'Check your API usage limits'
        ]
      };
    } else if (detail.includes('authentication') || detail.includes('unauthorized')) {
      appError = {
        title: 'Authentication Error',
        message: 'Please log in again to continue.',
        actionable: true,
        suggestions: [
          'Sign out and sign back in',
          'Clear your browser cache',
          'Contact support if the issue persists'
        ]
      };
    } else if (detail.includes('network') || detail.includes('connection')) {
      appError = {
        title: 'Connection Error',
        message: 'Unable to connect to our servers.',
        actionable: true,
        suggestions: [
          'Check your internet connection',
          'Try refreshing the page',
          'Contact support if the issue persists'
        ]
      };
    } else {
      appError.message = detail;
      appError.actionable = true;
    }
  } else if (error?.message) {
    // Handle JavaScript errors
    if (error.message.includes('fetch')) {
      appError = {
        title: 'Connection Error',
        message: 'Unable to reach the server. Please check your connection.',
        actionable: true,
        suggestions: [
          'Check your internet connection',
          'Try refreshing the page',
          'Contact support if the issue persists'
        ]
      };
    } else {
      appError.message = error.message;
      appError.actionable = true;
    }
  } else if (typeof error === 'string') {
    appError.message = error;
    appError.actionable = true;
  }

  return appError;
};

export const getErrorMessage = (error: any): string => {
  const appError = parseApiError(error);
  return appError.message;
};

export const getErrorTitle = (error: any): string => {
  const appError = parseApiError(error);
  return appError.title;
};