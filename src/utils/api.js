const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

export const getApiUrl = (endpoint) => {
    // If endpoint starts with /, remove it to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;

    // If API_BASE_URL is empty (local dev with proxy), return original relative path
    if (!API_BASE_URL) return `/${cleanEndpoint}`;

    // Ensure base URL doesn't end with /
    const base = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;

    return `${base}/${cleanEndpoint}`;
};

export default API_BASE_URL;
