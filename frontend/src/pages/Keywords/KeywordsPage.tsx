import React, { useState, useCallback, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab
} from '@mui/material';
import { 
  CloudUpload, 
  Download, 
  Search, 
  Article, 
  PlayArrow,
  Refresh,
  SelectAll,
  CheckBox,
  CheckBoxOutlineBlank,
  Replay,
  Delete
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';
import { keywordsApi, blogsApi, storesApi } from '../../services/api';

interface Keyword {
  id?: number;
  keyword: string;
  search_volume?: number;
  category?: string;
  keyword_difficulty?: number;
  status?: string;
  blog_generated?: boolean;
  created_at?: string;
}

interface Store {
  id: number;
  store_name: string;
  shop_url: string;
  is_active: boolean;
}

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
      id={`keywords-tabpanel-${index}`}
      aria-labelledby={`keywords-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const KeywordsPage: React.FC = () => {
  // Upload Tab State
  const [uploadedKeywords, setUploadedKeywords] = useState<Keyword[]>([]);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState('');
  const [campaignName, setCampaignName] = useState('');
  const [templateType, setTemplateType] = useState('ecommerce_general');

  // Keywords Tab State
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<number[]>([]);
  const [keywordStats, setKeywordStats] = useState<any>({});
  const [loadingKeywords, setLoadingKeywords] = useState(false);

  // Blog Generation State
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<number>(0);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [autoPublish, setAutoPublish] = useState(false);

  // Tab State
  const [tabValue, setTabValue] = useState(0);

  // Load data on component mount
  useEffect(() => {
    loadKeywords();
    loadStores();
    loadKeywordStats();
  }, []);

  const loadKeywords = async () => {
    setLoadingKeywords(true);
    try {
      const data = await keywordsApi.getKeywords();
      
      // Sort keywords: ungenerated first, then by status priority
      const sortedKeywords = data.sort((a: Keyword, b: Keyword) => {
        // First priority: ungenerated keywords (pending status, no blog generated)
        const aIsUngenerated = a.status === 'pending' && !a.blog_generated;
        const bIsUngenerated = b.status === 'pending' && !b.blog_generated;
        
        if (aIsUngenerated && !bIsUngenerated) return -1;
        if (!aIsUngenerated && bIsUngenerated) return 1;
        
        // Second priority: status priority order
        const statusPriority = {
          'processing': 1,
          'failed': 2,
          'completed': 3,
          'pending': 4
        };
        
        const aPriority = statusPriority[a.status as keyof typeof statusPriority] || 99;
        const bPriority = statusPriority[b.status as keyof typeof statusPriority] || 99;
        
        if (aIsUngenerated && bIsUngenerated) {
          // Both are ungenerated, sort by creation date (newest first)
          return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
        }
        
        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }
        
        // Final sort: by creation date (newest first)
        return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
      });
      
      setKeywords(sortedKeywords);
    } catch (error) {
      console.error('Failed to load keywords:', error);
    } finally {
      setLoadingKeywords(false);
    }
  };

  const loadStores = async () => {
    try {
      const data = await storesApi.getStores();
      setStores(data);
      if (data.length > 0) {
        setSelectedStore(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load stores:', error);
    }
  };

  const loadKeywordStats = async () => {
    try {
      const stats = await keywordsApi.getStats();
      setKeywordStats(stats);
    } catch (error) {
      console.error('Failed to load keyword stats:', error);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Upload functionality
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadStatus('uploading');
    setUploadMessage('Processing your file...');

    Papa.parse(file, {
      header: true,
      complete: (results) => {
        const parsedKeywords: Keyword[] = results.data
          .filter((row: any) => row.keyword || row.keywords || row.search_term)
          .map((row: any) => ({
            keyword: row.keyword || row.keywords || row.search_term || '',
            search_volume: parseInt(row.search_volume || row.volume || '0') || undefined,
            category: row.category || row.topic || 'General',
            keyword_difficulty: parseFloat(row.keyword_difficulty || row.difficulty || row.kd || '0') || undefined
          }));

        setUploadedKeywords(parsedKeywords);
        setUploadStatus('success');
        setUploadMessage(`Successfully parsed ${parsedKeywords.length} keywords from your file!`);
      },
      error: (error) => {
        setUploadStatus('error');
        setUploadMessage(`Error parsing file: ${error.message}`);
      }
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1
  });

  const handleUploadToBackend = async () => {
    if (uploadedKeywords.length === 0) {
      setUploadMessage('No keywords to upload');
      return;
    }

    setUploadStatus('uploading');
    setUploadMessage('Uploading keywords to server...');

    try {
      const csvContent = Papa.unparse(uploadedKeywords);
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const file = new File([blob], 'keywords.csv', { type: 'text/csv' });

      const result = await keywordsApi.uploadKeywords(
        file,
        undefined, // campaign_id
        campaignName || 'Uploaded Keywords',
        templateType
      );

      setUploadStatus('success');
      setUploadMessage(`Successfully uploaded ${result.keywords_added} keywords!`);
      setUploadedKeywords([]);
      setCampaignName('');
      // Refresh keywords list
      loadKeywords();
      loadKeywordStats();
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage('Failed to upload keywords to server');
    }
  };

  // Keyword selection
  const handleSelectKeyword = (keywordId: number) => {
    setSelectedKeywords(prev => 
      prev.includes(keywordId) 
        ? prev.filter(id => id !== keywordId)
        : [...prev, keywordId]
    );
  };

  const handleSelectAll = () => {
    const eligibleKeywords = keywords.filter(k => k.status === 'pending' && !k.blog_generated);
    if (selectedKeywords.length === eligibleKeywords.length) {
      setSelectedKeywords([]);
    } else {
      setSelectedKeywords(eligibleKeywords.map(k => k.id!));
    }
  };

  // Blog generation
  const handleGenerateBlogs = async () => {
    if (selectedKeywords.length === 0) return;

    setGenerating(true);
    try {
      const result = await blogsApi.generateBlogs({
        keyword_ids: selectedKeywords,
        store_id: selectedStore,
        template_type: templateType,
        auto_publish: autoPublish
      });

      setGenerateDialogOpen(false);
      setSelectedKeywords([]);
      loadKeywords();
      loadKeywordStats();

      alert(`Successfully queued ${result.blogs_queued} blogs for generation! Estimated completion: ${result.estimated_completion}`);
    } catch (error: any) {
      alert(`Failed to generate blogs: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const eligibleKeywords = keywords.filter(k => k.status === 'pending' && !k.blog_generated);
  const failedKeywords = keywords.filter(k => k.status === 'failed');
  const selectedEligibleCount = selectedKeywords.filter(id => 
    eligibleKeywords.some(k => k.id === id)
  ).length;

  // Retry failed keywords
  const handleRetryFailedKeywords = async () => {
    if (failedKeywords.length === 0) return;
    
    try {
      setGenerating(true);
      
      const failedIds = failedKeywords.map(k => k.id!);
      
      // First, reset failed keywords to pending status via backend
      const resetPromises = failedIds.map(async (keywordId) => {
        try {
          await keywordsApi.resetKeyword(keywordId);
          return true;
        } catch (error) {
          console.error(`Failed to reset keyword ${keywordId}:`, error);
          return false;
        }
      });
      
      const resetResults = await Promise.all(resetPromises);
      const successfulResets = resetResults.filter(Boolean).length;
      
      if (successfulResets === 0) {
        throw new Error('Failed to reset any keywords to pending status');
      }
      
      // Wait a moment for the database to update
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Refresh keywords to get updated status
      await loadKeywords();
      
      // Now try to generate blogs for the reset keywords
      const result = await blogsApi.generateBlogs({
        keyword_ids: failedIds,
        store_id: selectedStore || stores[0]?.id || 1,
        template_type: templateType,
        auto_publish: autoPublish
      });
      
      alert(`✅ Retry initiated for ${successfulResets} keywords!\n${result.message}`);
      
      // Refresh data
      loadKeywords();
      loadKeywordStats();
      
    } catch (error: any) {
      console.error('Failed to retry keywords:', error);
      alert(`❌ Failed to retry keywords: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Retry individual failed keyword
  const handleRetryIndividualKeyword = async (keywordId: number, keywordText: string) => {
    try {
      setGenerating(true);
      
      // First, reset the keyword to pending status
      const resetResult = await keywordsApi.resetKeyword(keywordId);
      console.log('Reset successful:', resetResult);
      
      // Wait a moment for database update
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Now generate blog for this keyword
      const result = await blogsApi.generateBlogs({
        keyword_ids: [keywordId],
        store_id: selectedStore || stores[0]?.id || 1,
        template_type: templateType,
        auto_publish: autoPublish
      });
      
      alert(`✅ Retry initiated for "${keywordText}"!\n${result.message}`);
      
      // Refresh data
      loadKeywords();
      loadKeywordStats();
      
    } catch (error: any) {
      console.error('Failed to retry keyword:', error);
      alert(`❌ Failed to retry "${keywordText}": ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Delete individual keyword
  const handleDeleteKeyword = async (keywordId: number, keywordText: string) => {
    if (!window.confirm(`Are you sure you want to delete the keyword "${keywordText}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/keywords/${keywordId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        alert(`✅ Keyword "${keywordText}" deleted successfully`);
        // Refresh data
        loadKeywords();
        loadKeywordStats();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete keyword');
      }
      
    } catch (error: any) {
      console.error('Failed to delete keyword:', error);
      alert(`❌ Failed to delete keyword: ${error.message}`);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Keywords Management
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<Search />} label="Manage Keywords" />
          <Tab icon={<CloudUpload />} label="Upload Keywords" />
        </Tabs>
      </Box>

      {/* Keywords Management Tab */}
      <TabPanel value={tabValue} index={0}>
        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Keywords
                </Typography>
                <Typography variant="h4">
                  {keywordStats.total_keywords || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pending
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {keywordStats.pending || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Blogs Generated
                </Typography>
                <Typography variant="h4" color="success.main">
                  {keywordStats.blogs_generated || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Completion Rate
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {keywordStats.completion_rate || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Keywords Actions */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadKeywords}
                  disabled={loadingKeywords}
                >
                  Refresh
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={selectedKeywords.length === eligibleKeywords.length ? <CheckBox /> : <CheckBoxOutlineBlank />}
                  onClick={handleSelectAll}
                  disabled={eligibleKeywords.length === 0}
                >
                  {selectedKeywords.length === eligibleKeywords.length ? 'Deselect All' : 'Select All Eligible'}
                </Button>

                {failedKeywords.length > 0 && (
                  <Button
                    variant="contained"
                    color="warning"
                    startIcon={<Replay />}
                    onClick={handleRetryFailedKeywords}
                    disabled={generating}
                  >
                    Retry {failedKeywords.length} Failed
                  </Button>
                )}
                
                <Typography variant="body2" color="textSecondary">
                  {selectedEligibleCount} of {eligibleKeywords.length} eligible keywords selected
                </Typography>
              </Box>

              <Button
                variant="contained"
                startIcon={<Article />}
                onClick={() => setGenerateDialogOpen(true)}
                disabled={selectedEligibleCount === 0}
                color="primary"
              >
                Generate {selectedEligibleCount} Blogs
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Keywords Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Your Keywords ({keywords.length})
            </Typography>
            
            {loadingKeywords ? (
              <LinearProgress sx={{ my: 2 }} />
            ) : (
              <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedKeywords.length === eligibleKeywords.length && eligibleKeywords.length > 0}
                          indeterminate={selectedKeywords.length > 0 && selectedKeywords.length < eligibleKeywords.length}
                          onChange={handleSelectAll}
                          disabled={eligibleKeywords.length === 0}
                        />
                      </TableCell>
                      <TableCell>Keyword</TableCell>
                      <TableCell align="right">Search Volume</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Difficulty</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Blog Generated</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {keywords.map((keyword) => {
                      const isEligible = keyword.status === 'pending' && !keyword.blog_generated;
                      return (
                        <TableRow key={keyword.id}>
                          <TableCell padding="checkbox">
                            <Checkbox
                              checked={selectedKeywords.includes(keyword.id!)}
                              onChange={() => handleSelectKeyword(keyword.id!)}
                              disabled={!isEligible}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {keyword.keyword}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {keyword.search_volume ? keyword.search_volume.toLocaleString() : '-'}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={keyword.category || 'General'} 
                              size="small" 
                              variant="outlined" 
                            />
                          </TableCell>
                          <TableCell align="right">{keyword.keyword_difficulty || '-'}</TableCell>
                          <TableCell>
                            <Chip
                              label={
                                keyword.status === 'processing' ? 'In Queue 🔄' :
                                keyword.status === 'completed' ? 'Completed' :
                                keyword.status === 'failed' ? 'Failed' :
                                'Ready'
                              }
                              size="small"
                              color={
                                keyword.status === 'completed' ? 'success' : 
                                keyword.status === 'processing' ? 'warning' : 
                                keyword.status === 'failed' ? 'error' : 'default'
                              }
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={keyword.blog_generated ? 'Yes' : 'No'}
                              size="small"
                              color={keyword.blog_generated ? 'success' : 'default'}
                              variant={keyword.blog_generated ? 'filled' : 'outlined'}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="textSecondary">
                              {keyword.created_at ? new Date(keyword.created_at).toLocaleDateString() : '-'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', justifyContent: 'center' }}>
                              {keyword.status === 'processing' ? (
                                <Chip
                                  label="In Queue 🔄"
                                  size="small"
                                  color="warning"
                                  variant="filled"
                                />
                              ) : isEligible || keyword.status === 'failed' ? (
                                <Button
                                  size="small"
                                  variant="contained"
                                  startIcon={<Article />}
                                  onClick={() => {
                                    // If failed, first reset the keyword, then generate
                                    if (keyword.status === 'failed') {
                                      handleRetryIndividualKeyword(keyword.id!, keyword.keyword);
                                    } else {
                                      setSelectedKeywords([keyword.id!]);
                                      setGenerateDialogOpen(true);
                                    }
                                  }}
                                  color={keyword.status === 'failed' ? 'warning' : 'primary'}
                                >
                                  {keyword.status === 'failed' ? 'Retry Blog' : 'Generate Blog'}
                                </Button>
                              ) : (
                                <Chip
                                  label={keyword.blog_generated ? 'Blog Created' : 'Not Available'}
                                  size="small"
                                  color={keyword.blog_generated ? 'success' : 'default'}
                                  variant="outlined"
                                />
                              )}
                              
                              <Button
                                size="small"
                                variant="outlined"
                                color="error"
                                startIcon={<Delete />}
                                onClick={() => handleDeleteKeyword(keyword.id!, keyword.keyword)}
                                sx={{ ml: 1 }}
                              >
                                Delete
                              </Button>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Upload Keywords Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upload Keywords from File
                </Typography>
                
                <Box
                  {...getRootProps()}
                  sx={{
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'grey.300',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    cursor: 'pointer',
                    bgcolor: isDragActive ? 'primary.light' : 'background.paper',
                    '&:hover': {
                      bgcolor: 'grey.50',
                    },
                  }}
                >
                  <input {...getInputProps()} />
                  <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {isDragActive ? 'Drop your file here' : 'Drag & drop your keyword file'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Supports CSV, XLS, XLSX files with keyword data
                  </Typography>
                  <Button variant="outlined" sx={{ mt: 2 }}>
                    Browse Files
                  </Button>
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Campaign Name"
                        value={campaignName}
                        onChange={(e) => setCampaignName(e.target.value)}
                        placeholder="My SEO Campaign"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Template Type</InputLabel>
                        <Select
                          value={templateType}
                          onChange={(e) => setTemplateType(e.target.value)}
                        >
                          <MenuItem value="ecommerce_general">Ecommerce General</MenuItem>
                          <MenuItem value="health_wellness">Health & Wellness</MenuItem>
                          <MenuItem value="technology">Technology</MenuItem>
                          <MenuItem value="lifestyle">Lifestyle</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Box>

                {uploadStatus === 'uploading' && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress />
                  </Box>
                )}

                {uploadMessage && (
                  <Alert 
                    severity={uploadStatus === 'success' ? 'success' : uploadStatus === 'error' ? 'error' : 'info'}
                    sx={{ mt: 2 }}
                  >
                    {uploadMessage}
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  File Format Guide
                </Typography>
                <Typography variant="body2" paragraph>
                  Your CSV/Excel file should contain these columns:
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <li><strong>keyword</strong> (required)</li>
                  <li><strong>search_volume</strong> (optional)</li>
                  <li><strong>keyword_difficulty</strong> (optional)</li>
                  <li><strong>category</strong> (optional)</li>
                </Box>
                
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Download />}
                  sx={{ mt: 2 }}
                  onClick={() => {
                    const csvContent = 'keyword,search_volume,category,keyword_difficulty\nCBD gummies for pain,18100,Pain Relief,45\nCBD for sleep,14800,Sleep Disorders,40';
                    const blob = new Blob([csvContent], { type: 'text/csv' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'keyword_template.csv';
                    a.click();
                  }}
                >
                  Download Template
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Preview Table */}
        {uploadedKeywords.length > 0 && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Preview ({uploadedKeywords.length} keywords)
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<CloudUpload />}
                  onClick={handleUploadToBackend}
                  disabled={uploadStatus === 'uploading'}
                >
                  {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload to Server'}
                </Button>
              </Box>
              
              <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Keyword</TableCell>
                      <TableCell align="right">Search Volume</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Difficulty</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {uploadedKeywords.slice(0, 50).map((keyword, index) => (
                      <TableRow key={index}>
                        <TableCell>{keyword.keyword}</TableCell>
                        <TableCell align="right">
                          {keyword.search_volume ? keyword.search_volume.toLocaleString() : '-'}
                        </TableCell>
                        <TableCell>
                          <Chip label={keyword.category} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="right">{keyword.keyword_difficulty || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      {/* Blog Generation Dialog */}
      <Dialog open={generateDialogOpen} onClose={() => setGenerateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Blogs</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Generate blogs for {selectedEligibleCount} selected keywords
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Shopify Store</InputLabel>
            <Select
              value={selectedStore}
              onChange={(e) => setSelectedStore(Number(e.target.value))}
            >
              {stores.map((store) => (
                <MenuItem key={store.id} value={store.id}>
                  {store.store_name} ({store.shop_url})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Template Type</InputLabel>
            <Select
              value={templateType}
              onChange={(e) => setTemplateType(e.target.value)}
            >
              <MenuItem value="ecommerce_general">Ecommerce General</MenuItem>
              <MenuItem value="health_wellness">Health & Wellness</MenuItem>
              <MenuItem value="technology">Technology</MenuItem>
              <MenuItem value="lifestyle">Lifestyle</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Checkbox
              checked={autoPublish}
              onChange={(e) => setAutoPublish(e.target.checked)}
            />
            <Typography>Auto-publish blogs to Shopify after generation</Typography>
          </Box>

          <Alert severity="info" sx={{ mt: 2 }}>
            <strong>Estimated time:</strong> {selectedEligibleCount * 3} minutes<br />
            <strong>Estimated cost:</strong> ${(selectedEligibleCount * 0.10).toFixed(2)} (OpenAI API)
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleGenerateBlogs}
            variant="contained"
            disabled={generating || selectedStore === 0}
            startIcon={<PlayArrow />}
          >
            {generating ? 'Generating...' : `Generate ${selectedEligibleCount} Blogs`}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default KeywordsPage;