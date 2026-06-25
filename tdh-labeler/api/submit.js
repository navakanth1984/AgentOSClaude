const { handle, githubCommit } = require("./_core.js");

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  if (req.method !== "POST") {
    res.statusCode = 405;
    return res.end(JSON.stringify({ ok: false, error: "method" }));
  }
  let raw = "";
  for await (const chunk of req) raw += chunk;
  const result = await handle({ track: "expert", requireCode: true },
    raw, process.env, githubCommit);
  res.statusCode = result.status;
  res.end(JSON.stringify(result.body));
};
