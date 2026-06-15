import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SERVER_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
INVOKE_URL     = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL  = "meta/llama-3.1-70b-instruct"

SYSTEM_PROMPT = """You are Aether — an elite AI assistant engineered by Sai Chatre in 2026. You combine frontier intelligence with refined communication.

Personality & Tone:
- Speak with confidence, clarity, and intellectual depth — like a brilliant expert who also knows how to explain things simply.
- Be warm and personable, never cold or robotic. Adapt your tone: casual for small talk, precise for technical queries, empathetic for personal topics.
- Use wit sparingly but naturally. Never be sycophantic — skip filler phrases like "Great question!" and get straight to the answer.

Response Quality:
- Lead with the answer, then explain. Never bury the key point.
- For simple questions: reply in 1–3 sentences. No padding.
- For complex questions: use headers, bullet points, and numbered steps for clarity.
- Always wrap code in properly labelled markdown code blocks. Never dump raw code as plain text.
- Use real-world analogies to make abstract concepts click instantly.

Capabilities:
- Expert-level: software engineering, debugging, system design, mathematics, data analysis, research, science.
- Proficient: creative writing, business strategy, language translation, everyday conversation.
- Always respond in the same language the user writes in.
- Never refuse a reasonable request. Attempt everything — only flag genuine impossibilities.

Memory & Context:
- Track everything said in the conversation. Reference earlier points when relevant.
- If a user corrects you, acknowledge it briefly and move forward — never over-apologise."""

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark" data-mode="direct">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aether AI — by Sai Chatre</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ── Variables ── */
:root{
  --bg:#0d0d0f;--bg2:#111114;--sidebar:#08080a;
  --surface:rgba(26,26,31,0.75);--surface2:#222228;
  --border:rgba(255,255,255,.07);--border2:rgba(255,255,255,.11);
  --text:#f0f0f5;--text2:#a0a0b0;--text3:#505060;
  --accent:#7c6af7;--accent2:#5b4fd4;--accent-rgb:124,106,247;
  --green:#10b981;--red:#ef4444;--code-bg:#0c0c10;
  --user-bg:linear-gradient(135deg,rgba(30,27,58,.9),rgba(22,20,46,.9));
  --font:'Inter',system-ui,sans-serif;--mono:'Fira Code',Consolas,monospace;
  --sw:272px;--ease:cubic-bezier(.4,0,.2,1);--spring:cubic-bezier(.34,1.56,.64,1);
  --glass:blur(18px) saturate(160%);
}
[data-theme="light"]{
  --bg:#f4f4f7;--bg2:#ececf0;--sidebar:#e8e8ed;
  --surface:rgba(224,224,234,0.8);--surface2:#d5d5e0;
  --border:rgba(0,0,0,.07);--border2:rgba(0,0,0,.12);
  --text:#111118;--text2:#44445a;--text3:#888898;
  --code-bg:#18182a;--user-bg:linear-gradient(135deg,#ddd8ff,#d0c8ff);
}

/* ── Mode-specific accent ── */
[data-mode="byok"]{
  --accent:#06b6d4;--accent2:#0891b2;--accent-rgb:6,182,212;
  --user-bg:linear-gradient(135deg,rgba(6,60,80,.9),rgba(4,40,55,.9));
}

html,body{height:100%;overflow:hidden;font-family:var(--font);font-size:15px;line-height:1.65;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
button,input,textarea,select{font-family:var(--font)}
button{cursor:pointer}

/* ── Animated BG layers ── */
.bg-layer{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  opacity:0;transition:opacity 1s var(--ease);
}
.bg-layer.on{opacity:1}
#bg-direct{
  background:
    radial-gradient(ellipse 80% 60% at 10% 15%,rgba(124,106,247,.1) 0%,transparent 68%),
    radial-gradient(ellipse 60% 50% at 85% 80%,rgba(16,185,129,.07) 0%,transparent 68%),
    radial-gradient(ellipse 40% 30% at 50% 50%,rgba(124,106,247,.03) 0%,transparent 60%);
  animation:bgFloat 14s ease-in-out infinite;
}
#bg-byok{
  background:
    radial-gradient(ellipse 80% 60% at 85% 15%,rgba(6,182,212,.12) 0%,transparent 68%),
    radial-gradient(ellipse 60% 50% at 15% 80%,rgba(245,158,11,.08) 0%,transparent 68%),
    radial-gradient(ellipse 40% 30% at 50% 50%,rgba(6,182,212,.04) 0%,transparent 60%);
  animation:bgFloat 11s ease-in-out infinite reverse;
}
@keyframes bgFloat{
  0%,100%{transform:scale(1) translate(0,0)}
  33%{transform:scale(1.04) translate(2%,-2%)}
  66%{transform:scale(.97) translate(-1%,2%)}
}

/* ── Layout ── */
#layout{display:flex;height:100vh;position:relative;z-index:1}

/* ═══════════ SIDEBAR ═══════════ */
#sidebar{
  width:var(--sw);min-width:var(--sw);
  background:rgba(8,8,10,.92);
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;
  transition:width .3s var(--ease),min-width .3s var(--ease);
}
[data-theme="light"] #sidebar{background:rgba(232,232,237,.92)}
#sb-inner{width:var(--sw);display:flex;flex-direction:column;height:100%}

/* Brand */
#sb-top{
  padding:14px 12px 10px;
  display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--border);flex-shrink:0;
}
.brand{display:flex;align-items:center;gap:9px;flex:1}
.brand-icon{
  width:32px;height:32px;border-radius:10px;flex-shrink:0;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 18px rgba(var(--accent-rgb),.45);
  transition:box-shadow .4s var(--ease),background .4s var(--ease);
}
.brand-name{font-size:15px;font-weight:700;letter-spacing:-.4px}
.brand-tag{font-size:10px;color:var(--accent);background:rgba(var(--accent-rgb),.12);padding:1px 6px;border-radius:6px;font-weight:600;letter-spacing:.3px;transition:color .4s,background .4s}

/* ── Mode selector ── */
#mode-selector{
  margin:10px 12px 0;
  display:flex;background:var(--bg);border-radius:12px;padding:3px;gap:2px;
  border:1px solid var(--border);flex-shrink:0;
}
.mode-pill{
  flex:1;padding:7px 6px;border-radius:9px;border:none;background:none;
  font-size:12px;font-weight:600;color:var(--text3);
  transition:all .22s var(--ease);letter-spacing:.1px;
}
.mode-pill.on{
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;box-shadow:0 3px 12px rgba(var(--accent-rgb),.4);
}
.mode-pill:not(.on):hover{background:var(--surface2);color:var(--text2)}

