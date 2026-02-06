import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function EngagementChartEnhanced() {
  const [showComparison, setShowComparison] = useState(false);

  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const views = [120, 132, 101, 134, 90, 130, 110];
  const engagement = [22, 28, 19, 25, 18, 26, 21];

  const maxViews = Math.max(...views);
  const maxEngagement = Math.max(...engagement);

  const viewsPercentages = views.map(v => (v / maxViews) * 100);
  const engagementPercentages = engagement.map(e => (e / maxEngagement) * 100);

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-gray-600 mb-1">Video Performance</p>
          <h3 className="text-2xl font-bold text-gray-900">1.2M Views</h3>
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
        <svg className="w-full h-48" viewBox="0 0 700 200" preserveAspectRatio="xMidYMid meet">
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
                d={`M ${viewsPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.8}`).join(' L ')} L 700,160 L 0,160 Z`}
                fill="url(#grayGrad)"
                opacity="0.5"
              />
              <polyline
                points={viewsPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.8}`).join(' ')}
                fill="none"
                stroke="#9ca3af"
                strokeWidth="1.5"
                strokeDasharray="5,5"
                opacity="0.4"
              />
            </>
          )}

          <path
            d={`M ${viewsPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.8}`).join(' L ')} L 700,160 L 0,160 Z`}
            fill="url(#orangeGrad)"
          />
          <polyline
            points={viewsPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.8}`).join(' ')}
            fill="none"
            stroke="#f97316"
            strokeWidth="2.5"
          />

          <path
            d={`M ${engagementPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.6}`).join(' L ')} L 700,160 L 0,160 Z`}
            fill="url(#blueGrad)"
          />
          <polyline
            points={engagementPercentages.map((p, i) => `${i * 100 + 50},${160 - p * 0.6}`).join(' ')}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2.5"
          />

          {daysOfWeek.map((_, i) => (
            <line
              key={i}
              x1={i * 100 + 50}
              y1="0"
              x2={i * 100 + 50}
              y2="160"
              stroke="#e5e7eb"
              strokeWidth="1"
              opacity="0.3"
            />
          ))}
        </svg>

        <div className="flex justify-between px-2 text-xs text-gray-500 mt-4">
          {daysOfWeek.map((day) => (
            <span key={day}>{day}</span>
          ))}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
        <div className="p-2 bg-orange-50 rounded-lg">
          <p className="text-gray-600 mb-1">Avg Views/Day</p>
          <p className="font-bold text-orange-600">{Math.round(views.reduce((a, b) => a + b) / views.length)}K</p>
        </div>
        <div className="p-2 bg-blue-50 rounded-lg">
          <p className="text-gray-600 mb-1">Avg Engagement</p>
          <p className="font-bold text-blue-600">{Math.round(engagement.reduce((a, b) => a + b) / engagement.length)}%</p>
        </div>
      </div>
    </div>
  );
}
