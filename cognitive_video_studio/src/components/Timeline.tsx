import React, { useRef } from 'react';
import { 
  Scissors, 
  Magnet, 
  ZoomIn, 
  ZoomOut, 
  Volume2, 
  VolumeX, 
  Lock, 
  Unlock, 
  Eye, 
  EyeOff,
  Plus
} from 'lucide-react';
import { TimelineTrack, TimelineClip } from '../types/studio';

interface TimelineProps {
  tracks: TimelineTrack[];
  currentTimeSec: number;
  totalDurationSec: number;
  onSeek: (time: number) => void;
  onSelectClip: (clip: TimelineClip) => void;
  selectedClipId?: string;
  zoomLevel: number;
  onZoomChange: (zoom: number) => void;
  soundscapeActive?: boolean;
  onToggleSoundscape?: () => void;
  onToggleMuteTrack?: (trackId: string) => void;
}

export const Timeline: React.FC<TimelineProps> = ({
  tracks,
  currentTimeSec,
  totalDurationSec,
  onSeek,
  onSelectClip,
  selectedClipId,
  zoomLevel,
  onZoomChange,
  soundscapeActive = true,
  onToggleSoundscape,
  onToggleMuteTrack
}) => {
  const rulerRef = useRef<HTMLDivElement>(null);

  // Pixel scaling: base width 80px per second * zoom
  const pxPerSec = 45 * zoomLevel;
  const timelineWidth = Math.max(1200, totalDurationSec * pxPerSec);

  // Generate ruler tick marks every 5 seconds
  const rulerTicks = [];
  for (let s = 0; s <= totalDurationSec + 5; s += 2) {
    rulerTicks.push(s);
  }

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const seekSec = Math.max(0, Math.min(totalDurationSec, clickX / pxPerSec));
    onSeek(seekSec);
  };

  return (
    <div className="h-60 border-t border-zinc-800 bg-zinc-950 flex flex-col select-none">
      {/* Timeline Control Ribbon */}
      <div className="h-9 border-b border-zinc-800 bg-zinc-900/70 px-4 flex items-center justify-between text-xs text-zinc-400">
        <div className="flex items-center space-x-3">
          {/* Tools */}
          <button className="flex items-center space-x-1 px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors">
            <Scissors className="w-3 h-3 text-amber-400" />
            <span className="text-[10px] font-medium">Split (C)</span>
          </button>
          <button className="flex items-center space-x-1 px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-amber-300 transition-colors">
            <Magnet className="w-3 h-3" />
            <span className="text-[10px] font-medium">Snap On</span>
          </button>
          <div className="h-3.5 w-px bg-zinc-800" />
          <span className="text-[10px] font-mono text-zinc-400">
            Total Sequence: {totalDurationSec.toFixed(1)}s
          </span>

          {/* Soundscape Synthesizer Master Toggle */}
          {onToggleSoundscape && (
            <button
              onClick={onToggleSoundscape}
              className={`flex items-center space-x-1.5 px-2 py-0.5 rounded border transition-all ${
                soundscapeActive
                  ? 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300 shadow-sm shadow-emerald-950/50'
                  : 'bg-zinc-800 border-zinc-700 text-zinc-500 hover:text-zinc-400'
              }`}
              title="Toggle Web Audio Multi-Track Ambience, Score Drones & Foley Synthesizer"
            >
              <Volume2 className={`w-3 h-3 ${soundscapeActive ? 'text-emerald-400 animate-pulse' : ''}`} />
              <span className="text-[9px] font-bold font-mono">
                SOUNDSCAPE: {soundscapeActive ? 'ACTIVE' : 'MUTED'}
              </span>
            </button>
          )}
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => onZoomChange(Math.max(0.5, zoomLevel - 0.25))}
            className="p-1 rounded hover:bg-zinc-800 text-zinc-400"
            title="Zoom Out"
          >
            <ZoomOut className="w-3 h-3" />
          </button>
          <input
            type="range"
            min="0.5"
            max="3"
            step="0.1"
            value={zoomLevel}
            onChange={(e) => onZoomChange(parseFloat(e.target.value))}
            className="w-20 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <button 
            onClick={() => onZoomChange(Math.min(3, zoomLevel + 0.25))}
            className="p-1 rounded hover:bg-zinc-800 text-zinc-400"
            title="Zoom In"
          >
            <ZoomIn className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Main Track Workspace & Ruler */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Headers (Left Sidebar) */}
        <div className="w-48 border-r border-zinc-800 bg-zinc-900/50 flex flex-col shrink-0 z-10">
          {/* Ruler Header Blank Space */}
          <div className="h-7 border-b border-zinc-800/80 px-2.5 flex items-center justify-between text-[9px] text-zinc-500 font-mono">
            <span>TRACKS ({tracks.length})</span>
            <span className="text-[8px] text-amber-400">AUDIO DESIGN</span>
          </div>

          {/* Track Labels */}
          <div className="flex-1 overflow-y-auto flex flex-col py-0.5">
            {tracks.map((track) => (
              <div 
                key={track.id} 
                className="h-8 px-2.5 border-b border-zinc-800/40 flex items-center justify-between text-xs shrink-0"
              >
                <div className="flex items-center space-x-1.5 font-medium text-zinc-300 min-w-0 pr-1">
                  <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                    track.type === 'video' 
                      ? 'bg-amber-400' 
                      : track.id === 'track_a2'
                      ? 'bg-teal-400'
                      : track.id === 'track_a3'
                      ? 'bg-indigo-400'
                      : track.id === 'track_a4'
                      ? 'bg-orange-400'
                      : 'bg-emerald-400'
                  }`} />
                  <span className="text-[10px] font-semibold truncate" title={track.name}>
                    {track.name}
                  </span>
                </div>
                <div className="flex items-center space-x-0.5 text-zinc-500 shrink-0">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMuteTrack?.(track.id);
                    }}
                    className="p-0.5 hover:text-zinc-200 transition-colors"
                    title={track.isMuted ? 'Unmute Track' : 'Mute Track'}
                  >
                    {track.isMuted ? <VolumeX className="w-3 h-3 text-rose-400" /> : <Volume2 className="w-3 h-3" />}
                  </button>
                  <button className="p-0.5 hover:text-zinc-300">
                    {track.isLocked ? <Lock className="w-3 h-3 text-amber-400" /> : <Unlock className="w-3 h-3" />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Scrollable Tracks Canvas with Ruler */}
        <div className="flex-1 overflow-x-auto relative bg-zinc-950 flex flex-col" onClick={handleTimelineClick}>
          {/* Time Ruler */}
          <div 
            ref={rulerRef} 
            className="h-7 border-b border-zinc-800/80 bg-zinc-900/30 relative shrink-0 cursor-pointer"
            style={{ width: `${timelineWidth}px` }}
          >
            {rulerTicks.map((sec) => (
              <div
                key={sec}
                className="absolute top-0 bottom-0 border-l border-zinc-800 flex items-end pb-1 pl-1 text-[9px] font-mono text-zinc-500"
                style={{ left: `${sec * pxPerSec}px` }}
              >
                {sec}s
              </div>
            ))}

            {/* Draggable Playhead Needle Top Marker */}
            <div
              className="absolute top-0 w-3 h-3 bg-amber-400 -translate-x-1/2 rotate-45 z-30 shadow-md shadow-amber-500/50"
              style={{ left: `${currentTimeSec * pxPerSec}px` }}
            />
          </div>

          {/* Tracks Area */}
          <div 
            className="flex-1 relative flex flex-col py-0.5 overflow-y-auto"
            style={{ width: `${timelineWidth}px` }}
          >
            {tracks.map((track) => (
              <div
                key={track.id}
                className="h-8 border-b border-zinc-900 relative bg-zinc-950/40 flex items-center shrink-0"
              >
                {/* Track Clips */}
                {track.clips.map((clip) => {
                  const clipLeft = clip.startSec * pxPerSec;
                  const clipWidth = clip.durationSec * pxPerSec;
                  const isSelected = selectedClipId === clip.id;

                  return (
                    <div
                      key={clip.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectClip(clip);
                      }}
                      className={`absolute h-6.5 rounded-md border flex items-center px-2 overflow-hidden transition-all shadow cursor-pointer group ${
                        isSelected
                          ? 'border-amber-400 ring-2 ring-amber-400/30 shadow-amber-950/40 z-10'
                          : 'border-zinc-700/80 hover:border-zinc-500'
                      }`}
                      style={{
                        left: `${clipLeft}px`,
                        width: `${clipWidth}px`,
                        backgroundColor: clip.color
                      }}
                    >
                      {/* Left & Right Trim Handles */}
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/20 group-hover:bg-white/40 cursor-ew-resize" />
                      <div className="absolute right-0 top-0 bottom-0 w-1 bg-white/20 group-hover:bg-white/40 cursor-ew-resize" />

                      <div className="flex flex-col justify-center min-w-0 pr-1">
                        <span className="text-[9px] font-bold text-white truncate drop-shadow">
                          {clip.title}
                        </span>
                        <span className="text-[7.5px] font-mono text-zinc-300">
                          {clip.durationSec.toFixed(1)}s
                        </span>
                      </div>

                      {/* Simulated Audio Waveform Bar (for Audio Tracks) */}
                      {track.type === 'audio' && (
                        <div className="absolute inset-x-2 bottom-1 h-3 flex items-end space-x-0.5 opacity-60 pointer-events-none">
                          {[30, 70, 45, 90, 60, 80, 20, 50, 85, 40, 65, 95, 30, 75, 50].map((h, i) => (
                            <div key={i} className="flex-1 bg-white/80 rounded-t-sm" style={{ height: `${h}%` }} />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}

            {/* Draggable Playhead Vertical Red Needle Line */}
            <div
              className="absolute top-0 bottom-0 w-px bg-amber-400 pointer-events-none z-20 shadow-[0_0_8px_rgba(251,191,36,0.8)]"
              style={{ left: `${currentTimeSec * pxPerSec}px` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