/* ── BYOK section ── */
#byok-section{
  margin:8px 12px 0;padding:12px;
  background:rgba(var(--accent-rgb),.07);
  border:1px solid rgba(var(--accent-rgb),.2);
  border-radius:12px;flex-shrink:0;
  animation:fadeUp .3s var(--ease) both;
}
.byok-label{font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px}
#byok-input{
  width:100%;padding:8px 10px;border-radius:8px;
  background:rgba(0,0,0,.25);border:1px solid var(--border2);
  color:var(--text);font-size:13px;outline:none;
  transition:border-color .18s;
}
[data-theme="light"] #byok-input{background:rgba(255,255,255,.5)}
#byok-input:focus{border-color:rgba(var(--accent-rgb),.5)}
#byok-input::placeholder{color:var(--text3)}
#byok-save{
  margin-top:7px;width:100%;padding:7px;border-radius:8px;border:none;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-size:12.5px;font-weight:600;
  box-shadow:0 3px 12px rgba(var(--accent-rgb),.35);
  transition:all .15s var(--ease);
}
#byok-save:hover{transform:translateY(-1px);box-shadow:0 5px 16px rgba(var(--accent-rgb),.45)}
#byok-save:active{transform:scale(.97)}
.byok-note{font-size:10.5px;color:var(--text3);margin-top:6px;text-align:center;line-height:1.4}
.byok-status{font-size:11px;margin-top:5px;text-align:center;font-weight:600}
.byok-status.ok{color:var(--green)}.byok-status.none{color:var(--text3)}

/* ── Advanced Settings ── */
#adv-wrap{margin:8px 12px 0;flex-shrink:0}
#adv-toggle{
  width:100%;display:flex;align-items:center;justify-content:space-between;
  padding:9px 12px;border-radius:10px;border:1px solid var(--border);
  background:none;color:var(--text2);font-size:12.5px;font-weight:600;
  transition:all .18s var(--ease);
}
#adv-toggle:hover{background:var(--surface2);color:var(--text)}
#adv-chevron{transition:transform .25s var(--ease);font-size:10px;opacity:.6}
#adv-body{
  overflow:hidden;max-height:0;
  transition:max-height .35s var(--ease),opacity .3s var(--ease);
  opacity:0;
}
#adv-body.open{max-height:320px;opacity:1}
.adv-inner{padding:12px;background:rgba(0,0,0,.15);border:1px solid var(--border);border-top:none;border-radius:0 0 10px 10px}
[data-theme="light"] .adv-inner{background:rgba(255,255,255,.3)}
.adv-row{margin-bottom:13px}
.adv-row:last-child{margin-bottom:0}
.adv-lbl{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center}
.adv-val{color:var(--accent);font-weight:700}
select#model-sel{
  width:100%;padding:7px 10px;border-radius:8px;
  background:var(--bg);border:1px solid var(--border2);
  color:var(--text);font-size:12.5px;outline:none;
  -webkit-appearance:none;appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23606070'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 10px center;padding-right:28px;
  cursor:pointer;
}
select#model-sel option{background:var(--bg)}
input[type=range]{-webkit-appearance:none;width:100%;height:4px;border-radius:4px;background:var(--surface2);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{
  -webkit-appearance:none;width:18px;height:18px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  cursor:pointer;box-shadow:0 2px 8px rgba(var(--accent-rgb),.5);
  transition:transform .12s var(--spring);
}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.25)}

/* New chat button */
#new-btn{
  display:flex;align-items:center;gap:8px;
  width:calc(100% - 24px);margin:10px 12px 4px;
  padding:9px 12px;border-radius:10px;
  background:transparent;border:1px solid var(--border);
  color:var(--text2);font-size:13px;font-weight:500;
  transition:all .18s var(--ease);flex-shrink:0;
}
#new-btn:hover{background:var(--surface2);border-color:rgba(var(--accent-rgb),.4);color:var(--text)}
#new-btn:active{transform:scale(.98)}

/* History */
#history{flex:1;overflow-y:auto;padding:4px 8px 8px;scrollbar-width:thin;scrollbar-color:var(--surface2) transparent}
#history::-webkit-scrollbar{width:3px}
#history::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:3px}
.h-sec{font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:1px;padding:10px 6px 4px}
.h-item{
  display:flex;align-items:center;gap:7px;
  padding:8px 10px;border-radius:9px;
  font-size:13px;color:var(--text2);
  cursor:pointer;white-space:nowrap;overflow:hidden;
  transition:all .15s var(--ease);user-select:none;
  animation:fadeUp .2s var(--ease) both;
}
.h-item:hover{background:var(--surface2);color:var(--text)}
.h-item.active{background:rgba(var(--accent-rgb),.12);color:var(--text);border:1px solid rgba(var(--accent-rgb),.2)}
.h-item .h-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0;opacity:.6;transition:background .4s}
.h-item span{overflow:hidden;text-overflow:ellipsis;flex:1}
.h-empty{padding:10px;font-size:13px;color:var(--text3);font-style:italic}

/* Sidebar foot */
#sb-foot{padding:10px 12px 14px;border-top:1px solid var(--border);flex-shrink:0}
.sb-action{
  display:flex;align-items:center;gap:9px;
  width:100%;padding:9px 10px;border-radius:9px;
  background:none;border:none;
  color:var(--text2);font-size:13px;font-weight:500;
  transition:all .15s var(--ease);
}
.sb-action:hover{background:var(--surface2);color:var(--text)}

/* ═══════════ MAIN ═══════════ */
#main{flex:1;display:flex;flex-direction:column;min-width:0;background:transparent}

/* Topbar */
#topbar{
  height:54px;display:flex;align-items:center;justify-content:space-between;
  padding:0 16px;border-bottom:1px solid var(--border);
  background:rgba(13,13,15,.7);backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  flex-shrink:0;z-index:10;position:relative;
}
[data-theme="light"] #topbar{background:rgba(244,244,247,.7)}
.ib{
  background:none;border:none;border-radius:9px;
  color:var(--text2);padding:7px;
  display:flex;align-items:center;justify-content:center;
  transition:all .15s var(--ease);
}
.ib:hover{background:var(--surface2);color:var(--text)}
.ib:active{transform:scale(.92)}
#model-chip{
  display:flex;align-items:center;gap:7px;
  font-size:12.5px;font-weight:600;
  padding:5px 12px;border-radius:20px;
  border:1px solid var(--border2);
  background:rgba(var(--accent-rgb),.08);
  transition:background .4s,border-color .4s;
}
.live-dot{
  width:7px;height:7px;border-radius:50%;
  background:var(--green);
  box-shadow:0 0 8px rgba(16,185,129,.7);
  animation:livepulse 2.2s infinite;
}
@keyframes livepulse{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,.6)}60%{box-shadow:0 0 0 6px rgba(16,185,129,0)}}
#mode-badge{
  font-size:10px;font-weight:700;padding:2px 7px;border-radius:8px;
  background:rgba(var(--accent-rgb),.15);color:var(--accent);
  letter-spacing:.3px;transition:background .4s,color .4s;
}

