// Configuration for API Connection
// VITE_API_URL is set in .env files or deployment platform variables
// Fallback to http://localhost:8000 for local development if not set

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
