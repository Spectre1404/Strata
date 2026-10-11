import { startApp } from 'modelence/server';
import panelsModule from '@/server/panels';

startApp({
  modules: [panelsModule],

  security: {
    frameAncestors: ['https://modelence.com', 'https://*.modelence.com', 'http://localhost:*', 'https://*.exp.direct'],
  },
});
