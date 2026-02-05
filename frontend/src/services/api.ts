import { secureStorage } from '../utils/secureStorage';

const API_BASE = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = secureStorage.getAuthToken();
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const dashboardApi = {
  getStats: async () => {
    const response = await fetch(`${API_BASE}/api/dashboard`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard stats');
    return response.json();
  },
};

export const keywordsApi = {
  getKeywords: async (params = {}) => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE}/api/keywords/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch keywords');
    return response.json();
  },
  
  getCampaigns: async () => {
    const response = await fetch(`${API_BASE}/api/keywords/campaigns`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch campaigns');
    return response.json();
  },
  
  getStats: async () => {
    const response = await fetch(`${API_BASE}/api/keywords/stats`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch keyword stats');
    return response.json();
  },
  
  uploadKeywords: async (file: File, campaignId?: number, campaignName?: string, templateType?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (campaignId) formData.append('campaign_id', campaignId.toString());
    if (campaignName) formData.append('campaign_name', campaignName);
    if (templateType) formData.append('template_type', templateType);
    
    const token = secureStorage.getAuthToken();
    const response = await fetch(`${API_BASE}/api/keywords/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type for FormData, let browser set it
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload keywords');
    }
    return response.json();
  },

  resetKeyword: async (keywordId: number) => {
    const response = await fetch(`${API_BASE}/api/keywords/${keywordId}/reset`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset keyword');
    }
    return response.json();
  },

  deleteKeyword: async (keywordId: number) => {
    const response = await fetch(`${API_BASE}/api/keywords/${keywordId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete keyword');
    }
    return response.json();
  },

  bulkDeleteKeywords: async (keywordIds: number[]) => {
    const response = await fetch(`${API_BASE}/api/keywords/bulk-delete`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(keywordIds),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete keywords');
    }
    return response.json();
  },
};

export const blogsApi = {
  generateBlogs: async (data: {
    keyword_ids: number[];
    store_id: number;
    template_type?: string;
    auto_publish?: boolean;
    allow_regenerate?: boolean;
  }) => {
    const response = await fetch(`${API_BASE}/api/blogs/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate blogs');
    }
    return response.json();
  },
  
  getBlogs: async (params = {}) => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE}/api/blogs?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch blogs');
    return response.json();
  },
  
  getBlog: async (blogId: number) => {
    const response = await fetch(`${API_BASE}/api/blogs/${blogId}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch blog');
    return response.json();
  },
  
  publishBlog: async (blogId: number) => {
    const response = await fetch(`${API_BASE}/api/blogs/${blogId}/publish`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to publish blog');
    }
    return response.json();
  },
  
  getStats: async () => {
    const response = await fetch(`${API_BASE}/api/blogs/stats/overview`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch blog stats');
    return response.json();
  },
};

export const storesApi = {
  getStores: async () => {
    const response = await fetch(`${API_BASE}/api/stores`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch stores');
    return response.json();
  },
  
  createStore: async (data: {
    store_name: string;
    shop_url: string;
    access_token: string;
    blog_handle?: string;
    auto_publish?: boolean;
    default_product_url?: string;
  }) => {
    const response = await fetch(`${API_BASE}/api/stores`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create store');
    }
    return response.json();
  },
  
  updateStore: async (storeId: number, data: {
    store_name?: string;
    shop_url?: string;
    access_token?: string;
    blog_handle?: string;
    auto_publish?: boolean;
    default_product_url?: string;
    is_active?: boolean;
  }) => {
    const response = await fetch(`${API_BASE}/api/stores/${storeId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update store');
    }
    return response.json();
  },
  
  deleteStore: async (storeId: number) => {
    const response = await fetch(`${API_BASE}/api/stores/${storeId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete store');
    }
    return response.json();
  },
};

export const productsApi = {
  getProducts: async (storeId?: number, activeOnly: boolean = true) => {
    const params = new URLSearchParams();
    if (storeId) params.append('store_id', storeId.toString());
    params.append('active_only', activeOnly.toString());
    
    const response = await fetch(`${API_BASE}/api/products?${params}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch products');
    return response.json();
  },

  createProduct: async (data: {
    name: string;
    description?: string;
    url: string;
    price?: string;
    keywords?: string;
    integration_text?: string;
    store_id: number;
    priority?: number;
  }) => {
    const response = await fetch(`${API_BASE}/api/products`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create product');
    }
    return response.json();
  },

  updateProduct: async (productId: number, data: {
    name?: string;
    description?: string;
    url?: string;
    price?: string;
    keywords?: string;
    integration_text?: string;
    is_active?: boolean;
    priority?: number;
  }) => {
    const response = await fetch(`${API_BASE}/api/products/${productId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update product');
    }
    return response.json();
  },

  deleteProduct: async (productId: number) => {
    const response = await fetch(`${API_BASE}/api/products/${productId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete product');
    }
    return response.json();
  },

  getProductsByKeyword: async (keyword: string, storeId: number) => {
    const response = await fetch(`${API_BASE}/api/products/by-keywords/${encodeURIComponent(keyword)}?store_id=${storeId}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch products by keyword');
    return response.json();
  },
};

export const shopifyOAuthApi = {
  // Start OAuth flow - returns authorization URL
  startOAuth: async (shop_url: string, store_name: string) => {
    const response = await fetch(`${API_BASE}/api/shopify/oauth/authorize`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ shop_url, store_name }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start OAuth flow');
    }
    return response.json();
  },

  // Get connected OAuth stores
  getConnectedStores: async () => {
    const response = await fetch(`${API_BASE}/api/shopify/oauth/connected`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch connected stores');
    return response.json();
  },

  // Test store connection
  testConnection: async (storeId: number) => {
    const response = await fetch(`${API_BASE}/api/shopify/oauth/test-connection/${storeId}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to test connection');
    return response.json();
  },

  // Disconnect store
  disconnectStore: async (storeId: number) => {
    const response = await fetch(`${API_BASE}/api/shopify/oauth/disconnect/${storeId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to disconnect store');
    }
    return response.json();
  },
};

export const settingsApi = {
  getApiKeys: async () => {
    const response = await fetch(`${API_BASE}/api/settings/api-keys`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch API keys');
    return response.json();
  },
  
  saveApiKeys: async (data: {
    openai_api_key?: string;
    serper_api_key?: string;
    unsplash_api_key?: string;
    google_sheets_credentials?: string;
    google_sheets_id?: string;
  }) => {
    const response = await fetch(`${API_BASE}/api/settings/api-keys`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save API keys');
    }
    return response.json();
  },
  
  getProfile: async () => {
    const response = await fetch(`${API_BASE}/api/settings/profile`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
  },
};