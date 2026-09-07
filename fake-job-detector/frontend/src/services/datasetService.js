import { apiClient } from './api';

export const datasetService = {
  async getSummary() {
    try {
      const response = await apiClient.get('/dataset/summary');
      return response.data;
    } catch (err) {
      console.warn('Dataset summary fallback:', err);
      return {
        total_dataset_records: 17880,
        confirmed_scams_count: 866,
        scam_ratio_percentage: 4.84,
        categories_breakdown: [
          { category: 'Task Recharge / YouTube Rating', count: 215, risk_level: 'CRITICAL' },
          { category: 'Upfront Registration / Software Fee', count: 194, risk_level: 'CRITICAL' },
          { category: 'Fake Check / Equipment Deposit', count: 182, risk_level: 'CRITICAL' },
          { category: 'Fake IT Appointment Letter', count: 145, risk_level: 'HIGH' },
          { category: 'Telegram / WhatsApp-Only Interview', count: 130, risk_level: 'HIGH' },
        ],
      };
    }
  },

  async getSamples(params = {}) {
    try {
      const response = await apiClient.get('/dataset/sample', { params });
      return response.data;
    } catch (err) {
      console.warn('Dataset samples fallback:', err);
      return {
        total: 12,
        records: [
          {
            incident_id: 'IN-SCAM-01',
            scam_category: 'YouTube Like & Subscribe Recharge',
            platform: 'WhatsApp / Telegram',
            claimed_compensation: 'Rs. 150/video (Rs. 3,000 daily)',
            payment_channel: 'UPI / Crypto USDT',
            scam_script_snippet: 'Like 3 YouTube videos to get Rs. 150 instantly. Join Telegram to recharge VIP task account.',
            advisory_agency: 'I4C 1930 Helpline',
          },
          {
            incident_id: 'IN-SCAM-02',
            scam_category: 'Data Entry Daily Pay Trap',
            platform: 'SMS / WhatsApp',
            claimed_compensation: 'Rs. 3,500 - Rs. 5,000 / day',
            payment_channel: 'UPI / Google Pay',
            scam_script_snippet: 'Urgent Part-time home typing work. Pay Rs. 1,999 registration fee for software license key.',
            advisory_agency: 'MHA cybercrime.gov.in',
          },
          {
            incident_id: 'IN-SCAM-03',
            scam_category: 'Fake TCS / Wipro Appointment Letter',
            platform: 'Email / WhatsApp',
            claimed_compensation: '6.5 LPA',
            payment_channel: 'UPI QR Code',
            scam_script_snippet: 'Selected for System Engineer without interview. Transfer Rs. 4,500 refundable security deposit.',
            advisory_agency: 'TCS Security Advisory / 1930',
          },
        ],
      };
    }
  },

  getDownloadUrl() {
    return '/api/v1/dataset/export/csv';
  },
};

export default datasetService;
