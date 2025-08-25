import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Chip,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Store,
  Link,
  Search
} from '@mui/icons-material';
import { productsApi, storesApi } from '../../services/api';

interface Product {
  id: number;
  name: string;
  description?: string;
  url: string;
  price?: string;
  keywords?: string;
  integration_text?: string;
  store_id: number;
  is_active: boolean;
  priority: number;
  created_at: string;
}

interface Store {
  id: number;
  store_name: string;
  shop_url: string;
  is_active: boolean;
}

const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [selectedStoreId, setSelectedStoreId] = useState<number>(0);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    url: '',
    price: '',
    keywords: '',
    integration_text: '',
    store_id: 0,
    priority: 0,
    is_active: true
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedStoreId) {
      loadProducts();
    }
  }, [selectedStoreId]);

  const loadInitialData = async () => {
    try {
      const storesData = await storesApi.getStores();
      setStores(storesData);
      
      if (storesData.length > 0) {
        setSelectedStoreId(storesData[0].id);
      }
    } catch (error) {
      console.error('Failed to load stores:', error);
    }
  };

  const loadProducts = async () => {
    if (!selectedStoreId) return;
    
    setLoading(true);
    try {
      const data = await productsApi.getProducts(selectedStoreId, false);
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (product?: Product) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        name: product.name,
        description: product.description || '',
        url: product.url,
        price: product.price || '',
        keywords: product.keywords || '',
        integration_text: product.integration_text || '',
        store_id: product.store_id,
        priority: product.priority,
        is_active: product.is_active
      });
    } else {
      setEditingProduct(null);
      setFormData({
        name: '',
        description: '',
        url: '',
        price: '',
        keywords: '',
        integration_text: '',
        store_id: selectedStoreId,
        priority: 0,
        is_active: true
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingProduct(null);
  };

  const handleFormSubmit = async () => {
    try {
      if (editingProduct) {
        await productsApi.updateProduct(editingProduct.id, formData);
      } else {
        await productsApi.createProduct(formData);
      }
      
      handleCloseDialog();
      loadProducts();
      alert(editingProduct ? '✅ Product updated successfully' : '✅ Product created successfully');
    } catch (error: any) {
      alert(`❌ ${error.message}`);
    }
  };

  const handleDeleteProduct = async (productId: number, productName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${productName}"?`)) {
      return;
    }

    try {
      await productsApi.deleteProduct(productId);
      loadProducts();
      alert('✅ Product deleted successfully');
    } catch (error: any) {
      alert(`❌ ${error.message}`);
    }
  };

  const handleToggleActive = async (product: Product) => {
    try {
      await productsApi.updateProduct(product.id, { is_active: !product.is_active });
      loadProducts();
    } catch (error: any) {
      alert(`❌ ${error.message}`);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Products Management
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        Manage products that will be automatically integrated into your blog posts
      </Typography>

      {/* Store Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Store />
            <Typography variant="h6">Select Store</Typography>
          </Box>
          
          <FormControl fullWidth>
            <InputLabel>Store</InputLabel>
            <Select
              value={selectedStoreId}
              label="Store"
              onChange={(e) => setSelectedStoreId(Number(e.target.value))}
            >
              {stores.map((store) => (
                <MenuItem key={store.id} value={store.id}>
                  {store.store_name} ({store.shop_url})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {/* Products Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              Products ({products.length})
            </Typography>
            
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => handleOpenDialog()}
              disabled={!selectedStoreId}
            >
              Add Product
            </Button>
          </Box>

          {loading ? (
            <Typography>Loading products...</Typography>
          ) : products.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="textSecondary">
                No products found. Add your first product to start integrating them into blog posts.
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Product</TableCell>
                    <TableCell>URL</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Keywords</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {products.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {product.name}
                          </Typography>
                          {product.description && (
                            <Typography variant="body2" color="textSecondary" noWrap>
                              {product.description}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }} noWrap>
                          {product.url}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {product.price && (
                          <Chip label={product.price} size="small" color="primary" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 150 }} noWrap>
                          {product.keywords || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={product.priority} 
                          size="small" 
                          color={product.priority > 0 ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={product.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={product.is_active ? 'success' : 'default'}
                          variant={product.is_active ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<Edit />}
                            onClick={() => handleOpenDialog(product)}
                          >
                            Edit
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            color="error"
                            startIcon={<Delete />}
                            onClick={() => handleDeleteProduct(product.id, product.name)}
                          >
                            Delete
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Product Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProduct ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  label="Product Name"
                  fullWidth
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  fullWidth
                  multiline
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
              
              <Grid item xs={12} sm={8}>
                <TextField
                  label="Product URL"
                  fullWidth
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  placeholder="https://your-store.com/products/product-name"
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Price"
                  fullWidth
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  placeholder="$29.99"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Related Keywords"
                  fullWidth
                  value={formData.keywords}
                  onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                  placeholder="cbd oil, pain relief, fibromyalgia, sleep"
                  helperText="Comma-separated keywords that this product relates to. Used to automatically select products for blog posts."
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Integration Text"
                  fullWidth
                  multiline
                  rows={3}
                  value={formData.integration_text}
                  onChange={(e) => setFormData({ ...formData, integration_text: e.target.value })}
                  placeholder="For premium quality CBD products, check out our..."
                  helperText="Custom text that will be used when integrating this product into blog posts"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Priority"
                  type="number"
                  fullWidth
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: Number(e.target.value) })}
                  helperText="Higher priority products are preferred for blog integration"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                  }
                  label="Active"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleFormSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.url}
          >
            {editingProduct ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProductsPage;