const { test } = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");

test("bluff core is byte-identical to labeler core (no drift)", () => {
  const a = fs.readFileSync(__dirname + "/../api/_core.js");
  const b = fs.readFileSync(__dirname + "/../../tdh-labeler/api/_core.js");
  assert.ok(a.equals(b), "tdh-bluff/api/_core.js has drifted from the labeler core");
});
