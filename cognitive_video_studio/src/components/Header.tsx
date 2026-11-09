import React, { useState } from 'react';
import { 
  Clapperboard, 
  Sparkles, 
  Cloud, 
  Cpu, 
  Share2, 
  Ratio, 
  Upload, 
  FolderOpen, 
  Film, 
  BookOpen,
  Menu,
  X
} from 'lucide-react';
import { ProjectMode, AspectRatio } from '../types/studio';

interface HeaderProps {
  mode: ProjectMode;
  onModeChange: (mode: ProjectMode) => void;
  aspectRatio: AspectRatio;
  onAspectRatioChange: (ratio: AspectRatio) => void;
  timecode: string;
  onOpenExport: () => void;
  onTriggerUpload: () => void;
  onLoadPentaTakes: (day?: '211212' | '221212') => void;
  onOpenStoryReview?: () => void;
  onOpenStoryContext?: () => void;
  onOpenDeepCatalog?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  onModeChange,
  aspectRatio,
  onAspectRatioChange,
  timecode,
  onOpenExport,
  onTriggerUpload,
  onLoadPentaTakes,
  onOpenStoryReview,
  onOpenStoryContext,
  onOpenDeepCatalog
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="h-14 border-b border-zinc-800 bg-zinc-950 px-3 md:px-4 flex items-center justify-between z-30 select-none relative">
      {/* Brand & Desktop Mode Toggle */}
      <div className="flex items-center space-x-3 md:space-x-5">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-rose-950/40 shrink-0">
            <Clapperboard className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-bold text-sm tracking-tight text-zinc-100">CINE<span className="text-amber-400">AI</span></span>
              <span className="hidden sm:inline text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded font-mono font-medium">v1.0</span>
            </div>
            <p className="hidden sm:block text-[9px] text-zinc-500 -mt-0.5">Editorial Engine</p>
          </div>
        </div>

