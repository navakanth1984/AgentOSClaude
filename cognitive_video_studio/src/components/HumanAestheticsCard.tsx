import React, { useState } from 'react';
import { 
  Sparkles, 
  Award, 
  Eye, 
  Layers, 
  Sun, 
  Smile, 
  Scissors, 
  CheckCircle2, 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp,
  Sliders,
  Maximize2
} from 'lucide-react';
import { Take } from '../types/studio';

interface HumanAestheticsCardProps {
  take: Take;
  onOpenInspector?: (take: Take) => void;
}

export const HumanAestheticsCard: React.FC<HumanAestheticsCardProps> = ({
  take,
  onOpenInspector
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showComparison, setShowComparison] = useState(false);

  const aesthetics = take.aesthetics;
  if (!aesthetics) return null;

  const isHeroTake = aesthetics.verdict === 'Circle Take (Hero Shot)';

  return (
    <div className={`rounded-xl border transition-all overflow-hidden ${
      isHeroTake 
        ? 'border-amber-500/60 bg-gradient-to-b from-amber-950/40 via-zinc-900 to-zinc-950 shadow-xl shadow-amber-950/20' 
        : 'border-zinc-800 bg-zinc-900/60'
    }`}>
      {/* Header Banner */}
      <div 
        className="p-3.5 flex items-center justify-between cursor-pointer select-none border-b border-zinc-800/80"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2.5">
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shadow-md ${
            isHeroTake
              ? 'bg-gradient-to-tr from-amber-500 to-rose-600 text-zinc-950 shadow-amber-950/40'
              : 'bg-zinc-800 text-zinc-400'
          }`}>
            <Award className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-zinc-100 text-xs">Human Cinematic Aesthetics</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide uppercase ${
                isHeroTake
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
              }`}>
                {aesthetics.verdict}
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Why professional Directors, DPs & Editors judge this clip as looking great
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <div className="text-right">
            <div className="font-mono font-extrabold text-sm text-amber-400">
              {aesthetics.overallGreatnessScore}<span className="text-[10px] text-zinc-500">/100</span>
            </div>
            <div className="text-[9px] text-zinc-400 uppercase tracking-wider font-semibold">Greatness Index</div>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="p-3.5 space-y-3.5 text-xs">
          {/* Director & DP Quote Callout */}
          <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-200/90 text-[11px] italic leading-relaxed flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-amber-300 not-italic">Director & DP Consensus: </span>
              "{aesthetics.humanDirectorQuote}"
            </div>
          </div>

          {/* 5-Dimensional Human Aesthetic Scorecard */}
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            {/* 1. Composition & Framing */}
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1.5">
              <div className="flex items-center justify-between text-zinc-300 font-semibold">
                <span className="flex items-center space-x-1">
                  <Eye className="w-3.5 h-3.5 text-amber-400" />
                  <span>Rule of Thirds & Eyeline</span>
                </span>
                <span className="font-mono text-amber-400 font-bold">{aesthetics.compositionRuleOfThirds.score}%</span>
              </div>
              <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-amber-400 h-full rounded-full transition-all" 
                  style={{ width: `${aesthetics.compositionRuleOfThirds.score}%` }} 
                />
              </div>
              <p className="text-[10px] text-zinc-400 line-clamp-2 leading-tight">
                {aesthetics.compositionRuleOfThirds.naturalFraming}
              </p>
            </div>

            {/* 2. Visual Depth & Separation */}
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1.5">
              <div className="flex items-center justify-between text-zinc-300 font-semibold">
                <span className="flex items-center space-x-1">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Depth Layering (FG/MG/BG)</span>
                </span>
                <span className="font-mono text-emerald-400 font-bold">{aesthetics.depthAndSeparation.score}%</span>
              </div>
              <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-emerald-400 h-full rounded-full transition-all" 
                  style={{ width: `${aesthetics.depthAndSeparation.score}%` }} 
                />
              </div>
              <p className="text-[10px] text-zinc-400 line-clamp-2 leading-tight">
                FG chair silhouette → Tack-sharp subject → Soft background falloff.
              </p>
            </div>

            {/* 3. Lighting & Catchlight */}
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1.5">
              <div className="flex items-center justify-between text-zinc-300 font-semibold">
                <span className="flex items-center space-x-1">
                  <Sun className="w-3.5 h-3.5 text-sky-400" />
                  <span>Lighting & Catchlight</span>
                </span>
                <span className="font-mono text-sky-400 font-bold">{aesthetics.lightingAndMood.score}%</span>
              </div>
              <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-sky-400 h-full rounded-full transition-all" 
                  style={{ width: `${aesthetics.lightingAndMood.score}%` }} 
                />
              </div>
              <p className="text-[10px] text-zinc-400 line-clamp-2 leading-tight">
                {aesthetics.lightingAndMood.keyToFillRatio} • {aesthetics.lightingAndMood.catchlightDescription}
              </p>
            </div>

            {/* 4. Acting & Emotional Truth */}
            <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 space-y-1.5">
              <div className="flex items-center justify-between text-zinc-300 font-semibold">
                <span className="flex items-center space-x-1">
                  <Smile className="w-3.5 h-3.5 text-rose-400" />
                  <span>Performance Authenticity</span>
                </span>
                <span className="font-mono text-rose-400 font-bold">{aesthetics.performanceAuthenticity.score}%</span>
              </div>
              <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-rose-400 h-full rounded-full transition-all" 
                  style={{ width: `${aesthetics.performanceAuthenticity.score}%` }} 
                />
              </div>
              <p className="text-[10px] text-zinc-400 line-clamp-2 leading-tight">
                {aesthetics.performanceAuthenticity.deliveryNaturalism}
              </p>
            </div>
          </div>

          {/* Why Human Film Professionals Love This Clip */}
          <div className="space-y-1.5">
            <h4 className="text-[11px] font-bold text-zinc-200 flex items-center space-x-1.5">
              <span>Why This Clip Looks Great in Scene Context:</span>
            </h4>
            <div className="space-y-1">
              {aesthetics.whyHumanJudgesLoveThis.map((point, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-[10.5px] text-zinc-300 bg-zinc-900/60 p-2 rounded-lg border border-zinc-800/80">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{point}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Toggle Flawed vs Winner Comparison */}
          <div className="pt-2 border-t border-zinc-800/80 flex items-center justify-between">
            <button
              onClick={() => setShowComparison(!showComparison)}
              className="text-[10px] font-mono text-amber-400 hover:text-amber-300 flex items-center space-x-1 cursor-pointer"
            >
              <Sliders className="w-3 h-3" />
              <span>{showComparison ? 'Hide Take Comparison' : 'Compare: Why Take 2 Beats Take 1'}</span>
            </button>

            {onOpenInspector && (
              <button
                onClick={() => onOpenInspector(take)}
                className="text-[10px] text-zinc-400 hover:text-zinc-200 flex items-center space-x-1 cursor-pointer font-medium"
              >
                <Maximize2 className="w-3 h-3 text-amber-400" />
                <span>Deep Optical Inspection</span>
              </button>
            )}
          </div>

          {showComparison && (
            <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800 space-y-2 text-[10.5px]">
              <div className="font-bold text-zinc-200 text-[11px]">Human Diagnostic Comparison: Take 1 vs Take 2</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2 rounded bg-rose-950/20 border border-rose-900/40 space-y-1">
                  <div className="font-bold text-rose-400 flex items-center space-x-1">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Take 1 (Rejected)</span>
                  </div>
                  <ul className="text-zinc-400 list-disc list-inside space-y-0.5 text-[10px]">
                    <li>Wobbly handheld zoom-out at 00:08s</li>
                    <li>Missed focal mark on eyes (soft focus 72%)</li>
                    <li>Actor broke eyeline looking toward crew</li>
                    <li>Dead eyes: No specular catchlight reflected</li>
                  </ul>
                </div>
                <div className="p-2 rounded bg-emerald-950/20 border border-emerald-900/40 space-y-1">
                  <div className="font-bold text-emerald-400 flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Take 2 (Circle Take ⭐)</span>
                  </div>
                  <ul className="text-zinc-300 list-disc list-inside space-y-0.5 text-[10px]">
                    <li>Rock-solid tripod through foreground chairs</li>
                    <li>Tack-sharp eye focus (96% sharpness)</li>
                    <li>Locked 35° eyeline matching reverse angle</li>
                    <li>Specular daylight catchlight in both pupils</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
