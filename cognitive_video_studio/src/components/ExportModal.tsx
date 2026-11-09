import React, { useState } from 'react';
import { X, FileCode, Film, Cloud, Check, Download, AlertCircle } from 'lucide-react';
import { TimelineTrack } from '../types/studio';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  tracks: TimelineTrack[];
  totalDurationSec: number;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  tracks,
  totalDurationSec
}) => {
  const [copied, setCopied] = useState(false);
  const [cloudRenderTriggered, setCloudRenderTriggered] = useState(false);

  if (!isOpen) return null;

  // Generate sample CMX 3600 EDL string
  const generateEDL = () => {
    let edl = `TITLE: CINEAI_STUDIO_SEQUENCE\nFCM: NON-DROP FRAME\n\n`;
    let eventNum = 1;

    tracks.forEach((track) => {
      track.clips.forEach((clip) => {
        const inMins = Math.floor(clip.inPointSec / 60);
        const inSecs = Math.floor(clip.inPointSec % 60);
        const outMins = Math.floor(clip.outPointSec / 60);
        const outSecs = Math.floor(clip.outPointSec % 60);

        const srcIn = `01:${String(inMins).padStart(2, '0')}:${String(inSecs).padStart(2, '0')}:00`;
        const srcOut = `01:${String(outMins).padStart(2, '0')}:${String(outSecs).padStart(2, '0')}:00`;

        const startMins = Math.floor(clip.startSec / 60);
        const startSecs = Math.floor(clip.startSec % 60);
        const endSec = clip.startSec + clip.durationSec;
        const endMins = Math.floor(endSec / 60);
        const endRemSecs = Math.floor(endSec % 60);

        const recIn = `01:${String(startMins).padStart(2, '0')}:${String(startSecs).padStart(2, '0')}:00`;
        const recOut = `01:${String(endMins).padStart(2, '0')}:${String(endRemSecs).padStart(2, '0')}:00`;

        edl += `${String(eventNum).padStart(3, '0')}  AX       V     C        ${srcIn} ${srcOut} ${recIn} ${recOut}\n`;
        edl += `* FROM CLIP NAME: ${clip.title}\n\n`;
        eventNum++;
      });
    });

    return edl;
  };

  const handleCopyEDL = () => {
    navigator.clipboard.writeText(generateEDL());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTriggerCloudRender = () => {
    setCloudRenderTriggered(true);
    setTimeout(() => setCloudRenderTriggered(false), 4000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6">
      <div className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center space-x-2">
            <Film className="w-5 h-5 text-amber-400" />
            <h3 className="font-bold text-sm text-zinc-100">Export Timeline Sequence</h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {/* Standard EDL Export */}
            <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center space-x-2 text-zinc-200 font-bold text-xs mb-1">
                  <FileCode className="w-4 h-4 text-emerald-400" />
                  <span>Standard CMX 3600 EDL</span>
                </div>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Export edit decision list to open this assembled cut directly inside DaVinci Resolve, Premiere Pro, or Final Cut Pro.
                </p>
              </div>

              <button
                onClick={handleCopyEDL}
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all cursor-pointer"
              >
                {copied ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
                <span>{copied ? 'EDL Copied to Clipboard!' : 'Copy / Download EDL'}</span>
              </button>
            </div>

            {/* Azure Cloud GPU Master Render */}
            <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center space-x-2 text-zinc-200 font-bold text-xs mb-1">
                  <Cloud className="w-4 h-4 text-sky-400" />
                  <span>Azure Spot GPU 4K Render</span>
                </div>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Offload heavy 4K AV1/NVENC master rendering to Azure GPU Spot instances via Zoho Catalyst with automatic checkpointing.
                </p>
              </div>

              <button
                onClick={handleTriggerCloudRender}
                className="w-full py-2 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all cursor-pointer"
              >
                {cloudRenderTriggered ? <Check className="w-4 h-4" /> : <Film className="w-4 h-4" />}
                <span>{cloudRenderTriggered ? 'Job Dispatched to Azure Batch!' : 'Dispatch 4K Master Render'}</span>
              </button>
            </div>
          </div>

          {/* Raw EDL Preview Snippet */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Generated CMX 3600 Preview</span>
            <pre className="p-3 rounded-lg bg-black border border-zinc-900 font-mono text-[10px] text-amber-300/90 overflow-x-auto max-h-36">
              {generateEDL()}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/40 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold rounded-lg text-xs"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
