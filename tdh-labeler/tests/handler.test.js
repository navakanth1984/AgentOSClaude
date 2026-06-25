const { test } = require("node:test");
const assert = require("node:assert");
const handler = require("../api/submit.js");

function mockReq(method, bodyStr) {
  async function* gen() { yield Buffer.from(bodyStr || ""); }
  const r = gen();
  r.method = method;
  return r;
}
function mockRes() {
  return {
    statusCode: 0, headers: {}, body: "",
    setHeader(k, v) { this.headers[k] = v; },
    end(s) { this.body = s; },
  };
}

test("non-POST -> 405", async () => {
  const res = mockRes();
  await handler(mockReq("GET", ""), res);
  assert.equal(res.statusCode, 405);
});

test("POST with bad code -> 401 (no allowlist match)", async () => {
  process.env.RATER_ALLOWLIST = "good:expert_a";
  process.env.GITHUB_REPO = "o/r";
  process.env.GITHUB_TOKEN = "t";
  const res = mockRes();
  await handler(mockReq("POST", JSON.stringify({ code: "bad",
    labels: { t01: { classification: "transfer" } } })), res);
  assert.equal(res.statusCode, 401);
});
