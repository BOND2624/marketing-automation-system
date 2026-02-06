import axios, { AxiosProgressEvent } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const youtubeApi = {
    getStats: () => api.get('/youtube/stats'),
    getAnalytics: () => api.get('/youtube/analytics'),
    getStatus: () => api.get('/youtube/status'),
};

export const campaignApi = {
    list: () => api.get('/campaigns'),
    create: (data: any) => api.post('/campaigns', data),
    execute: (id: number) => api.post(`/campaigns/${id}/execute`),
};

export const uploadsApi = {
    list: () => api.get('/uploads'),
    upload: (file: File, onProgress?: (event: AxiosProgressEvent) => void) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/uploads', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: onProgress,
        });
    },
    publish: (filename: string, metadata: any) =>
        api.post(`/uploads/${filename}/publish`, metadata),
    getTaskStatus: (taskId: string) =>
        api.get(`/uploads/task/${taskId}`),
};

export const systemApi = {
    getStatus: () => api.get('/status'),
};

export default api;
