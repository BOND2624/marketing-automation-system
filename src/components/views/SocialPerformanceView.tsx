'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  Youtube,
  Instagram,
  Facebook,
  RefreshCw,
  AlertCircle,
  Eye,
  Heart,
  Users,
  BarChart3,
  ExternalLink,
} from 'lucide-react';
import { socialPerformanceApi } from '@/services/api';

type Platform = 'youtube' | 'instagram' | 'facebook';

interface OverviewPost {
  id: string;
  title: string;
  subtitle: string;
  permalink?: string;
  media_type?: string;
  metrics: Record<string, number | string | undefined | null>;
}

interface ChannelBlock {
  connected?: boolean;
  channel?: Record<string, unknown> | null;
  posts: OverviewPost[];
  error?: string;
  videos_error?: string;
  posts_error?: string;
  insights_error?: string;
}

interface Overview {
  youtube: ChannelBlock;
  instagram: ChannelBlock;
  facebook: ChannelBlock;
}

const emptyOverview: Overview = {
  youtube: { connected: false, channel: null, posts: [] },
  instagram: { connected: false, channel: null, posts: [] },
  facebook: { connected: false, channel: null, posts: [] },
};

const OV_STORAGE_KEY = 'mas.socialOverview.v1';

function loadOverviewFromSession(): Overview | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = sessionStorage.getItem(OV_STORAGE_KEY);
    if (!raw) return null;
    const { payload } = JSON.parse(raw) as { payload?: Overview };
    if (!payload?.youtube || !payload?.instagram || !payload?.facebook) return null;
    return {
      youtube: { ...emptyOverview.youtube, ...payload.youtube },
      instagram: { ...emptyOverview.instagram, ...payload.instagram },
      facebook: { ...emptyOverview.facebook, ...payload.facebook },
    };
  } catch {
    return null;
  }
}

function OverviewSkeleton() {
  return (
    <div className="space-y-8 animate-pulse" aria-hidden>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-2xl border border-gray-100 bg-gradient-to-br from-gray-50 to-gray-100/80 h-28" />
        ))}
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
        <div className="h-6 bg-gray-100 rounded-lg w-52" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-gray-50 rounded-xl border border-gray-100" />
          ))}
        </div>
      </div>
      <div className="rounded-2xl border border-gray-100 bg-gray-50/80 min-h-[320px]" />
    </div>
  );
}

function formatNum(n: unknown): string {
  if (n === null || n === undefined) return '—';
  if (typeof n === 'number') return n.toLocaleString();
  const x = Number(n);
  return Number.isFinite(x) ? x.toLocaleString() : String(n);
}