        {/* Desktop Project Mode Toggle */}
        <div className="hidden xl:flex items-center bg-zinc-900 border border-zinc-800 p-0.5 rounded-lg text-xs">
          <button
            onClick={() => onModeChange('live_action')}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all font-medium cursor-pointer ${
              mode === 'live_action'
                ? 'bg-zinc-800 text-amber-300 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Clapperboard className="w-3.5 h-3.5" />
            <span>Live Action Takes</span>
          </button>
          <button
            onClick={() => onModeChange('gen_ai_prompt')}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all font-medium cursor-pointer ${
              mode === 'gen_ai_prompt'
                ? 'bg-zinc-800 text-indigo-300 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Gen-AI Variants</span>
          </button>
        </div>

        {/* Quick Penta Shoot Loader in Header */}
        <div className="hidden 2xl:flex items-center space-x-1.5 bg-amber-950/30 border border-amber-600/40 px-2.5 py-1 rounded-lg">
          <Film className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          <span className="text-[11px] font-semibold text-amber-300">Penta Takes:</span>
          <button
            onClick={() => onLoadPentaTakes('211212')}
            className="px-2 py-0.5 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 rounded text-[10px] font-mono font-semibold transition-colors cursor-pointer"
            title="Load 65 takes from E:\Nav\Work\Penta\211212"
          >
            Day 211212
          </button>
          <button
            onClick={() => onLoadPentaTakes('221212')}
            className="px-2 py-0.5 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 rounded text-[10px] font-mono font-semibold transition-colors cursor-pointer"
            title="Load 82 takes from E:\Nav\Work\Penta\221212"
          >
            Day 221212
          </button>
        </div>
      </div>

      {/* Center: Timecode & Aspect Ratio */}
      <div className="flex items-center space-x-2 md:space-x-3">
        <div className="bg-zinc-900 border border-zinc-800 px-2.5 md:px-3.5 py-1 rounded-lg font-mono text-xs md:text-sm tracking-wider text-amber-400 font-semibold shadow-inner">
          {timecode}
        </div>
        
        {/* Desktop Aspect Ratio Selector */}
        <div className="hidden sm:flex items-center space-x-1 bg-zinc-900 border border-zinc-800 p-0.5 rounded-lg text-xs">
          <div className="px-1.5 py-0.5 text-zinc-500 flex items-center space-x-1">
            <Ratio className="w-3 h-3" />
          </div>
          {(['16:9', '9:16', '1:1', '2.39:1'] as AspectRatio[]).map((r) => (
            <button
              key={r}
              onClick={() => onAspectRatioChange(r)}
              className={`px-1.5 md:px-2 py-0.5 rounded text-[10px] md:text-[11px] font-mono transition-colors cursor-pointer ${
                aspectRatio === r
                  ? 'bg-zinc-800 text-zinc-100 font-semibold'
                  : 'text-zinc-400 hover:text-zinc-300'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Right: Desktop Action Buttons */}
      <div className="hidden lg:flex items-center space-x-2 md:space-x-2.5 text-xs">
        {/* Zoho Catalyst Sync Pill */}
        <div className="hidden 2xl:flex items-center space-x-1 px-2 py-1 rounded-md bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 text-[10px]" title="Connected to Zoho Catalyst BaaS">
          <Cloud className="w-3 h-3 text-emerald-400 animate-pulse" />
          <span className="font-medium">Catalyst</span>
        </div>

        {/* Upload Take Button */}
        <button
          onClick={onTriggerUpload}
          className="flex items-center space-x-1 px-2.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 rounded-lg text-xs transition-colors"
          title="Upload video or audio takes (MP4, MOV, WAV)"
        >
          <Upload className="w-3.5 h-3.5 text-amber-400" />
          <span>Upload</span>
        </button>

        {/* Story Context / Narrative Bible Button */}
        {onOpenStoryContext && (
          <button
            onClick={onOpenStoryContext}
            className="flex items-center space-x-1 px-2.5 py-1.5 bg-indigo-950/40 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 font-medium rounded-lg text-xs transition-all"
            title="Inspect Macro Story Intelligence"
          >
            <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
            <span>Story Bible</span>
          </button>
        )}

        {/* Deep 202-Take Catalog Explorer Button */}
        {onOpenDeepCatalog && (
          <button
            onClick={onOpenDeepCatalog}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-amber-950/60 via-zinc-900 to-zinc-900 hover:from-amber-900/70 text-amber-300 border border-amber-500/40 font-bold rounded-lg shadow-sm transition-all text-xs cursor-pointer active:scale-95"
            title="Browse all 202 camera takes from Penta shoot"
          >
            <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>202 Takes</span>
          </button>
        )}

        {/* First Assembly Review Dossier Button */}
        {onOpenStoryReview && (
          <button
            onClick={onOpenStoryReview}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-zinc-700 font-semibold rounded-lg shadow-sm transition-all text-xs active:scale-95 cursor-pointer"
            title="Open First Assembly Dossier"
          >
            <Film className="w-3.5 h-3.5 text-amber-400" />
            <span>Review</span>
          </button>
        )}

        {/* Export / Assemble Button */}
        <button
          onClick={onOpenExport}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-zinc-950 font-bold rounded-lg shadow-md transition-all text-xs active:scale-95 cursor-pointer"
        >
          <Share2 className="w-3.5 h-3.5" />
          <span>Export</span>
        </button>
      </div>

      {/* Mobile Menu Hamburger Button (Min 44x44px Touch Target) */}
      <div className="flex lg:hidden items-center space-x-2">
        <button
          onClick={() => setIsMobileMenuOpen((o) => !o)}
          className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-200 hover:text-white hover:bg-zinc-800 active:scale-95 transition-all cursor-pointer"
          aria-label="Open Mobile Studio Menu"
        >
          {isMobileMenuOpen ? <X className="w-5 h-5 text-amber-400" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Slide-Down Quick Actions Drawer */}
      {isMobileMenuOpen && (
        <div className="lg:hidden absolute top-14 left-0 right-0 bg-zinc-950/95 border-b border-zinc-800 backdrop-blur-xl p-4 shadow-2xl z-50 flex flex-col space-y-3.5 animate-in slide-in-from-top-2 duration-150">
          {/* Mobile Mode Switcher */}
          <div className="grid grid-cols-2 gap-2 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
            <button
              onClick={() => {
                onModeChange('live_action');
                setIsMobileMenuOpen(false);
              }}
              className={`min-h-[44px] rounded-lg font-bold text-xs flex items-center justify-center space-x-1.5 ${
                mode === 'live_action'
                  ? 'bg-amber-500 text-zinc-950 shadow'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Clapperboard className="w-4 h-4" />
              <span>Live Action</span>
            </button>
            <button
              onClick={() => {
                onModeChange('gen_ai_prompt');
                setIsMobileMenuOpen(false);
              }}
              className={`min-h-[44px] rounded-lg font-bold text-xs flex items-center justify-center space-x-1.5 ${
                mode === 'gen_ai_prompt'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Gen-AI Variants</span>
            </button>
          </div>

          {/* Mobile Aspect Ratio Selector */}
          <div>
            <span className="text-[10px] font-mono text-zinc-500 mb-1.5 block">ASPECT RATIO</span>
            <div className="grid grid-cols-4 gap-2">
              {(['16:9', '9:16', '1:1', '2.39:1'] as AspectRatio[]).map((r) => (
                <button
                  key={r}
                  onClick={() => {
                    onAspectRatioChange(r);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`min-h-[44px] rounded-lg text-xs font-mono font-bold border flex items-center justify-center ${
                    aspectRatio === r
                      ? 'bg-zinc-800 border-amber-400 text-amber-300'
                      : 'bg-zinc-900 border-zinc-800 text-zinc-400'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Primary Quick Actions (Thumb-Friendly >= 44px Height) */}
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-zinc-900">
            {onOpenDeepCatalog && (
              <button
                onClick={() => {
                  onOpenDeepCatalog();
                  setIsMobileMenuOpen(false);
                }}
                className="min-h-[44px] px-3 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 active:scale-95 transition-all"
              >
                <FolderOpen className="w-4 h-4" />
                <span>202 Shoot Takes</span>
              </button>
            )}

            {onOpenStoryContext && (
              <button
                onClick={() => {
                  onOpenStoryContext();
                  setIsMobileMenuOpen(false);
                }}
                className="min-h-[44px] px-3 bg-indigo-950/60 text-indigo-300 border border-indigo-700/50 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 active:scale-95 transition-all"
              >
                <BookOpen className="w-4 h-4" />
                <span>Story Bible</span>
              </button>
            )}

            {onOpenStoryReview && (
              <button
                onClick={() => {
                  onOpenStoryReview();
                  setIsMobileMenuOpen(false);
                }}
                className="min-h-[44px] px-3 bg-zinc-900 text-zinc-200 border border-zinc-800 rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 active:scale-95 transition-all"
              >
                <Film className="w-4 h-4 text-amber-400" />
                <span>Review Dossier</span>
              </button>
            )}

            <button
              onClick={() => {
                onTriggerUpload();
                setIsMobileMenuOpen(false);
              }}
              className="min-h-[44px] px-3 bg-zinc-900 text-zinc-200 border border-zinc-800 rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 active:scale-95 transition-all"
            >
              <Upload className="w-4 h-4 text-amber-400" />
              <span>Upload File</span>
            </button>
          </div>

          {/* Export Action */}
          <button
            onClick={() => {
              onOpenExport();
              setIsMobileMenuOpen(false);
            }}
            className="min-h-[48px] w-full bg-gradient-to-r from-amber-500 to-rose-600 text-zinc-950 font-bold rounded-xl text-sm flex items-center justify-center space-x-2 shadow-lg active:scale-95 transition-all"
          >
            <Share2 className="w-4 h-4" />
            <span>Export Final Timeline (EDL)</span>
          </button>
        </div>
      )}
    </header>
  );
};
