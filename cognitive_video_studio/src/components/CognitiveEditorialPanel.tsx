import React, { useRef, useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  Camera, 
  Smile, 
  Mic, 
  Award, 
  Upload, 
  Film, 
  Scissors, 
  Clapperboard, 
  PenTool, 
  Check, 
  XCircle, 
  Clock, 
  Sparkles,
  Play,
  FileText,
  ArrowRight,
  Layers,
  BookOpen
} from 'lucide-react';
import { SceneShot, Take, StorySequence, StudioViewMode, MacroStoryContext } from '../types/studio';
import { HumanAestheticsCard } from './HumanAestheticsCard';

interface CognitiveEditorialPanelProps {
  currentScene: SceneShot;
  activeTake: Take;
  onSelectTake: (take: Take) => void;
  onAssembleToTimeline: (take: Take) => void;
  onAssembleStorySequence: () => void;
  onOpenInspector: (take: Take) => void;
  onUploadTakes: (files: FileList | File[]) => void;
  onLoadPentaTakes: (day?: '211212' | '221212') => void;
  sequence?: StorySequence;
  viewMode: StudioViewMode;
  onToggleViewMode: (mode: StudioViewMode) => void;
  onOpenStoryReview: () => void;
  storyContext?: MacroStoryContext;
  onOpenStoryContext?: () => void;
  onOpenDeepCatalog?: () => void;
}

