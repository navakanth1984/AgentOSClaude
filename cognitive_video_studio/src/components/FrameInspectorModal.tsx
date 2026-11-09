import React from 'react';
import { X, Scan, Eye, Activity, Mic, Target, CheckCircle2, Smile } from 'lucide-react';
import { Take } from '../types/studio';

interface FrameInspectorModalProps {
  take: Take | null;
  onClose: () => void;
  timecode: string;
}

export const FrameInspectorModal: React.FC<FrameInspectorModalProps> = ({
  take,
  onClose,
  timecode
}) => {
  if (!take) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6">
      <div className="w-full max-w-4xl bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <Scan className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-zinc-100 flex items-center space-x-2">
                <span>Frame-by-Frame Cognitive Diagnostic Inspector</span>
                <span className="text-[11px] font-mono bg-zinc-800 text-amber-400 px-2 py-0.5 rounded font-normal">{timecode}</span>
              </h3>
              <p className="text-[11px] text-zinc-400">Analyzing {take.label} at frame resolution with sub-millisecond telemetry</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Top Diagnostics Overview */}
          <div className="grid grid-cols-4 gap-4">
            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80">
              <div className="flex items-center space-x-1.5 text-zinc-400 text-xs mb-1">
                <Eye className="w-3.5 h-3.5 text-emerald-400" />
                <span>Pupil Focus (Laplacian)</span>
              </div>
              <div className="text-xl font-bold font-mono text-zinc-100">
                {take.cinematography.focusSharpnessScore}%
              </div>
              <div className="text-[10px] text-emerald-400 mt-1">Tack-Sharp Core Focus</div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80">
              <div className="flex items-center space-x-1.5 text-zinc-400 text-xs mb-1">
                <Target className="w-3.5 h-3.5 text-amber-400" />
                <span>Lighting Contrast</span>
              </div>
              <div className="text-xl font-bold font-mono text-zinc-100">
                {take.cinematography.lightingRatio}
              </div>
              <div className="text-[10px] text-zinc-400 mt-1">ΔE: {take.cinematography.lightingDeltaE} (Color Match)</div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80">
              <div className="flex items-center space-x-1.5 text-zinc-400 text-xs mb-1">
                <Activity className="w-3.5 h-3.5 text-rose-400" />
                <span>Camera Dynamics</span>
              </div>
              <div className="text-sm font-bold text-zinc-100 truncate mt-1">
                {take.cinematography.cameraMotion}
              </div>
              <div className="text-[10px] text-zinc-400 mt-1">Optical Flow Vector: Steady</div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80">
              <div className="flex items-center space-x-1.5 text-zinc-400 text-xs mb-1">
                <Mic className="w-3.5 h-3.5 text-sky-400" />
                <span>Acoustic SNR</span>
              </div>
              <div className="text-xl font-bold font-mono text-zinc-100">
                {take.audio.snrDb} dB
              </div>
              <div className="text-[10px] text-sky-400 mt-1">Clarity: {take.audio.dialogueClarity}%</div>
            </div>
          </div>

          {/* Simulated Frame Visualization with Landmark Geometry */}
          <div className="relative aspect-video rounded-xl border border-zinc-800 overflow-hidden bg-gradient-to-tr from-zinc-950 via-zinc-900 to-zinc-950 flex items-center justify-center shadow-inner">
            <div className="absolute inset-0 bg-[radial-gradient(#27272a_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />
            
            {/* Synthetic Face Mesh & Feature Vectors */}
            <div className="relative w-64 h-72 border border-dashed border-amber-400/50 rounded-2xl flex flex-col items-center justify-center p-4">
              <div className="absolute top-2 left-2 text-[10px] font-mono text-amber-400 bg-black/60 px-1.5 rounded">
                FACIAL MESH #01
              </div>

              {/* Eyeline Vector */}
              <div className="w-48 h-10 border-b-2 border-emerald-400/80 flex items-center justify-between px-6 relative">
                <div className="w-5 h-5 rounded-full border-2 border-emerald-400 flex items-center justify-center animate-ping">
                  <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                </div>
                <div className="w-5 h-5 rounded-full border-2 border-emerald-400 flex items-center justify-center animate-ping">
                  <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 mt-1">Eyeline Lock: 0.2° deviation</span>

              {/* Jaw & Chin Clench Indicator */}
              <div className="mt-14 w-32 border-t-2 border-amber-400/80 flex justify-center pt-1 text-[10px] font-mono text-amber-300">
                <span>AU17 Chin Raiser Active</span>
              </div>
            </div>
          </div>

          {/* FACS Action Units & WhisperX Forced Word Alignment */}
          <div className="grid grid-cols-2 gap-6">
            {/* Left: FACS Action Unit Breakdown */}
            <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-3">
              <h4 className="font-bold text-xs text-zinc-200 flex items-center space-x-1.5">
                <Smile className="w-4 h-4 text-amber-400" />
                <span>Facial Action Coding System (FACS AUs)</span>
              </h4>

              <div className="space-y-2 text-xs">
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-zinc-300 font-medium">AU4 — Brow Lowerer / Furrow</span>
                    <span className="font-mono text-amber-400">88% Intensity</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: '88%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-zinc-300 font-medium">AU17 — Chin Raiser (Controlled Menace)</span>
                    <span className="font-mono text-amber-400">94% Intensity</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: '94%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-zinc-300 font-medium">AU24 — Lip Pressor (Suppressed Emotion)</span>
                    <span className="font-mono text-amber-400">76% Intensity</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: '76%' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Right: WhisperX Forced Phonetic Alignment */}
            <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-3">
              <h4 className="font-bold text-xs text-zinc-200 flex items-center space-x-1.5">
                <Mic className="w-4 h-4 text-sky-400" />
                <span>Word-Level Phonetic Alignment (WhisperX)</span>
              </h4>

              <div className="space-y-2">
                {[
                  { word: 'Tell', start: '00:02.12', end: '00:02.40', phonemes: 'T - EH - L' },
                  { word: 'me', start: '00:02.45', end: '00:02.68', phonemes: 'M - IY' },
                  { word: 'where', start: '00:02.72', end: '00:03.05', phonemes: 'W - EH - R' },
                  { word: 'you', start: '00:03.10', end: '00:03.35', phonemes: 'Y - UW' },
                  { word: 'hid', start: '00:03.40', end: '00:03.78', phonemes: 'HH - IH - D' },
                  { word: 'the cipher', start: '00:03.85', end: '00:04.60', phonemes: 'DH - AH | S - AY - F - ER' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-1.5 rounded bg-zinc-950/60 border border-zinc-800/60 text-xs">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-amber-300">"{item.word}"</span>
                      <span className="text-[10px] font-mono text-zinc-500">[{item.phonemes}]</span>
                    </div>
                    <span className="text-[10px] font-mono text-zinc-400">{item.start} - {item.end}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-zinc-400">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Telemetry calibrated against golden acting performance rubric</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold rounded-lg text-xs"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
