import api from './api';

export const educationalService = {
  /**
   * Fetch 25 Red Flags matrix with optional filters
   */
  async getRedFlags({ category, search, severity } = {}) {
    const params = {};
    if (category && category !== 'ALL') params.category = category;
    if (search) params.search = search;
    if (severity && severity !== 'ALL') params.severity = severity;

    const response = await api.get('/api/v1/educational/red-flags', { params });
    return response.data;
  },

  /**
   * Fetch simulator scenarios for interactive play
   */
  async getSimulatorScenarios({ difficulty } = {}) {
    const params = {};
    if (difficulty && difficulty !== 'ALL') params.difficulty = difficulty;

    const response = await api.get('/api/v1/educational/simulator/scenarios', { params });
    return response.data;
  },

  /**
   * Evaluate a user's guess on a simulator scenario
   */
  async evaluateScenarioAttempt({ scenarioId, userChoiceIsScam, userFlaggedClues = [] }) {
    const response = await api.post('/api/v1/educational/simulator/evaluate', {
      scenario_id: scenarioId,
      user_choice_is_scam: userChoiceIsScam,
      user_flagged_clues: userFlaggedClues,
    });
    return response.data;
  },
};

export default educationalService;
