import http from 'node:http';
import https from 'node:https';

const SARVAM_API_KEY = process.env.SARVAM_API_KEY;
const SARVAM_HOST = "api.sarvam.ai";
const SARVAM_PATH = "/v1/chat/completions";

const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/v1/chat/completions') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const parsed = JSON.parse(body);
                const { model, messages, ...rest } = parsed;

                // Convert messages to Sarvam format (string content)
                const sarvamMessages = messages.map(msg => {
                    let content = msg.content;
                    if (Array.isArray(content)) {
                        content = content.map(block => {
                            if (block.type === 'text') return block.text;
                            return '';
                        }).join('');
                    }
                    return {
                        role: msg.role,
                        content: content
                    };
                });

                const payload = {
                    model: "sarvam-m",
                    messages: sarvamMessages,
                    ...rest
                };

                const sarvamReq = https.request({
                    hostname: SARVAM_HOST,
                    path: SARVAM_PATH,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'api-subscription-key': SARVAM_API_KEY
                    }
                }, sarvamRes => {
                    res.statusCode = sarvamRes.statusCode;
                    sarvamRes.pipe(res);
                });

                sarvamReq.on('error', error => {
                    res.statusCode = 500;
                    res.end(JSON.stringify({ error: error.message }));
                });

                sarvamReq.write(JSON.stringify(payload));
                sarvamReq.end();
            } catch (error) {
                res.statusCode = 500;
                res.end(JSON.stringify({ error: error.message }));
            }
        });
    } else {
        res.statusCode = 404;
        res.end();
    }
});

const PORT = 18790;
server.listen(PORT, () => {
    console.log(`Spartan Bridge running at http://127.0.0.1:${PORT}`);
});