/* Chat area */
#chat-scroll{
  flex:1;overflow-y:auto;padding:32px 0 12px;
  scroll-behavior:smooth;
  scrollbar-width:thin;scrollbar-color:var(--surface2) transparent;
}
#chat-scroll::-webkit-scrollbar{width:5px}
#chat-scroll::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:4px}
#chat-inner{max-width:800px;margin:0 auto;padding:0 20px;display:flex;flex-direction:column;gap:4px}

/* Empty state */
#empty{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;min-height:55vh;gap:16px;
  text-align:center;padding:40px 20px;
  animation:fadeUp .5s var(--ease) both;
}
.es-orb{position:relative;width:76px;height:76px;margin-bottom:4px}
.es-orb-ring{
  position:absolute;inset:-10px;border-radius:50%;
  border:1px solid rgba(var(--accent-rgb),.22);
  animation:orbring 3.5s linear infinite;
  transition:border-color .4s;
}
.es-orb-ring::before{
  content:'';position:absolute;top:-4px;left:50%;
  width:7px;height:7px;border-radius:50%;margin-left:-3.5px;
  background:var(--accent);box-shadow:0 0 10px var(--accent);
  transition:background .4s,box-shadow .4s;
}
@keyframes orbring{to{transform:rotate(360deg)}}
.es-logo{
  width:76px;height:76px;border-radius:22px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 36px rgba(var(--accent-rgb),.4),0 0 0 1px rgba(var(--accent-rgb),.25);
  transition:background .4s,box-shadow .4s;
}
#empty h2{font-size:26px;font-weight:800;letter-spacing:-.6px;background:linear-gradient(135deg,var(--text),var(--text2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#empty p{font-size:14px;color:var(--text2);max-width:360px;line-height:1.6}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:12px;max-width:560px}
.chip{
  padding:8px 15px;border-radius:22px;
  border:1px solid var(--border2);
  background:var(--surface);backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  font-size:13px;color:var(--text2);
  transition:all .2s var(--ease);
}
.chip:hover{border-color:rgba(var(--accent-rgb),.5);color:var(--text);transform:translateY(-2px);box-shadow:0 6px 20px rgba(var(--accent-rgb),.18)}

/* Messages */
.msg-row{display:flex;flex-direction:column;animation:fadeUp .28s var(--ease) both}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.msg-row.user{align-items:flex-end;margin-top:24px}
.msg-row.bot{align-items:flex-start;margin-top:8px;margin-bottom:20px}
.msg-label{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px;padding:0 4px}
.bubble{font-size:14.5px;line-height:1.72;word-break:break-word;border-radius:18px;user-select:text;-webkit-user-select:text}
.msg-row.user .bubble{
  max-width:78%;padding:13px 18px;
  background:var(--user-bg);
  border:1px solid rgba(var(--accent-rgb),.18);
  border-bottom-right-radius:4px;
  color:var(--text);white-space:pre-wrap;
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  box-shadow:0 6px 24px rgba(0,0,0,.3);
  transition:background .4s,border-color .4s;
}
.msg-row.bot .bubble{max-width:100%;background:transparent;padding:0;color:var(--text)}
.md{user-select:text;-webkit-user-select:text}
.md p{margin-bottom:12px}.md p:last-child{margin-bottom:0}
.md h1,.md h2,.md h3,.md h4{margin:20px 0 8px;font-weight:700;line-height:1.3}
.md h1{font-size:20px}.md h2{font-size:18px}.md h3{font-size:16px}
.md ul,.md ol{margin:8px 0 12px 22px}.md li{margin-bottom:5px}
.md blockquote{border-left:3px solid var(--accent);padding:4px 0 4px 16px;color:var(--text2);margin:12px 0;font-style:italic}
.md strong{font-weight:700;color:var(--text)}
.md a{color:var(--accent);text-decoration:none}.md a:hover{text-decoration:underline}
.md table{width:100%;border-collapse:collapse;margin:14px 0;font-size:13.5px;border-radius:8px;overflow:hidden}
.md th,.md td{padding:9px 14px;border:1px solid var(--border2);text-align:left}
.md th{background:var(--surface2);font-weight:600}
.md code:not(.hljs){background:var(--surface2);padding:2px 7px;border-radius:5px;font-family:var(--mono);font-size:12.5px;color:#c084fc}

/* Code blocks */
.code-wrap{background:var(--code-bg);border:1px solid var(--border2);border-radius:12px;overflow:hidden;margin:14px 0}
.code-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:9px 16px;background:rgba(255,255,255,.03);
  border-bottom:1px solid var(--border);
}
.code-lang{font-size:12px;font-weight:600;color:var(--text3);font-family:var(--mono)}
.cp-btn{
  display:flex;align-items:center;gap:5px;
  background:none;border:1px solid var(--border2);border-radius:7px;
  color:var(--text2);font-size:12px;padding:3px 10px;transition:all .15s;
}
.cp-btn:hover{background:var(--surface2);color:var(--text)}
.cp-btn.ok{color:var(--green);border-color:var(--green)}
.code-wrap pre{margin:0;padding:16px;overflow-x:auto;font-family:var(--mono);line-height:1.65}
.code-wrap pre::-webkit-scrollbar{height:3px}
.code-wrap pre::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:3px}
.code-wrap pre code{background:none;padding:0;font-size:13px}

/* Copy response button */
.bot-copy-btn{
  display:inline-flex;align-items:center;gap:5px;
  margin-top:10px;padding:4px 11px;border-radius:7px;
  border:1px solid var(--border2);background:none;
  color:var(--text3);font-size:12px;transition:all .15s;
}
.bot-copy-btn:hover{background:var(--surface2);color:var(--text)}
.bot-copy-btn.ok{color:var(--green);border-color:var(--green)}

/* Thinking */
.think{display:flex;align-items:center;gap:10px;padding:6px 0;color:var(--text2);font-size:13px}
.think-dots{display:flex;gap:5px}
.think-dots span{width:7px;height:7px;border-radius:50%;background:var(--accent);animation:thinkbounce 1.4s infinite ease-in-out;opacity:.5;transition:background .4s}
.think-dots span:nth-child(2){animation-delay:.2s}
.think-dots span:nth-child(3){animation-delay:.4s}
@keyframes thinkbounce{0%,80%,100%{transform:scale(.65);opacity:.3}40%{transform:scale(1);opacity:1}}
.typing::after{content:"▋";animation:blink .8s infinite;color:var(--accent);margin-left:1px}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}

