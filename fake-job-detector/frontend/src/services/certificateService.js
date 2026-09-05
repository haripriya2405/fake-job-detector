import { apiClient } from './api';

export const certificateService = {
  /**
   * Fetch public verification certificate by ID, UUID, or Cert ID
   */
  async getCertificate(identifier) {
    const response = await apiClient.get(`/verify/${identifier}`);
    return response.data;
  },

  /**
   * Return URL for direct SVG badge embed
   */
  getBadgeSvgUrl(identifier) {
    const base = apiClient.defaults.baseURL || '/api/v1';
    return `${base}/verify/${identifier}/badge.svg`;
  },
};

export default certificateService;
