# Scarlet AI 🤖✨

Scarlet is a **privacy-aware, emotionally intelligent, voice-first AI assistant framework** designed to run on both **high-performance systems (Raspberry Pi 5 / PC)** and **low-resource devices (Raspberry Pi Zero 2 W)**.

This repository provides a **sanitized, demo-friendly version** of Scarlet intended for **learning, showcasing architecture, and portfolio/interview purposes**, while keeping sensitive or personal implementations private.

---

## 🌟 Vision

Scarlet is not just a chatbot, but she is personal companion.

She is designed as:

* A **human-like conversational assistant**
* A **voice-first AI companion**
* A **modular AI platform** for experimentation
* A **safe, controllable, and explainable AI system**

Primary long-term goals include:

* Elder-care and hospital assistance
* Hands-free home AI
* Emotion-aware interactions
* Safe semi-autonomous behaviors

---

## 🧠 Core Concepts

Scarlet is built around the following principles:

* **Voice First** – Wake-word, VAD-based listening, TTS responses
* **Session Awareness** – Conversations persist without repeated wake-words
* **Role-Based Behavior** – Creator / Known User / Guest logic
* **Emotion & Tone Modeling** – Responses adapt to context and user
* **Safety First** – Explicit rules, filters, and kill-switch design
* **Hardware-Aware** – Same architecture scales from Pi Zero to Pi 5

---

## 🧩 Projects in the Scarlet Ecosystem

### 1️⃣ Scarlet (Main)

High-capability version designed for:

* Raspberry Pi 5 / PC
* Offline + Online hybrid usage
* Rich TTS (Piper / Google TTS)
* Advanced VAD + Faster-Whisper STT
* Emotion videos / expressions

### 2️⃣ Jasmine (Mini Scarlet)

Lightweight online-only version designed for:

* Raspberry Pi Zero 2 W
* Low memory and CPU
* Groq-hosted Whisper + LLM
* gTTS / lightweight TTS

> This repository primarily focuses on **Scarlet Core Architecture**, with references to Jasmine where relevant.

---

## 🏗️ High-Level Architecture

```
Wake Word Detection
        ↓
Face / User Identification (Optional)
        ↓
Conversation Session Manager
        ↓
Voice Activity Detection (Silero VAD)
        ↓
Speech-to-Text (Faster-Whisper / Groq Whisper)
        ↓
Intent & Behavior Routing
        ↓
LLM (Groq / Mistral / Mock)
        ↓
Response Styling & Emotion Layer
        ↓
Text-to-Speech (Piper / gTTS / Google TTS)
```

---

## 📁 Repository Structure (Sanitized)

```
scarlet/
├── main.py                 # Entry point
├── conversation_mode.py    # VAD-based conversation loop
├── handler.py              # Intent + role-based routing
├── tts.py                  # Text-to-Speech abstraction
├── wake_word.py            # Wake word logic (stub/demo)
├── memory_mood.py          # Mood & affect tracking
├── persona/
│   ├── persona.yaml        # Assistant personality (sanitized)
│   └── rules.yaml          # Behavior & safety rules
├── utils/
│   ├── utils_time.py       # Date & time handling
│   └── audio_utils.py
├── demo/
│   ├── mock_llm.py         # Mock LLM for demo mode
│   └── mock_tts.py
├── requirements.txt
└── README.md
```

> ⚠️ **Note:** Some internal files (face recognition, private scripts, expression assets) are intentionally excluded.

---

## 🔊 Speech Stack

### 🎙️ Input (STT)

* **Faster-Whisper** (local, high accuracy)
* **Groq Whisper API** (online, low latency)

### 🗣️ Output (TTS)

* Piper (offline, natural voice)
* gTTS (lightweight)
* Google Cloud TTS (neural voices – optional)

---

## 🧠 LLM Integration

Scarlet supports pluggable LLM backends:

* **Groq API** (Ultra-fast inference)
* **Mistral 7B** (local / self-hosted)
* **Mock LLM** (demo & testing)

LLMs are **never allowed to act directly** — all actions pass through:

* Rule filters
* Role checks
* Safety guards

---

## 🎭 Personality & Behavior

Behavior is **configuration-driven**, not hardcoded.

### Role Examples:

* **Creator** – Full access
* **Known User** – Helpful, respectful
* **Guest** – Restricted, safe defaults

### Features:

* Emotional tone mirroring
* Respectful boundaries
* No disclosure of private/internal data
* Context-aware response shaping

---

## 🛡️ Safety & Control Model

Scarlet is designed with **explicit safety layers**:

* Kill-switch architecture
* Action caps
* Two-step confirmations
* Wake-word & face-gated commands
* Sensor consent rules
* Tool isolation
* Audit-friendly logs

This makes Scarlet suitable for **real-world environments**, not just demos.

---


```
Demo mode uses:

* Mock LLM
* Mock TTS
* Keyboard input fallback

---

## 🧪 Who Is This Repo For?

* AI / ML Engineers
* Voice Assistant Developers
* Embedded AI enthusiasts
* Recruiters & Interview Panels
* System architects

---

## 📌 What This Repo Is NOT

* ❌ A consumer-ready assistant
* ❌ A fully autonomous AI
* ❌ A jailbreak / uncensored LLM project

This is a **responsible AI system design project**.

---

## 🧭 Roadmap (Public)

* [ ] Barge-in during TTS
* [ ] Unified SSML emotion profiles
* [ ] LED / hardware feedback hooks
* [ ] Better memory TTL handling
* [ ] Plugin-based skills

---

## 👤 Author

**Naga**
AI Engineer | Middleware Architect | Voice AI Systems

> Built as a solo project with a focus on learning, safety, and real-world usability.

---

## 📜 License

This project is licensed under the Apache License, Version 2.0.

You may use, modify, and distribute this code in compliance with the Apache-2.0 license.
Attribution and inclusion of the license notice are required.

This repository contains a sanitized, demo-friendly version of the Scarlet project intended for learning, architectural review, and portfolio purposes.

Private extensions, internal assets, datasets, credentials, and personal configurations are not included in this repository and are not covered by this license.

See the LICENSE file for the full license text.

---

## ⭐ Final Note

Scarlet represents a **bridge between classic software engineering and modern AI systems** — combining discipline, safety, and creativity.

If you are reviewing this repo as part of an interview or evaluation, please treat it as a **system design showcase**, not just a codebase.
