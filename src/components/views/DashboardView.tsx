'use client';

import { Users, Eye, PlayCircle, Activity, Youtube, Instagram, Facebook, ChevronRight, BarChart3 } from 'lucide-react';
import StatCard from '@/components/StatCard';
import EngagementChart from '@/components/EngagementChart';
import TimeRangeSelector from '@/components/TimeRangeSelector';
import QuickInsights from '@/components/QuickInsights';
import CdpActivity from '@/components/CdpActivity';
import { useState, useMemo, useEffect, type ReactNode } from 'react';
import { analyticsApi, youtubeApi, socialPerformanceApi } from '@/services/api';

interface DashboardViewProps {
  /** Opens the dedicated Social performance screen (YouTube + Instagram + Facebook). */
  onGoToSocialPerformance?: () => void;
}

export default function DashboardView({ onGoToSocialPerformance }: DashboardViewProps) {
    const [timeRange, setTimeRange] = useState('7d');
    const [stats, setStats] = useState<any>(null);
    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [socialOverview, setSocialOverview] = useState<{
        youtube: { connected?: boolean; channel?: Record<string, unknown> | null; posts?: unknown[]; error?: string };
        instagram: { connected?: boolean; channel?: Record<string, unknown> | null; posts?: unknown[]; error?: string };
        facebook: { connected?: boolean; channel?: Record<string, unknown> | null; posts?: unknown[]; error?: string };
    } | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [statsRes, analyticsRes, socialRes] = await Promise.allSettled([
                    analyticsApi.getGlobalStats(timeRange),
                    youtubeApi.getVideos(),
                    socialPerformanceApi.getOverview(),
                ]);
                if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
                if (analyticsRes.status === 'fulfilled') setAnalyticsData(analyticsRes.value.data);
                if (socialRes.status === 'fulfilled') setSocialOverview(socialRes.value.data);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [timeRange]);

    const subTrend = stats?.trends?.subscribers || { percentage_change: 0, trend: 'neutral' };
    const viewTrend = stats?.trends?.views || { percentage_change: 0, trend: 'neutral' };

    const topVideo = useMemo(() => {
        if (!Array.isArray(analyticsData?.videos) || analyticsData.videos.length === 0) return null;
        return [...analyticsData.videos].sort((a, b) => (b.views || 0) - (a.views || 0))[0];
    }, [analyticsData]);

    const insightsData = {
        top_video: topVideo ? {
            title: topVideo.title,
            views: topVideo.views,
            engagement: topVideo.views > 0 
                ? `${(((topVideo.likes + topVideo.comments) / topVideo.views) * 100).toFixed(1)}%`
                : '0%'
        } : null
    };

    return (
        <div className="animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                        Unified Marketing Command
                    </h1>
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-1">
                        System Hub & Automation Control
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg shadow-sm">
                        <Activity className="w-4 h-4 text-orange-500" />
                        <span className="text-[10px] font-black uppercase text-gray-600">v2.6.0 Live</span>
                    </div>
                </div>
            </div>

            {/* Cross-platform strip — full post/channel drill-down lives on Social performance */}
            {socialOverview && (
                <div className="mb-8 rounded-2xl border-2 border-orange-200 bg-gradient-to-br from-orange-50/90 to-white p-5 shadow-sm">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                        <div className="flex items-start gap-3">
                            <div className="rounded-xl bg-orange-500 text-white p-2.5 shadow-md shadow-orange-500/25">
                                <BarChart3 className="w-5 h-5" />
                            </div>
                            <div>
                                <h2 className="text-sm font-black text-gray-900 uppercase tracking-tight">
                                    Performance across channels
                                </h2>
                                <p className="text-xs text-gray-600 mt-0.5 max-w-xl">
                                    YouTube, Instagram, and Facebook in one place. Open{' '}
                                    <strong className="text-gray-800">Social performance</strong> in the sidebar to
                                    pick posts and load detailed insights.
                                </p>
                            </div>
                        </div>
                        {onGoToSocialPerformance && (
                            <button
                                type="button"
                                onClick={onGoToSocialPerformance}
                                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-orange-600 text-white text-sm font-bold shadow-lg shadow-orange-600/25 hover:bg-orange-700 transition-colors whitespace-nowrap"
                            >
                                Open social insights
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <PlatformMini
                            icon={<Youtube className="w-4 h-4" />}
                            label="YouTube"
                            ok={!!socialOverview.youtube?.connected}
                            line1={
                                socialOverview.youtube?.channel
                                    ? `${Number((socialOverview.youtube.channel as { subscribers?: number }).subscribers ?? 0).toLocaleString()} subscribers`
                                    : '—'
                            }
                            line2={
                                socialOverview.youtube?.channel
                                    ? `${Number((socialOverview.youtube.channel as { total_views?: number }).total_views ?? 0).toLocaleString()} views`
                                    : `${(socialOverview.youtube?.posts as unknown[] | undefined)?.length ?? 0} videos loaded`
                            }
                            err={socialOverview.youtube?.error}
                        />
                        <PlatformMini
                            icon={<Instagram className="w-4 h-4" />}
                            label="Instagram"
                            ok={!!socialOverview.instagram?.connected}
                            line1={
                                socialOverview.instagram?.channel
                                    ? `@${(socialOverview.instagram.channel as { username?: string }).username || '—'}`
                                    : '—'
                            }
                            line2={
                                socialOverview.instagram?.channel
                                    ? `${Number((socialOverview.instagram.channel as { followers?: number }).followers ?? 0).toLocaleString()} followers`
                                    : '—'
                            }
                            err={socialOverview.instagram?.error}
                        />
                        <PlatformMini
                            icon={<Facebook className="w-4 h-4" />}
                            label="Facebook"
                            ok={!!socialOverview.facebook?.connected}
                            line1={
                                socialOverview.facebook?.channel
                                    ? String((socialOverview.facebook.channel as { name?: string }).name || 'Page')
                                    : '—'
                            }
                            line2={
                                socialOverview.facebook?.channel
                                    ? `${Number((socialOverview.facebook.channel as { fan_count?: number }).fan_count ?? 0).toLocaleString()} likes`
                                    : '—'
                            }
                            err={socialOverview.facebook?.error}
                        />
                    </div>
                </div>
            )}

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard
                    title="Audience Reach"
                    value={stats?.subscriber_count?.toLocaleString() || (loading ? '...' : '0')}
                    change={`${subTrend.percentage_change > 0 ? '+' : ''}${subTrend.percentage_change}%`}
                    changeLabel="Growth Trend"
                    trend={subTrend.trend}
                    sparkline={stats?.sparklines?.subscribers || []}
                    icon={<Users className="w-6 h-6 text-orange-600" />}
                    iconBg="bg-orange-50"
                />
                <StatCard
                    title="Visual Impact"
                    value={stats?.view_count?.toLocaleString() || (loading ? '...' : '0')}
                    change={`${viewTrend.percentage_change > 0 ? '+' : ''}${viewTrend.percentage_change}%`}
                    changeLabel="Global Views"
                    trend={viewTrend.trend}
                    sparkline={stats?.sparklines?.views || []}
                    icon={<Eye className="w-6 h-6 text-green-600" />}
                    iconBg="bg-green-50"
                />
                <StatCard
                    title="Campaign Velocity"
                    value={stats?.video_count?.toLocaleString() || '0'}
                    change="Total"
                    changeLabel="Active Loops"
                    trend="neutral"
                    icon={<PlayCircle className="w-6 h-6 text-blue-600" />}
                    iconBg="bg-blue-50"
                />
            </div>

            {/* Quick Insights Section */}
            <QuickInsights data={insightsData} />

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 pb-8">
                <div className="xl:col-span-2">
                     <EngagementChart data={analyticsData?.videos || []} />
                </div>
                <div className="xl:col-span-1">
                    <CdpActivity />
                </div>
            </div>
        </div>
    );
}

function PlatformMini({
    icon,
    label,
    ok,
    line1,
    line2,
    err,
}: {
    icon: ReactNode;
    label: string;
    ok: boolean;
    line1: string;
    line2: string;
    err?: string;
}) {
    return (
        <div className="rounded-xl border border-white/80 bg-white/90 px-4 py-3 shadow-sm">
            <div className="flex items-center justify-between gap-2 mb-2">
                <span className="flex items-center gap-2 text-xs font-black text-gray-800 uppercase tracking-tight">
                    {icon}
                    {label}
                </span>
                <span
                    className={`h-2 w-2 rounded-full shrink-0 ${ok ? 'bg-emerald-500' : 'bg-gray-300'}`}
                    title={ok ? 'Connected' : 'Not connected'}
                />
            </div>
            <p className="text-sm font-bold text-gray-900 truncate">{line1}</p>
            <p className="text-xs text-gray-500">{line2}</p>
            {err && <p className="text-[10px] text-amber-700 mt-1 line-clamp-2">{err}</p>}
        </div>
    );
}
