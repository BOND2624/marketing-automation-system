'use client';

import UploadQueue from '@/components/UploadQueue';

interface UploadQueueViewProps {
    videos: any[];
    setVideos: any;
    ytAuthValid: boolean | null;
}

export default function UploadQueueView({ videos, setVideos, ytAuthValid }: UploadQueueViewProps) {
    return (
        <div className="animate-in fade-in duration-700 max-w-7xl mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">Media Command</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Asset Sequencing & YouTube Broadcast</p>
            </div>

            <div className="h-[calc(100vh-250px)]">
                <UploadQueue videos={videos} setVideos={setVideos} ytAuthValid={ytAuthValid} />
            </div>
        </div>
    );
}