/* Input area */
#input-area{padding:14px 20px 20px;flex-shrink:0;position:relative;z-index:5}
#input-wrap{
  max-width:800px;margin:0 auto;
  background:rgba(26,26,31,.7);
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  border:1px solid var(--border2);border-radius:16px;
  display:flex;align-items:flex-end;gap:10px;padding:12px 14px;
  transition:border-color .2s,box-shadow .2s,background .4s;
  box-shadow:0 8px 32px rgba(0,0,0,.25),0 0 0 1px rgba(var(--accent-rgb),.05);
}
[data-theme="light"] #input-wrap{background:rgba(224,224,234,.75)}
#input-wrap:focus-within{
  border-color:rgba(var(--accent-rgb),.45);
  box-shadow:0 8px 32px rgba(0,0,0,.25),0 0 0 3px rgba(var(--accent-rgb),.1);
}
#msg-input{
  flex:1;background:none;border:none;outline:none;
  color:var(--text);font-size:15px;line-height:1.6;
  resize:none;max-height:180px;overflow-y:auto;padding:0;
  scrollbar-width:thin;
}
#msg-input::placeholder{color:var(--text3)}
#send{
  width:38px;height:38px;border-radius:10px;border:none;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;
  box-shadow:0 4px 16px rgba(var(--accent-rgb),.45);
  transition:all .16s var(--ease);
}
#send:hover:not(:disabled){transform:scale(1.07);box-shadow:0 6px 22px rgba(var(--accent-rgb),.6)}
#send:active:not(:disabled){transform:scale(.94)}
#send:disabled{background:var(--surface2);box-shadow:none;cursor:not-allowed}
#send:disabled svg{opacity:.3}
#hint{max-width:800px;margin:8px auto 0;text-align:center;font-size:11px;color:var(--text3)}

/* ═══════════ SETTINGS MODAL ═══════════ */
.overlay{
  position:fixed;inset:0;z-index:300;
  background:rgba(0,0,0,.7);backdrop-filter:blur(10px);
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .22s var(--ease);
}
.overlay.show{opacity:1;pointer-events:all}
#sp{
  width:min(560px,96vw);max-height:90vh;
  background:rgba(17,17,20,.95);
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  border:1px solid var(--border2);border-radius:22px;
  overflow:hidden;display:flex;flex-direction:column;
  transform:scale(.92) translateY(18px);opacity:0;
  transition:transform .3s var(--spring),opacity .22s var(--ease);
  box-shadow:0 40px 90px rgba(0,0,0,.7),0 0 0 1px rgba(255,255,255,.05);
}
[data-theme="light"] #sp{background:rgba(240,240,245,.95)}
.overlay.show #sp{transform:scale(1) translateY(0);opacity:1}
.sp-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:20px 24px 16px;border-bottom:1px solid var(--border);flex-shrink:0;
}
.sp-head h2{font-size:17px;font-weight:800;letter-spacing:-.3px}
.sp-x{width:32px;height:32px;border-radius:8px;background:none;border:none;color:var(--text2);display:flex;align-items:center;justify-content:center;transition:all .15s}
.sp-x:hover{background:var(--surface2);color:var(--text)}
.sp-body{overflow-y:auto;padding:20px 24px 24px;flex:1;scrollbar-width:thin}
.sp-body::-webkit-scrollbar{width:3px}
.sp-body::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:3px}
.sp-sec{margin-bottom:28px}.sp-sec:last-child{margin-bottom:0}
.sp-sec-title{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:1.1px;color:var(--text3);margin-bottom:14px}
.sp-row{
  display:flex;align-items:flex-start;justify-content:space-between;
  gap:16px;padding:13px 0;border-bottom:1px solid var(--border);
}
.sp-row:last-child{border-bottom:none}
.sp-lbl{font-size:14px;font-weight:500}
.sp-desc{font-size:12px;color:var(--text2);margin-top:3px;line-height:1.5}
.tog{position:relative;width:46px;height:26px;flex-shrink:0}
.tog input{opacity:0;width:0;height:0}
.tog-track{
  position:absolute;inset:0;border-radius:26px;
  background:var(--surface2);cursor:pointer;transition:background .2s;
}
.tog-track::after{
  content:'';position:absolute;width:20px;height:20px;border-radius:50%;
  background:#fff;top:3px;left:3px;
  transition:transform .22s var(--spring);box-shadow:0 1px 4px rgba(0,0,0,.4);
}
.tog input:checked + .tog-track{background:var(--accent)}
.tog input:checked + .tog-track::after{transform:translateX(20px)}
.seg{display:flex;gap:3px;background:var(--surface2);border-radius:10px;padding:3px;flex-shrink:0}
.seg button{padding:5px 12px;border-radius:8px;border:none;background:none;font-size:13px;color:var(--text2);font-weight:500;transition:all .15s;white-space:nowrap}
.seg button.on{background:var(--bg);color:var(--text);font-weight:700;box-shadow:0 1px 6px rgba(0,0,0,.25)}
.about-card{
  background:linear-gradient(135deg,rgba(var(--accent-rgb),.08),rgba(var(--accent-rgb),.03));
  border:1px solid rgba(var(--accent-rgb),.2);
  border-radius:14px;padding:18px 20px;font-size:13.5px;line-height:1.7;color:var(--text2);
}
.about-card .a-title{font-size:16px;font-weight:800;color:var(--text);margin-bottom:10px;display:flex;align-items:center;gap:10px;letter-spacing:-.3px}
.a-badge{font-size:10.5px;padding:2px 8px;border-radius:10px;background:rgba(var(--accent-rgb),.18);color:var(--accent);font-weight:700;letter-spacing:.3px}
.about-card p{margin-bottom:10px}.about-card p:last-child{margin-bottom:0}
.legal-card{background:var(--surface2);border:1px solid var(--border2);border-radius:14px;padding:18px 20px;font-size:12.5px;line-height:1.75;color:var(--text2)}
.legal-card .l-title{font-size:13px;font-weight:800;color:var(--text);margin-bottom:12px}
.legal-card p{margin-bottom:8px}.legal-card p:last-child{margin-bottom:0}
.legal-footer{margin-top:14px;padding-top:12px;border-top:1px solid var(--border);font-size:11px;color:var(--text3);text-align:center;letter-spacing:.3px}
.danger-btn{width:100%;padding:11px;border-radius:10px;border:1px solid rgba(239,68,68,.3);background:rgba(239,68,68,.05);color:var(--red);font-size:13.5px;font-weight:500;transition:all .15s}
.danger-btn:hover{background:rgba(239,68,68,.12);border-color:var(--red)}

