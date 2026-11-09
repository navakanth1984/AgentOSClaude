import { SceneShot } from '../types/studio';

export const MOCK_SCENES: SceneShot[] = [
  {
    id: 'scene_04_shot_2b',
    sceneNumber: 4,
    shotNumber: '2B',
    title: 'Interrogation Table — Lead Detective Close-Up',
    scriptExcerpt: 'DETECTIVE VANCE (leaning in): "Tell me where you hid the cipher, or we both drown in this room."',
    targetEmotion: 'Cold, restrained menace with subtle vulnerability',
    mode: 'live_action',
    selectedTakeId: 'take_02',
    takes: [
      {
        id: 'take_01',
        takeNumber: 1,
        label: 'Take 1 (Safety Master)',
        durationSec: 14.2,
        thumbnailColor: 'from-amber-950 to-zinc-900',
        confidence: 0.88,
        isAbstained: false,
        isVetoed: false,
        cinematography: {
          focusSharpnessScore: 72,
          lightingDeltaE: 2.1,
          lightingRatio: '3:1',
          cameraMotion: 'Locked Tripod',
          headroomPct: 15.2
        },
        performance: {
          detailLevel: 'Level 2 Character',
          facsActionUnits: ['AU4 Brow Furrow'],
          emotionalRegister: 'Aggressive vocal projection, but facial posture remained static.',
          eyelineStability: 'wavering',
          microActionSummary: 'Actor wavered eyeline toward boom mic at 00:04.1; generic anger delivery.'
        },
        audio: {
          dialogueClarity: 92,
          tempoWpm: 145,
          clippingDetected: false,
          snrDb: 28,
          vocalTremorDetected: false
        },
        compositeScore: 68,
        isRecommended: false,
        editorialRationale: 'Serviceable performance, but missed focus mark on eyes (soft focus 72%) and actor broke character eyeline.',
        aesthetics: {
          overallGreatnessScore: 64,
          verdict: 'Flawed / Soft Focus',
          compositionRuleOfThirds: {
            score: 62,
            eyelineOffsetPx: 38,
            headroomStatus: 'excessive',
            lookSpaceDirection: 'centered',
            naturalFraming: 'Operator zoomed out erratically at 00:08s, breaking thirds alignment and introducing motion blur.'
          },
          depthAndSeparation: {
            score: 68,
            planesIdentified: {
              foreground: 'Crowded frame edge',
              midground: 'Seated actor (soft focus 72%)',
              background: 'Flat wall reflection'
            },
            subjectIsolationQuality: 'adequate'
          },
          lightingAndMood: {
            score: 70,
            keyToFillRatio: '2.8:1 (Flatter contrast)',
            skinToneIre: 58,
            eyeCatchlightDetected: false,
            catchlightDescription: 'Missed specular daylight window reflection; eyes appear flat and shadowed.'
          },
          performanceAuthenticity: {
            score: 65,
            emotionalTruth: 'staged',
            microExpressions: ['generic frown'],
            deliveryNaturalism: 'Actor hesitated and glanced toward camera operator during zoom jitter.'
          },
          sceneContinuityFit: {
            score: 55,
            eyelineMatchDeltaDeg: 8.4,
            lightingDeltaE: 2.1,
            cutOnActionAnchor: 'No clean kinetic anchor; hand movement was hesitant and stopped prematurely.'
          },
          whyHumanJudgesLoveThis: [
            'Camera wobbly zoom-out at 00:08s introduces distracting handheld jitter.',
            'Missed focal plane on eyes (soft focus 72% vs 97% in Take 2).',
            'Actor eyeline broke toward crew during the reframing.',
            'Lacks the organic foreground framing that made Take 2 so visually striking.'
          ],
          humanDirectorQuote: 'Good rehearsal energy, but the camera zoom-out wobble and soft focus mark make this unusable as a master.'
        }
      },
      {
        id: 'take_02',
        takeNumber: 2,
        label: 'Take 2 (Director Selected)',
        durationSec: 15.0,
        thumbnailColor: 'from-emerald-950 to-zinc-900',
        confidence: 0.96,
        isAbstained: false,
        isVetoed: false,
        cinematography: {
          focusSharpnessScore: 97,
          lightingDeltaE: 0.4,
          lightingRatio: '4.2:1',
          cameraMotion: 'Slow Dolly-In',
          headroomPct: 10.4
        },
        performance: {
          detailLevel: 'Level 3 Intricate',
          facsActionUnits: ['AU4 Brow Furrow', 'AU17 Chin Raiser', 'AU24 Lip Pressor'],
          emotionalRegister: 'Controlled sub-vocal menace; jaw tightens before voice drops.',
          eyelineStability: 'locked',
          microActionSummary: 'Level 3 intricate detail at 00:04.2: delayed swallow, jaw clench, gaze unblinking on suspect.'
        },
        audio: {
          dialogueClarity: 99,
          tempoWpm: 128,
          clippingDetected: false,
          snrDb: 34,
          vocalTremorDetected: true
        },
        compositeScore: 95,
        isRecommended: true,
        editorialRationale: 'Outstanding aesthetic & acting parity. Tack-sharp focus (97%), seamless lighting match to reverse angle (ΔE 0.4), and authentic Level 3 emotional physics.',
        aesthetics: {
          overallGreatnessScore: 97,
          verdict: 'Circle Take (Hero Shot)',
          compositionRuleOfThirds: {
            score: 96,
            eyelineOffsetPx: 4,
            headroomStatus: 'optimal',
            lookSpaceDirection: 'right',
            naturalFraming: 'Low-angle perspective shooting through foreground fallen chairs creates organic geometric framing that heightens vulnerability.'
          },
          depthAndSeparation: {
            score: 95,
            planesIdentified: {
              foreground: 'Overturned green chair silhouette (soft foreground anchor)',
              midground: 'Seated elder & companion (tack-sharp focal plane 97%)',
              background: 'Suburban living room shelves and door (pleasing optical falloff)'
            },
            subjectIsolationQuality: 'pristine'
          },
          lightingAndMood: {
            score: 95,
            keyToFillRatio: '4.2:1 (Dramatic Chiaroscuro)',
            skinToneIre: 68,
            eyeCatchlightDetected: true,
            catchlightDescription: 'Natural directional daylight reflects specular catchlight in both pupils, giving an urgent, alive, pleading gaze.'
          },
          performanceAuthenticity: {
            score: 98,
            emotionalTruth: 'authentic',
            microExpressions: ['AU4 brow lowerer', 'AU24 lip pressor', 'organic involuntary hand tremor'],
            deliveryNaturalism: 'Elder actor pauses organically before raising hands; companion reaches out on the exact emotional crest.'
          },
          sceneContinuityFit: {
            score: 96,
            eyelineMatchDeltaDeg: 1.2,
            lightingDeltaE: 0.4,
            cutOnActionAnchor: 'Hand gesture reaches apex extension at 00:09.12s, creating seamless cut-on-action into companion reverse shot.'
          },
          whyHumanJudgesLoveThis: [
            'Natural Foreground Framing: Low tripod perspective past overturned chairs creates cinematic spatial depth, avoiding flat television staging.',
            'Three-Dimensional Depth Pop: Clear separation across foreground silhouette, tack-sharp subjects, and soft background falloff.',
            'Living Eye Catchlights: Window daylight reflects crisp specular highlights in the elder\'s eyes, conveying raw vulnerability without artificial fill glare.',
            'Textbook Cut-on-Action Anchor: The pleading hand gesture reaches peak kinetic extension at 00:09.12s, enabling an invisible match cut into Take 3.'
          ],
          humanDirectorQuote: 'The composition breathes like high cinema: the overturned chair frames his helplessness, the window catchlight makes his eyes teary and alive, and the hand rise gives us an unmissable cut on action.'
        }
      },
      {
        id: 'take_03',
        takeNumber: 3,
        label: 'Take 3 (High Energy)',
        durationSec: 13.8,
        thumbnailColor: 'from-rose-950 to-zinc-900',
        confidence: 0.91,
        isAbstained: false,
        isVetoed: true,
        vetoReason: 'Audio digital clipping (+0.4 dBFS) during table slam at 00:08.5; face plunged into shadow.',
        cinematography: {
          focusSharpnessScore: 89,
          lightingDeltaE: 4.8,
          lightingRatio: '7:1',
          cameraMotion: 'Handheld Shake',
          headroomPct: 6.1
        },
        performance: {
          detailLevel: 'Level 2 Character',
          facsActionUnits: ['AU4 Brow Lowerer', 'AU25 Lips Part'],
          emotionalRegister: 'High explosive rage with sudden lunging movement.',
          eyelineStability: 'locked',
          microActionSummary: 'Actor lunged past the key light into dead shadow during the line climax.'
        },
        audio: {
          dialogueClarity: 81,
          tempoWpm: 165,
          clippingDetected: true,
          snrDb: 22,
          vocalTremorDetected: false
        },
        compositeScore: 54,
        isRecommended: false,
        editorialRationale: 'Vetoed due to microphone overload distortion and violent turn out of key lighting.'
      },
      {
        id: 'take_04',
        takeNumber: 4,
        label: 'Take 4 (Off-Angle Trial)',
        durationSec: 16.1,
        thumbnailColor: 'from-zinc-900 to-zinc-950',
        confidence: 0.42,
        isAbstained: true,
        abstainReason: 'Face angled > 45° off-axis with hand occlusion; insufficient facial landmark confidence.',
        isVetoed: false,
        cinematography: {
          focusSharpnessScore: 65,
          lightingDeltaE: 3.2,
          lightingRatio: '2.5:1',
          cameraMotion: 'Handheld Shake',
          headroomPct: 18.0
        },
        performance: {
          detailLevel: 'Level 1 Generic',
          facsActionUnits: [],
          emotionalRegister: 'Undetermined (Face obscured by actor hand gesture)',
          eyelineStability: 'broken',
          microActionSummary: 'Actor face concealed behind clipboard; eye pupils undetected.'
        },
        audio: {
          dialogueClarity: 89,
          tempoWpm: 135,
          clippingDetected: false,
          snrDb: 29,
          vocalTremorDetected: false
        },
        compositeScore: 40,
        isRecommended: false,
        editorialRationale: 'System abstained: face is occluded beyond reliable measurement threshold.'
      }
    ]
  },
  {
    id: 'scene_09_shot_1a',
    sceneNumber: 9,
    shotNumber: '1A',
    title: 'Neon Skyscraper Edge — Cyberpunk Infiltration',
    scriptExcerpt: 'AI PROMPT: "Cinematic drone tracking shot orbiting Kira standing on a neon rainy rooftop, trenchcoat billowing, 35mm anamorphic."',
    targetEmotion: 'High-tech isolation and epic scale',
    mode: 'gen_ai_prompt',
    selectedTakeId: 'seed_8831',
    takes: [
      {
        id: 'seed_1042',
        takeNumber: 1,
        label: 'Seed #1042 (Model Veo 2.1)',
        durationSec: 8.0,
        thumbnailColor: 'from-blue-950 to-zinc-900',
        confidence: 0.85,
        isAbstained: false,
        isVetoed: false,
        cinematography: {
          focusSharpnessScore: 84,
          lightingDeltaE: 1.8,
          lightingRatio: '3.5:1',
          cameraMotion: 'Steadicam Glide',
          headroomPct: 20.0
        },
        performance: {
          detailLevel: 'Level 2 Character',
          facsActionUnits: ['AU1 Inner Brow Raiser'],
          emotionalRegister: 'Synthetic neutral stance',
          eyelineStability: 'locked',
          microActionSummary: 'Minor background neon flicker artifact between frames 60-80.'
        },
        audio: {
          dialogueClarity: 95,
          tempoWpm: 0,
          clippingDetected: false,
          snrDb: 35,
          vocalTremorDetected: false
        },
        compositeScore: 78,
        isRecommended: false,
        editorialRationale: 'Acceptable prompt adherence, but slight temporal morphing on background skyscrapers.'
      },
      {
        id: 'seed_8831',
        takeNumber: 2,
        label: 'Seed #8831 (Model Veo 2.1)',
        durationSec: 8.0,
        thumbnailColor: 'from-purple-950 to-zinc-900',
        confidence: 0.98,
        isAbstained: false,
        isVetoed: false,
        cinematography: {
          focusSharpnessScore: 98,
          lightingDeltaE: 0.2,
          lightingRatio: '5:1',
          cameraMotion: 'Steadicam Glide',
          headroomPct: 15.0
        },
        performance: {
          detailLevel: 'Level 3 Intricate',
          facsActionUnits: ['AU4 Brow Furrow', 'AU9 Nose Wrinkler'],
          emotionalRegister: 'Consistent character model avatar lock',
          eyelineStability: 'locked',
          microActionSummary: 'Zero identity drift; coat physics match rain velocity; perfect 2.39:1 anamorphic bokeh.'
        },
        audio: {
          dialogueClarity: 98,
          tempoWpm: 0,
          clippingDetected: false,
          snrDb: 38,
          vocalTremorDetected: false
        },
        compositeScore: 96,
        isRecommended: true,
        editorialRationale: 'Winner: Flawless temporal coherence, pristine volumetric lighting, zero character avatar drift.'
      },
      {
        id: 'seed_9912',
        takeNumber: 3,
        label: 'Seed #9912 (Model Veo 2.1)',
        durationSec: 8.0,
        thumbnailColor: 'from-red-950 to-zinc-900',
        confidence: 0.74,
        isAbstained: false,
        isVetoed: true,
        vetoReason: 'Avatar identity drift detected: character facial structure distorted at frame 42.',
        cinematography: {
          focusSharpnessScore: 90,
          lightingDeltaE: 3.5,
          lightingRatio: '4:1',
          cameraMotion: 'Steadicam Glide',
          headroomPct: 14.0
        },
        performance: {
          detailLevel: 'Level 1 Generic',
          facsActionUnits: [],
          emotionalRegister: 'Deformed mesh transition',
          eyelineStability: 'broken',
          microActionSummary: 'Left hand spawned extra finger in rain reflection.'
        },
        audio: {
          dialogueClarity: 90,
          tempoWpm: 0,
          clippingDetected: false,
          snrDb: 30,
          vocalTremorDetected: false
        },
        compositeScore: 48,
        isRecommended: false,
        editorialRationale: 'Vetoed due to severe character identity mutation and hand hallucination.'
      }
    ]
  }
];
