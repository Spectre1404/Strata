import { lazy } from 'react';
import { createBrowserRouter, RouteObject } from 'react-router';

// No auth in this app — Strata's panel page is public, no login.
const routes: RouteObject[] = [
  {
    path: '/',
    Component: lazy(() => import('./pages/HomePage'))
  },
  {
    path: '*',
    Component: lazy(() => import('./pages/NotFoundPage'))
  }
];

export const router = createBrowserRouter(routes);
