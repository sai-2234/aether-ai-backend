---
title: Aether AI Backend
emoji: ⚡
colorFrom: purple
colorTo: cyan
sdk: docker
pinned: false
---

# Aether AI — Backend API

Flask API backend for [Aether AI](https://aether-ai.pages.dev) by Sai Chatre.

## Setup

Add your NVIDIA API key as a Space secret:
- Key name: `NVIDIA_API_KEY`
- Value: your key from [build.nvidia.com](https://build.nvidia.com)

## Endpoints

- `GET /` — health check
- `POST /api/chat` — send a message, get a reply
