export type ProjectMode = 'live_action' | 'gen_ai_prompt';

export type AspectRatio = '16:9' | '9:16' | '1:1' | '2.39:1';

export interface PerformanceMetrics {
  detailLevel: 'Level 1 Generic' | 'Level 2 Character' | 'Level 3 Intricate';
  facsActionUnits: string[];
  emotionalRegister: string;
  eyelineStability: 'locked' | 'wavering' | 'broken';
  microActionSummary: string;
}

export interface CinematographyMetrics {
  focusSharpnessScore: number; // 0 - 100
  lightingDeltaE: number; // color difference to reverse shot, lower is better
  lightingRatio: string; // e.g. "4:1"
  cameraMotion: 'Locked Tripod' | 'Slow Dolly-In' | 'Handheld Shake' | 'Steadicam Glide';
  headroomPct: number;
}

export interface AudioMetrics {
  dialogueClarity: number; // 0 - 100
  tempoWpm: number;
  clippingDetected: boolean;
  snrDb: number;
  vocalTremorDetected: boolean;
}

export interface DetectedCharacter {
  id: string;
  name: string;
  role: string;
  box: { x: number; y: number; width: number; height: number }; // normalized 0..100%
  focusScore: number;
  eyeline: 'locked' | 'wavering' | 'broken';
  action: string;
  isOccluded?: boolean;
}

export type RoleVerdict = 'approved' | 'conditional' | 'rejected';

export interface FilmmakerScorecard {
  cinematographer: {
    verdict: RoleVerdict;
    score: number; // 0 - 100
    rationale: string;
    framingCheck: 'balanced' | 'awkward' | 'ruined';
    lightingContinuity: 'matched' | 'drift' | 'mismatched';
    opticalStability: 'locked' | 'usable' | 'shaky';
  };
  director: {
    verdict: RoleVerdict;
    score: number;
    rationale: string;
    emotionalTruth: 'authentic' | 'serviceable' | 'forced';
    subtextClarity: string;
    characterChemistry: 'strong' | 'neutral' | 'disconnected';
  };
  screenwriter: {
    verdict: RoleVerdict;
    score: number;
    rationale: string;
    beatAccomplished: boolean;
    dialogueDelivery: 'clean' | 'flubbed' | 'rushed';
    narrativeEconomy: 'tight' | 'bloated' | 'repetitive';
  };
  editor: {
    verdict: RoleVerdict;
    score: number;
    rationale: string;
    suggestedInSec: number;      // trims slate/pre-roll dead air
    suggestedOutSec: number;     // cuts tail dead air/director cut call
    actionCutAnchorSec?: number; // exact frame to cut on action (e.g. hand gesture)
    deadPausePrunedSec: number;  // total dead air trimmed
    rhythmPacing: 'punchy' | 'balanced' | 'sluggish';
  };
}

export type TakeStage = 'ingested' | 'stage_1_evaluated' | 'stage_2_trimmed' | 'stage_3_story_ready' | 'rejected';

export type StudioViewMode = 'take_inspection' | 'story_assembly';

export interface CharacterProfile {
  id: string;
  name: string;
  relationship: string;
  appearance: string;
  dramaticNeed: string;
  recurringFaceClusterId: string;
  totalTakesPresent: number;
}

export interface PentaCatalogTake {
  id: string;
  day: string;
  filename: string;
  fullPath: string;
  thumbnailUrl: string;
  videoStreamUrl: string;
  durationSec: number;
  sizeMb: number;
  resolution: string;
  role: string;
  sceneKey: string;
}

export interface PentaCatalogScene {
  title: string;
  day: string;
  location: string;
  description: string;
  takeIds: string[];
}

export interface PentaDeepCatalog {
  scanDate: string;
  totalTakes: number;
  scenes: { [key: string]: PentaCatalogScene };
  takes: PentaCatalogTake[];
}

export interface MacroStoryContext {
  title: string;
  logline: string;
  coreConflict: string;
  theme: string;
  setting: string;
  characters: CharacterProfile[];
  inferredFromTakesCount: number;
  confidenceScore: number;
  acts: {
    actNumber: number;
    title: string;
    dramaticObjective: string;
    takeRange: string;
  }[];
}

