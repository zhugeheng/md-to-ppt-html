import { writeFileSync } from "node:fs";
import { spawn } from "node:child_process";

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const targetUrl = process.argv[2] || "file:///D:/codex/ppt-html/dist/template.html#4";
const screenshotPath = process.argv[3] || "dist/template-page4-after-key.png";
const targetHash = new URL(targetUrl).hash || "#4";
const keyPresses = Math.max(Number.parseInt(process.argv[4] || "1", 10), 0);
const port = 9333 + Math.floor(Math.random() * 1000);

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchTab() {
  for (let i = 0; i < 20; i += 1) {
    try {
      const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      return tabs.find((tab) => tab.url.includes("template.html")) || tabs[0];
    } catch {
      await wait(250);
    }
  }
  throw new Error("Chrome debugging endpoint did not become available.");
}

function createClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let nextId = 0;

  const opened = new Promise((resolve) => {
    ws.addEventListener("open", resolve, { once: true });
  });

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++nextId;
      const onMessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.id !== id) {
          return;
        }
        ws.removeEventListener("message", onMessage);
        if (data.error) {
          reject(new Error(JSON.stringify(data.error)));
        } else {
          resolve(data.result || {});
        }
      };
      ws.addEventListener("message", onMessage);
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  return { ws, opened, send };
}

const chrome = spawn(chromePath, [
  "--headless=new",
  `--remote-debugging-port=${port}`,
  "--disable-gpu",
  "--no-sandbox",
  targetUrl,
], {
  stdio: "ignore",
});

try {
  const tab = await fetchTab();
  const client = createClient(tab.webSocketDebuggerUrl);
  await client.opened;
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1920,
    height: 1080,
    deviceScaleFactor: 1,
    mobile: false,
  });

  await client.send("Runtime.evaluate", { expression: `location.hash = ${JSON.stringify(targetHash)}` });
  await wait(300);

  const before = await client.send("Runtime.evaluate", {
    expression: "({ hash: location.hash, visible: document.querySelectorAll('.slide.active .fragment.visible').length, active: document.querySelector('.slide.active')?.dataset.page })",
    returnByValue: true,
  });

  for (let i = 0; i < keyPresses; i += 1) {
    await client.send("Input.dispatchKeyEvent", {
      type: "keyDown",
      key: "ArrowRight",
      code: "ArrowRight",
      windowsVirtualKeyCode: 39,
    });
    await client.send("Input.dispatchKeyEvent", {
      type: "keyUp",
      key: "ArrowRight",
      code: "ArrowRight",
      windowsVirtualKeyCode: 39,
    });
    await wait(120);
  }
  await wait(300);

  const after = await client.send("Runtime.evaluate", {
    expression: "({ hash: location.hash, visible: document.querySelectorAll('.slide.active .fragment.visible').length, active: document.querySelector('.slide.active')?.dataset.page, counter: document.querySelector('#counter')?.textContent, progress: document.querySelector('#progress span')?.style.width })",
    returnByValue: true,
  });

  const screenshot = await client.send("Page.captureScreenshot", { format: "png" });
  writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
  client.ws.close();

  console.log(JSON.stringify({
    before: before.result.value,
    after: after.result.value,
    screenshot: screenshotPath,
  }, null, 2));
} finally {
  chrome.kill("SIGKILL");
}
