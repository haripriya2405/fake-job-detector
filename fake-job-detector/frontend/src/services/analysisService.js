import apiClient from './api';

export const analysisService = {
  // Returns a unique local storage key per user (or guest)
  getStorageKey() {
    try {
      const rawUser = localStorage.getItem('sentinel_user');
      if (rawUser) {
        const parsed = JSON.parse(rawUser);
        if (parsed?.email) {
          return `sentinel_scan_history_${parsed.email.toLowerCase().trim()}`;
        }
        if (parsed?.id) {
          return `sentinel_scan_history_${parsed.id}`;
        }
      }
    } catch (err) {
      console.warn('Could not determine user storage key:', err);
    }
    return 'sentinel_scan_history_guest';
  },

  async analyzeText(text, metadata = {}) {
    try {
      const response = await apiClient.post('/analysis', {
        raw_content: text,
        job_title: metadata.job_title,
        company_name: metadata.company_name,
        source_type: 'text'
      });
      if (response.data?.id) {
        const key = this.getStorageKey();
        const history = JSON.parse(localStorage.getItem(key) || '[]');
        localStorage.setItem(key, JSON.stringify([response.data, ...history.filter(h => h.id !== response.data.id)]));
        return response.data;
      }
      throw new Error('Analysis response missing ID');
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Analysis failed';
      throw new Error(errMsg);
    }
  },

  async analyzeUpload(file, type = 'pdf', metadata = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_type', type);
      if (metadata.job_title) formData.append('job_title', metadata.job_title);
      if (metadata.company_name) formData.append('company_name', metadata.company_name);

      const response = await apiClient.post('/analysis/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (response.data?.id) {
        const key = this.getStorageKey();
        const history = JSON.parse(localStorage.getItem(key) || '[]');
        localStorage.setItem(key, JSON.stringify([response.data, ...history.filter(h => h.id !== response.data.id)]));
        return response.data;
      }
      throw new Error('Upload analysis response missing ID');
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'File analysis failed';
      throw new Error(errMsg);
    }
  },

  async analyzeUrl(jobUrl, metadata = {}) {
    try {
      const response = await apiClient.post('/analysis/url', {
        job_url: jobUrl,
        job_title: metadata.job_title,
        company_name: metadata.company_name,
      });
      if (response.data?.id) {
        const key = this.getStorageKey();
        const history = JSON.parse(localStorage.getItem(key) || '[]');
        localStorage.setItem(key, JSON.stringify([response.data, ...history.filter(h => h.id !== response.data.id)]));
        return response.data;
      }
      throw new Error('URL analysis response missing ID');
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'URL analysis failed';
      throw new Error(errMsg);
    }
  },

  async getAnalysisById(id) {
    try {
      const response = await apiClient.get(`/analysis/${id}`);
      if (response.data?.id) {
        return response.data;
      }
    } catch (err) {
      const key = this.getStorageKey();
      const history = JSON.parse(localStorage.getItem(key) || '[]');
      const foundInHistory = history.find((a) => a.id === id);
      if (foundInHistory) return foundInHistory;
      
      const errMsg = err.response?.data?.detail || err.message || 'Report not found';
      throw new Error(errMsg);
    }

    const key = this.getStorageKey();
    const history = JSON.parse(localStorage.getItem(key) || '[]');
    const foundInHistory = history.find((a) => a.id === id);
    if (foundInHistory) return foundInHistory;

    throw new Error(`Analysis report '${id}' not found`);
  },

  async getHistory() {
    let serverItems = [];
    try {
      const response = await apiClient.get('/analysis/history');
      if (Array.isArray(response.data)) {
        serverItems = response.data;
      }
    } catch (err) {
      console.warn('Backend history fetch unavailable, retrieving local user history:', err.message);
    }

    const key = this.getStorageKey();
    const localItems = JSON.parse(localStorage.getItem(key) || '[]');
    const map = new Map();
    
    // Merge server records for THIS user
    for (const item of serverItems) {
      if (item && item.id) map.set(item.id, item);
    }
    // Merge locally cached scans for THIS user
    for (const item of localItems) {
      if (item && item.id && !map.has(item.id)) {
        map.set(item.id, item);
      }
    }

    const merged = Array.from(map.values()).sort(
      (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)
    );

    localStorage.setItem(key, JSON.stringify(merged));
    return merged;
  },

  async getAnalysisHistory() {
    return this.getHistory();
  },

  async analyzeBatch(jobsList) {
    try {
      const response = await apiClient.post('/analysis/batch', {
        items: jobsList.map(j => ({
          raw_content: j.raw_content || j.text,
          job_title: j.job_title || j.title,
          company_name: j.company_name || j.company,
          source_type: 'text'
        }))
      });
      if (response.data?.results) {
        const key = this.getStorageKey();
        const history = JSON.parse(localStorage.getItem(key) || '[]');
        const newItems = response.data.results;
        localStorage.setItem(key, JSON.stringify([...newItems, ...history]));
        return response.data;
      }
      throw new Error('Batch response missing results');
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Batch analysis failed';
      throw new Error(errMsg);
    }
  },

  async exportCsv() {
    try {
      const response = await apiClient.get('/analysis/export/csv', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'jobscamscore_audit_history.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      return true;
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Export CSV failed';
      throw new Error(errMsg);
    }
  },

  async deleteAnalysis(id) {
    try {
      await apiClient.delete(`/analysis/${id}`);
    } catch (err) {
      console.warn('Backend delete unavailable, removing locally:', err.message);
    }

    const key = this.getStorageKey();
    const history = JSON.parse(localStorage.getItem(key) || '[]');
    const filtered = history.filter((a) => a.id !== id);
    localStorage.setItem(key, JSON.stringify(filtered));
    return { success: true };
  },

  async claimAnalysis(id) {
    try {
      const response = await apiClient.post(`/analysis/${id}/claim`);
      return response.data;
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Claim scan failed';
      throw new Error(errMsg);
    }
  },
};

export default analysisService;