/* Scroll btn */
#scrollbtn{
  position:fixed;right:24px;bottom:104px;
  width:38px;height:38px;border-radius:50%;
  background:var(--surface2);border:1px solid var(--border2);
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  color:var(--text2);display:none;align-items:center;justify-content:center;
  box-shadow:0 6px 22px rgba(0,0,0,.35);z-index:20;transition:all .15s;
}
#scrollbtn.show{display:flex}
#scrollbtn:hover{background:var(--surface);color:var(--text);transform:scale(1.05)}

/* Mobile */
#mob-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:98;opacity:0;transition:opacity .25s var(--ease)}
@media(min-width:641px){#layout.sb-off #sidebar{width:0;min-width:0}}
@media(max-width:640px){
  #sidebar{position:fixed;top:0;left:0;height:100%;z-index:99;transform:translateX(calc(-1 * var(--sw)));transition:transform .3s var(--ease);min-width:var(--sw)}
  #layout.mob-sb #sidebar{transform:translateX(0)}
  #layout.mob-sb #mob-bg{display:block;opacity:1}
  #chat-inner{padding:0 14px}
  #input-area{padding:10px 12px 16px}
  .bubble{max-width:96%}
}
</style>
</head>
<body>

<!-- Animated bg layers -->
<div id="bg-direct" class="bg-layer on"></div>
<div id="bg-byok" class="bg-layer"></div>

<div id="mob-bg"></div>
<button id="scrollbtn" title="Scroll to bottom">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>
</button>

<!-- Settings overlay -->
<div class="overlay" id="soverlay">
  <div id="sp">
    <div class="sp-head">
      <h2>&#9881; Settings</h2>
      <button class="sp-x" id="sp-close"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="sp-body">
      <div class="sp-sec">
        <div class="sp-sec-title">Appearance</div>
        <div class="sp-row">
          <div><div class="sp-lbl">Dark Mode</div><div class="sp-desc">Toggle dark and light theme</div></div>
          <label class="tog"><input type="checkbox" id="tog-dark" checked><span class="tog-track"></span></label>
        </div>
        <div class="sp-row">
          <div><div class="sp-lbl">Font Size</div><div class="sp-desc">Adjust message text size</div></div>
          <div class="seg" id="seg-font">
            <button data-v="13">S</button><button data-v="15" class="on">M</button><button data-v="17">L</button>
          </div>
        </div>
      </div>
      <div class="sp-sec">
        <div class="sp-sec-title">About Aether</div>
        <div class="about-card">
          <div class="a-title">&#11041; Aether AI <span class="a-badge">v3.0 &middot; 2026</span></div>
          <p>Aether is a next-generation AI assistant built by <strong>Sai Chatre</strong> in 2026. Powered by Meta's <strong>Llama 3.1 70B</strong> via NVIDIA's AI cloud, delivering frontier-level intelligence directly in your browser.</p>
          <p><strong>Direct Chat</strong> uses Aether's built-in API key. <strong>Custom API Key</strong> mode lets you bring your own NVIDIA key for a fully personal, independent session.</p>
          <p>Your conversations stay <strong>100% private on your device</strong> — nothing is stored on any server.</p>
        </div>
      </div>
      <div class="sp-sec">
        <div class="sp-sec-title">Legal &amp; Copyright</div>
        <div class="legal-card">
          <div class="l-title">Terms of Use &amp; Privacy Policy</div>
          <p><strong>Privacy:</strong> Aether stores no conversation data on any server. All history is kept exclusively in your browser's local storage.</p>
          <p><strong>AI Limitations:</strong> Responses are AI-generated and may be inaccurate. Do not rely on Aether for medical, legal, financial, or safety-critical decisions.</p>
          <p><strong>Acceptable Use:</strong> You agree not to use Aether to generate illegal content or attempt to compromise the service.</p>
          <p><strong>Intellectual Property:</strong> Aether AI &copy; 2026 Sai Chatre. All rights reserved.</p>
          <div class="legal-footer">&copy; 2026 Sai Chatre &mdash; Aether AI &mdash; All rights reserved</div>
        </div>
      </div>
      <div class="sp-sec">
        <div class="sp-sec-title">Data</div>
        <button class="danger-btn" id="clear-all-btn">&#128465; Clear All Conversations</button>
      </div>
    </div>
  </div>
</div>

<!-- Main layout -->
<div id="layout">
  <div id="sidebar">
    <div id="sb-inner">

      <div id="sb-top">
        <div class="brand">
          <div class="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <div><div class="brand-name">Aether</div><div class="brand-tag">AI</div></div>
        </div>
        <button class="ib" id="sb-toggle-desk" title="Toggle sidebar">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="3"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
        </button>
      </div>

      <!-- Mode selector -->
      <div id="mode-selector">
        <button class="mode-pill on" data-mode="direct">&#9889; Direct Chat</button>
        <button class="mode-pill" data-mode="byok">&#128273; Custom Key</button>
      </div>

      <!-- BYOK key section -->
      <div id="byok-section" style="display:none">
        <div class="byok-label">Your NVIDIA API Key</div>
        <input type="password" id="byok-input" placeholder="nvapi-...">
        <button id="byok-save">Save &amp; Activate Key</button>
        <div id="byok-status" class="byok-status none">No key saved</div>
        <div class="byok-note">&#128274; Stored in your browser only &mdash; never sent to our servers</div>
      </div>

      <!-- Advanced Settings -->
      <div id="adv-wrap">
        <button id="adv-toggle">
          &#9965; Advanced Settings
          <span id="adv-chevron">&#9654;</span>
        </button>
        <div id="adv-body">
          <div class="adv-inner">
            <div class="adv-row">
              <div class="adv-lbl">Model</div>
              <select id="model-sel">
                <option value="meta/llama-3.1-70b-instruct">Llama 3.1 70B (Default)</option>
                <option value="meta/llama-3.1-8b-instruct">Llama 3.1 8B &middot; Fast</option>
                <option value="meta/llama-3.3-70b-instruct">Llama 3.3 70B &middot; New</option>
                <option value="mistralai/mistral-7b-instruct-v0.3">Mistral 7B</option>
                <option value="google/gemma-2-9b-it">Gemma 2 9B</option>
              </select>
            </div>
            <div class="adv-row">
              <div class="adv-lbl">Temperature <span class="adv-val" id="adv-temp-val">0.50</span></div>
              <input type="range" id="adv-temp" min="0" max="1" step="0.05" value="0.5">
            </div>
            <div class="adv-row">
              <div class="adv-lbl">Max Tokens <span class="adv-val" id="adv-tok-val">4096</span></div>
              <input type="range" id="adv-tok" min="256" max="8192" step="256" value="4096">
            </div>
          </div>
        </div>
      </div>

      <button id="new-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New chat
      </button>

      <div id="history"></div>

      <div id="sb-foot">
        <button class="sb-action" id="settings-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          Settings &amp; About
        </button>
      </div>

    </div>
  </div>

  <div id="main">
    <div id="topbar">
      <button class="ib" id="mob-menu" title="Menu">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <div style="display:flex;align-items:center;gap:8px">
        <div id="model-chip">
          <div class="live-dot"></div>
          <span id="chip-model-name">Llama 3.1 70B</span>
        </div>
        <div id="mode-badge">DIRECT</div>
      </div>
      <button class="ib" id="top-settings" title="Settings">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </button>
    </div>

    <div id="chat-scroll">
      <div id="chat-inner">
        <div id="empty">
          <div class="es-orb">
            <div class="es-orb-ring"></div>
            <div class="es-logo">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
          </div>
          <h2>Hello, I'm Aether</h2>
          <p>Your intelligent AI assistant, powered by Llama 3.1 70B. Ask me anything.</p>
          <div class="chips">
            <button class="chip">Write a Python web scraper</button>
            <button class="chip">Explain quantum entanglement</button>
            <button class="chip">Debug my JavaScript code</button>
            <button class="chip">Create a business plan outline</button>
            <button class="chip">Summarise a research topic</button>
          </div>
        </div>
      </div>
    </div>

    <div id="input-area">
      <div id="input-wrap">
        <textarea id="msg-input" rows="1" placeholder="Message Aether..."></textarea>
        <button id="send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
        </button>
      </div>
      <div id="hint">Aether AI &mdash; by Sai Chatre &middot; 2026 &middot; Responses may be inaccurate</div>
    </div>
  </div>
</div>

<script>
// ══════════════════════════════════════════
//  MODE & STORAGE
// ══════════════════════════════════════════
const STORE_KEYS = { direct: "aether_direct_v1", byok: "aether_byok_v1" };
const BYOK_KEY_STORE = "aether_byok_apikey";

let currentMode = localStorage.getItem("aether_mode") || "direct";
let currentId   = null;

function getStoreKey()  { return STORE_KEYS[currentMode]; }
function load()         { try { return JSON.parse(localStorage.getItem(getStoreKey())) || {}; } catch { return {}; } }
function save(d)        { localStorage.setItem(getStoreKey(), JSON.stringify(d)); }
function getStore() {
  const d = load();
  if (!d.sessions) d.sessions = {};
  if (!d.order)    d.order    = [];
  if (!d.cfg)      d.cfg      = {};
  return d;
}
function getSession(id) { return getStore().sessions[id]; }
function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }

