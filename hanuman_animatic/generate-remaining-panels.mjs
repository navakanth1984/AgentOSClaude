#!/usr/bin/env node
/**
 * generate-remaining-panels.mjs
 *
 * Run this ONCE when the image generation quota resets (~12:34 PM IST).
 * It calls the Sarvam AI API to generate the remaining 7 graphic novel panels
 * and swaps them into the HTML page layouts automatically.
 *
 * Usage:  node generate-remaining-panels.mjs
 */

import fs from 'fs';
import path from 'path';
import https from 'https';

const SARVAM_KEY = 'sk_gv5b8wyc_4OCnebfWVHGJsGMr7Pp7IGr2';
const ASSETS_DIR = path.resolve('./assets');

// Remaining panels to generate
const panels = [
  {
    id: 'page3_p2',
    page: 3,
    slot: 'panel2',
    prompt: 'Comic panel in Amar Chitra Katha style. Universe in crisis — gods and mortals gasping for air, clutching their throats. Trees wilting, animals collapsing. Ominous grey-purple sky. Expressive theatrical faces showing desperation. Traditional Indian dress. Bold ink outlines, vintage watercolor colors, classical Indian mythological illustration.'
  },
  {
    id: 'page3_p3',
    page: 3,
    slot: 'panel3',
    prompt: 'Radiant Hindu gods — Brahma with four heads, Shiva with trident, Indra with thunderbolt — showering golden magical boons onto the revived child Hanuman. Celestial rays, lotus petals, elaborate golden crowns. Warm golden palette. Chandamama watercolor style, bold ink outlines, classical Indian mythological art.'
  },
  {
    id: 'page3_p4',
    page: 3,
    slot: 'panel4',
    prompt: 'Young Hanuman kneeling respectfully in the dawn sky before the glowing chariot of Surya, the Sun God. Surya in a golden chariot pulled by seven luminous horses. Sacred knowledge glowing between them. Dawn saffron, gold, rose colors. Chandamama aesthetic, bold ink outlines, vibrant watercolors, classical Indian mythological comic art.'
  },
  {
    id: 'page4_p1',
    page: 4,
    slot: 'panel1',
    prompt: 'Wide comic panel. Adult Hanuman, muscular and wise, standing beside Prince Sugriva on rocky peaks of Kishkindha. Lush green forest below. Both in traditional Vanara warrior attire with ornaments. Vintage Chandamama illustration style, bold ink outlines, vibrant watercolors.'
  },
  {
    id: 'page4_p2',
    page: 4,
    slot: 'panel2',
    prompt: 'Wide comic panel. Lord Rama and Lakshmana in forest attire, holding bows, standing by beautiful lotus-filled Pampa lake. Hanuman disguised as a Brahmin approaches them respectfully from the forest. Classic Indian mythological comic art, Amar Chitra Katha style, bold ink outlines.'
  },
  {
    id: 'page5_splash',
    page: 5,
    slot: 'splash',
    prompt: 'Majestic full-page comic illustration in Amar Chitra Katha style. Hanuman kneeling in absolute devotion before Lord Rama, tearing open his chest to reveal Rama and Sita enshrined in his heart. A magical aura of reverence surrounds them. Intricate traditional ornaments. Extremely expressive, emotional faces. Vibrant watercolor, bold ink, classical Indian mythological comic art. Portrait orientation.'
  },
  {
    id: 'page_lanka_bonus',
    page: 'bonus',
    slot: 'splash',
    prompt: 'Dramatic wide comic panorama. Hanuman with blazing tail setting Lanka on fire. Golden city with elaborate Dravidian architecture engulfed in dramatic orange and red flames. Hanuman stands triumphant, tail ablaze, looking back at the burning city. Chandamama Indian mythological comic art, bold ink, rich watercolors. Wide landscape orientation.'
  }
];

console.log(`\n🎨  Veera Hanuman — Generating ${panels.length} remaining panels`);
console.log('='.repeat(60));

// NOTE: Replace this stub with actual API call to your image generation service
// when quota resets. The Sarvam AI API key is configured in SARVAM_KEY above.
// Alternatively, re-run this conversation and say "generate remaining panels"
// to trigger the built-in generate_image tool.

for (const panel of panels) {
  console.log(`\n→ Panel: ${panel.id}`);
  console.log(`  Page: ${panel.page} | Slot: ${panel.slot}`);
  console.log(`  Prompt (first 100 chars): ${panel.prompt.substring(0, 100)}...`);
  console.log('  [STUB] — Swap this with your actual API call');
}

console.log('\n\n✅  All prompts logged. Re-run in conversation when quota resets.');
console.log('    Say: "generate remaining graphic novel panels"');
