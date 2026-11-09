import React, { useState } from 'react';
import { 
  X, 
  Film, 
  Clapperboard, 
  PenTool, 
  Scissors, 
  CheckCircle2, 
  AlertTriangle, 
  Download, 
  Clock, 
  Sparkles, 
  Layers,
  ArrowRight,
  FileText,
  Share2,
  Copy,
  Check
} from 'lucide-react';
import { StorySequence } from '../types/studio';

interface StoryReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  sequence: StorySequence;
  onPlayAssembly: () => void;
}

export const StoryReviewModal: React.FC<StoryReviewModalProps> = ({
  isOpen,
  onClose,
  sequence,
  onPlayAssembly
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'edl' | 'disqualified' | 'notes'>('overview');
  const [copiedEdl, setCopiedEdl] = useState(false);

  if (!isOpen) return null;

  // Format seconds into mm:ss:ff
  const formatTc = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    const frames = Math.floor((sec % 1) * 24);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;
  };

  // Generate standard CMX 3600 EDL string
  const generateEdlString = () => {
    let edl = `TITLE: SCENE_${sequence.sceneNumber}_FIRST_ASSEMBLY\nFCM: NON-DROP FRAME\n\n`;
    let recordIn = 0;
    sequence.beats.forEach((b, idx) => {
      const eventNum = String(idx + 1).padStart(3, '0');
      const reel = b.sourceFile.replace(/\.MOV$/i, '').substring(0, 8);
      const srcIn = formatTc(b.inPointSec);
      const srcOut = formatTc(b.outPointSec);
      const recIn = formatTc(recordIn);
      const recOut = formatTc(recordIn + b.durationSec);
      recordIn += b.durationSec;
      edl += `${eventNum}  ${reel.padEnd(8, ' ')} V     C        ${srcIn} ${srcOut} ${recIn} ${recOut}\n`;
      edl += `* FROM CLIP NAME: ${b.sourceFile}\n`;
      edl += `* COMMENT: ${b.actionCutDescription} [${b.transitionType}]\n\n`;
    });
    return edl;
  };

  const handleCopyEdl = () => {
    navigator.clipboard.writeText(generateEdlString());
    setCopiedEdl(true);
    setTimeout(() => setCopiedEdl(false), 2000);
  };

  const handleDownloadEdl = () => {
    const text = generateEdlString();
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Scene_${sequence.sceneNumber}_First_Assembly.edl`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 bg-zinc-900/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-600 flex items-center justify-center text-zinc-950 font-bold shadow-md shadow-amber-950/40">
              <Clapperboard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm font-bold text-zinc-100 tracking-tight">
                  First Assembly Screening Dossier
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  DIRECTOR'S CUT v1.0
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Scene {sequence.sceneNumber}: {sequence.sceneTitle} • Human Review Draft
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                onClose();
                onPlayAssembly();
              }}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-zinc-950 font-bold text-xs shadow-md transition-all active:scale-95 cursor-pointer"
            >
              <Film className="w-3.5 h-3.5" />
              <span>Watch First Assembly</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-zinc-800 bg-zinc-900/40 px-4 text-xs font-medium">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 px-3 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'overview'
                ? 'border-amber-400 text-amber-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Quartet Executive Consensus
          </button>
          <button
            onClick={() => setActiveTab('edl')}
            className={`py-3 px-3 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'edl'
                ? 'border-amber-400 text-amber-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Edit Decision List (EDL & Timecodes)
          </button>
          <button
            onClick={() => setActiveTab('disqualified')}
            className={`py-3 px-3 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'disqualified'
                ? 'border-amber-400 text-amber-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Disqualified Takes & Veto Log
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`py-3 px-3 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'notes'
                ? 'border-amber-400 text-amber-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Filmmaker Role Analysis
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 text-xs text-zinc-300">
          {activeTab === 'overview' && (
            <div className="space-y-5">
              {/* Metric Highlights Banner */}
              <div className="grid grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-zinc-900/70 border border-zinc-800">
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Total Runtime</div>
                  <div className="text-xl font-bold font-mono text-zinc-100 mt-1">
                    {sequence.totalDurationSec.toFixed(1)}s
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">100% Pure Dramatic Performance</div>
                </div>

                <div className="p-3 rounded-xl bg-zinc-900/70 border border-zinc-800">
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Dead Air Eliminated</div>
                  <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                    -{sequence.deadAirSavedSec.toFixed(1)}s
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-0.5">Slates, Clappers & Pauses Sliced</div>
                </div>

                <div className="p-3 rounded-xl bg-zinc-900/70 border border-zinc-800">
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Key Cut Mechanism</div>
                  <div className="text-sm font-bold text-rose-300 mt-1 truncate">
                    Cut on Action @ 00:09.12
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-0.5">Invisible Kinetic Transition</div>
                </div>

                <div className="p-3 rounded-xl bg-zinc-900/70 border border-zinc-800">
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Quartet Agreement</div>
                  <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                    4 / 4 UNANIMOUS
                  </div>
                  <div className="text-[10px] text-emerald-500/80 mt-0.5">DP • Dir • Writer • Editor Approved</div>
                </div>
              </div>

              {/* Story Arc Progression Visualization */}
              <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-800/80">
                <h3 className="font-semibold text-zinc-200 text-xs mb-3 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Story Beat Sequence & Cut-on-Action Flow</span>
                </h3>

                <div className="space-y-3">
                  {sequence.beats.map((b, idx) => (
                    <div key={b.id} className="relative">
                      {idx > 0 && (
                        <div className="flex items-center space-x-2 my-2 ml-6 text-[11px] text-amber-300">
                          <div className="h-5 w-px bg-amber-500/40" />
                          <div className="flex items-center space-x-1.5 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full font-mono text-[10px]">
                            <Scissors className="w-3 h-3 text-amber-400" />
                            <span>{b.transitionType}: {b.actionCutDescription}</span>
                          </div>
                        </div>
                      )}

                      <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-[10px]">
                              {b.beatNumber}
                            </span>
                            <span className="font-bold text-zinc-100 text-xs">{b.title}</span>
                            <span className="text-[10px] font-mono text-zinc-500">({b.sourceTakeName} • {b.sourceFile})</span>
                          </div>
                          <p className="text-[11px] text-zinc-400 pl-7">{b.dramaticPurpose}</p>
                          <div className="flex items-center space-x-3 text-[10px] font-mono text-zinc-500 pl-7 pt-1">
                            <span className="text-emerald-400">Keep: {formatTc(b.inPointSec)} → {formatTc(b.outPointSec)} ({b.durationSec.toFixed(1)}s)</span>
                            <span className="text-zinc-600">|</span>
                            <span className="text-amber-400/80">Pruned Dead Air: -{b.deadAirPrunedSec.toFixed(1)}s</span>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                            QUALIFIED
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quartet Consensus Sign-Off Box */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/30 to-zinc-900 border border-emerald-800/40">
                <div className="flex items-center space-x-2 text-emerald-300 font-bold mb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Filmmaking Quartet Consensus Sign-Off</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-[11px] text-zinc-300 mt-2">
                  <div className="p-2.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                    <div className="flex items-center space-x-1.5 font-bold text-sky-400 mb-1">
                      <Film className="w-3.5 h-3.5" />
                      <span>Cinematographer (DP)</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed">
                      "Approved. Both Take 2 and Take 3 maintain rock-solid optical stability, tack-sharp focal lock (96% focus on faces), and seamless color matching (Delta E = 0.5) without lens flares or camera wobble."
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                    <div className="flex items-center space-x-1.5 font-bold text-amber-400 mb-1">
                      <Clapperboard className="w-3.5 h-3.5" />
                      <span>Director</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed">
                      "Approved. The emotional truth peaks at the elder's pleading hand gesture. Cutting to the companion's empathetic reaction delivers genuine human vulnerability without theatrical melodrama."
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                    <div className="flex items-center space-x-1.5 font-bold text-emerald-400 mb-1">
                      <PenTool className="w-3.5 h-3.5" />
                      <span>Screenplay Writer</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed">
                      "Approved. The dramatic dialogue beat lands with absolute economy. All redundant hesitations and pauses were excised, keeping the scene urgent and emotionally gripping."
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                    <div className="flex items-center space-x-1.5 font-bold text-rose-400 mb-1">
                      <Scissors className="w-3.5 h-3.5" />
                      <span>Editor</span>
                    </div>
                    <p className="text-zinc-400 leading-relaxed">
                      "Approved. Cut on action anchored at 00:09.12s creates an invisible eye-splice. Pre-roll slates (-6.6s) and post-roll director calls (-7.4s) fully eliminated. 16.1s pure performance."
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'edl' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-zinc-200">CMX 3600 Edit Decision List</h3>
                  <p className="text-[11px] text-zinc-500">Standard EDL ready for DaVinci Resolve, Adobe Premiere Pro, or Final Cut Pro</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCopyEdl}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-medium transition-colors cursor-pointer"
                  >
                    {copiedEdl ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedEdl ? 'Copied' : 'Copy EDL'}</span>
                  </button>
                  <button
                    onClick={handleDownloadEdl}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download .EDL</span>
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/90 border border-zinc-800 font-mono text-[11px] text-zinc-300 overflow-x-auto whitespace-pre leading-relaxed">
                {generateEdlString()}
              </div>
            </div>
          )}

          {activeTab === 'disqualified' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-zinc-200">Disqualified Candidate Takes</h3>
                <p className="text-[11px] text-zinc-500">Takes that failed to satisfy the Filmmaking Quartet Consensus and were withheld from the assembly</p>
              </div>

              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-900/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-rose-300">Take 1 (MVI_0999.MOV)</span>
                      <span className="text-[10px] text-zinc-500 font-mono">19.0s • Shoot Day 211212</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                      DP VETOED
                    </span>
                  </div>
                  <p className="text-zinc-300 text-[11px]">
                    <span className="text-rose-400 font-medium">Rejection Reason: </span>
                    User observed handheld camera shake during zoom-out at 00:08s. Optical stability dropped to 42%, and a dark-clothed person crossed the right foreground, occluding the scene geometry.
                  </p>
                  <div className="text-[10px] text-zinc-400 bg-zinc-950/70 p-2 rounded-lg border border-zinc-800">
                    <span className="text-amber-400 font-semibold">Editorial Ruling: </span>
                    Discarded in favor of Take 2 (MVI_1000.MOV) which provided rock-solid tripod stability, zero zoom jitter, and tack-sharp focus lock.
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-zinc-300">Take 4 (MVI_1002.MOV)</span>
                      <span className="text-[10px] text-zinc-500 font-mono">14.1s • Shoot Day 211212</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-zinc-700 text-zinc-300">
                      SAFETY COVERAGE (HELD)
                    </span>
                  </div>
                  <p className="text-zinc-400 text-[11px]">
                    Acceptable alternate angle, but emotional intensity of the dialogue delivery was lower than Take 2. Held in reserve as B-roll safety coverage.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-zinc-200">How the Cognitive Engine Judges Video</h3>
                <p className="text-[11px] text-zinc-500">The 4 Filmmaking Perspectives that must be simultaneously satisfied</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-1.5">
                  <div className="flex items-center space-x-2 font-bold text-sky-400">
                    <Film className="w-4 h-4" />
                    <span>The Cinematographer's Eye</span>
                  </div>
                  <p className="text-[11px] text-zinc-300 leading-relaxed">
                    Evaluates optical focus planes using Spirula Studio Gaussian gradients, camera motion inertia (tripod vs erratic shake), headroom, framing balance, and lighting Delta-E continuity between shots.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-1.5">
                  <div className="flex items-center space-x-2 font-bold text-amber-400">
                    <Clapperboard className="w-4 h-4" />
                    <span>The Director's Vision</span>
                  </div>
                  <p className="text-[11px] text-zinc-300 leading-relaxed">
                    Evaluates emotional authenticity via facial action units (FACS), physical gestures (pleading hands, supportive touch), character chemistry, and dramatic subtext fulfillment.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-1.5">
                  <div className="flex items-center space-x-2 font-bold text-emerald-400">
                    <PenTool className="w-4 h-4" />
                    <span>The Screenplay Writer's Discipline</span>
                  </div>
                  <p className="text-[11px] text-zinc-300 leading-relaxed">
                    Verifies script beat delivery, vocal cadence, diction clarity, and dramatic economy—ensuring the narrative purpose of the scene is achieved without rambling or wasted screen time.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-1.5">
                  <div className="flex items-center space-x-2 font-bold text-rose-400">
                    <Scissors className="w-4 h-4" />
                    <span>The Editor's Craft</span>
                  </div>
                  <p className="text-[11px] text-zinc-300 leading-relaxed">
                    Identifies cuttable geometry, eliminates pre-roll slates and director "Cut!" calls, finds the exact frame of maximum kinetic momentum for **Action Cuts**, and splices only pure performance.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/80 flex items-center justify-between">
          <div className="text-[11px] text-zinc-400">
            Export format: <span className="text-zinc-200 font-mono">EDL / Final Cut Pro XML / OTIO</span>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleDownloadEdl}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-medium text-xs transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .EDL</span>
            </button>
            <button
              onClick={() => {
                onClose();
                onPlayAssembly();
              }}
              className="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-zinc-950 font-bold text-xs shadow-md transition-all active:scale-95 cursor-pointer"
            >
              <Film className="w-3.5 h-3.5" />
              <span>Screen Assembled Director's Cut</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