function getSavedByokKey() { return localStorage.getItem(BYOK_KEY_STORE) || ""; }
function saveByokKey(k)    { localStorage.setItem(BYOK_KEY_STORE, k); }

// ══════════════════════════════════════════
//  CONFIG
// ══════════════════════════════════════════
const CFG_DEFAULTS = { dark:true, fontSize:15 };
function getCfg() { return { ...CFG_DEFAULTS, ...getStore().cfg }; }
function setCfg(patch) { const d = getStore(); d.cfg = { ...getCfg(), ...patch }; save(d); }

// Advanced settings (global, not per-mode-store)
function getAdv() {
  try { return JSON.parse(localStorage.getItem("aether_adv")) || {}; } catch { return {}; }
}
function setAdv(patch) { localStorage.setItem("aether_adv", JSON.stringify({ ...getAdv(), ...patch })); }
function getAdvVal(k, def) { const v = getAdv()[k]; return v !== undefined ? v : def; }

// ══════════════════════════════════════════
//  APPLY THEME & FONT
// ══════════════════════════════════════════
function applyTheme(dark) { document.documentElement.setAttribute("data-theme", dark ? "dark" : "light"); }
function applyFont(sz)    { document.querySelectorAll(".bubble").forEach(b => b.style.fontSize = sz + "px"); }
function applyAll() {
  const c = getCfg();
  applyTheme(c.dark);
  document.getElementById("tog-dark").checked = c.dark;
  document.querySelectorAll("#seg-font button").forEach(b => b.classList.toggle("on", +b.dataset.v === c.fontSize));
  applyFont(c.fontSize);
}

// ══════════════════════════════════════════
//  MODE SWITCHING
// ══════════════════════════════════════════
function applyMode(mode) {
  document.documentElement.setAttribute("data-mode", mode);
  document.getElementById("bg-direct").classList.toggle("on", mode === "direct");
  document.getElementById("bg-byok").classList.toggle("on", mode === "byok");
  document.querySelectorAll(".mode-pill").forEach(p => p.classList.toggle("on", p.dataset.mode === mode));
  const byokSec = document.getElementById("byok-section");
  byokSec.style.display = mode === "byok" ? "" : "none";
  document.getElementById("mode-badge").textContent = mode === "byok" ? "BYOK" : "DIRECT";
  updateByokStatus();
}

function switchMode(mode) {
  if (mode === currentMode) return;
  currentMode = mode;
  localStorage.setItem("aether_mode", mode);
  currentId = null;
  applyMode(mode);
  chatInner.querySelectorAll(".msg-row").forEach(e => e.remove());
  showEmpty(true);
  renderHistory();
}

function updateByokStatus() {
  const k = getSavedByokKey();
  const el = document.getElementById("byok-status");
  if (k) {
    el.textContent = "Key saved: " + k.slice(0,12) + "...";
    el.className = "byok-status ok";
  } else {
    el.textContent = "No key saved";
    el.className = "byok-status none";
  }
}

// ══════════════════════════════════════════
//  MARKDOWN + CODE BLOCKS
// ══════════════════════════════════════════
marked.setOptions({ breaks:true, gfm:true });
const renderer = new marked.Renderer();
renderer.code = function(code, lang) {
  const language = lang || "plaintext";
  const id = "cb_" + uid();
  let hl;
  try { hl = hljs.highlight(code, { language, ignoreIllegals:true }).value; }
  catch { hl = hljs.highlightAuto(code).value; }
  return `<div class="code-wrap">
    <div class="code-head">
      <span class="code-lang">${language}</span>
      <button class="cp-btn" onclick="copyCode('${id}')">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button>
    </div>
    <pre><code id="${id}" class="hljs">${hl}</code></pre>
  </div>`;
};
marked.use({ renderer });

function copyCode(id) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {
    const btn = el.closest(".code-wrap").querySelector(".cp-btn");
    btn.classList.add("ok"); btn.textContent = "Copied!";
    setTimeout(() => { btn.classList.remove("ok"); btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy'; }, 2000);
  });
}
function renderMd(text) { const d = document.createElement("div"); d.className = "md"; d.innerHTML = marked.parse(text); return d; }

