'use client';

export default function QuotaMonitor() {
  const used = 1250; // In a real app, this would be fetched from /api/youtube/status
  const total = 10000;
  const percentage = (used / total) * 100;

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-900">YouTube API Quota</h3>
      </div>

      <div className="relative pt-4 flex-1">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600 font-medium">{used.toLocaleString()} used</span>
          <span className="text-gray-400">{total.toLocaleString()} limit</span>
        </div>

        <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-orange-500 to-red-600 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${percentage}%` }}
          />
        </div>

        <div className="mt-4 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-gray-600 font-medium">Reset in 12h</span>
          </div>
          <p className="text-orange-600 font-bold">{(total - used).toLocaleString()} units left</p>
        </div>
      </div>
    </div>
  );
}
