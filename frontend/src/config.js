// Configuration for API Connection
// VITE_API_URL is set in .env files or deployment platform variables
// Fallback to http://localhost:8000 for local development if not set

// Use empty string to allow Vite proxy to handle routing to backend
// This avoids firewall issues with accessing port 8000 directly
export const API_BASE_URL = import.meta.env.VITE_API_URL || '';
