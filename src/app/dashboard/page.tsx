'use client';

import { useState, useEffect } from 'react';
import { ShieldCheck } from 'lucide-react';
import Navigation from '@/components/Navigation';
import Sidebar from '@/components/Sidebar';
import { youtubeApi, systemApi, uploadsApi } from '@/services/api';

// View Components
import DashboardView from '@/components/views/DashboardView';
import CustomerCdpView from '@/components/views/CustomerCdpView';
import SocialPublishView from '@/components/views/SocialPublishView';
import SocialPerformanceView from '@/components/views/SocialPerformanceView';
import IntegrationView from '@/components/views/IntegrationView';
import SettingsView from '@/components/views/SettingsView';
import UploadQueueView from '@/components/views/UploadQueueView';

const DashboardSkeleton = () => (
  <div className="animate-pulse space-y-8">
    <div className="h-10 w-64 bg-gray-200 rounded-lg"></div>
    <div className="grid grid-cols-3 gap-6">
      {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-200 rounded-2xl"></div>)}
    </div>
    <div className="grid grid-cols-3 gap-6">
      <div className="h-[500px] col-span-1 bg-gray-200 rounded-2xl"></div>
      <div className="h-[500px] col-span-1 bg-gray-200 rounded-2xl"></div>
      <div className="h-[500px] col-span-1 bg-gray-200 rounded-2xl"></div>
    </div>
  </div>
);

interface VideoItem {
  filename: string;
  size_mb: number;
  status: 'ready' | 'uploading' | 'publishing' | 'done' | 'failed';
  progress?: number;
  task_id?: string;
  error?: string;
  thumbnail?: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState<any>({ system: 'online' });
  const [isOffline, setIsOffline] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeMenu, setActiveMenu] = useState('dashboard');

  // Lifted Upload State
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [ytAuthValid, setYtAuthValid] = useState<boolean | null>(null);
  const [analyticsData, setAnalyticsData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const results = await Promise.allSettled([
          youtubeApi.getStats(),
          systemApi.getStatus(),
          uploadsApi.list(),
          youtubeApi.getStatus(),
          youtubeApi.getAnalytics()
        ]);

        const [statsRes, statusRes, uploadsRes, authRes, analyticsRes] = results;

        // General System Offline Check
        if (statusRes.status === 'rejected') {
          console.error('System API offline:', statusRes.reason);
          // Only truly offline if the core status check itself fails to reach the server
          setIsOffline(true);
        } else {
          setIsOffline(false);
          // If the request succeeded but returned something we didn't expect, we're still "online" but maybe degraded
        }

        // Stats
        if (statsRes.status === 'fulfilled') {
          setStats(statsRes.value.data);
        } else {
          console.warn('Failed to fetch stats:', statsRes.reason);
          setStats(null); // Fallback UI will handle this
        }

        // System Status Mapping
        let newSystemStatus: any = { system: isOffline ? 'offline' : 'online' };
        if (statusRes.status === 'fulfilled') {
          newSystemStatus = { ...newSystemStatus, ...statusRes.value.data };
        } else {
          newSystemStatus = { ...newSystemStatus, database: 'error', celery: 'error' };
        }

        // YouTube Auth
        if (authRes.status === 'fulfilled') {
          newSystemStatus.youtube = authRes.value.data.status || 'Valid';
          setYtAuthValid(authRes.value.data.is_valid);
        } else {
          console.warn('Failed to check Youtube auth:', authRes.reason);
          newSystemStatus.youtube = 'Disconnected';
          setYtAuthValid(false);
        }
        
        setSystemStatus(newSystemStatus);

        // Analytics
        if (analyticsRes.status === 'fulfilled' && analyticsRes.value.data && !analyticsRes.value.data.error) {
          setAnalyticsData(analyticsRes.value.data);
        } else {
          if (analyticsRes.status === 'rejected') {
            console.warn('Analytics API failed:', analyticsRes.reason);
          }
          if (!analyticsData) setAnalyticsData({ videos: [] });
        }

        // Uploads
        if (uploadsRes.status === 'fulfilled') {
          const remoteVideos = uploadsRes.value.data.map((file: any) => ({
            ...file,
            status: 'ready',
            thumbnail: `https://images.pexels.com/photos/4348401/pexels-photo-4348401.jpeg?auto=compress&cs=tinysrgb&w=200`
          }));

          setVideos(prev => {
            const localOnly = prev.filter(v => ['uploading', 'publishing', 'failed'].includes(v.status));
            const merged = [...remoteVideos];
            localOnly.forEach(l => {
              const idx = merged.findIndex(m => m.filename === l.filename);
              if (idx !== -1) merged[idx] = l;
              else merged.push(l);
            });
            return merged;
          });
        }

      } catch (error) {
        console.error('Critical failure in data fetch cycle:', error);
        setIsOffline(true);
        if (!analyticsData) setAnalyticsData({ videos: [] });
      } finally {
        setTimeout(() => setIsLoading(false), 1000);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Polling logic for tasks
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      const activeTasks = videos.filter(v => v.status === 'publishing' && v.task_id);
      if (activeTasks.length === 0) return;

      for (const video of activeTasks) {
        try {
          const res = await uploadsApi.getTaskStatus(video.task_id!);
          const { status, error } = res.data;

          if (status === 'SUCCESS') {
            setVideos(prev => prev.map(v => v.filename === video.filename ? { ...v, status: 'done', task_id: undefined } : v));
          } else if (status === 'FAILURE') {
            setVideos(prev => prev.map(v => v.filename === video.filename ? { ...v, status: 'failed', error: error || 'YouTube API Error', task_id: undefined } : v));
          }
        } catch (e) {
          console.error('Polling error:', e);
        }
      }
    }, 3000);
    return () => clearInterval(pollInterval);
  }, [videos]);

  const renderContent = () => {
    switch (activeMenu) {
      case 'dashboard':
      case 'home':
        return (
          <div className="max-w-7xl mx-auto">
            <DashboardView onGoToSocialPerformance={() => setActiveMenu('video-performance')} />
          </div>
        );
      case 'customer-cdp':
        return (
          <div className="max-w-7xl mx-auto">
            <CustomerCdpView />
          </div>
        );
      case 'social-publish':
        return (
          <div className="max-w-7xl mx-auto">
            <SocialPublishView />
          </div>
        );
      case 'video-performance':
        return (
          <div className="max-w-7xl mx-auto w-full">
            <SocialPerformanceView />
          </div>
        );
      case 'integration':
        return (
          <div className="max-w-7xl mx-auto">
            <IntegrationView systemStatus={systemStatus} />
          </div>
        );
      case 'uploads':
        return (
          <UploadQueueView
            videos={videos}
            setVideos={setVideos}
            ytAuthValid={ytAuthValid}
          />
        );
      case 'settings':
        return (
          <div className="max-w-7xl mx-auto">
            <SettingsView />
          </div>
        );
      default:
        return (
          <div className="max-w-7xl mx-auto">
            <DashboardView onGoToSocialPerformance={() => setActiveMenu('video-performance')} />
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      <Sidebar activeMenu={activeMenu} onMenuClick={setActiveMenu} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navigation
          isOffline={isOffline}
          onUploadSuccess={(newVideo) => setVideos(prev => [newVideo, ...prev])}
        />

        <main className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth">
          {isOffline && (
            <div className="mb-6 p-4 bg-orange-50 border border-orange-200 rounded-xl flex items-center justify-between text-orange-800 animate-in fade-in slide-in-from-top-4">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-orange-500" />
                <span className="text-sm font-bold uppercase tracking-tight">API Optimization in Progress</span>
              </div>
              <p className="text-xs font-medium">Standard latency detected. Connecting to global nodes...</p>
            </div>
          )}

          {isLoading ? <DashboardSkeleton /> : renderContent()}
        </main>
      </div>
    </div>
  );
}
