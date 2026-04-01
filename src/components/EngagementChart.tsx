import { useState, useMemo } from 'react';
import { ChevronDown } from 'lucide-react';

interface EngagementChartProps {
  data?: any[];
}

export default function EngagementChartEnhanced({ data = [] }: EngagementChartProps) {
  const [showComparison, setShowComparison] = useState(false);

  const { chartData, totalViews, avgViews, avgEngagement } = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        chartData: [],
        totalViews: "0",
        avgViews: "0",
        avgEngagement: "0%"
      };
    }

    // Process real data (taking last 7 items or all if less)
    const recent = [...data].sort((a, b) => new Date(a.published_at).getTime() - new Date(b.published_at).getTime()).slice(-7);

    // Format for chart
    const processed = recent.map(v => ({
      views: v.views,
      engagement: v.views > 0 ? ((v.likes + v.comments) / v.views) * 100 : 0,
      label: new Date(v.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }));

    // Pad with placeholders if less than 7 data points to maintain chart look (optional, but good for UI)
    // For now, just use what we have.

    const total = data.reduce((sum, v) => sum + v.views, 0);
    const avgV = processed.length ? Math.round(processed.reduce((sum, v) => sum + v.views, 0) / processed.length) : 0;
    const avgE = processed.length ? Math.round(processed.reduce((sum, v) => sum + v.engagement, 0) / processed.length) : 0;

    return {
      chartData: processed,
      totalViews: total.toLocaleString(),
      avgViews: avgV.toLocaleString(),
      avgEngagement: avgE + "%"
    };
  }, [data]);

  const views = chartData.map(d => d.views);
  const engagement = chartData.map(d => d.engagement);
  const labels = chartData.map(d => d.label);

  const maxViews = Math.max(...views, 1);
  const maxEngagement = Math.max(...engagement, 1);

  const viewsPercentages = views.map(v => (v / maxViews) * 100);
  const engagementPercentages = engagement.map(e => (e / maxEngagement) * 100);

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-gray-600 mb-1">Video Performance</p>
          <h3 className="text-2xl font-bold text-gray-900">{totalViews} Views</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span className="text-xs text-gray-600">Views</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-xs text-gray-600">Engagement</span>
          </div>
        </div>
      </div>

      <div className="mb-4 flex items-center gap-2">
        <button
          onClick={() => setShowComparison(!showComparison)}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
        >
          Compare
          <ChevronDown className={`w-3 h-3 transition-transform ${showComparison ? 'rotate-180' : ''}`} />
        </button>
        <span className="text-xs text-gray-500">vs Last Week</span>
      </div>

      <div className="relative flex-1 flex flex-col justify-end">
        {chartData.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
            No analytics data available
          </div>
        ) : (
          <svg className="w-full h-48" viewBox="0 0 700 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#f97316" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#f97316" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="blueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="grayGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#d1d5db" stopOpacity="0.1" />
                <stop offset="100%" stopColor="#d1d5db" stopOpacity="0" />
              </linearGradient>
            </defs>

            {showComparison && (
              <>
                <path
                  d={`M ${viewsPercentages.map((p, i) => `${i * (700 / Math.max(1, viewsPercentages.length - 1))},${160 - p * 0.8}`).join(' L ')} L 700,160 L 0,160 Z`}
                  fill="url(#grayGrad)"
                  opacity="0.5"
                />
                <polyline
                  points={viewsPercentages.map((p, i) => `${i * (700 / Math.max(1, viewsPercentages.length - 1))},${160 - p * 0.8}`).join(' ')}
                  fill="none"
                  stroke="#9ca3af"
                  strokeWidth="1.5"
                  strokeDasharray="5,5"
                  opacity="0.4"
                />
              </>
            )}

            <path
              d={`M ${viewsPercentages.map((p, i) => `${i * (700 / Math.max(1, viewsPercentages.length - 1))},${160 - p * 0.8}`).join(' L ')} L ${viewsPercentages.length > 1 ? 700 : 0},160 L 0,160 Z`}
              fill="url(#orangeGrad)"
            />
            <polyline
              points={viewsPercentages.map((p, i) => `${i * (700 / Math.max(1, viewsPercentages.length - 1))},${160 - p * 0.8}`).join(' ')}
              fill="none"
              stroke="#f97316"
              strokeWidth="2.5"
            />

            <path
              d={`M ${engagementPercentages.map((p, i) => `${i * (700 / Math.max(1, engagementPercentages.length - 1))},${160 - p * 0.6}`).join(' L ')} L ${engagementPercentages.length > 1 ? 700 : 0},160 L 0,160 Z`}
              fill="url(#blueGrad)"
            />
            <polyline
              points={engagementPercentages.map((p, i) => `${i * (700 / Math.max(1, engagementPercentages.length - 1))},${160 - p * 0.6}`).join(' ')}
              fill="none"
              stroke="#3b82f6"
              strokeWidth="2.5"
            />

            {labels.map((_, i) => (
              <line
                key={i}
                x1={i * (700 / Math.max(1, labels.length - 1))}
                y1="0"
                x2={i * (700 / Math.max(1, labels.length - 1))}
                y2="160"
                stroke="#e5e7eb"
                strokeWidth="1"
                opacity="0.3"
              />
            ))}
          </svg>
        )}

        <div className="flex justify-between px-2 text-xs text-gray-500 mt-4">
          {labels.map((day, i) => (
            <span key={i}>{day}</span>
          ))}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
        <div className="p-2 bg-orange-50 rounded-lg">
          <p className="text-gray-600 mb-1">Avg Views/Day</p>
          <p className="font-bold text-orange-600">{avgViews}</p>
        </div>
        <div className="p-2 bg-blue-50 rounded-lg">
          <p className="text-gray-600 mb-1">Avg Engagement</p>
          <p className="font-bold text-blue-600">{avgEngagement}</p>
        </div>
      </div>
    </div>
  );
}
