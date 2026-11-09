import React, { useState } from 'react';
import { 
  X, 
  BookOpen, 
  Sparkles, 
  Users, 
  Compass, 
  Film, 
  Edit3, 
  Check, 
  Layers, 
  Cpu, 
  Share2, 
  AlertCircle,
  HelpCircle
} from 'lucide-react';
import { MacroStoryContext } from '../types/studio';

interface StoryContextModalProps {
  isOpen: boolean;
  onClose: () => void;
  storyContext: MacroStoryContext;
  onUpdateStoryContext: (updated: MacroStoryContext) => void;
}

export const StoryContextModal: React.FC<StoryContextModalProps> = ({
  isOpen,
  onClose,
  storyContext,
  onUpdateStoryContext
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [logline, setLogline] = useState(storyContext.logline);
  const [coreConflict, setCoreConflict] = useState(storyContext.coreConflict);
  const [theme, setTheme] = useState(storyContext.theme);

  if (!isOpen) return null;

  const handleSave = () => {
    onUpdateStoryContext({
      ...storyContext,
      logline,
      coreConflict,
      theme
    });
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden text-xs">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 bg-zinc-900/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-rose-950/40">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm font-bold text-zinc-100 tracking-tight">
                  Macro Story Intelligence & Narrative Bible
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  CONSOLIDATED FROM {storyContext.inferredFromTakesCount} TAKES
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Inferred from multi-clip dialogue transcripts, recurring face clusters, and visual staging
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {isEditing ? (
              <button
                onClick={handleSave}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold transition-all cursor-pointer"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save Premise</span>
              </button>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-zinc-700 font-semibold transition-all cursor-pointer"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Refine Story</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 text-zinc-300">
          {/* Story Premise & Logline Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-amber-950/40 via-zinc-900/80 to-zinc-950 border border-amber-600/40 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold uppercase text-amber-400 tracking-wider flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Consolidated Logline & Dramatic Premise</span>
              </span>
              <span className="text-[10px] font-mono text-zinc-500">
                Confidence: <span className="text-emerald-400 font-semibold">{storyContext.confidenceScore}%</span>
              </span>
            </div>

            {isEditing ? (
              <textarea
                value={logline}
                onChange={(e) => setLogline(e.target.value)}
                rows={3}
                className="w-full bg-zinc-950 border border-amber-500/50 rounded-lg p-2.5 text-xs text-zinc-100 font-sans focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            ) : (
              <p className="text-zinc-100 text-xs font-serif italic leading-relaxed pl-3 border-l-2 border-amber-500">
                "{storyContext.logline}"
              </p>
            )}

            <div className="grid grid-cols-2 gap-3 pt-2 text-[11px]">
              <div>
                <span className="text-zinc-500 font-medium">Core Conflict: </span>
                {isEditing ? (
                  <input
                    type="text"
                    value={coreConflict}
                    onChange={(e) => setCoreConflict(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-200 mt-1"
                  />
                ) : (
                  <span className="text-rose-300 font-semibold">{storyContext.coreConflict}</span>
                )}
              </div>
              <div>
                <span className="text-zinc-500 font-medium">Overarching Theme: </span>
                {isEditing ? (
                  <input
                    type="text"
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-200 mt-1"
                  />
                ) : (
                  <span className="text-amber-300 font-semibold">{storyContext.theme}</span>
                )}
              </div>
            </div>
          </div>

          {/* Inferred Character Profiles & Relationships */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-zinc-200 font-semibold">
              <Users className="w-4 h-4 text-sky-400" />
              <span>Inferred Character Dynamics & Recurring Cast</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {storyContext.characters.map((char) => (
                <div key={char.id} className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-zinc-100 text-xs">{char.name}</h4>
                      <p className="text-[10px] text-amber-300 font-medium">{char.relationship}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-zinc-800 text-zinc-300 border border-zinc-700">
                      {char.totalTakesPresent} takes present
                    </span>
                  </div>

                  <div className="space-y-1 text-[11px] text-zinc-400">
                    <div>
                      <span className="text-zinc-500">Visual Staging: </span>
                      <span className="text-zinc-300">{char.appearance}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Dramatic Need: </span>
                      <span className="text-zinc-300">{char.dramaticNeed}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Macro Acts & Scene Chronology */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-zinc-200 font-semibold">
              <Compass className="w-4 h-4 text-emerald-400" />
              <span>Narrative Arc & Take Distribution (147 Raw Takes)</span>
            </div>

            <div className="grid grid-cols-4 gap-2.5">
              {storyContext.acts.map((act) => (
                <div key={act.actNumber} className="p-3 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-amber-400 font-mono">ACT {act.actNumber}</span>
                    <span className="text-[9px] text-zinc-500 font-mono">{act.takeRange}</span>
                  </div>
                  <h5 className="font-semibold text-zinc-200 text-[11px]">{act.title}</h5>
                  <p className="text-[10px] text-zinc-400 leading-snug">{act.dramaticObjective}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Technical Architecture: Open Source Tools vs Custom Engine */}
          <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 space-y-2.5">
            <div className="flex items-center space-x-2 text-zinc-200 font-semibold">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>How This Capability Operates (Open Source Primitives vs Custom Tool)</span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-[11px]">
              <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1">
                <div className="font-bold text-sky-400">1. Dialogue & Speech</div>
                <div className="text-[10px] text-zinc-400 font-mono">faster-whisper • pyannote</div>
                <p className="text-zinc-300 text-[10px] leading-relaxed">
                  Extracts raw dialogue text, filters out director shouts ("Action!", "Cut!"), and separates Father's vocal pitch from Son's voice.
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1">
                <div className="font-bold text-amber-400">2. Actor & Scene Clustering</div>
                <div className="text-[10px] text-zinc-400 font-mono">InsightFace • SigLIP • OpenCV</div>
                <p className="text-zinc-300 text-[10px] leading-relaxed">
                  Clusters the 147 takes into persistent character identities across camera setups and recognizes foreign room props (passports, floor, chairs).
                </p>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1">
                <div className="font-bold text-emerald-400">3. Narrative Synthesizer</div>
                <div className="text-[10px] text-zinc-400 font-mono">CineAI Studio Pipeline (Custom)</div>
                <p className="text-zinc-300 text-[10px] leading-relaxed">
                  Consolidates 100+ take dossiers into one cohesive story bible, deducing the visa rejection crisis and survival quest.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 border-t border-zinc-800 bg-zinc-900/80 flex items-center justify-between">
          <span className="text-[10px] text-zinc-500">
            Dramaturgical Memory Status: <span className="text-emerald-400 font-semibold font-mono">Active (147 Takes Grounded)</span>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold transition-all cursor-pointer"
          >
            Apply to Studio View
          </button>
        </div>
      </div>
    </div>
  );
};