export const CognitiveEditorialPanel: React.FC<CognitiveEditorialPanelProps> = ({
  currentScene,
  activeTake,
  onSelectTake,
  onAssembleToTimeline,
  onAssembleStorySequence,
  onOpenInspector,
  onUploadTakes,
  onLoadPentaTakes,
  sequence,
  viewMode,
  onToggleViewMode,
  onOpenStoryReview,
  storyContext,
  onOpenStoryContext,
  onOpenDeepCatalog
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [expandedTakeId, setExpandedTakeId] = useState<string | null>(null);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadTakes(e.target.files);
      e.target.value = '';
    }
  };

  const isStoryReady = activeTake.stage === 'stage_3_story_ready';
  const isStoryMode = viewMode === 'story_assembly';

  return (
    <div className="w-full lg:w-[480px] xl:w-[520px] border-l border-zinc-800 bg-zinc-950 flex flex-col h-full overflow-hidden text-xs shrink-0">
      {/* Hidden File Input for uploading media files */}
      <input
        ref={fileInputRef}
        type="file"
        accept="video/*,audio/*,.mov,.mp4,.webm,.wav,.mkv"
        multiple
        onChange={handleFileInputChange}
        className="hidden"
      />

      {/* Panel Header */}
      <div className="p-3.5 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 rounded bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs">
            ★
          </div>
          <div>
            <h2 className="font-semibold text-zinc-100 text-xs tracking-tight flex items-center space-x-1.5">
              <span>Filmmaking Quartet Copilot</span>
              <span className="text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-1 rounded">Director • DP • Writer • Editor</span>
            </h2>
            <p className="text-[10px] text-zinc-400">Multi-disciplinary take qualification & smart trim gate</p>
          </div>
        </div>

        {/* Action Buttons: Upload & Assemble */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center space-x-1 px-2 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-amber-300 font-bold rounded-md border border-zinc-700 shadow-sm transition-all active:scale-95 cursor-pointer text-xs"
            title="Upload real video/audio files from your computer"
          >
            <Upload className="w-3.5 h-3.5 text-amber-400" />
            <span>Upload</span>
          </button>

          <button
            onClick={() => onAssembleToTimeline(activeTake)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 font-bold rounded-md shadow-sm transition-all active:scale-95 cursor-pointer text-xs ${
              isStoryReady
                ? 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-zinc-950'
                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700 border border-zinc-700'
            }`}
            title="Assemble active trimmed take into the timeline"
          >
            <Scissors className="w-3.5 h-3.5" />
            <span>{isStoryReady ? 'Assemble Beat' : 'Assemble (Force)'}</span>
          </button>
        </div>
      </div>

      {/* Penta Shoot Quick Ingestion Banner */}
      <div className="p-2.5 bg-gradient-to-r from-amber-950/40 via-zinc-900 to-zinc-950 border-b border-amber-900/40 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Film className="w-4 h-4 text-amber-400" />
          <div>
            <div className="font-semibold text-zinc-200 text-[11px] flex items-center space-x-1.5">
              <span>Penta Local Takes</span>
              <span className="text-[9px] bg-amber-500/20 text-amber-300 px-1 py-0.2 rounded font-mono">202 takes</span>
            </div>
            <p className="text-[10px] text-zinc-500">3 Shoot Days • Hyderabad</p>
          </div>
        </div>
        <div className="flex items-center space-x-1.5">
          {onOpenDeepCatalog && (
            <button
              onClick={onOpenDeepCatalog}
              className="px-2 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 rounded text-[10px] font-mono font-bold transition-all cursor-pointer flex items-center space-x-1"
              title="Open full 202-take coverage archive with scene filtering and B-roll inserts"
            >
              <span>Browse 202</span>
            </button>
          )}
          <button
            onClick={() => onLoadPentaTakes('211212')}
            className="px-2 py-1 bg-zinc-800 hover:bg-amber-600/30 text-amber-300 hover:text-amber-200 border border-zinc-700 hover:border-amber-500/50 rounded text-[10px] font-mono font-medium transition-all cursor-pointer"
            title="Load 65 raw camera takes from E:\Nav\Work\Penta\211212"
          >
            211212 (Day 1)
          </button>
          <button
            onClick={() => onLoadPentaTakes('221212')}
            className="px-2 py-1 bg-zinc-800 hover:bg-amber-600/30 text-amber-300 hover:text-amber-200 border border-zinc-700 hover:border-amber-500/50 rounded text-[10px] font-mono font-medium transition-all cursor-pointer"
            title="Load 82 raw camera takes from E:\Nav\Work\Penta\221212"
          >
            221212 (Day 2)
          </button>
        </div>
      </div>

      {/* Macro Story Context Ribbon */}
      {storyContext && onOpenStoryContext && (
        <div 
          onClick={onOpenStoryContext}
          className="p-2.5 bg-gradient-to-r from-indigo-950/40 via-zinc-900 to-zinc-950 border-b border-indigo-900/50 flex items-center justify-between cursor-pointer hover:bg-indigo-950/60 transition-colors"
          title="Click to inspect Macro Story Intelligence & Narrative Bible"
        >
          <div className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-indigo-400 shrink-0" />
            <div className="truncate max-w-[340px]">
              <span className="font-bold text-[11px] text-indigo-200">Story Premise: </span>
              <span className="text-[10px] text-zinc-300 italic">"{storyContext.logline}"</span>
            </div>
          </div>
          <span className="text-[9px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-1.5 py-0.5 rounded font-mono font-bold shrink-0">
            STORY BIBLE
          </span>
        </div>
      )}

      {/* Scene Context Brief */}
      <div className="p-3 border-b border-zinc-800/70 bg-zinc-900/30">
        <div className="flex items-center justify-between text-[11px] mb-1">
          <span className="font-bold text-amber-400">SCENE {currentScene.sceneNumber} • SHOT {currentScene.shotNumber}</span>
          <span className="text-zinc-500 uppercase tracking-wider text-[10px]">{currentScene.mode.replace('_', ' ')}</span>
        </div>
        <p className="text-zinc-200 font-semibold text-[11px] leading-snug mb-1">{currentScene.title}</p>
        <p className="text-zinc-400 text-[10px] italic border-l-2 border-amber-600/60 pl-2 my-1.5 line-clamp-2">
          {currentScene.scriptExcerpt}
        </p>
        <div className="text-[10px] text-zinc-500 flex items-center space-x-1 mt-1">
          <span className="text-zinc-400 font-medium">Dramatic Objective:</span>
          <span className="text-amber-300/90">{currentScene.targetEmotion}</span>
        </div>
      </div>

      {/* Scrollable Takes & Sequence Container */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3.5">
        {/* Story First Assembly Showcase Card */}
        {sequence && (
          <div className="rounded-xl border-2 border-amber-500/50 bg-gradient-to-b from-amber-950/30 via-zinc-900 to-zinc-950 p-3.5 shadow-xl shadow-amber-950/20 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-amber-500 to-rose-600 flex items-center justify-center text-zinc-950 font-bold shadow-md shadow-amber-950/40">
                  <Film className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="font-bold text-xs text-amber-200 flex items-center space-x-1.5">
                    <span>First Assembly • Director's Cut v1</span>
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                      READY
                    </span>
                  </h3>
                  <p className="text-[10px] text-zinc-400">
                    Sequenced from {sequence.beats.length} qualified takes with action-cut splicing
                  </p>
                </div>
              </div>

              <div className="text-right font-mono">
                <div className="text-xs font-bold text-emerald-400">{sequence.totalDurationSec.toFixed(1)}s Runtime</div>
                <div className="text-[9px] text-amber-400">-{sequence.deadAirSavedSec.toFixed(1)}s dead air</div>
              </div>
            </div>

            {/* Assembled Beats Progression */}
            <div className="space-y-1.5 text-[11px] font-mono bg-zinc-950/90 p-2.5 rounded-lg border border-zinc-800">
              {sequence.beats.map((b, idx) => (
                <div key={b.id} className="space-y-1">
                  {idx > 0 && (
                    <div className="flex items-center space-x-1.5 text-[9px] text-amber-400 py-0.5 pl-3 border-l-2 border-amber-500/50 my-1">
                      <Scissors className="w-3 h-3 text-amber-400 shrink-0" />
                      <span className="font-bold">{b.transitionType}: {b.actionCutDescription}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-zinc-300 pl-1">
                    <span className="flex items-center space-x-1.5">
                      <span className="w-4 h-4 rounded-full bg-zinc-800 text-zinc-300 text-[9px] flex items-center justify-center font-bold">
                        {b.beatNumber}
                      </span>
                      <span className="font-semibold text-zinc-100">{b.title}</span>
                      <span className="text-[10px] text-zinc-500">({b.sourceTakeName})</span>
                    </span>
                    <span className="text-emerald-400 font-bold text-[10px]">{b.durationSec.toFixed(1)}s</span>
                  </div>
                </div>
              ))}
            </div>

            {/* First Assembly Action Buttons */}
            <div className="grid grid-cols-3 gap-2 pt-1">
              <button
                onClick={() => onToggleViewMode('story_assembly')}
                className={`flex items-center justify-center space-x-1 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95 cursor-pointer ${
                  isStoryMode
                    ? 'bg-amber-400 text-zinc-950 shadow-md shadow-amber-950/40'
                    : 'bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-zinc-700'
                }`}
                title="Watch the edited first version continuously across all cuts"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isStoryMode ? 'Screening Now' : 'Screen Cut'}</span>
              </button>

              <button
                onClick={onOpenStoryReview}
                className="flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-medium transition-all active:scale-95 cursor-pointer"
                title="Inspect the detailed review dossier for Human Director, Writer & Editor"
              >
                <FileText className="w-3.5 h-3.5 text-amber-400" />
                <span>Review Dossier</span>
              </button>

              <button
                onClick={onAssembleStorySequence}
                className="flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-zinc-950 text-xs font-bold transition-all active:scale-95 cursor-pointer shadow-md"
                title="Populate the complete edited scene sequence onto the timeline"
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Load to Timeline</span>
              </button>
            </div>
          </div>
        )}

        {/* Human Aesthetic & Cinematic Fit Card */}
        {activeTake.aesthetics && (
          <HumanAestheticsCard take={activeTake} onOpenInspector={onOpenInspector} />
        )}

        {/* Candidate Takes Header */}
        <div className="flex items-center justify-between text-[11px] font-semibold text-zinc-400 px-1 pt-1">
          <span>CANDIDATE TAKES ({currentScene.takes.length})</span>
          <span className="text-[10px] text-zinc-500">Filmmaking Quartet Consensus</span>
        </div>

        {/* Takes Comparison List */}
        {currentScene.takes.map((take) => {
          const isSelected = activeTake.id === take.id && !isStoryMode;
          const isExpanded = expandedTakeId === take.id;
          const sc = take.scorecard;
          const isReady = take.stage === 'stage_3_story_ready';

          return (
            <div
              key={take.id}
              onClick={() => {
                if (isStoryMode) onToggleViewMode('take_inspection');
                onSelectTake(take);
              }}
              className={`rounded-xl border transition-all cursor-pointer relative overflow-hidden ${
                isSelected
                  ? 'bg-zinc-900/95 border-amber-500 shadow-xl shadow-amber-950/20 ring-1 ring-amber-500/40'
                  : 'bg-zinc-900/40 border-zinc-800/80 hover:bg-zinc-900/70 hover:border-zinc-700'
              }`}
            >
              {/* Card Header: Take Title, Duration, Stage Gate Badge */}
              <div className="p-3 pb-2 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className={`font-bold text-xs ${isSelected ? 'text-amber-300' : 'text-zinc-200'}`}>
                    {take.label}
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {take.durationSec.toFixed(1)}s
                  </span>
                  {isReady ? (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                      <Check className="w-2.5 h-2.5" />
                      <span>STORY QUALIFIED</span>
                    </span>
                  ) : take.isVetoed || take.stage === 'rejected' ? (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center space-x-1">
                      <AlertTriangle className="w-2.5 h-2.5" />
                      <span>GATE REJECTED</span>
                    </span>
                  ) : (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-zinc-700/50 text-zinc-400 border border-zinc-600/40">
                      CONDITIONAL
                    </span>
                  )}
                </div>

                {/* Score Pill */}
                <div className={`px-2 py-0.5 rounded-full font-mono text-[11px] font-bold border ${
                  take.stage === 'rejected' || take.isVetoed
                    ? 'bg-rose-950/60 text-rose-400 border-rose-800'
                    : isReady
                    ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
                    : 'bg-amber-950/60 text-amber-400 border-amber-800'
                }`}>
                  {take.compositeScore}<span className="text-[9px] text-zinc-500">/100</span>
                </div>
              </div>

              {/* The 4 Filmmaker Roles Consensus Grid */}
              {sc && (
                <div className="mx-3 my-1.5 p-2 rounded-lg bg-zinc-950/80 border border-zinc-800 space-y-1.5 text-[10px]">
                  {/* Cinematographer */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-1.5 text-zinc-400">
                      <Film className="w-3 h-3 text-sky-400 shrink-0" />
                      <span className="font-semibold text-zinc-300">Cinematographer:</span>
                      <span className="text-zinc-400 truncate max-w-[270px]">{sc.cinematographer.rationale}</span>
                    </div>
                    <span className={`px-1.5 py-0.2 rounded font-mono font-bold text-[9px] shrink-0 ml-1 ${
                      sc.cinematographer.verdict === 'approved' ? 'text-emerald-400 bg-emerald-950/40' : 'text-rose-400 bg-rose-950/40'
                    }`}>
                      {sc.cinematographer.verdict.toUpperCase()}
                    </span>
                  </div>

                  {/* Director */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-1.5 text-zinc-400">
                      <Clapperboard className="w-3 h-3 text-amber-400 shrink-0" />
                      <span className="font-semibold text-zinc-300">Director:</span>
                      <span className="text-zinc-400 truncate max-w-[270px]">{sc.director.rationale}</span>
                    </div>
                    <span className={`px-1.5 py-0.2 rounded font-mono font-bold text-[9px] shrink-0 ml-1 ${
                      sc.director.verdict === 'approved' ? 'text-emerald-400 bg-emerald-950/40' : 'text-amber-400 bg-amber-950/40'
                    }`}>
                      {sc.director.verdict.toUpperCase()}
                    </span>
                  </div>

                  {/* Screenplay Writer */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-1.5 text-zinc-400">
                      <PenTool className="w-3 h-3 text-emerald-400 shrink-0" />
                      <span className="font-semibold text-zinc-300">Writer:</span>
                      <span className="text-zinc-400 truncate max-w-[270px]">{sc.screenwriter.rationale}</span>
                    </div>
                    <span className={`px-1.5 py-0.2 rounded font-mono font-bold text-[9px] shrink-0 ml-1 ${
                      sc.screenwriter.verdict === 'approved' ? 'text-emerald-400 bg-emerald-950/40' : 'text-amber-400 bg-amber-950/40'
                    }`}>
                      {sc.screenwriter.verdict.toUpperCase()}
                    </span>
                  </div>

                  {/* Editor */}
                  <div className="flex items-start justify-between border-t border-zinc-800/80 pt-1">
                    <div className="flex items-center space-x-1.5 text-zinc-400">
                      <Scissors className="w-3 h-3 text-rose-400 shrink-0" />
                      <span className="font-semibold text-zinc-300">Editor:</span>
                      <span className="text-emerald-300 font-mono font-medium">
                        [{sc.editor.suggestedInSec}s → {sc.editor.suggestedOutSec}s] (-{sc.editor.deadPausePrunedSec.toFixed(1)}s dead air)
                      </span>
                    </div>
                    <span className={`px-1.5 py-0.2 rounded font-mono font-bold text-[9px] shrink-0 ml-1 ${
                      sc.editor.verdict === 'approved' ? 'text-emerald-400 bg-emerald-950/40' : 'text-rose-400 bg-rose-950/40'
                    }`}>
                      {sc.editor.verdict.toUpperCase()}
                    </span>
                  </div>
                </div>
              )}

              {/* Editorial Rationale Summary */}
              <div className="p-3 pt-1 text-[10px] space-y-1">
                <p className="text-zinc-300 leading-relaxed">
                  <span className="text-zinc-500 font-medium">Performance Detail: </span>
                  {take.performance.microActionSummary}
                </p>

                {/* Card Footer: Confidence & Frame Inspector Button */}
                <div className="flex items-center justify-between pt-1.5 text-[10px] border-t border-zinc-800/60">
                  <span className="text-zinc-500 font-mono">
                    Consensus Confidence: <span className="text-zinc-300 font-semibold">{Math.round(take.confidence * 100)}%</span>
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenInspector(take);
                      }}
                      className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-amber-300 transition-colors cursor-pointer"
                    >
                      Inspect Frame
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (isStoryMode) onToggleViewMode('take_inspection');
                        onSelectTake(take);
                      }}
                      className="px-2 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 transition-colors cursor-pointer font-medium"
                    >
                      Preview Take
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {/* Drag and Drop Upload Card */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
              onUploadTakes(e.dataTransfer.files);
            }
          }}
          onClick={() => fileInputRef.current?.click()}
          className="p-4 border-2 border-dashed border-amber-600/50 hover:border-amber-400 rounded-xl bg-amber-950/10 hover:bg-amber-950/20 flex flex-col items-center justify-center text-center cursor-pointer transition-all group shadow-inner"
        >
          <div className="w-10 h-10 rounded-full bg-amber-500/20 group-hover:bg-amber-500/30 flex items-center justify-center text-amber-300 mb-2 transition-colors">
            <Upload className="w-5 h-5" />
          </div>
          <span className="text-amber-200 font-bold text-xs group-hover:text-amber-100 transition-colors">
            + Click to Upload Local Video / Audio Takes
          </span>
          <span className="text-[10px] text-zinc-400 mt-1 max-w-xs">
            Drag & drop or click to import local MP4, MOV, WebM, WAV takes from your computer
          </span>
        </div>
      </div>
    </div>
  );
};
