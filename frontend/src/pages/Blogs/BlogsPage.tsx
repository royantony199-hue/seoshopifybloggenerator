import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Box,
  IconButton,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Refresh,
  Visibility,
  Publish,
  Article,
  TrendingUp,
  Schedule,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { blogsApi, keywordsApi } from '../../services/api';

interface Blog {
  id: number;
  title: string;
  keyword?: string;
  word_count?: number;
  status: string;
  live_url?: string;
  published: boolean;
  created_at: string;
  published_at?: string;
  content_html?: string;
  meta_description?: string;
}

interface BlogStats {
  total_blogs: number;
  published_blogs: number;
  draft_blogs: number;
  avg_word_count: number;
}

interface KeywordStats {
  total_keywords: number;
  blogs_generated: number;
  completion_rate: number;
}

const BlogsPage: React.FC = () => {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [blogStats, setBlogStats] = useState<BlogStats>({
    total_blogs: 0,
    published_blogs: 0,
    draft_blogs: 0,
    avg_word_count: 0,
  });
  const [keywordStats, setKeywordStats] = useState<KeywordStats>({
    total_keywords: 0,
    blogs_generated: 0,
    completion_rate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  const loadBlogs = async () => {
    try {
      const data = await blogsApi.getBlogs();
      setBlogs(data);
    } catch (error) {
      console.error('Failed to load blogs:', error);
    }
  };

  const loadStats = async () => {
    try {
      const [blogStatsData, keywordStatsData] = await Promise.all([
        blogsApi.getStats().catch(() => ({ total_blogs: 0, published_blogs: 0 })),
        keywordsApi.getStats().catch(() => ({ total_keywords: 0, blogs_generated: 0 }))
      ]);
      
      setBlogStats({
        total_blogs: blogStatsData.total_blogs || 0,
        published_blogs: blogStatsData.published_blogs || 0,
        draft_blogs: (blogStatsData.total_blogs || 0) - (blogStatsData.published_blogs || 0),
        avg_word_count: blogStatsData.avg_word_count || 0,
      });
      
      setKeywordStats({
        total_keywords: keywordStatsData.total_keywords || 0,
        blogs_generated: keywordStatsData.blogs_generated || 0,
        completion_rate: keywordStatsData.completion_rate || 0,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const refreshAll = async () => {
    setLoading(true);
    await Promise.all([loadBlogs(), loadStats()]);
    setLoading(false);
  };

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(refreshAll, 10000); // Refresh every 10 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const handlePublishBlog = async (blogId: number) => {
    try {
      const result = await blogsApi.publishBlog(blogId);
      refreshAll();
      
      if (result.demo_mode) {
        alert(`✅ Blog published successfully (Demo Mode)!\n\n📝 Note: This is a demo URL - the blog is not actually published to your Shopify store.\n\n🔗 Demo URL: ${result.live_url}\n\n⚙️ To publish to your real Shopify store:\n1. Go to Settings → Shopify Stores\n2. Add valid API credentials\n3. Make sure the blog handle exists in your Shopify admin`);
      } else {
        alert(`✅ Blog published successfully!\nLive URL: ${result.live_url || 'Check blog details for URL'}`);
      }
    } catch (error: any) {
      console.error('Failed to publish blog:', error);
      let errorMessage = 'Failed to publish blog';
      
      if (error.message.includes('already published')) {
        errorMessage = 'This blog has already been published. Refresh the page to see the updated status.';
      } else if (error.message.includes('not found')) {
        errorMessage = 'Blog not found. Please refresh the page and try again.';
      } else if (error.message.includes('No Shopify store')) {
        errorMessage = 'No Shopify store configured. Please add a store in Settings → Shopify Stores.';
      } else {
        errorMessage = `Publishing failed: ${error.message}`;
      }
      
      alert(`❌ ${errorMessage}`);
    }
  };

  const handlePreviewBlog = async (blog: Blog) => {
    try {
      const fullBlog = await blogsApi.getBlog(blog.id);
      setSelectedBlog(fullBlog);
      setPreviewOpen(true);
    } catch (error) {
      console.error('Failed to load blog content:', error);
      alert('Failed to load blog content');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'processing': return <Schedule />;
      case 'failed': return <Error />;
      default: return <Schedule />;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Generated Blogs
        </Typography>
        <Box>
          <Button
            variant={autoRefresh ? 'contained' : 'outlined'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            sx={{ mr: 2 }}
          >
            {autoRefresh ? 'Auto-Refresh ON' : 'Auto-Refresh OFF'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshAll}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Blogs
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {blogStats.total_blogs}
                  </Typography>
                </Box>
                <Article sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Published
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {blogStats.published_blogs}
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Keywords Processed
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {keywordStats.blogs_generated}/{keywordStats.total_keywords}
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Progress
                </Typography>
                <Typography variant="h4" fontWeight="bold" mb={1}>
                  {keywordStats.completion_rate}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={keywordStats.completion_rate} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {blogs.length === 0 && !loading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            No blogs generated yet
          </Typography>
          <Typography>
            Go to the Keywords page and click "Generate Blog" next to any keyword to start creating SEO-optimized blog content.
          </Typography>
        </Alert>
      )}

      {/* Blogs Table */}
      {blogs.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Keyword</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Words</TableCell>
                <TableCell>Published</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {blogs.map((blog) => (
                <TableRow key={blog.id}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {blog.title}
                    </Typography>
                  </TableCell>
                  <TableCell>{blog.keyword || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      icon={getStatusIcon(blog.status)}
                      label={blog.status}
                      color={getStatusColor(blog.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{blog.word_count || '-'}</TableCell>
                  <TableCell>
                    {blog.published ? (
                      <Chip label="Published" color="success" size="small" />
                    ) : (
                      <Chip label="Draft" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(blog.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handlePreviewBlog(blog)}
                      title="Preview Content"
                    >
                      <Visibility />
                    </IconButton>
                    {!blog.published && blog.status === 'draft' && (
                      <Button
                        size="small"
                        variant="contained"
                        color="primary"
                        startIcon={<Publish />}
                        onClick={() => handlePublishBlog(blog.id)}
                        sx={{ mr: 1 }}
                      >
                        Publish
                      </Button>
                    )}
                    {blog.live_url && (
                      <Box>
                        <Button
                          size="small"
                          href={blog.live_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          color="primary"
                          variant="contained"
                        >
                          View Live Blog
                        </Button>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Blog Preview Dialog */}
      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="lg" fullWidth maxHeight="90vh">
        <DialogTitle>
          <Typography variant="h5">Blog Preview</Typography>
        </DialogTitle>
        <DialogContent sx={{ maxHeight: '70vh', overflow: 'auto' }}>
          {selectedBlog && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedBlog.title}
              </Typography>
              <Typography color="textSecondary" gutterBottom sx={{ mb: 3 }}>
                Keyword: {selectedBlog.keyword} | Words: {selectedBlog.word_count}
              </Typography>
              
              {/* Render the actual blog content */}
              <Box sx={{ 
                mt: 2, 
                '& h1': { fontSize: '1.8rem', fontWeight: 'bold', mb: 2 },
                '& h2': { fontSize: '1.5rem', fontWeight: 'bold', mt: 3, mb: 2 },
                '& h3': { fontSize: '1.3rem', fontWeight: 'bold', mt: 2, mb: 1 },
                '& p': { mb: 2, lineHeight: 1.6 },
                '& ul, & ol': { mb: 2, pl: 3 },
                '& li': { mb: 1 },
                '& table': { width: '100%', borderCollapse: 'collapse', mb: 2 },
                '& th, & td': { border: '1px solid #ddd', padding: '8px', textAlign: 'left' },
                '& th': { backgroundColor: '#f2f2f2', fontWeight: 'bold' }
              }}>
                {selectedBlog.content_html ? (
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: selectedBlog.content_html.replace(/```html\n/, '').replace(/\n```$/, '') 
                    }} 
                  />
                ) : (
                  <Typography color="textSecondary">
                    Blog content is not available for preview.
                  </Typography>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)} variant="outlined">
            Close
          </Button>
          {selectedBlog && !selectedBlog.published && (
            <Button 
              variant="contained"
              onClick={() => {
                handlePublishBlog(selectedBlog.id);
                setPreviewOpen(false);
              }}
            >
              Publish to Shopify
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BlogsPage;