import { apiClient } from './api';

export const communityService = {
  /**
   * Fetch paginated list of community reported scams
   */
  async getScams(params = {}) {
    const response = await apiClient.get('/community/scams', { params });
    return response.data;
  },

  /**
   * Get single scam threat detail by ID or public ID
   */
  async getScamDetail(scamId) {
    const response = await apiClient.get(`/community/scams/${scamId}`);
    return response.data;
  },

  /**
   * Upvote/confirm a community threat
   */
  async confirmThreat(scamId) {
    const response = await apiClient.post(`/community/scams/${scamId}/confirm`);
    return response.data;
  },

  /**
   * Anonymize and publish an analysis result to the public database
   */
  async publishScan(analysisId, customNotes = '') {
    const response = await apiClient.post('/community/scams/publish', {
      analysis_id: analysisId,
      consent_anonymize: true,
      custom_notes: customNotes,
    });
    return response.data;
  },
};

export default communityService;
