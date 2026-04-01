import { Calendar } from 'lucide-react';

interface TimeRangeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function TimeRangeSelector({ value, onChange }: TimeRangeSelectorProps) {
  const options = [
    { label: 'Today', value: '1d' },
    { label: 'Last 7 Days', value: '7d' },
    { label: 'Last 30 Days', value: '30d' },
    { label: 'All Time', value: 'all' },
  ];

  return (
    <div className="flex items-center gap-2 p-1 bg-gray-100 rounded-xl border border-gray-200 shadow-inner">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-4 py-1.5 text-xs font-black uppercase tracking-wider rounded-lg transition-all ${
            value === option.value
              ? 'bg-white text-orange-600 shadow-sm scale-105'
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50/50'
          }`}
        >
          {option.label}
        </button>
      ))}
      <div className="ml-2 pl-4 border-l border-gray-200">
        <button className="p-1.5 text-gray-400 hover:text-orange-600 transition-colors">
          <Calendar className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