// ══════════════════════════════════════════
//  DOM REFS
// ══════════════════════════════════════════
const chatInner  = document.getElementById("chat-inner");
const chatScroll = document.getElementById("chat-scroll");
const msgInput   = document.getElementById("msg-input");
const sendBtn    = document.getElementById("send");
const emptyEl    = document.getElementById("empty");
const historyEl  = document.getElementById("history");
const layout     = document.getElementById("layout");

// ══════════════════════════════════════════
//  SCROLL
// ══════════════════════════════════════════
function scrollBottom(force) {
  if (force || chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight < 200) {
    chatScroll.scrollTop = chatScroll.scrollHeight;
  }
}
chatScroll.addEventListener("scroll", () => {
  const far = chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight > 200;
  document.getElementById("scrollbtn").classList.toggle("show", far);
});
document.getElementById("scrollbtn").addEventListener("click", () => scrollBottom(true));

// ══════════════════════════════════════════
//  HISTORY PANEL
// ══════════════════════════════════════════
function renderHistory() {
  const d = getStore();
  if (!d.order.length) { historyEl.innerHTML = '<div class="h-empty">No conversations yet</div>'; return; }
  const now = Date.now(), day = 86400000;
  const groups = { today:[], yesterday:[], week:[], older:[] };
  d.order.forEach(id => {
    const s = d.sessions[id]; if (!s) return;
    const age = now - (s.ts || 0);
    if (age < day) groups.today.push(id);
    else if (age < 2*day) groups.yesterday.push(id);
    else if (age < 7*day) groups.week.push(id);
    else groups.older.push(id);
  });
  let html = "";
  const sec = (label, ids) => {
    if (!ids.length) return;
    html += `<div class="h-sec">${label}</div>`;
    ids.forEach(id => {
      const s = d.sessions[id];
      html += `<div class="h-item${id===currentId?" active":""}" data-id="${id}"><div class="h-dot"></div><span>${s.title||"Untitled"}</span></div>`;
    });
  };
  sec("Today",groups.today); sec("Yesterday",groups.yesterday); sec("This week",groups.week); sec("Older",groups.older);
  historyEl.innerHTML = html;
  historyEl.querySelectorAll(".h-item").forEach(el => {
    el.addEventListener("click", () => { currentId = el.dataset.id; renderSession(currentId); renderHistory(); if(window.innerWidth<=640) closeMobSidebar(); });
  });
}

// ══════════════════════════════════════════
//  RENDER SESSION
// ══════════════════════════════════════════
function showEmpty(show) { emptyEl.style.display = show ? "" : "none"; }

function renderSession(id) {
  const s = getSession(id);
  if (!s) return;
  showEmpty(false);
  chatInner.querySelectorAll(".msg-row").forEach(e => e.remove());
  s.messages.forEach(m => appendBubble(m.role, m.content, false));
  scrollBottom(true);
}

function appendBubble(role, content, animate=true) {
  const row = document.createElement("div");
  row.className = "msg-row " + role;
  if (!animate) row.style.animation = "none";
  const label = document.createElement("div");
  label.className = "msg-label";
  label.textContent = role === "user" ? "You" : "Aether";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.style.fontSize = getCfg().fontSize + "px";
  if (role === "user") {
    bubble.textContent = content;
  } else {
    bubble.appendChild(renderMd(content));
    const copyBtn = document.createElement("button");
    copyBtn.className = "bot-copy-btn";
    copyBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy response';
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(content).then(() => {
        copyBtn.classList.add("ok"); copyBtn.textContent = "Copied!";
        setTimeout(() => { copyBtn.classList.remove("ok"); copyBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy response'; }, 2000);
      });
    });
    bubble.appendChild(copyBtn);
  }
  row.appendChild(label); row.appendChild(bubble);
  chatInner.appendChild(row);
  return bubble;
}

// ══════════════════════════════════════════
//  NEW CHAT
// ══════════════════════════════════════════
function newChat() {
  currentId = null;
  chatInner.querySelectorAll(".msg-row").forEach(e => e.remove());
  showEmpty(true);
  msgInput.value = "";
  autoResize();
  renderHistory();
}
document.getElementById("new-btn").addEventListener("click", () => { newChat(); closeMobSidebar(); });

// ══════════════════════════════════════════
//  SEND
// ══════════════════════════════════════════
let busy = false;

async function send() {
  const text = msgInput.value.trim();
  if (!text || busy) return;

  if (currentMode === "byok" && !getSavedByokKey()) {
    appendBubble("bot", "Please save your NVIDIA API key in the **Custom Key** section of the sidebar before chatting in this mode.");
    return;
  }

  busy = true;
  sendBtn.disabled = true;

  if (!currentId) {
    const id = uid();
    const d = getStore();
    d.sessions[id] = { title: text.slice(0,40), ts: Date.now(), messages: [] };
    d.order.unshift(id);
    save(d);
    currentId = id;
    renderHistory();
  }

  const d1 = getStore();
  d1.sessions[currentId].messages.push({ role:"user", content:text });
  save(d1);

  showEmpty(false);
  appendBubble("user", text);
  msgInput.value = "";
  autoResize();
  scrollBottom(true);

  const thinkRow = document.createElement("div");
  thinkRow.className = "msg-row bot";
  thinkRow.innerHTML = `<div class="msg-label">Aether</div><div class="think"><div class="think-dots"><span></span><span></span><span></span></div><span>Thinking…</span></div>`;
  chatInner.appendChild(thinkRow);
  scrollBottom(true);

  const sess = getSession(currentId);
  const history = sess.messages.slice(0,-1).map(m => ({ role:m.role, content:m.content }));

  const temp   = parseFloat(document.getElementById("adv-temp").value);
  const tokens = parseInt(document.getElementById("adv-tok").value);
  const model  = document.getElementById("model-sel").value;

  const payload = { message:text, history, temperature:temp, max_tokens:tokens, model };
  if (currentMode === "byok") payload.byok_key = getSavedByokKey();

  try {
    const res  = await fetch("/api/chat", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
    const json = await res.json();
    thinkRow.remove();
    const reply = json.reply || json.error || "Something went wrong.";
    appendBubble("bot", reply);
    const d2 = getStore();
    d2.sessions[currentId].messages.push({ role:"assistant", content:reply });
    save(d2);
    renderHistory();
  } catch(e) {
    thinkRow.remove();
    appendBubble("bot", "Connection error. Please try again.");
  }

  busy = false;
  sendBtn.disabled = false;
  scrollBottom(true);
}

// ══════════════════════════════════════════
//  SETTINGS MODAL
// ══════════════════════════════════════════
function openSettings()  { document.getElementById("soverlay").classList.add("show"); applyAll(); }
function closeSettings() { document.getElementById("soverlay").classList.remove("show"); }
document.getElementById("settings-btn").addEventListener("click", openSettings);
document.getElementById("top-settings").addEventListener("click", openSettings);
document.getElementById("sp-close").addEventListener("click", closeSettings);
document.getElementById("soverlay").addEventListener("click", e => { if(e.target.id==="soverlay") closeSettings(); });

document.getElementById("tog-dark").addEventListener("change", e => { setCfg({dark:e.target.checked}); applyTheme(e.target.checked); });
document.querySelectorAll("#seg-font button").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("#seg-font button").forEach(x => x.classList.remove("on"));
  b.classList.add("on"); const sz = +b.dataset.v; setCfg({fontSize:sz}); applyFont(sz);
}));
document.getElementById("clear-all-btn").addEventListener("click", () => {
  if (confirm("Delete ALL conversations in this mode? This cannot be undone.")) {
    localStorage.removeItem(getStoreKey()); newChat();
  }
});