export default function SocialPerformanceView() {
  const [overview, setOverview] = useState<Overview>(emptyOverview);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [platform, setPlatform] = useState<Platform>('youtube');

  const loadOverview = useCallback(async (forceRefresh = false) => {
    const hasSession = typeof window !== 'undefined' && !!sessionStorage.getItem(OV_STORAGE_KEY);
    if (forceRefresh) {
      setRefreshing(true);
    } else if (hasSession) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      const { data } = await socialPerformanceApi.getOverview({ forceRefresh });
      const next: Overview = {
        youtube: { ...emptyOverview.youtube, ...data.youtube },
        instagram: { ...emptyOverview.instagram, ...data.instagram },
        facebook: { ...emptyOverview.facebook, ...data.facebook },
      };
      setOverview(next);
      try {
        sessionStorage.setItem(OV_STORAGE_KEY, JSON.stringify({ savedAt: Date.now(), payload: next }));
      } catch {
        /* quota / private mode */
      }
    } catch (e) {
      console.error(e);
      if (!hasSession) setOverview(emptyOverview);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const cached = loadOverviewFromSession();
    if (cached) {
      setOverview(cached);
      setLoading(false);
    }
    void loadOverview(false);
  }, [loadOverview]);

  const block = overview[platform];
  const posts = block.posts || [];

  const platformTabs: { key: Platform; label: string; icon: React.ReactNode }[] = [
    { key: 'youtube', label: 'YouTube', icon: <Youtube className="w-5 h-5" /> },
    { key: 'instagram', label: 'Instagram', icon: <Instagram className="w-5 h-5" /> },
    { key: 'facebook', label: 'Facebook', icon: <Facebook className="w-5 h-5" /> },
  ];

  return (
    <div className="animate-in fade-in duration-500 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-gray-900 tracking-tight">Social performance</h1>
          <p className="text-sm text-gray-500 mt-1 max-w-xl">
            Compare YouTube, Instagram, and Facebook. Pick a platform for channel stats, then scroll
            the full list of videos or posts with metrics in each row.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {refreshing && !loading && (
            <span className="text-xs font-medium text-orange-600 tabular-nums">Updating…</span>
          )}
          <button
            type="button"
            onClick={() => void loadOverview(true)}
            disabled={loading || refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 bg-white text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading || refreshing ? 'animate-spin' : ''}`} />
            Refresh data
          </button>
        </div>
      </div>

      {loading ? (
        <OverviewSkeleton />
      ) : (
        <>
      {/* Platform switch */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {platformTabs.map((t) => {
          const b = overview[t.key];
          const active = platform === t.key;
          const ok = b.connected && !b.error;
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => setPlatform(t.key)}
              className={`text-left rounded-2xl border p-5 transition-all ${
                active
                  ? 'border-orange-400 bg-orange-50/80 shadow-md ring-2 ring-orange-200'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="flex items-center gap-2 text-gray-900 font-bold">
                  {t.icon}
                  {t.label}
                </span>
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    ok ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-gray-300'
                  }`}
                  title={ok ? 'Connected' : 'Not connected or error'}
                />
              </div>
              <p className="text-xs text-gray-500 line-clamp-2">
                {b.error ||
                  (t.key === 'youtube' && b.videos_error) ||
                  (t.key === 'facebook' && (b.posts_error || b.insights_error)) ||
                  (ok ? 'Data loaded from API' : 'Connect in Integration / Settings')}
              </p>
            </button>
          );
        })}
      </div>

      {/* Channel insights */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-6">
          <BarChart3 className="w-5 h-5 text-orange-500" />
          <h2 className="text-lg font-black text-gray-900">Channel insights</h2>
          <span className="text-xs font-bold uppercase text-gray-400 tracking-wider">
            {platform}
          </span>
        </div>

        {block.error && (
          <div className="flex items-start gap-2 text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{block.error}</span>
          </div>
        )}

        {platform === 'youtube' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Metric label="Channel" value={(block.channel?.name as string) || '—'} accent />
            <Metric label="Subscribers" value={formatNum(block.channel?.subscribers)} icon={<Users className="w-4 h-4" />} />
            <Metric label="Total views" value={formatNum(block.channel?.total_views)} icon={<Eye className="w-4 h-4" />} />
            <Metric label="Videos" value={formatNum(block.channel?.video_count)} />
          </div>
        )}

        {platform === 'instagram' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Metric label="Account" value={`@${block.channel?.username || '—'}`} accent />
            <Metric label="Followers" value={formatNum(block.channel?.followers)} icon={<Users className="w-4 h-4" />} />
            <Metric label="Media count" value={formatNum(block.channel?.media_count)} />
            <div className="rounded-xl bg-gray-50 border border-gray-100 p-4 flex items-center justify-center">
              {block.channel?.profile_picture_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={String(block.channel.profile_picture_url)}
                  alt=""
                  className="h-16 w-16 rounded-full object-cover border border-gray-200"
                />
              ) : (
                <span className="text-xs text-gray-400">No avatar</span>
              )}
            </div>
          </div>
        )}

        {platform === 'facebook' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Metric label="Page" value={(block.channel?.name as string) || '—'} accent />
            <Metric label="Page likes" value={formatNum(block.channel?.fan_count)} icon={<Heart className="w-4 h-4" />} />
            <Metric label="Impressions (30d)" value={formatNum(block.channel?.impressions_30d)} icon={<Eye className="w-4 h-4" />} />
            <Metric label="Engaged users (30d)" value={formatNum(block.channel?.engaged_users_30d)} />
          </div>
        )}
      </div>

      {/* Videos / posts — full width */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm flex flex-col w-full max-h-[min(72vh,720px)] min-h-[280px]">
        <div className="p-4 sm:p-5 border-b border-gray-100 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2">
          <div>
            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">
              {platform === 'youtube' ? 'Videos' : 'Posts'}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {posts.length}{' '}
              {platform === 'youtube'
                ? posts.length === 1
                  ? 'video'
                  : 'videos'
                : posts.length === 1
                  ? 'post'
                  : 'posts'}{' '}
              · metrics per row
            </p>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
          {posts.length === 0 ? (
            <p className="p-6 text-sm text-gray-500">No items returned. Check API keys and permissions.</p>
          ) : (
            posts.map((p) => (
              <div
                key={p.id}
                className="px-4 sm:px-5 py-4 hover:bg-gray-50/80 transition-colors flex flex-col sm:flex-row sm:items-start sm:gap-6 gap-3"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-gray-900 sm:line-clamp-2">{p.title}</p>
                  <p className="text-[10px] font-mono text-gray-400 truncate mt-0.5">{p.subtitle}</p>
                </div>
                <div className="flex flex-wrap items-center gap-2 sm:justify-end sm:shrink-0 sm:max-w-[50%]">
                  {Object.entries(p.metrics).map(([k, v]) => (
                    <span
                      key={k}
                      className="text-[10px] uppercase font-bold text-gray-600 bg-gray-100 px-2.5 py-1 rounded-md border border-gray-100"
                    >
                      {k.replace(/_/g, ' ')}: {formatNum(v)}
                    </span>
                  ))}
                  {p.permalink && (
                    <a
                      href={p.permalink}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-[10px] font-bold text-orange-600 px-2 py-1 rounded-md hover:bg-orange-50"
                    >
                      Open <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
        </>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  accent,
  icon,
}: {
  label: string;
  value: string;
  accent?: boolean;
  icon?: React.ReactNode;
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        accent ? 'bg-gradient-to-br from-orange-50 to-white border-orange-100' : 'bg-gray-50 border-gray-100'
      }`}
    >
      <p className="text-[10px] font-black uppercase text-gray-400 tracking-wider flex items-center gap-1">
        {icon}
        {label}
      </p>
      <p className={`mt-2 font-black ${accent ? 'text-lg text-gray-900' : 'text-xl text-gray-900'}`}>{value}</p>
    </div>
  );
}
