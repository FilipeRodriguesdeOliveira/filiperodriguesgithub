import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Connections
  getConnections: () => axios.get(`${API}/connections`, { headers: getAuthHeader() }),
  createConnection: (data) => axios.post(`${API}/connections`, data, { headers: getAuthHeader() }),

  // Goals
  getGoals: () => axios.get(`${API}/goals`, { headers: getAuthHeader() }),
  createGoal: (data) => axios.post(`${API}/goals`, data, { headers: getAuthHeader() }),

  // Data Collection
  getDataCollection: () => axios.get(`${API}/data-collection`, { headers: getAuthHeader() }),

  // AI Analysis
  analyzeWithAI: (data) => axios.post(`${API}/ai/analyze`, data, { headers: getAuthHeader() }),
  getAnalyses: (type) => axios.get(`${API}/ai/analyses${type ? `?ai_type=${type}` : ''}`, { headers: getAuthHeader() }),

  // Campaigns
  getCampaigns: () => axios.get(`${API}/campaigns`, { headers: getAuthHeader() }),
  createCampaign: (data) => axios.post(`${API}/campaigns`, data, { headers: getAuthHeader() }),

  // Metrics
  getMetrics: () => axios.get(`${API}/metrics`, { headers: getAuthHeader() }),
  getDashboardStats: () => axios.get(`${API}/dashboard/stats`, { headers: getAuthHeader() }),

  // OAuth Platform Integrations
  getOAuthPlatforms: () => axios.get(`${API}/oauth/platforms`, { headers: getAuthHeader() }),
  authorizeOAuthPlatform: (platform) => axios.get(`${API}/oauth/${platform}/authorize`, { headers: getAuthHeader() }),
  getOAuthConnections: () => axios.get(`${API}/oauth/connections`, { headers: getAuthHeader() }),
  disconnectOAuthPlatform: (platform) => axios.delete(`${API}/oauth/${platform}`, { headers: getAuthHeader() }),
  syncOAuthPlatform: (platform) => axios.post(`${API}/oauth/${platform}/sync`, {}, { headers: getAuthHeader() })
};