export interface StoryBeat {
  id: string;
  beatNumber: number;
  title: string;
  dramaticPurpose: string;
  takeId: string;
  sourceTakeName: string;
  sourceFile: string;
  videoStreamUrl: string;
  inPointSec: number;
  outPointSec: number;
  durationSec: number;
  transitionType: 'Cut on Action' | 'Match Eyeline' | 'L-Cut Dialogue' | 'Hard Cut';
  actionCutDescription: string;
  deadAirPrunedSec: number;
  quartetRationale: {
    dp: string;
    director: string;
    writer: string;
    editor: string;
  };
}

export interface StorySequence {
  id: string;
  sceneTitle: string;
  sceneNumber: number;
  totalDurationSec: number;
  deadAirSavedSec: number;
  beats: StoryBeat[];
}

export interface HumanAestheticsEvaluation {
  overallGreatnessScore: number; // 0 - 100
  verdict: 'Circle Take (Hero Shot)' | 'Strong Candidate' | 'Flawed / Soft Focus' | 'Camera Instability';
  compositionRuleOfThirds: {
    score: number;
    eyelineOffsetPx: number;
    headroomStatus: 'optimal' | 'excessive' | 'crowded';
    lookSpaceDirection: 'right' | 'left' | 'centered';
    naturalFraming: string;
  };
  depthAndSeparation: {
    score: number;
    planesIdentified: {
      foreground: string;
      midground: string;
      background: string;
    };
    subjectIsolationQuality: 'pristine' | 'adequate' | 'flat';
  };
  lightingAndMood: {
    score: number;
    keyToFillRatio: string;
    skinToneIre: number;
    eyeCatchlightDetected: boolean;
    catchlightDescription: string;
  };
  performanceAuthenticity: {
    score: number;
    emotionalTruth: 'authentic' | 'staged' | 'broken';
    microExpressions: string[];
    deliveryNaturalism: string;
  };
  sceneContinuityFit: {
    score: number;
    eyelineMatchDeltaDeg: number;
    lightingDeltaE: number;
    cutOnActionAnchor: string;
  };
  whyHumanJudgesLoveThis: string[];
  humanDirectorQuote: string;
}

export interface Take {
  id: string;
  takeNumber: number;
  label: string;
  durationSec: number;
  thumbnailColor: string;
  videoBlobUrl?: string;
  fileName?: string;
  confidence: number; // 0.0 - 1.0
  isAbstained: boolean;
  abstainReason?: string;
  isVetoed: boolean;
  vetoReason?: string;
  cinematography: CinematographyMetrics;
  performance: PerformanceMetrics;
  audio: AudioMetrics;
  compositeScore: number; // 0 - 100
  isRecommended: boolean;
  editorialRationale: string;
  characters?: DetectedCharacter[];
  heatmapUrl?: string;
  scorecard?: FilmmakerScorecard;
  stage?: TakeStage;
  aesthetics?: HumanAestheticsEvaluation;
}

export interface SceneShot {
  id: string;
  sceneNumber: number;
  shotNumber: string;
  title: string;
  scriptExcerpt: string;
  targetEmotion: string;
  mode: ProjectMode;
  takes: Take[];
  selectedTakeId?: string;
}

export interface TimelineClip {
  id: string;
  takeId: string;
  sceneShotId: string;
  title: string;
  trackId: string;
  startSec: number;
  durationSec: number;
  color: string;
  inPointSec: number;
  outPointSec: number;
}

export interface TimelineTrack {
  id: string;
  name: string;
  type: 'video' | 'audio';
  isMuted: boolean;
  isLocked: boolean;
  clips: TimelineClip[];
}

export interface InspectorFrameData {
  timecode: string;
  frameNumber: number;
  faceDetected: boolean;
  pupilSharpness: number;
  keyFillRatio: string;
  activeActionUnits: { au: string; name: string; intensity: number }[];
  activePhoneme: { word: string; phoneme: string; startMs: number; endMs: number };
}
