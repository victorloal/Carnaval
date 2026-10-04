const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const dom = new JSDOM("<!DOCTYPE html><body></body>", { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.DOMPurify = undefined;
global.CSSStyleSheet = class CSSStyleSheet {};
if (!dom.window.CSSStyleSheet) dom.window.CSSStyleSheet = global.CSSStyleSheet;
if (!dom.window.CSS) dom.window.CSS = { escape: (s) => String(s) };

// Diagram-like syntax that a non-mermaid fence must never carry. GitHub renders
// ```text and bare ``` fences as plain text, so any of these produces NO diagram
// at all -- silently, which is how two C4 blocks stayed broken.
const FOREIGN_DIAGRAM =
  /(^\s*)(C4Context|C4Container|C4Component|C4Deployment|C4Dynamic|@start(?:uml|mindmap|gantt)|@enduml|skinparam|Person\s*\(|System_Ext\s*\(|ContainerDb\s*\(|System_Boundary\s*\(|[A-Za-z]+ -> [A-Za-z]+ :)/m;

const MERMAID_LANGS = new Set(["mermaid"]);
// These are "plain" fences: allowed in general, but not for diagram syntax.
const PLAIN_LANGS = new Set(["", "text", "txt", "plaintext", "plantuml", "uml"]);

function detectMermaidType(src) {
  const line = src
    .split(/\r?\n/)
    .map((l) => l.trim())
    .find((l) => l && !l.startsWith("%%"));
  if (!line) return "(empty)";
  const m = line.match(
    /^(flowchart|graph|sequenceDiagram|stateDiagram(?:-v2)?|erDiagram|classDiagram(?:-v2)?|journey|gantt|pie|requirementDiagram|gitGraph|mindmap|timeline|quadrantChart|sankey-beta|block-beta|packet-beta|kanban|architecture-beta|xychart-beta|razzle dazzle)/
  );
  if (m) return m[1];
  return "(unknown: " + line.slice(0, 24) + ")";
}

(async () => {
  const mermaid = (await import("mermaid")).default;
  mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });

  const root = process.argv[2];
  const files = [];
  (function walk(d) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith(".md")) files.push(p);
    }
  })(root);

  const failures = [];
  const langCounts = new Map();
  const typeCounts = new Map();
  let total = 0, ok = 0;

  const bump = (map, key) => map.set(key, (map.get(key) || 0) + 1);

  for (const f of files) {
    const text = fs.readFileSync(f, "utf8");
    const rel = path.relative(root, f);

    // Match every fenced block together with its language tag, not just mermaid.
    const fences = [...text.matchAll(/^[ \t]*```([^\r\n`]*)\r?\n([\s\S]*?)^[ \t]*```[ \t]*$/gm)];
    let n = 0;
    for (const m of fences) {
      n++;
      total++;
      const lang = m[1].trim().toLowerCase();
      const body = m[2];
      bump(langCounts, lang === "" ? "(bare)" : lang);

      if (MERMAID_LANGS.has(lang)) {
        const type = detectMermaidType(body);
        bump(typeCounts, type);
        try {
          await mermaid.parse(body);
          ok++;
        } catch (e) {
          failures.push(
            `FAIL  ${rel}  block#${n}  [mermaid/${type}]\n      ` +
              String(e.message || e).split("\n").slice(0, 4).join("\n      ")
          );
        }
        continue;
      }

      if (PLAIN_LANGS.has(lang) && FOREIGN_DIAGRAM.test(body)) {
        const kind = /C4[A-Z]/.test(body) ? "PlantUML C4 DSL" : "PlantUML / foreign diagram syntax";
        failures.push(
          `FAIL  ${rel}  block#${n}  [fence '${lang || "(bare)"}']\n` +
            `      ${kind} inside a non-mermaid fence: it renders as plain text, so no\n` +
            `      diagram appears at all. Rewrite it as Mermaid (ADR 0014) or drop it.`
        );
      }
    }
  }

  console.log("--- fence breakdown by language ---");
  for (const [k, v] of [...langCounts.entries()].sort((a, b) => b[1] - a[1]))
    console.log(`  ${String(k).padEnd(14)} ${v}`);
  console.log("--- mermaid breakdown by diagram type ---");
  if (typeCounts.size === 0) console.log("  (none)");
  for (const [k, v] of [...typeCounts.entries()].sort((a, b) => b[1] - a[1]))
    console.log(`  ${String(k).padEnd(14)} ${v}`);

  if (failures.length) {
    console.log("");
    for (const x of failures) console.log(x);
  }
  console.log(`\nTOTAL ${total}  PARSED ${ok}  FAILED ${failures.length}`);
  process.exit(failures.length ? 1 : 0);
})();
