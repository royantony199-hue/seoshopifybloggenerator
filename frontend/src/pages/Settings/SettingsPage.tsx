import React, { useState, useEffect } from 'react';
import { settingsApi, storesApi } from '../../services/api';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Box,
  Alert,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Link,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Save,
  Visibility,
  VisibilityOff,
  OpenInNew,
  Store,
  Key,
  Article,
  Analytics,
  Delete,
  Add,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const SettingsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showSerperKey, setShowSerperKey] = useState(false);
  const [showUnsplashKey, setShowUnsplashKey] = useState(false);
  const [showGoogleCredentials, setShowGoogleCredentials] = useState(false);
  const [showShopifyKey, setShowShopifyKey] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('');
  const [loading, setLoading] = useState(true);

  // API Keys State
  const [openAIKey, setOpenAIKey] = useState('');
  const [serperAPIKey, setSerperAPIKey] = useState('');
  const [unsplashAPIKey, setUnsplashAPIKey] = useState('');
  const [googleSheetsCredentials, setGoogleSheetsCredentials] = useState('');
  const [googleSheetsID, setGoogleSheetsID] = useState('');

  // Load API keys on component mount
  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const apiKeys = await settingsApi.getApiKeys();
      
      // Set the field values, including masked ones (so user knows they exist)
      if (apiKeys.openai_api_key) {
        setOpenAIKey(apiKeys.openai_api_key);
      }
      if (apiKeys.serper_api_key) {
        setSerperAPIKey(apiKeys.serper_api_key);
      }
      if (apiKeys.unsplash_api_key) {
        setUnsplashAPIKey(apiKeys.unsplash_api_key);
      }
      if (apiKeys.google_sheets_credentials) {
        setGoogleSheetsCredentials(apiKeys.google_sheets_credentials);
      }
      if (apiKeys.google_sheets_id) {
        setGoogleSheetsID(apiKeys.google_sheets_id);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadShopifyStores = async () => {
    try {
      const stores = await storesApi.getStores();
      setShopifyStores(stores.length > 0 ? stores : [
        {
          id: Date.now(), // Use timestamp as temp ID for new stores
          store_name: '',
          shop_url: '',
          access_token: '',
          blog_handle: 'news',
          is_active: true,
        }
      ]);
    } catch (error) {
      console.error('Failed to load stores:', error);
      // Initialize with empty store if loading fails
      setShopifyStores([
        {
          id: Date.now(),
          store_name: '',
          shop_url: '',
          access_token: '',
          blog_handle: 'news',
          is_active: true,
        }
      ]);
    }
  };

  const [shopifyStores, setShopifyStores] = useState([]);

  useEffect(() => {
    loadApiKeys();
    loadShopifyStores();
  }, []);

  // Published Links State
  const [publishedLinks] = useState([
    {
      id: 1,
      title: 'CBD Gummies for Pain: Complete Evidence-Based Guide 2025',
      keyword: 'CBD gummies for pain',
      live_url: 'https://demo-store.myshopify.com/blogs/news/cbd-gummies-pain-relief-guide',
      published_at: '2024-01-15T10:30:00Z',
      status: 'published',
      word_count: 2500,
      views: 1250,
    },
    {
      id: 2,
      title: 'CBD for Sleep: Complete Guide for Natural Wellness',
      keyword: 'CBD for sleep',
      live_url: 'https://demo-store.myshopify.com/blogs/news/cbd-sleep-natural-guide',
      published_at: '2024-01-14T15:45:00Z',
      status: 'published',
      word_count: 2300,
      views: 980,
    },
    {
      id: 3,
      title: 'CBD Cream: Complete Skincare Guide',
      keyword: 'CBD cream',
      live_url: 'https://demo-store.myshopify.com/blogs/news/cbd-cream-skincare-guide',
      published_at: '2024-01-13T09:15:00Z',
      status: 'published',
      word_count: 2100,
      views: 750,
    },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSaveAPIKeys = async () => {
    setSaveStatus('saving');
    setSaveMessage('Saving API keys...');

    try {
      await settingsApi.saveApiKeys({
        openai_api_key: openAIKey || undefined,
        serper_api_key: serperAPIKey || undefined,
        unsplash_api_key: unsplashAPIKey || undefined,
        google_sheets_credentials: googleSheetsCredentials || undefined,
        google_sheets_id: googleSheetsID || undefined,
      });
      
      setSaveStatus('success');
      setSaveMessage('API keys saved successfully!');
      
      setTimeout(() => {
        setSaveStatus('idle');
        setSaveMessage('');
      }, 3000);
    } catch (error: any) {
      setSaveStatus('error');
      setSaveMessage(`Failed to save API keys: ${error.message}`);
      
      setTimeout(() => {
        setSaveStatus('idle');
        setSaveMessage('');
      }, 5000);
    }
  };

  const handleAddStore = () => {
    const newStore = {
      id: Date.now(), // Use timestamp as temp ID
      store_name: '',
      shop_url: '',
      access_token: '',
      blog_handle: 'news',
      is_active: true,
    };
    setShopifyStores([...shopifyStores, newStore]);
  };

  const handleUpdateStore = (index: number, field: string, value: string) => {
    const updatedStores = [...shopifyStores];
    updatedStores[index] = { ...updatedStores[index], [field]: value };
    setShopifyStores(updatedStores);
  };

  const handleDeleteStore = async (index: number) => {
    const store = shopifyStores[index];
    try {
      // If store has an ID > 0, it exists in the backend
      if (store.id > 0) {
        await storesApi.deleteStore(store.id);
      }
      const updatedStores = shopifyStores.filter((_, i) => i !== index);
      setShopifyStores(updatedStores);
    } catch (error) {
      console.error('Failed to delete store:', error);
      alert('Failed to delete store');
    }
  };

  const handleSaveStore = async (index: number) => {
    const store = shopifyStores[index];
    
    // Validate required fields
    if (!store.store_name || !store.shop_url || !store.access_token) {
      alert('Please fill in all required fields (Store Name, Shop URL, Access Token)');
      return;
    }
    
    try {
      if (store.id > 1000000) {
        // New store (has temporary timestamp ID) - create it
        const newStore = await storesApi.createStore({
          store_name: store.store_name,
          shop_url: store.shop_url,
          access_token: store.access_token,
          blog_handle: store.blog_handle || 'news',
          auto_publish: false,
        });
        
        // Update the local state with the new ID
        const updatedStores = [...shopifyStores];
        updatedStores[index] = { ...newStore };
        setShopifyStores(updatedStores);
        
        alert('Store saved successfully!');
      } else {
        // Existing store - update it
        const updatedStore = await storesApi.updateStore(store.id, {
          store_name: store.store_name,
          shop_url: store.shop_url,
          access_token: store.access_token,
          blog_handle: store.blog_handle || 'news',
        });
        
        const updatedStores = [...shopifyStores];
        updatedStores[index] = { ...updatedStore };
        setShopifyStores(updatedStores);
        
        alert('Store updated successfully!');
      }
    } catch (error) {
      console.error('Failed to save store:', error);
      alert('Failed to save store');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Settings & Configuration
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Typography>Loading settings...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Settings & Configuration
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<Key />} label="API Keys" />
          <Tab icon={<Store />} label="Shopify Stores" />
          <Tab icon={<Article />} label="Published Blogs" />
          <Tab icon={<Analytics />} label="Analytics" />
        </Tabs>
      </Box>

      {/* API Keys Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* OpenAI API Key */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Key sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    OpenAI API Key
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Required for generating high-quality blog content. Get your API key from{' '}
                  <Link href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">
                    OpenAI Platform
                  </Link>
                </Typography>
                
                <TextField
                  fullWidth
                  label="OpenAI API Key"
                  type={showOpenAIKey ? 'text' : 'password'}
                  value={openAIKey}
                  onChange={(e) => setOpenAIKey(e.target.value)}
                  placeholder="sk-proj-..."
                  InputProps={{
                    endAdornment: (
                      <IconButton
                        onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                        edge="end"
                      >
                        {showOpenAIKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <strong>Cost Estimate:</strong> Blog generation costs approximately $0.05-$0.15 per 2000-word blog
                </Alert>
              </CardContent>
            </Card>
          </Grid>

          {/* Serper API Key */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Key sx={{ mr: 1, color: 'secondary.main' }} />
                  <Typography variant="h6">
                    Serper API Key
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Required for Google search results and SEO research. Get your API key from{' '}
                  <Link href="https://serper.dev" target="_blank" rel="noopener">
                    Serper.dev
                  </Link>
                </Typography>
                
                <TextField
                  fullWidth
                  label="Serper API Key"
                  type={showSerperKey ? 'text' : 'password'}
                  value={serperAPIKey}
                  onChange={(e) => setSerperAPIKey(e.target.value)}
                  placeholder="abc123..."
                  InputProps={{
                    endAdornment: (
                      <IconButton
                        onClick={() => setShowSerperKey(!showSerperKey)}
                        edge="end"
                      >
                        {showSerperKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    ),
                  }}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Unsplash API Key */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Key sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">
                    Unsplash API Key
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Required for high-quality blog images. Get your API key from{' '}
                  <Link href="https://unsplash.com/developers" target="_blank" rel="noopener">
                    Unsplash Developers
                  </Link>
                </Typography>
                
                <TextField
                  fullWidth
                  label="Unsplash Access Key"
                  type={showUnsplashKey ? 'text' : 'password'}
                  value={unsplashAPIKey}
                  onChange={(e) => setUnsplashAPIKey(e.target.value)}
                  placeholder="xyz789..."
                  InputProps={{
                    endAdornment: (
                      <IconButton
                        onClick={() => setShowUnsplashKey(!showUnsplashKey)}
                        edge="end"
                      >
                        {showUnsplashKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    ),
                  }}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Google Sheets Integration */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Key sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="h6">
                    Google Sheets Integration
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Required for tracking published blogs and analytics. Get credentials from{' '}
                  <Link href="https://console.cloud.google.com" target="_blank" rel="noopener">
                    Google Cloud Console
                  </Link>
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Google Sheets ID"
                      value={googleSheetsID}
                      onChange={(e) => setGoogleSheetsID(e.target.value)}
                      placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                      sx={{ mb: 2 }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Service Account JSON"
                      type={showGoogleCredentials ? 'text' : 'password'}
                      value={googleSheetsCredentials}
                      onChange={(e) => setGoogleSheetsCredentials(e.target.value)}
                      placeholder="Paste your service account JSON here..."
                      multiline
                      rows={3}
                      InputProps={{
                        endAdornment: (
                          <IconButton
                            onClick={() => setShowGoogleCredentials(!showGoogleCredentials)}
                            edge="end"
                          >
                            {showGoogleCredentials ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>

                <Alert severity="warning" sx={{ mt: 2 }}>
                  <strong>Setup Instructions:</strong><br />
                  1. Create a project in Google Cloud Console<br />
                  2. Enable Google Sheets API<br />
                  3. Create a Service Account with Editor permissions<br />
                  4. Download the JSON key file and paste its contents above
                </Alert>
              </CardContent>
            </Card>
          </Grid>

          {/* Save Button */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSaveAPIKeys}
                disabled={saveStatus === 'saving' || !openAIKey}
                size="large"
              >
                {saveStatus === 'saving' ? 'Saving...' : 'Save API Keys'}
              </Button>
            </Box>

            {saveMessage && (
              <Alert
                severity={saveStatus === 'success' ? 'success' : saveStatus === 'error' ? 'error' : 'info'}
                sx={{ mt: 2 }}
              >
                {saveMessage}
              </Alert>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Shopify Stores Tab */}
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              Connected Shopify Stores
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddStore}
            >
              Add Store
            </Button>
          </Box>

          {shopifyStores.map((store, index) => (
            <Card key={store.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Store #{store.id}
                  </Typography>
                  <IconButton
                    color="error"
                    onClick={() => handleDeleteStore(index)}
                    disabled={shopifyStores.length === 1}
                  >
                    <Delete />
                  </IconButton>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Store Name"
                      value={store.store_name}
                      onChange={(e) => handleUpdateStore(index, 'store_name', e.target.value)}
                      placeholder="My Awesome Store"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Shop URL"
                      value={store.shop_url}
                      onChange={(e) => handleUpdateStore(index, 'shop_url', e.target.value)}
                      placeholder="my-store"
                      InputProps={{
                        endAdornment: <Typography color="textSecondary">.myshopify.com</Typography>
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Access Token"
                      type={showShopifyKey ? 'text' : 'password'}
                      value={store.access_token}
                      onChange={(e) => handleUpdateStore(index, 'access_token', e.target.value)}
                      placeholder="shpat_..."
                      InputProps={{
                        endAdornment: (
                          <IconButton
                            onClick={() => setShowShopifyKey(!showShopifyKey)}
                            edge="end"
                          >
                            {showShopifyKey ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        ),
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Blog Handle"
                      value={store.blog_handle}
                      onChange={(e) => handleUpdateStore(index, 'blog_handle', e.target.value)}
                      placeholder="news"
                    />
                  </Grid>
                </Grid>

                {/* Save Button */}
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => handleSaveStore(index)}
                    disabled={!store.store_name || !store.shop_url || !store.access_token}
                  >
                    Save Store
                  </Button>
                </Box>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <strong>How to get Shopify API credentials:</strong><br />
                  1. Go to your Shopify Admin → Apps → Private apps<br />
                  2. Create a private app with Blog posts write permissions<br />
                  3. Copy the Admin API access token
                </Alert>
              </CardContent>
            </Card>
          ))}
        </Box>
      </TabPanel>

      {/* Published Blogs Tab */}
      <TabPanel value={tabValue} index={2}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Published Blog Links
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            Track all your published blogs and their performance
          </Typography>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Keyword</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Words</TableCell>
                  <TableCell align="right">Views</TableCell>
                  <TableCell>Published</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {publishedLinks.map((blog) => (
                  <TableRow key={blog.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {blog.title.length > 50 ? `${blog.title.substring(0, 50)}...` : blog.title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={blog.keyword} 
                        size="small" 
                        variant="outlined"
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={blog.status}
                        color="success"
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {blog.word_count.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      {blog.views.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(blog.published_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => window.open(blog.live_url, '_blank')}
                        color="primary"
                      >
                        <OpenInNew />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              Quick Copy Links
            </Typography>
            {publishedLinks.map((blog) => (
              <Box key={blog.id} sx={{ mb: 1 }}>
                <Typography variant="body2" color="primary" component="div">
                  <strong>{blog.keyword}:</strong>{' '}
                  <Link href={blog.live_url} target="_blank" rel="noopener">
                    {blog.live_url}
                  </Link>
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </TabPanel>

      {/* Analytics Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Blog Performance
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Total Blogs Published:</Typography>
                    <Typography variant="body2" fontWeight="bold">3</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Total Views:</Typography>
                    <Typography variant="body2" fontWeight="bold">2,980</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Average Words:</Typography>
                    <Typography variant="body2" fontWeight="bold">2,300</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Success Rate:</Typography>
                    <Typography variant="body2" fontWeight="bold" color="success.main">100%</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Usage Summary
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Monthly Blogs Used:</Typography>
                    <Typography variant="body2" fontWeight="bold">3 / 500</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Keywords Uploaded:</Typography>
                    <Typography variant="body2" fontWeight="bold">20</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">API Calls This Month:</Typography>
                    <Typography variant="body2" fontWeight="bold">3</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Estimated Cost:</Typography>
                    <Typography variant="body2" fontWeight="bold">$0.45</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Container>
  );
};

export default SettingsPage;