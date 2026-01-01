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
  getDashboardStats: () => axios.get(`${API}/dashboard/stats`, { headers: getAuthHeader() })
};