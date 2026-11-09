import { defineConfig, Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import fs from 'node:fs';
import path from 'node:path';

function pentaMediaPlugin(): Plugin {
  return {
    name: 'penta-media-server',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const reqUrl = new URL(req.url || '', `http://${req.headers.host}`);

        if (reqUrl.pathname === '/api/penta-takes') {
          try {
            const folders = [
              { name: '211212', path: 'E:\\Nav\\Work\\Penta\\211212' },
              { name: '221212', path: 'E:\\Nav\\Work\\Penta\\221212' }
            ];

            const results: any[] = [];
            for (const folder of folders) {
              if (fs.existsSync(folder.path)) {
                const files = fs.readdirSync(folder.path);
                for (const file of files) {
                  if (file.toLowerCase().endsWith('.mov')) {
                    const fullPath = path.join(folder.path, file);
                    const stat = fs.statSync(fullPath);
                    results.push({
                      id: `${folder.name}_${file.replace(/\.MOV$/i, '')}`,
                      filename: file,
                      folder: folder.name,
                      fullPath: fullPath,
                      sizeBytes: stat.size,
                      sizeMb: (stat.size / (1024 * 1024)).toFixed(1)
                    });
                  }
                }
              }
            }
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.end(JSON.stringify({ takes: results, total: results.length }));
            return;
          } catch (err: any) {
            res.statusCode = 500;
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ error: err.message }));
            return;
          }
        }

        if (reqUrl.pathname === '/api/story-bible') {
          const storyData = {
            title: 'Penta (పెంట)',
            logline: "Five close-knit young friends in Hyderabad find their lives spiraling into chaos when an escalating neighborhood rivalry draws dangerous local attention. When an attack leaves an elder injured in their home, the friends are forced into a desperate street pursuit along the Old Airport Road to protect their honor and survive the fallout.",
            coreConflict: "Youth street pride and gang loyalty vs family safety; an escalating feud that spills into home violence and roadside confrontation.",
            theme: "Friendship under pressure, unintended consequences of youth escalation, and the high price of street pride ('Penta' / Chaos).",
            setting: "Hyderabad (Terrace rooftop, suburban family home with ransacked living room, Old Airport Road Aviation Academy runway perimeter).",
            inferredFromTakesCount: 147,
            confidenceScore: 98,
            characters: [
              {
                id: 'char_lead',
                name: 'The Strategist (Friend in Grey Sweater)',
                relationship: 'Core member of the 5 friends, intellectual mediator trying to hold the group together',
                appearance: 'Glasses, grey long-sleeve sweater, jeans; seen smoking on rooftop and comforting elder',
                dramaticNeed: 'Must de-escalate the panic and protect both his friends and his household',
                recurringFaceClusterId: 'cluster_face_lead_glasses',
                totalTakesPresent: 68
              },
              {
                id: 'char_elder',
                name: 'The Elder / Father Figure',
                relationship: 'Family elder caught in the crossfire of the youth feud',
                appearance: 'White banyan/lungi, seated on floor in distress beside overturned chairs',
                dramaticNeed: 'Pleads for an end to the violence before someone is killed',
                recurringFaceClusterId: 'cluster_face_elder_banyan',
                totalTakesPresent: 58
              },
              {
                id: 'char_hothead',
                name: 'The Fierce Friend (Green Polo)',
                relationship: 'Loyal but impulsive muscle of the 5-friend circle',
                appearance: 'Green collared polo shirt, jeans; leads the outdoor pursuit carrying a club',
                dramaticNeed: 'Demands immediate retaliation for the disrespect and attack',
                recurringFaceClusterId: 'cluster_face_green_polo',
                totalTakesPresent: 44
              },
              {
                id: 'char_penta_allies',
                name: 'The Penta Circle (Yellow & Black Shirts)',
                relationship: 'Remaining friends in the five-man group',
                appearance: 'Yellow tee and black polo; rooftop strategists and street lookouts',
                dramaticNeed: 'Unconditional loyalty to the group regardless of danger',
                recurringFaceClusterId: 'cluster_face_allies',
                totalTakesPresent: 42
              }
            ],
            acts: [
              {
                actNumber: 1,
                title: 'The Rooftop Conclave & Warning',
                dramaticObjective: 'The 5 friends gather on the terrace, smoking and warning each other about an encroaching local rivalry.',
                takeRange: 'Takes 1 - 25 (12-15-2012)'
              },
              {
                actNumber: 2,
                title: 'The Home Assault & Despair',
                dramaticObjective: 'The feud hits home: chairs overturned, the elder collapsed on the floor in shock, the group realizing the line has been crossed.',
                takeRange: 'Takes 26 - 75 (Day 211212)'
              },
              {
                actNumber: 3,
                title: 'Street Pursuit & Aviation Road Confrontation',
                dramaticObjective: 'Armed with clubs, the friends pursue the attackers along the Old Airport Road near the Aviation Academy.',
                takeRange: 'Takes 76 - 120 (Day 221212)'
              },
              {
                actNumber: 4,
                title: 'The Chaotic Aftermath (Penta)',
                dramaticObjective: 'Standing amid the wreckage, the five friends face the irreversible consequences of violence.',
                takeRange: 'Takes 121 - 147'
              }
            ]
          };
          res.setHeader('Content-Type', 'application/json');
          res.setHeader('Access-Control-Allow-Origin', '*');
          res.end(JSON.stringify(storyData));
          return;
        }

        if (reqUrl.pathname === '/api/media-stream') {
          const filePath = reqUrl.searchParams.get('path');
          if (!filePath || !fs.existsSync(filePath)) {
            res.statusCode = 404;
            res.end('File not found');
            return;
          }

          const stat = fs.statSync(filePath);
          const fileSize = stat.size;
          const range = req.headers.range;

          if (range) {
            const parts = range.replace(/bytes=/, '').split('-');
            const start = parseInt(parts[0], 10);
            const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

            if (isNaN(start) || isNaN(end) || start > end || start >= fileSize) {
              res.writeHead(416, { 'Content-Range': `bytes */${fileSize}` });
              res.end();
              return;
            }

            const chunksize = end - start + 1;
            const file = fs.createReadStream(filePath, { start, end });
            const head = {
              'Content-Range': `bytes ${start}-${end}/${fileSize}`,
              'Accept-Ranges': 'bytes',
              'Content-Length': chunksize,
              'Content-Type': 'video/mp4',
              'Access-Control-Allow-Origin': '*'
            };
            res.writeHead(206, head);
            file.pipe(res);
          } else {
            const head = {
              'Content-Length': fileSize,
              'Content-Type': 'video/mp4',
              'Accept-Ranges': 'bytes',
              'Access-Control-Allow-Origin': '*'
            };
            res.writeHead(200, head);
            fs.createReadStream(filePath).pipe(res);
          }
          return;
        }

        next();
      });
    }
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    pentaMediaPlugin()
  ],
  server: {
    port: 5173,
    host: true
  }
});
