import React from 'react';
import { Container, Typography, Card, CardContent } from '@mui/material';

const OnboardingPage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            Welcome to SEO Blog Automation!
          </Typography>
          <Typography variant="body1">
            Complete your setup to start generating high-quality blogs automatically.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default OnboardingPage;