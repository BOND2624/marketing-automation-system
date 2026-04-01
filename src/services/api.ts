import axios, { AxiosProgressEvent } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';
const YOUTUBE_API_BASE = `${API_BASE_URL}/youtube`;
const UPLOADS_API_BASE = `${API_BASE_URL}/uploads`;
const CDP_API_BASE = `${API_BASE_URL}/cdp`;

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const youtubeApi = {
    getStats: (timeRange: string = '7d') => api.get(`/youtube/stats?time_range=${timeRange}`),
    getVideos: () => api.get('/youtube/videos'),
    getStatus: () => api.get('/youtube/status'),
    getAnalytics: () => api.get('/youtube/videos'),
    seoCheck: (data: { title: string, description: string }) => 
        api.post('/youtube/seo-check', data),
    updateAuth: (token: any) => api.post('/youtube/auth', { token }),
    disconnect: () => api.delete('/youtube/auth'),
};

export const metaApi = {
    getStatus: () => api.get('/meta/status'),
    updateAuth: (data: { access_token: string, page_id?: string, instagram_business_id?: string }) => 
        api.post('/meta/auth', data),
    disconnect: () => api.delete('/meta/auth'),
};

export const uploadsApi = {
    list: () => api.get('/uploads/'),
    upload: (file: File, onProgress: (event: AxiosProgressEvent) => void) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/uploads/', formData, {
            onUploadProgress: onProgress,
        });
    },
    publish: (filename: string, metadata: any) =>
        api.post(`/uploads/${filename}/publish`, metadata),
    publishBatch: (files: { filename: string, metadata: any }[]) =>
        api.post('/uploads/publish-batch', { files }),
    getTaskStatus: (taskId: string) =>
        api.get(`/uploads/task/${taskId}`),
};

export const analyticsApi = {
  getGlobalStats: (timeRange: string = '7d') =>
    api.get(`/youtube/stats?time_range=${timeRange}`),
};

export const cdpApi = {
  getActivity: () => api.get(`/cdp/activity`),
};

export const publishApi = {
    social: (data: any) => api.post('/publish/social', data),
    /** Ollama-powered suggestions from user_input; review before applying to the form */
    personalize: (data: {
        user_input: string;
        platform: 'youtube' | 'instagram' | 'facebook';
        tone?: 'casual' | 'professional' | 'fun';
    }) =>
        api.post<{
            success: boolean;
            title: string;
            description: string;
            body: string;
            tags: string[];
            hashtags: string[];
        }>('/publish/personalize', data),
};

export const systemApi = {
    getStatus: () => api.get('/status'),
};

export const campaignApi = {
    getExecutions: (limit: number = 10) =>
        api.get('/campaigns/executions', { params: { limit } }),
};

/** YouTube + Instagram + Facebook channel & post metrics for the Social Performance dashboard */
export const socialPerformanceApi = {
    getOverview: (opts?: { forceRefresh?: boolean }) =>
        api.get('/social/overview', {
            params: { ...(opts?.forceRefresh ? { force_refresh: true } : {}) },
        }),
    getPostInsights: (
        platform: 'youtube' | 'instagram' | 'facebook',
        itemId: string,
        opts?: { forceRefresh?: boolean }
    ) =>
        api.get('/social/post-insights', {
            params: {
                platform,
                item_id: itemId,
                ...(opts?.forceRefresh ? { force_refresh: true } : {}),
            },
        }),
};

export default api;
