import { TrendingUp, ArrowUpRight } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  changeLabel: string;
  trend?: 'up' | 'down' | 'neutral';
  sparkline?: number[];
  icon: React.ReactNode;
  iconBg: string;
}

export default function StatCard({ title, value, change, changeLabel, trend = 'up', sparkline = [], icon, iconBg }: StatCardProps) {
  const isUp = trend === 'up';
  const isDown = trend === 'down';

  // Calculate sparkline path
  const points = sparkline.length;
  const max = Math.max(...sparkline, 1);
  const min = Math.min(...sparkline);
  const range = max - min || 1;
  const path = sparkline.length > 1 
    ? `M ${sparkline.map((v, i) => `${(i / (points - 1)) * 100},${100 - ((v - min) / range) * 80}`).join(' L ')}`
    : '';

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:border-orange-200 transition-all duration-300 group hover:shadow-xl hover:shadow-orange-500/5 cursor-pointer relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ArrowUpRight className="w-4 h-4 text-orange-400" />
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 ${iconBg} rounded-xl flex items-center justify-center transition-transform group-hover:scale-110 duration-300 shadow-sm`}>
            {icon}
          </div>
          <div>
            <p className="text-[10px] font-black uppercase text-gray-400 tracking-wider mb-0.5">{title}</p>
            <div className={`flex items-center gap-1.5 ${isUp ? 'text-green-600' : isDown ? 'text-red-600' : 'text-gray-400'}`}>
              <TrendingUp className={`w-3 h-3 ${isDown ? 'rotate-180' : ''}`} />
              <span className="text-[10px] font-black uppercase">{change}</span>
            </div>
          </div>
        </div>
        
        {/* Sparkline */}
        {sparkline.length > 1 && (
          <div className="w-16 h-8 opacity-40 group-hover:opacity-80 transition-opacity">
            <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="none">
              <path
                d={path}
                fill="none"
                stroke={isUp ? '#16a34a' : isDown ? '#dc2626' : '#9ca3af'}
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )}
      </div>

      <div className="flex items-end justify-between">
        <h3 className="text-3xl font-black text-gray-900 tracking-tight group-hover:text-orange-600 transition-colors">
          {value}
        </h3>
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1.5">{changeLabel}</p>
      </div>
    </div>
  );
}