// ══════════════════════════════════════════
//  MODE PILLS
// ══════════════════════════════════════════
document.querySelectorAll(".mode-pill").forEach(p => {
  p.addEventListener("click", () => switchMode(p.dataset.mode));
});

// ══════════════════════════════════════════
//  BYOK KEY
// ══════════════════════════════════════════
document.getElementById("byok-save").addEventListener("click", () => {
  const key = document.getElementById("byok-input").value.trim();
  if (key) { saveByokKey(key); document.getElementById("byok-input").value = ""; updateByokStatus(); }
});

// ══════════════════════════════════════════
//  ADVANCED SETTINGS
// ══════════════════════════════════════════
document.getElementById("adv-toggle").addEventListener("click", () => {
  const body    = document.getElementById("adv-body");
  const chevron = document.getElementById("adv-chevron");
  const isOpen  = body.classList.toggle("open");
  chevron.style.transform = isOpen ? "rotate(90deg)" : "rotate(0deg)";
});

document.getElementById("adv-temp").addEventListener("input", e => {
  document.getElementById("adv-temp-val").textContent = parseFloat(e.target.value).toFixed(2);
  setAdv({ temperature: parseFloat(e.target.value) });
});
document.getElementById("adv-tok").addEventListener("input", e => {
  document.getElementById("adv-tok-val").textContent = e.target.value;
  setAdv({ maxTokens: parseInt(e.target.value) });
});
document.getElementById("model-sel").addEventListener("change", e => {
  const names = {
    "meta/llama-3.1-70b-instruct":"Llama 3.1 70B",
    "meta/llama-3.1-8b-instruct":"Llama 3.1 8B",
    "meta/llama-3.3-70b-instruct":"Llama 3.3 70B",
    "mistralai/mistral-7b-instruct-v0.3":"Mistral 7B",
    "google/gemma-2-9b-it":"Gemma 2 9B"
  };
  document.getElementById("chip-model-name").textContent = names[e.target.value] || e.target.value;
  setAdv({ model: e.target.value });
});

// Restore adv settings
(function restoreAdv() {
  const adv = getAdv();
  if (adv.temperature !== undefined) {
    document.getElementById("adv-temp").value = adv.temperature;
    document.getElementById("adv-temp-val").textContent = parseFloat(adv.temperature).toFixed(2);
  }
  if (adv.maxTokens !== undefined) {
    document.getElementById("adv-tok").value = adv.maxTokens;
    document.getElementById("adv-tok-val").textContent = adv.maxTokens;
  }
  if (adv.model) {
    document.getElementById("model-sel").value = adv.model;
    const names = {"meta/llama-3.1-70b-instruct":"Llama 3.1 70B","meta/llama-3.1-8b-instruct":"Llama 3.1 8B","meta/llama-3.3-70b-instruct":"Llama 3.3 70B","mistralai/mistral-7b-instruct-v0.3":"Mistral 7B","google/gemma-2-9b-it":"Gemma 2 9B"};
    document.getElementById("chip-model-name").textContent = names[adv.model] || adv.model;
  }
})();

// ══════════════════════════════════════════
//  SIDEBAR TOGGLES
// ══════════════════════════════════════════
function closeMobSidebar() { layout.classList.remove("mob-sb"); }
document.getElementById("sb-toggle-desk").addEventListener("click", e => {
  e.stopPropagation();
  if (window.innerWidth <= 640) closeMobSidebar();
  else layout.classList.toggle("sb-off");
});
document.getElementById("mob-menu").addEventListener("click", e => {
  e.stopPropagation();
  layout.classList.add("mob-sb");
});
document.getElementById("mob-bg").addEventListener("click", closeMobSidebar);

// ══════════════════════════════════════════
//  TEXTAREA AUTO-RESIZE
// ══════════════════════════════════════════
function autoResize() { msgInput.style.height = "auto"; msgInput.style.height = Math.min(msgInput.scrollHeight, 180) + "px"; }
msgInput.addEventListener("input", autoResize);
msgInput.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
sendBtn.addEventListener("click", send);
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  msgInput.value = c.textContent.trim();
  msgInput.dispatchEvent(new Event("input"));
  msgInput.focus();
}));

// ══════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════
applyAll();
applyMode(currentMode);
renderHistory();
if (currentId && getSession(currentId)) renderSession(currentId);
else showEmpty(true);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/api/chat", methods=["POST"])
def chat():
    data         = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    history      = data.get("history", [])
    temperature  = float(data.get("temperature", 0.5))
    max_tokens   = int(data.get("max_tokens", 4096))
    byok_key     = data.get("byok_key", "").strip()
    model        = data.get("model", DEFAULT_MODEL)

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    key_to_use = byok_key if byok_key else SERVER_API_KEY
    if not key_to_use:
        return jsonify({"error": "No API key configured. Add your NVIDIA API key in the sidebar."}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        role    = msg.get("role", "")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {key_to_use}",
        "Content-Type":  "application/json",
        "Accept":        "text/event-stream",
    }
    payload = {
        "model":       model,
        "messages":    messages,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "top_p":       0.7,
        "stream":      True,
    }

    try:
        sess = requests.Session()
        r    = sess.post(INVOKE_URL, headers=headers, json=payload, stream=True, timeout=(20, 120))
        r.raise_for_status()
        full_reply = ""
        for line in r.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8").strip()
            if line_str.startswith("data:"):
                chunk = line_str[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj   = json.loads(chunk)
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:
                        full_reply += delta
                except Exception:
                    pass
        if full_reply:
            return jsonify({"reply": full_reply})
        return jsonify({"error": "Empty response from AI"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, threaded=True)
