// The fixture <-> Atlas swap point. Everything else imports from here, never
// directly from fixtures.ts or mongo.ts. Flip with DATA_SOURCE=mongo once
// Shiv's scripts/seed_fixtures.py has run and .env has real Atlas values.
import * as fixtures from './fixtures';
import * as mongo from './mongo';

const impl = process.env.DATA_SOURCE === 'mongo' ? mongo : fixtures;

export const getCounters = impl.getCounters;
export const getTrialStream = impl.getTrialStream;
export const getBarSeries = impl.getBarSeries;
