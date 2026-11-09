import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize2, 
  Eye, 
  Grid, 
  Scan, 
  RotateCcw,
  Target,
  AlertTriangle,
  Layers,
  Sparkles,
  Scissors,
  CheckCircle2,
  XCircle,
  Clapperboard,
  Film,
  PenTool,
  Bookmark,
  FileText,
  ChevronRight,
  Sun,
  Award
} from 'lucide-react';
import { Take, AspectRatio, StudioViewMode, StorySequence } from '../types/studio';

interface MasterViewportProps {
  activeTake: Take;
  isPlaying: boolean;
  onTogglePlay: () => void;
  aspectRatio: AspectRatio;
  currentTimeSec: number;
  durationSec: number;
  onSeek: (sec: number) => void;
  onOpenInspector: () => void;
  viewMode: StudioViewMode;
  onToggleViewMode: (mode: StudioViewMode) => void;
  sequence?: StorySequence;
  onOpenStoryReview: () => void;
}

export const MasterViewport: React.FC<MasterViewportProps> = ({
  activeTake,
  isPlaying,
  onTogglePlay,
  aspectRatio,
  currentTimeSec,
  durationSec,
  onSeek,
  onOpenInspector,
  viewMode,
  onToggleViewMode,
  sequence,
  onOpenStoryReview
}) => {
  const [showGrid, setShowGrid] = useState(false);
  const [showOverlays, setShowOverlays] = useState(true);
  const [showSpirulaMap, setShowSpirulaMap] = useState(false);
  const [showAestheticsHUD, setShowAestheticsHUD] = useState(true);
  const [playTrimmedOnly, setPlayTrimmedOnly] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const isStoryMode = viewMode === 'story_assembly';

  // Dynamic Story sequence calculations across all multi-scene beats
  let currentBeat = sequence?.beats[0];
  let activeVideoSrc = activeTake.videoBlobUrl;
  let inClipTargetTime = currentTimeSec;
  let currentBeatElapsedOffset = 0;

  if (isStoryMode && sequence && sequence.beats.length > 0) {
    let accumulated = 0;
    for (let i = 0; i < sequence.beats.length; i++) {
      const beat = sequence.beats[i];
      if (currentTimeSec >= accumulated && (currentTimeSec < accumulated + beat.durationSec || i === sequence.beats.length - 1)) {
        currentBeat = beat;
        currentBeatElapsedOffset = accumulated;
        activeVideoSrc = beat.videoStreamUrl;
        const offsetInBeat = Math.max(0, currentTimeSec - accumulated);
        inClipTargetTime = beat.inPointSec + offsetInBeat;
        break;
      }
      accumulated += beat.durationSec;
    }
  }

  // Single take trim points
  const editorTrim = activeTake.scorecard?.editor;
  const singleInSec = editorTrim?.suggestedInSec ?? 0;
  const singleOutSec = editorTrim?.suggestedOutSec ?? durationSec;
  const actionCutSec = editorTrim?.actionCutAnchorSec;

  // Sync real video element with play/pause and seek
  useEffect(() => {
    if (videoRef.current) {
      if (isPlaying) {
        if (!isStoryMode && playTrimmedOnly && (currentTimeSec < singleInSec || currentTimeSec >= singleOutSec)) {
          videoRef.current.currentTime = singleInSec;
          onSeek(singleInSec);
        }
        videoRef.current.play().catch(() => {});
      } else {
        videoRef.current.pause();
      }
    }
  }, [isPlaying, playTrimmedOnly, isStoryMode]);

  useEffect(() => {
    if (videoRef.current) {
      const targetTime = isStoryMode ? inClipTargetTime : currentTimeSec;
      if (Math.abs(videoRef.current.currentTime - targetTime) > 0.35) {
        videoRef.current.currentTime = targetTime;
      }
    }
    // Loop playback in trimmed mode or sequence mode
    if (!isStoryMode && playTrimmedOnly && currentTimeSec >= singleOutSec) {
      onSeek(singleInSec);
    } else if (isStoryMode && sequence && currentTimeSec >= sequence.totalDurationSec) {
      onSeek(0);
    }
  }, [currentTimeSec, playTrimmedOnly, singleInSec, singleOutSec, isStoryMode, sequence, inClipTargetTime]);

  // Compute aspect ratio CSS classes
  const getAspectRatioStyle = () => {
    switch (aspectRatio) {
      case '16:9': return 'aspect-video max-w-4xl';
      case '9:16': return 'aspect-[9/16] max-h-[460px]';
      case '1:1': return 'aspect-square max-h-[460px]';
      case '2.39:1': return 'aspect-[2.39/1] max-w-5xl';
      default: return 'aspect-video max-w-4xl';
    }
  };

  // Format seconds to mm:ss:ff
  const formatTimecode = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = Math.floor(totalSec % 60);
    const frames = Math.floor((totalSec % 1) * 24);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;
  };

  const isTakeShaky = activeTake.cinematography.cameraMotion.toLowerCase().includes('shake') ||
                      activeTake.cinematography.cameraMotion.toLowerCase().includes('unstable');

  return (
    <div className="flex-1 flex flex-col bg-zinc-950 border-r border-zinc-800/80 relative overflow-hidden">
      {/* Top Viewport Toolbar */}
      <div className="h-10 px-4 border-b border-zinc-800/70 bg-zinc-900/70 flex items-center justify-between text-xs text-zinc-400">
        <div className="flex items-center space-x-3">
          {/* View Mode Pill Switcher */}
          <div className="flex items-center bg-zinc-950 p-0.5 rounded-lg border border-zinc-800">
            <button
              onClick={() => onToggleViewMode('take_inspection')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                !isStoryMode
                  ? 'bg-zinc-800 text-amber-300 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Take Inspection
            </button>
            <button
              onClick={() => onToggleViewMode('story_assembly')}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                isStoryMode
                  ? 'bg-gradient-to-r from-amber-500 to-rose-600 text-zinc-950 shadow-md font-bold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Film className="w-3 h-3" />
              <span>🎬 Story First Assembly</span>
            </button>
          </div>

          <span className="text-zinc-600">|</span>

          {/* Current Mode Title */}
          {!isStoryMode ? (
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-zinc-200">{activeTake.label}</span>
              <span className="text-[11px] font-mono text-zinc-500">1080p 25fps</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="font-bold text-amber-300 flex items-center space-x-1">
                <span>First Assembly: {currentBeat?.title}</span>
              </span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.2 rounded font-mono">
                BEAT {currentBeat?.beatNumber || 1} OF {sequence?.beats.length || 1}
              </span>
            </div>
          )}

          {/* Filmmaker Quartet Consensus Pills (In Single Take Mode) */}
          {!isStoryMode && activeTake.scorecard && (
            <div className="hidden xl:flex items-center space-x-1.5 ml-2">
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold flex items-center space-x-1 ${
                activeTake.scorecard.cinematographer.verdict === 'approved' 
                  ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50' 
                  : 'bg-rose-950/70 text-rose-400 border border-rose-800/50'
              }`} title={activeTake.scorecard.cinematographer.rationale}>
                <Film className="w-3 h-3" />
                <span>DP: {activeTake.scorecard.cinematographer.verdict.toUpperCase()}</span>
              </span>

              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold flex items-center space-x-1 ${
                activeTake.scorecard.director.verdict === 'approved' 
                  ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50' 
                  : 'bg-rose-950/70 text-rose-400 border border-rose-800/50'
              }`} title={activeTake.scorecard.director.rationale}>
                <Clapperboard className="w-3 h-3" />
                <span>DIR: {activeTake.scorecard.director.verdict.toUpperCase()}</span>
              </span>

              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold flex items-center space-x-1 ${
                activeTake.scorecard.screenwriter.verdict === 'approved' 
                  ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50' 
                  : 'bg-amber-950/70 text-amber-400 border border-amber-800/50'
              }`} title={activeTake.scorecard.screenwriter.rationale}>
                <PenTool className="w-3 h-3" />
                <span>WRITER: {activeTake.scorecard.screenwriter.verdict.toUpperCase()}</span>
              </span>

              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold flex items-center space-x-1 ${
                activeTake.scorecard.editor.verdict === 'approved' 
                  ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50' 
                  : 'bg-rose-950/70 text-rose-400 border border-rose-800/50'
              }`} title={activeTake.scorecard.editor.rationale}>
                <Scissors className="w-3 h-3" />
                <span>EDIT: -{activeTake.scorecard.editor.deadPausePrunedSec.toFixed(1)}s Trim</span>
              </span>
            </div>
          )}
        </div>

        {/* Viewport Toggles */}
        <div className="flex items-center space-x-2">
          {/* Executive Review Dossier Button */}
          {sequence && (
            <button
              onClick={onOpenStoryReview}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[11px] font-bold transition-all cursor-pointer shadow-sm"
              title="Open First Assembly Dossier for Human Director, Writer & Editor"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Review Dossier</span>
            </button>
          )}

          {!isStoryMode ? (
            <>
              {/* Trimmed Beat Preview Toggle */}
              <button
                onClick={() => {
                  setPlayTrimmedOnly(!playTrimmedOnly);
                  if (!playTrimmedOnly) onSeek(singleInSec);
                }}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                  playTrimmedOnly
                    ? 'bg-emerald-500 text-zinc-950 shadow-md shadow-emerald-950/40'
                    : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                }`}
                title="Preview purely trimmed dramatic performance (skips dead air before action and after cut)"
              >
                <Scissors className="w-3 h-3" />
                <span>{playTrimmedOnly ? 'Trimmed Only' : 'Full Raw'}</span>
              </button>

              {/* Spirula Focus/Blur Heatmap Toggle */}
              <button
                onClick={() => setShowSpirulaMap(!showSpirulaMap)}
                className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
                  showSpirulaMap 
                    ? 'bg-amber-500 text-zinc-950 font-bold shadow-sm' 
                    : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                }`}
                title="Spirula Studio Focus & Depth-of-Field Blur Heatmap"
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Spirula Focus</span>
              </button>

              {/* Human Aesthetics & Composition HUD Toggle */}
              <button
                onClick={() => setShowAestheticsHUD(!showAestheticsHUD)}
                className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
                  showAestheticsHUD 
                    ? 'bg-gradient-to-r from-amber-500 to-rose-600 text-zinc-950 font-bold shadow-sm' 
                    : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                }`}
                title="Toggle Human Aesthetic Quality, Eyeline Horizon & Depth Layering HUD"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Aesthetic HUD</span>
              </button>

              <button
                onClick={() => setShowGrid(!showGrid)}
                className={`p-1 rounded hover:bg-zinc-800 transition-colors cursor-pointer ${
                  showGrid ? 'text-amber-400 bg-zinc-800' : 'text-zinc-400'
                }`}
                title="Toggle Rule-of-Thirds Grid"
              >
                <Grid className="w-3.5 h-3.5" />
              </button>
              
              <button
                onClick={() => setShowOverlays(!showOverlays)}
                className={`p-1 rounded hover:bg-zinc-800 transition-colors cursor-pointer ${
                  showOverlays ? 'text-amber-400 bg-zinc-800' : 'text-zinc-400'
                }`}
                title="Toggle Character Recognition & Tracking HUD"
              >
                <Scan className="w-3.5 h-3.5" />
              </button>
              
              <button
                onClick={onOpenInspector}
                className="flex items-center space-x-1 px-2 py-1 rounded bg-zinc-800/80 hover:bg-zinc-700 text-zinc-200 text-[11px] font-medium transition-all cursor-pointer"
                title="Deep Frame Diagnostic Modal"
              >
                <Eye className="w-3 h-3 text-amber-400" />
                <span>Inspector</span>
              </button>
            </>
          ) : (
            <div className="flex items-center space-x-2 text-[11px] text-zinc-400">
              <span className="font-mono text-emerald-400 font-semibold">100% Performance</span>
              <span className="text-zinc-600">•</span>
              <span className="font-mono text-amber-400">-{sequence?.deadAirSavedSec.toFixed(1)}s Trimmed</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Video Viewport Canvas */}
      <div className="flex-1 flex items-center justify-center p-4 bg-zinc-950/90 relative">
        <div className={`w-full relative rounded-lg overflow-hidden border border-zinc-800/80 shadow-2xl bg-gradient-to-br ${activeTake.thumbnailColor} transition-all duration-300 flex items-center justify-center ${getAspectRatioStyle()}`}>
          {/* Real Video Element */}
          {activeVideoSrc && (
            <video
              ref={videoRef}
              key={activeVideoSrc}
              src={activeVideoSrc}
              muted={isMuted}
              playsInline
              className="w-full h-full object-contain z-0"
              onTimeUpdate={(e) => {
                if (!isStoryMode) {
                  onSeek(e.currentTarget.currentTime);
                } else if (sequence && currentBeat) {
                  // In story mode, map in-clip time back to master sequence timecode
                  const offsetInBeat = Math.max(0, e.currentTarget.currentTime - currentBeat.inPointSec);
                  const seqTime = currentBeatElapsedOffset + offsetInBeat;
                  onSeek(seqTime);
                }
              }}
            />
          )}

          {/* Spirula Focus/Blur Heatmap Overlay (Single Take Mode) */}
          {!isStoryMode && showSpirulaMap && activeTake.heatmapUrl && (
            <img
              src={activeTake.heatmapUrl}
              alt="Spirula Depth & Focus Heatmap"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none z-10 opacity-75 mix-blend-screen"
            />
          )}

          {/* Overlays Container (Character Bounding Boxes & Tracking) */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            {!isStoryMode && showOverlays && (
              <>
                {/* Dynamic Character Detection Bounding Boxes */}
                {activeTake.characters && activeTake.characters.length > 0 ? (
                  activeTake.characters.map((char) => (
                    <div
                      key={char.id}
                      className={`absolute border-2 rounded-lg flex flex-col justify-between p-1 transition-all ${
                        char.focusScore >= 75
                          ? 'border-emerald-400/90 shadow-lg shadow-emerald-950/40 bg-emerald-500/5'
                          : 'border-amber-400/90 shadow-lg shadow-amber-950/40 bg-amber-500/5'
                      }`}
                      style={{
                        left: `${char.box.x}%`,
                        top: `${char.box.y}%`,
                        width: `${char.box.width}%`,
                        height: `${char.box.height}%`
                      }}
                    >
                      {/* Character ID Header Tag */}
                      <div className="flex justify-between items-center text-[9px] font-mono bg-zinc-950/90 text-zinc-100 px-1.5 py-0.5 rounded -mt-5 self-start border border-zinc-700 shadow-md">
                        <span className="font-bold text-amber-300">{char.name}</span>
                        <span className={`ml-1.5 font-bold ${char.focusScore >= 75 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {char.focusScore}% Sharp
                        </span>
                      </div>

                      {/* Feature Crosshair */}
                      <div className="self-center w-3 h-3 border border-emerald-400 rounded-full flex items-center justify-center">
                        <div className="w-1 h-1 bg-emerald-400 rounded-full" />
                      </div>

                      {/* Micro-Action & Eyeline Status */}
                      <div className="text-[8px] font-mono bg-zinc-950/90 px-1.5 py-0.5 rounded text-zinc-200 border border-zinc-700 -mb-5 self-start flex items-center space-x-1.5 shadow-md">
                        <span className="text-zinc-300">{char.action}</span>
                        <span className="text-zinc-500">|</span>
                        <span className="text-emerald-400 font-semibold">{char.eyeline.toUpperCase()}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="absolute top-[28%] left-[38%] w-[24%] h-[42%] border border-amber-400/60 rounded-md flex flex-col justify-between p-1 shadow-lg shadow-amber-950/20">
                    <div className="flex justify-between items-start text-[9px] font-mono text-amber-300 bg-black/60 px-1 rounded">
                      <span>PRIMARY SUBJECT</span>
                      <span>{activeTake.cinematography.focusSharpnessScore}% SHARP</span>
                    </div>
                  </div>
                )}

                {/* Camera Motion & Perspective Telemetry Tag */}
                <div className="absolute top-4 left-4 bg-zinc-950/90 border border-zinc-800 p-2.5 rounded-xl text-[10px] font-mono space-y-1 shadow-xl backdrop-blur-md">
                  <div className="flex items-center space-x-1.5 text-zinc-300">
                    <Target className="w-3.5 h-3.5 text-amber-400" />
                    <span>CAMERA: <span className="font-bold text-amber-300">{activeTake.cinematography.cameraMotion}</span></span>
                  </div>
                  <div className="text-zinc-400">LIGHTING: ΔE {activeTake.cinematography.lightingDeltaE} ({activeTake.cinematography.lightingRatio})</div>
                  {isTakeShaky && (
                    <div className="text-rose-400 font-bold flex items-center space-x-1 pt-0.5 border-t border-rose-900/40">
                      <AlertTriangle className="w-3 h-3" />
                      <span>Shaky Zoom-out Detected at 00:08s</span>
                    </div>
                  )}
                  {actionCutSec && (
                    <div className="text-amber-300 font-semibold flex items-center space-x-1 pt-0.5 border-t border-amber-900/40">
                      <Scissors className="w-3 h-3 text-amber-400" />
                      <span>Action Cut Anchor: {formatTimecode(actionCutSec)} (Gesture Peak)</span>
                    </div>
                  )}
                </div>

                {/* Spirula Focus Indicator */}
                {showSpirulaMap && (
                  <div className="absolute top-4 right-4 bg-amber-500/20 border border-amber-500/50 text-amber-200 px-3 py-1.5 rounded-xl text-[10px] font-mono backdrop-blur-md shadow-lg flex items-center space-x-2">
                    <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
                    <span>Spirula Focus/Bokeh Segmentation: Active</span>
                  </div>
                )}

                {/* Human Aesthetics HUD (Composition, Eyeline Horizon, Depth Planes & Catchlight) */}
                {showAestheticsHUD && activeTake.aesthetics && (
                  <>
                    {/* Golden Eyeline Horizon (Upper Third at 34%) */}
                    <div className="absolute top-[34%] left-0 right-0 border-t border-dashed border-amber-400/40 pointer-events-none flex items-center justify-between px-4">
                      <span className="text-[8px] font-mono bg-zinc-950/80 text-amber-300/80 px-1.5 py-0.2 rounded border border-amber-500/30">
                        GOLDEN EYELINE (1/3rd)
                      </span>
                      <span className="text-[8px] font-mono text-zinc-400 bg-zinc-950/80 px-1 rounded">
                        Δ {activeTake.aesthetics.compositionRuleOfThirds.eyelineOffsetPx}px offset
                      </span>
                    </div>

                    {/* Rule of Thirds Vertical Guides */}
                    <div className="absolute top-0 bottom-0 left-[33.3%] border-l border-dashed border-zinc-700/30 pointer-events-none" />
                    <div className="absolute top-0 bottom-0 left-[66.6%] border-l border-dashed border-zinc-700/30 pointer-events-none" />

                    {/* Three-Dimensional Depth Planes (FG, MG, BG) */}
                    {/* FG Foreground Silhouette Tag (Overturned Chair) */}
                    <div className="absolute bottom-14 left-6 bg-emerald-950/90 border border-emerald-500/70 text-emerald-300 px-2.5 py-1 rounded-lg text-[9px] font-mono shadow-xl backdrop-blur-md flex items-center space-x-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <div>
                        <span className="font-bold text-emerald-200">FG (Foreground): </span>
                        <span>{activeTake.aesthetics.depthAndSeparation.planesIdentified.foreground}</span>
                      </div>
                    </div>

                    {/* MG Midground Focal Subject Tag */}
                    <div className="absolute top-[22%] left-[45%] bg-amber-950/90 border border-amber-500/70 text-amber-200 px-2.5 py-1 rounded-lg text-[9px] font-mono shadow-xl backdrop-blur-md flex items-center space-x-1.5">
                      <Target className="w-3 h-3 text-amber-400" />
                      <div>
                        <span className="font-bold text-amber-300">MG (Focal Plane): </span>
                        <span>{activeTake.aesthetics.depthAndSeparation.planesIdentified.midground}</span>
                      </div>
                    </div>

                    {/* BG Background Falloff Tag */}
                    <div className="absolute top-14 right-6 bg-indigo-950/90 border border-indigo-500/60 text-indigo-300 px-2.5 py-1 rounded-lg text-[9px] font-mono shadow-xl backdrop-blur-md">
                      <span className="font-bold text-indigo-200">BG: </span>
                      <span>{activeTake.aesthetics.depthAndSeparation.planesIdentified.background}</span>
                    </div>

                    {/* Lighting & Catchlight Indicator (Bottom Right) */}
                    <div className="absolute bottom-14 right-6 bg-zinc-950/90 border border-zinc-800/90 p-2.5 rounded-xl text-[9px] font-mono space-y-1 shadow-2xl backdrop-blur-md">
                      <div className="flex items-center space-x-1.5 text-sky-300 font-bold">
                        <Sun className="w-3.5 h-3.5 text-sky-400" />
                        <span>LIGHTING: {activeTake.aesthetics.lightingAndMood.keyToFillRatio}</span>
                      </div>
                      <div className="text-zinc-300">EXPOSURE: IRE {activeTake.aesthetics.lightingAndMood.skinToneIre}% (Optimal Daylight)</div>
                      <div className="flex items-center space-x-1 text-emerald-400 font-semibold pt-0.5 border-t border-zinc-800">
                        <Eye className="w-3 h-3 text-emerald-400" />
                        <span>CATCHLIGHT: {activeTake.aesthetics.lightingAndMood.eyeCatchlightDetected ? 'Active Specular Pupil' : 'Diffused'}</span>
                      </div>
                    </div>

                    {/* Human Circle Take Top-Right Badge */}
                    <div className="absolute top-4 right-4 bg-zinc-950/95 border border-amber-500/80 p-2.5 rounded-xl text-[10px] font-mono space-y-1 shadow-2xl backdrop-blur-md max-w-xs">
                      <div className="flex items-center space-x-1.5 text-amber-300 font-bold">
                        <Award className="w-4 h-4 text-amber-400" />
                        <span>{activeTake.aesthetics.overallGreatnessScore}/100 • {activeTake.aesthetics.verdict.toUpperCase()}</span>
                      </div>
                      <div className="text-[9px] text-zinc-300 line-clamp-2">
                        {activeTake.aesthetics.whyHumanJudgesLoveThis[0]}
                      </div>
                    </div>
                  </>
                )}
              </>
            )}

            {/* Story First Assembly Heads-Up Display (When in Story Mode) */}
            {isStoryMode && sequence && (
              <>
                {/* Active Beat Banner */}
                <div className="absolute top-4 left-4 bg-zinc-950/90 border border-amber-500/60 p-3 rounded-xl text-xs font-mono space-y-1.5 shadow-2xl backdrop-blur-md max-w-sm">
                  <div className="flex items-center space-x-2">
                    <span className="w-4 h-4 rounded-full bg-amber-500 text-zinc-950 flex items-center justify-center font-bold text-[10px]">
                      {currentBeat?.beatNumber}
                    </span>
                    <span className="font-bold text-amber-300 text-[11px] tracking-tight">
                      {currentBeat?.title}
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-300">
                    Source: <span className="text-zinc-100 font-semibold">{currentBeat?.sourceTakeName}</span> ({currentBeat?.sourceFile})
                  </div>
                  <div className="text-[10px] text-zinc-400">
                    {currentBeat?.dramaticPurpose}
                  </div>
                  <div className="pt-1.5 border-t border-zinc-800 text-[9px] text-emerald-400 font-semibold flex items-center justify-between">
                    <span>CUT: {currentBeat?.transitionType}</span>
                    <span className="text-zinc-500">Pruned -{currentBeat?.deadAirPrunedSec.toFixed(1)}s dead air</span>
                  </div>
                </div>

                {/* Kinetic Cut on Action / Scene Cut Pulse Tag */}
                {(() => {
                  const offsetInBeat = currentTimeSec - currentBeatElapsedOffset;
                  const isNearBeatStart = offsetInBeat >= 0 && offsetInBeat < 1.4 && (currentBeat?.beatNumber || 1) > 1;
                  if (isNearBeatStart && currentBeat) {
                    return (
                      <div className="absolute top-4 right-4 bg-gradient-to-r from-amber-500 to-rose-600 text-zinc-950 px-3.5 py-1.5 rounded-xl text-xs font-bold font-mono shadow-2xl animate-pulse flex items-center space-x-2">
                        <Scissors className="w-4 h-4" />
                        <span>✂ CUT: {currentBeat.transitionType.toUpperCase()} ({currentBeat.title})</span>
                      </div>
                    );
                  }
                  return null;
                })()}

                {/* Director's Cut Seal */}
                <div className="absolute bottom-12 left-4 bg-black/80 border border-zinc-800 px-3 py-1.5 rounded-lg text-[10px] font-mono text-zinc-400 flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Quartet Consensus: DP • DIR • WRITER • EDIT APPROVED</span>
                </div>
              </>
            )}

            {/* Rule of Thirds Grid Overlay */}
            {showGrid && (
              <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 pointer-events-none">
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-b border-amber-400/20" />
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-b border-amber-400/20" />
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-r border-b border-amber-400/20" />
                <div className="border-amber-400/20" />
              </div>
            )}

            {/* Big Center Play Icon when paused */}
            {!isPlaying && (
              <div className="w-14 h-14 rounded-full bg-black/60 border border-zinc-700/60 flex items-center justify-center backdrop-blur-sm text-zinc-200">
                <Play className="w-6 h-6 ml-1" />
              </div>
            )}
          </div>

          {/* Bottom Burn-in Timecode */}
          <div className="absolute bottom-3 right-3 bg-black/80 font-mono text-xs px-2.5 py-1 rounded border border-zinc-800 text-amber-400 tracking-wider">
            {formatTimecode(currentTimeSec)} / {formatTimecode(isStoryMode && sequence ? sequence.totalDurationSec : durationSec)}
          </div>
        </div>
      </div>

      {/* Editorial In/Out Trim Rail (Single Take Mode) */}
      {!isStoryMode && editorTrim && (
        <div className="h-6 px-4 bg-zinc-950 border-t border-zinc-800/60 flex items-center text-[10px] font-mono text-zinc-400">
          <span className="text-zinc-500 mr-2 shrink-0">EDIT TRIM:</span>
          <div className="flex-1 h-3 bg-zinc-900 rounded relative overflow-hidden flex items-center">
            {/* Pre-roll Slate Trim (Cut) */}
            <div 
              className="h-full bg-rose-950/60 border-r border-rose-800/80" 
              style={{ width: `${(singleInSec / durationSec) * 100}%` }}
              title={`Pre-roll Cut: 00:00 - ${singleInSec.toFixed(1)}s (Slate & action pause)`}
            />
            {/* Pure Performance Usable Range (Pass) */}
            <div 
              className="h-full bg-emerald-500/20 border-x border-emerald-500/50 flex items-center justify-between px-1 text-[8px] text-emerald-300 font-bold"
              style={{ width: `${((singleOutSec - singleInSec) / durationSec) * 100}%` }}
              title={`Pure Performance Range: ${singleInSec.toFixed(1)}s - ${singleOutSec.toFixed(1)}s`}
            >
              <span>IN: {singleInSec.toFixed(1)}s</span>
              {actionCutSec && (
                <span className="text-amber-400" title={`Action Cut Anchor at ${actionCutSec}s`}>✂ {actionCutSec}s</span>
              )}
              <span>OUT: {singleOutSec.toFixed(1)}s</span>
            </div>
            {/* Post-roll Cut */}
            <div 
              className="h-full bg-rose-950/60 border-l border-rose-800/80" 
              style={{ width: `${((durationSec - singleOutSec) / durationSec) * 100}%` }}
              title={`Post-roll Cut: ${singleOutSec.toFixed(1)}s - ${durationSec.toFixed(1)}s`}
            />
          </div>
          <span className="text-emerald-400 font-semibold ml-2 shrink-0">
            Keep: {(singleOutSec - singleInSec).toFixed(1)}s (-{editorTrim.deadPausePrunedSec.toFixed(1)}s dead air)
          </span>
        </div>
      )}

      {/* Story First Assembly Splice Rail (When in Story Mode) */}
      {isStoryMode && sequence && (
        <div className="h-6 px-4 bg-zinc-950 border-t border-amber-900/40 flex items-center text-[10px] font-mono text-zinc-400">
          <span className="text-amber-400 font-bold mr-2 shrink-0">STORY CUTS:</span>
          <div className="flex-1 h-3.5 bg-zinc-900 rounded relative overflow-hidden flex items-center">
            {sequence.beats.map((beat, idx) => {
              const widthPct = (beat.durationSec / sequence.totalDurationSec) * 100;
              const isCurrent = currentBeat?.id === beat.id;
              const colors = [
                'bg-emerald-900/60 text-emerald-200 border-amber-400',
                'bg-teal-900/60 text-teal-200 border-amber-400',
                'bg-cyan-900/60 text-cyan-200 border-amber-400',
                'bg-blue-900/60 text-blue-200 border-amber-400',
                'bg-indigo-900/60 text-indigo-200 border-amber-400',
              ];
              const colorClass = colors[idx % colors.length];
              return (
                <div
                  key={beat.id}
                  className={`h-full ${colorClass} ${idx < sequence.beats.length - 1 ? 'border-r-2' : ''} ${isCurrent ? 'brightness-125 ring-1 ring-amber-300' : ''} flex items-center justify-between px-1.5 text-[8px] font-bold overflow-hidden truncate`}
                  style={{ width: `${widthPct}%` }}
                  title={`${beat.title} (${beat.durationSec.toFixed(1)}s) - ${beat.transitionType}`}
                >
                  <span className="truncate">B{beat.beatNumber}: {beat.title.split(':')[0]}</span>
                  {idx < sequence.beats.length - 1 && (
                    <span className="text-amber-300 shrink-0 ml-1">✂</span>
                  )}
                </div>
              );
            })}
          </div>
          <span className="text-amber-300 font-bold ml-2 shrink-0">
            Total Cut: {sequence.totalDurationSec.toFixed(1)}s (-{sequence.deadAirSavedSec.toFixed(1)}s slate pruned)
          </span>
        </div>
      )}

      {/* Viewport Playback Transport Bar (Thumb-Friendly Ergonomics) */}
      <div className="h-16 border-t border-zinc-800/80 bg-zinc-900/60 px-3 md:px-4 flex items-center justify-between shrink-0">
        {/* Playback Transport Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onSeek(Math.max(0, currentTimeSec - 1))}
            className="w-11 h-11 rounded-xl bg-zinc-800/90 hover:bg-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-all active:scale-95 cursor-pointer border border-zinc-700/60"
            title="Step Back 1 Sec (J)"
            aria-label="Step Back 1 Sec"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Primary Play/Pause Hero Button (48x48px) */}
          <button
            onClick={onTogglePlay}
            className="w-12 h-12 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-zinc-950 font-bold flex items-center justify-center transition-all active:scale-90 shadow-lg shadow-amber-950/50 cursor-pointer border border-amber-300/40"
            title="Play / Pause (Space)"
            aria-label="Play or Pause Video"
          >
            {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
          </button>

          <button
            onClick={() => onSeek(Math.min(isStoryMode && sequence ? sequence.totalDurationSec : durationSec, currentTimeSec + 1))}
            className="w-11 h-11 rounded-xl bg-zinc-800/90 hover:bg-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-all active:scale-95 cursor-pointer border border-zinc-700/60"
            title="Step Forward 1 Sec (L)"
            aria-label="Step Forward 1 Sec"
          >
            <RotateCcw className="w-4 h-4 transform scale-x-[-1]" />
          </button>

          {/* Mini Playback Scrubber */}
          <div className="flex items-center space-x-2 ml-2 md:ml-4">
            <span className="font-mono text-xs text-zinc-200 font-semibold">{formatTimecode(currentTimeSec)}</span>
            <input
              type="range"
              min={0}
              max={isStoryMode && sequence ? sequence.totalDurationSec : durationSec}
              step={0.0416}
              value={currentTimeSec}
              onChange={(e) => onSeek(parseFloat(e.target.value))}
              className="w-28 sm:w-44 md:w-56 h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-amber-400 hover:accent-amber-300"
              aria-label="Seek Video Position"
            />
            <span className="font-mono text-xs text-zinc-500 hidden sm:inline">
              {formatTimecode(isStoryMode && sequence ? sequence.totalDurationSec : durationSec)}
            </span>
          </div>
        </div>

        {/* Viewport Actions (Mute & Fullscreen with min 44x44px touch targets) */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="w-11 h-11 rounded-xl bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-all active:scale-95 cursor-pointer border border-zinc-700/40"
            title={isMuted ? 'Unmute Player' : 'Mute Player'}
            aria-label="Mute or Unmute Audio"
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4" />}
          </button>
          <button 
            className="w-11 h-11 rounded-xl bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-all active:scale-95 cursor-pointer border border-zinc-700/40"
            title="Toggle Fullscreen"
            aria-label="Toggle Fullscreen"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
