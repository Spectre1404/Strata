import { Module } from 'modelence/server';
import { getBarSeries, getCounters, getTrialStream } from './db';

export default new Module('panels', {
  queries: {
    async getCounters() {
      return await getCounters();
    },

    async getTrialStream(args: unknown) {
      const limit = typeof args === 'object' && args !== null && 'limit' in args ? Number((args as { limit: unknown }).limit) : 20;
      return await getTrialStream(Number.isFinite(limit) && limit > 0 ? limit : 20);
    },

    async getBarSeries() {
      return await getBarSeries();
    }
  }
});
