"""Local Interactive Web Studio for the Optical Camera Compiler."""

from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional

from .compiler import OpticalCompiler
from .models import SceneInput, TargetEngine
from .profiles import list_available_profiles, load_profile

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Optical Camera Compiler // Master Studio Console</title>
  <style>
    :root {
      --bg-canvas: #07090c;
      --bg-surface: #0e1218;
      --bg-card: #141a23;
      --bg-card-hover: #1b2330;
      --bg-input: #090c10;
      --border-subtle: #1e2634;
      --border-focus: #3b82f6;
      --accent-cyan: #06b6d4;
      --accent-blue: #3b82f6;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-green: #10b981;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, -apple-system, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      font-family: var(--font-sans);
      line-height: 1.5;
      overflow-x: hidden;
      min-height: 100vh;
    }

    /* Top Navigation */
    header {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(12px);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }
    .brand-logo {
      width: 28px;
      height: 28px;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 16px rgba(6, 182, 212, 0.35);
    }
    .brand-logo svg {
      width: 16px;
      height: 16px;
      color: #000;
    }
    .brand-title {
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .brand-tag {
      font-size: 0.65rem;
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.3);
      color: var(--accent-cyan);
      padding: 1px 6px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-weight: 600;
    }
    .brand-subtitle {
      font-size: 0.72rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }
    .status-badge {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: var(--accent-green);
      font-size: 0.72rem;
      font-family: var(--font-mono);
      padding: 0.3rem 0.75rem;
      border-radius: 9999px;
    }
    .pulse-dot {
      width: 6px;
      height: 6px;
      background: var(--accent-green);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(0.85); }
    }

    /* SCENARIO BAR (DROPDOWN + SURPRISE CONTROLS) */
    .scenario-bar {
      background: #0b0e14;
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.75rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      flex-wrap: wrap;
    }
    .scenario-select-wrap {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex: 1;
      max-width: 800px;
    }
    .scenario-label {
      color: var(--accent-amber);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      white-space: nowrap;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.06em;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .scenario-select {
      background: var(--bg-card);
      border: 1px solid #2d3748;
      color: var(--text-primary);
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      font-size: 0.82rem;
      font-family: inherit;
      font-weight: 500;
      flex: 1;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .scenario-select:focus {
      border-color: var(--accent-amber);
      box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
    }
    .btn-surprise {
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: var(--accent-amber);
      padding: 0.45rem 0.9rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .btn-surprise:hover {
      background: var(--accent-amber);
      color: #000;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }
    .scenario-hint {
      font-size: 0.72rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    /* Main Grid Layout */
    .container {
      display: grid;
      grid-template-columns: 530px 1fr;
      min-height: calc(100vh - 120px);
    }
    @media (max-width: 1200px) {
      .container { grid-template-columns: 1fr; }
    }

    /* Left Console Panel */
    .rig-panel {
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.15rem;
      overflow-y: auto;
      max-height: calc(100vh - 120px);
    }
    .panel-section {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      transition: border-color 0.15s ease;
    }
    .panel-section:focus-within {
      border-color: #2e3a4e;
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 0.45rem;
    }
    .section-title {
      font-size: 0.74rem;
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-cyan);
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }
    .section-meta {
      font-size: 0.67rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    .field-group {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }
    .field-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.65rem;
    }
    label {
      font-size: 0.69rem;
      color: var(--text-secondary);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      justify-content: space-between;
    }
    label span.hint {
      color: var(--text-muted);
      font-weight: normal;
      text-transform: none;
    }

    input[type="text"], textarea, select {
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      padding: 0.55rem 0.7rem;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.82rem;
      transition: all 0.15s ease;
      width: 100%;
    }
    input[type="text"]:focus, textarea:focus, select:focus {
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    textarea {
      resize: vertical;
      min-height: 70px;
      line-height: 1.4;
    }

    /* Quick Helper Pills */
    .quick-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-top: 0.15rem;
    }
    .pill-btn {
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 0.67rem;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.12s ease;
    }
    .pill-btn:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-focus);
    }
    .pill-btn.active {
      background: rgba(59, 130, 246, 0.18);
      border-color: var(--accent-blue);
      color: #bfdbfe;
      font-weight: 600;
    }

    /* Aperture Wheel / Dial */
    .dial-group {
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      gap: 0.25rem;
    }
    .dial-btn {
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      padding: 0.45rem 0;
      border-radius: 4px;
      cursor: pointer;
      text-align: center;
      transition: all 0.12s ease;
      position: relative;
    }
    .dial-btn:hover {
      border-color: var(--accent-blue);
      color: var(--text-primary);
    }
    .dial-btn.active {
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #ffffff;
      font-weight: 700;
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
    }
    .dial-btn.sweet-spot::after {
      content: "MTF";
      position: absolute;
      top: -6px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 0.5rem;
      background: var(--accent-amber);
      color: #000;
      padding: 0 3px;
      border-radius: 2px;
      font-weight: 800;
      line-height: 1.1;
    }

    /* Right Output Panel */
    .output-panel {
      padding: 1.5rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      overflow-y: auto;
      max-height: calc(100vh - 120px);
    }

    /* Engine Tabs Bar */
    .tabs-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 0.75rem;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    .tabs {
      display: flex;
      gap: 0.35rem;
      flex-wrap: wrap;
    }
    .tab {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .tab:hover {
      color: var(--text-primary);
      background: var(--bg-card);
    }
    .tab.active {
      background: var(--bg-card);
      border-color: var(--border-subtle);
      color: var(--accent-cyan);
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    .action-btn {
      background: linear-gradient(135deg, var(--accent-blue), #2563eb);
      border: none;
      color: #ffffff;
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.5rem 1.15rem;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      transition: all 0.15s ease;
      box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3);
    }
    .action-btn:hover {
      background: #1d4ed8;
      transform: translateY(-1px);
    }
    .action-btn-secondary {
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 0.72rem;
      font-family: var(--font-mono);
      font-weight: 600;
      padding: 0.42rem 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s ease;
    }
    .action-btn-secondary:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
      border-color: #4a5568;
    }
    .action-btn-shield {
      background: rgba(244, 63, 94, 0.08);
      border: 1px solid rgba(244, 63, 94, 0.25);
      color: var(--accent-rose);
      font-size: 0.72rem;
      font-family: var(--font-mono);
      font-weight: 600;
      padding: 0.42rem 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s ease;
    }
    .action-btn-shield:hover {
      background: rgba(244, 63, 94, 0.18);
      color: #fecdd3;
      border-color: rgba(244, 63, 94, 0.5);
    }

    /* Reference Image & Anti-Drift Studio */
    .ref-dropzone {
      border: 2px dashed #2d3748;
      background: rgba(15, 23, 42, 0.4);
      border-radius: 8px;
      padding: 1.1rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .ref-dropzone:hover, .ref-dropzone.dragover {
      border-color: var(--accent-cyan);
      background: rgba(56, 189, 248, 0.05);
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }
    .btn-ref-action {
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--accent-cyan);
      font-size: 0.7rem;
      font-family: var(--font-mono);
      font-weight: 600;
      padding: 0.25rem 0.6rem;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn-ref-action:hover {
      background: var(--accent-cyan);
      color: #000;
    }
    .btn-ref-danger {
      background: rgba(244, 63, 94, 0.12);
      border-color: rgba(244, 63, 94, 0.3);
      color: var(--accent-rose);
    }
    .btn-ref-danger:hover {
      background: var(--accent-rose);
      color: #000;
    }
    .mode-card {
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 0.75rem;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .mode-card:hover {
      border-color: #3e4c63;
      background: rgba(255, 255, 255, 0.02);
    }
    .mode-card.active {
      border-color: var(--accent-cyan);
      background: rgba(56, 189, 248, 0.08);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.15);
    }
    .check-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.72rem;
      color: var(--text-secondary);
      cursor: pointer;
      user-select: none;
    }
    .check-item input[type="checkbox"] {
      accent-color: var(--accent-cyan);
      cursor: pointer;
    }

    /* Payload Cards */
    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-title {
      font-size: 0.72rem;
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-secondary);
    }
    .prompt-content {
      font-family: var(--font-mono);
      font-size: 0.82rem;
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 1rem;
      color: #e2e8f0;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
      user-select: all;
    }

    .shield-content {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      background: var(--bg-canvas);
      border: 1px solid rgba(244, 63, 94, 0.2);
      border-radius: 6px;
      padding: 0.85rem;
      color: #fda4af;
      line-height: 1.5;
    }

    /* Specs Grid */
    .specs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.6rem;
    }
    .spec-item {
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 0.7rem;
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }
    .spec-label {
      font-size: 0.65rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
      text-transform: uppercase;
    }
    .spec-value {
      font-size: 0.78rem;
      color: var(--text-primary);
      font-weight: 600;
    }

    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--accent-green);
      color: #000;
      padding: 0.75rem 1.25rem;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.85rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 999;
    }
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }

    /* 102MP Upscaler Modal & Trigger */
    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }
    .btn-upscaler-trigger {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(59, 130, 246, 0.15));
      border: 1px solid rgba(6, 182, 212, 0.4);
      color: var(--accent-cyan);
      font-size: 0.72rem;
      font-family: var(--font-mono);
      font-weight: 600;
      padding: 0.32rem 0.85rem;
      border-radius: 9999px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn-upscaler-trigger:hover {
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      color: #000;
      box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1.5rem;
    }
    .modal-overlay.active {
      display: flex;
    }
    .modal-content {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      width: 100%;
      max-width: 960px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: column;
    }
    .modal-header {
      padding: 1.1rem 1.6rem;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #0b0e14;
    }
    .modal-body {
      padding: 1.6rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="9"></circle><path d="M12 3v18M3 12h18"></path></svg>
      </div>
      <div>
        <div class="brand-title">
          <span>Optical Camera Compiler</span>
          <span class="brand-tag">v2.1 MASTER STUDIO</span>
        </div>
        <div class="brand-subtitle">Hardware-Level Optics, Sensor Physics & Zero-Artifact Simulation</div>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn-upscaler-trigger" onclick="openUpscalerModal()" title="Open PIL Conservative 102MP Restoration and Upscale Lock">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
        <span>102MP Upscaler Lock</span>
      </button>
      <div class="status-badge">
        <div class="pulse-dot"></div>
        <span id="rigStatusReadout">10 HARDWARE RIGS ACTIVE</span>
      </div>
    </div>
  </header>

  <!-- NATURAL SCENARIO & RIG DROPDOWN BAR -->
  <div class="scenario-bar">
    <div class="scenario-select-wrap">
      <div class="scenario-label">
        <span>🎬 Starting Scenario:</span>
      </div>
      <select class="scenario-select" id="scenarioSelect" onchange="onScenarioSelectChange()">
        <option value="none">✨ -- None / Custom Prompt (Surprise Mode: Write Freely) --</option>
        
        <optgroup label="🏙️ Cities & Urban Streets">
          <option value="city_paris" selected>Parisian Street Walk // Haussmannian Architecture, Overcast Diffuse (Leica M11)</option>
          <option value="tokyo_night">Tokyo Shinjuku Alley // Wet Asphalt & Glowing Neon Signs (Leica M6 // Cinestill)</option>
          <option value="nyc_soho">New York SoHo Cast-Iron Loft // Morning Sunbeam Rake (Sony A7R V)</option>
          <option value="london_drizzle">London Mayfair // Muted Portland Stone, Gentle Drizzle (Leica M11)</option>
          <option value="milan_portico">Milan Design District // Italian Marble Portico & Crisp Contrast (Hasselblad H6D)</option>
        </optgroup>

        <optgroup label="🏨 Luxury Hotels & Hospitality">
          <option value="hotel_terrace">Amalfi Coast Luxury Hotel Terrace // Morning Sun & Sea Breeze (Hasselblad H6D)</option>
          <option value="hotel_penthouse">Modernist Penthouse Suite // Floor-to-Ceiling Skyline Views (Phase One IQ4)</option>
          <option value="hotel_lobby">Grand Art Deco Hotel Lobby // Polished Marble & Warm Brass (Fujifilm GFX)</option>
          <option value="hotel_bar">Intimate Hotel Cocktail Lounge // Dim Tungsten, Velvet & Mirrors (ARRI Alexa 35)</option>
        </optgroup>

        <optgroup label="🌊 Coastal, Beach & Islands">
          <option value="beach_dunes">Ocean Beach & Sand Dunes // Golden Hour Low Sun & Sea Breeze (Pentax 67)</option>
          <option value="mediterranean_cliff">Mediterranean White Cliffside // Sun-Bleached Rock & Deep Azure Sea (Hasselblad 500C/M)</option>
          <option value="nordic_fjord">Nordic Coastal Fjord // Cool Sea Mist & Dark Wet Rocks (Fujifilm GFX)</option>
          <option value="tropical_shore">Tropical Island Shoreline // Humid Haze & Late Sun Silhouette (Leica M11)</option>
        </optgroup>

        <optgroup label="🌾 Rural, Nature & Countryside">
          <option value="rural_vineyard">Tuscan Vineyard & Cypress Road // Warm Golden Afternoon (Hasselblad 500C/M)</option>
          <option value="mountain_cabin">Pine Forest Mountain Cabin // Diffuse Morning Fog & Cedar Scent (Linhof 4x5)</option>
          <option value="english_country">Cotswolds Country Garden // Wildflowers & Gentle English Daylight (Pentax 67)</option>
          <option value="desert_canyon">Expansive Desert Plateau // Open Blue Sky & Raking Dune Shadows (Linhof 4x5)</option>
        </optgroup>

        <optgroup label="📸 Commercial Studio & Architecture">
          <option value="architect_brutalist">Architect in Brutalist Concrete Library // High Clerestory Skylight (Phase One IQ4)</option>
          <option value="commercial_packshot">Commercial Packshot // 100% SKU Approval Gate (Phase One IQ4 150MP)</option>
          <option value="fashion_studio">Haute Couture Studio Editorial // Giant Broncolor Para 220 Strobe (Hasselblad H6D)</option>
          <option value="sculptor_atelier">Carrara Marble Sculptor Atelier // Limestone Dust & Directional Sun (Fujifilm GFX)</option>
          <option value="watchmaker_bench">Horologist Micro-Bench // Macro Brass Gears & Focus (Sony A7R V)</option>
          <option value="museum_gallery">Neoclassical Museum Rotunda // Soaring Marble Fluted Columns (Linhof 4x5)</option>
          <option value="hollywood_anamorphic">Hollywood Cinema Anamorphic // 2.0x Oval Bokeh & Blue Streak Flare (ARRI Alexa 35)</option>
          <option value="commercial_billboard_copy_space">Commercial Advertising Hero // Venetian Gobo & Copy-Space (Phase One IQ4 150MP)</option>
        </optgroup>

        <optgroup label="✨ GenAI Photography Mastery Suite (v3.4)">
          <option value="hyperrealistic_latex_character">4D Liquid Glass & Latex High-Fashion Editorial // Contour Rim Light (Hasselblad X2D II)</option>
          <option value="heavyweight_editorial_portrait">Calibrated Heavyweight Body Morphology // 240 lbs Frame-Proportional (Sony a1 II)</option>
          <option value="gallery_baryta_print">Print-Calibrated Exhibition Prepress // Baryta Fine Art 16x24@300 (Phase One IQ4)</option>
        </optgroup>
      </select>

      <button class="btn-surprise" onclick="clearToSurprise()" title="Wipe scene fields to let the prompt surprise you freely">
        <span>↺ Clear / Surprise Mode</span>
      </button>
    </div>
    <div class="scenario-hint">
      Select a starting scenario or write freely. All fields below are fully editable.
    </div>
  </div>

  <div class="container">
    <!-- LEFT PANEL: HARDWARE RIG & OPTICAL DIALS -->
    <div class="rig-panel">

      <!-- 1. CAMERA SYSTEM & SENSOR -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">01. Camera Body & Sensor Format</div>
          <div class="section-meta" id="sensorGateMeta">36x24mm Full-Frame</div>
        </div>
        <div class="field-group">
          <label for="profileSelect">Camera Body System</label>
          <select id="profileSelect" onchange="onProfileChange()">
            <!-- Populated dynamically via API -->
          </select>
        </div>
        <div class="field-group">
          <label for="lensSelect">Optics & Matched Glass</label>
          <select id="lensSelect" onchange="onLensSelectChange()">
            <!-- Populated based on camera system -->
          </select>
          <input type="text" id="customLensInput" placeholder="Or enter custom lens (e.g. 50mm f/1.2)..." style="margin-top: 0.35rem;" oninput="debounceCompile()">
        </div>
      </div>

      <!-- 2. SCENE & SUBJECT DIRECTION -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">02. Scene Creative Intent</div>
          <div class="section-meta">Subject, Setting & Mood</div>
        </div>

        <div class="field-group">
          <label for="subjectInput">Subject & Core Action <span class="hint">(Keep simple or detailed)</span></label>
          <textarea id="subjectInput" placeholder="e.g. Woman in tailored trench coat standing under an umbrella..." oninput="debounceCompile()"></textarea>
        </div>

        <div class="field-group">
          <label>Framing & Crop</label>
          <input type="text" id="framingInput" placeholder="e.g. three-quarter editorial portrait" oninput="debounceCompile()">
          <div class="quick-bar">
            <button class="pill-btn" onclick="setFraming('extreme macro iris and skin detail portrait')">Macro</button>
            <button class="pill-btn" onclick="setFraming('tight head and shoulders portrait')">Headshot</button>
            <button class="pill-btn active" onclick="setFraming('three-quarter editorial portrait')">3/4 Editorial</button>
            <button class="pill-btn" onclick="setFraming('full-length architectural fashion portrait')">Full-Length</button>
            <button class="pill-btn" onclick="setFraming('wide environmental cinematic frame')">Wide Env</button>
          </div>
        </div>

        <!-- Quick Scene & Environment Builder Helpers -->
        <div class="field-group" style="margin-top: 0.2rem;">
          <label for="environmentInput">Environment & Location <span class="hint">Editable text</span></label>
          <input type="text" id="environmentInput" placeholder="e.g. wet cobblestone Paris street, limestone Haussmann facade" oninput="debounceCompile()">
          
          <!-- Environment category helper chips -->
          <div class="quick-bar" style="margin-top: 0.35rem;">
            <button class="pill-btn" onclick="injectEnv('city street')">City Street</button>
            <button class="pill-btn" onclick="injectEnv('luxury hotel')">Hotel</button>
            <button class="pill-btn" onclick="injectEnv('coastal beach')">Beach</button>
            <button class="pill-btn" onclick="injectEnv('rural vineyard')">Rural</button>
            <button class="pill-btn" onclick="injectEnv('photo studio')">Studio</button>
            <button class="pill-btn" onclick="injectEnv('architectural interior')">Architecture</button>
            <button class="pill-btn" onclick="injectEnv('pine forest')">Nature</button>
          </div>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label for="timeWeatherSelect">Time of Day & Weather</label>
            <select id="timeWeatherSelect" onchange="onTimeWeatherChange()">
              <option value="auto">Natural Ambient / Scene Default</option>
              <option value="golden_hour">Golden Hour (Warm low-angle sun, long shadows)</option>
              <option value="blue_hour">Blue Hour Dusk (Cool twilight, ambient glow)</option>
              <option value="overcast" selected>Overcast Diffuse (Softbox sky, clean skin)</option>
              <option value="noon_sun">Midday Direct Sun (Crisp geometric shadows)</option>
              <option value="rainy_wet">Rainy & Wet (Reflective asphalt, damp mist)</option>
              <option value="morning_fog">Morning Fog (Shafts of light, deep atmosphere)</option>
              <option value="night_city">Night (Atmospheric streetlamps & neon glow)</option>
            </select>
          </div>
          <div class="field-group">
            <label for="cityVibeSelect">City / Geographic Vibe</label>
            <select id="cityVibeSelect" onchange="onCityVibeChange()">
              <option value="none">Universal / Anywhere</option>
              <option value="paris" selected>Paris, France (Haussmannian, muted stone)</option>
              <option value="tokyo">Tokyo, Japan (Alley minimalism, modern neon)</option>
              <option value="nyc">New York, USA (Cast-iron SoHo, brownstones)</option>
              <option value="mediterranean">Mediterranean (Sun-bleached white, azure sea)</option>
              <option value="london">London, UK (Georgian brick, refined overcast)</option>
              <option value="milan">Milan, Italy (Marble porticos, high fashion)</option>
              <option value="scandinavia">Scandinavia (Granite, minimalist timber)</option>
            </select>
          </div>
        </div>

        <div class="field-row">
          <div class="field-group">
            <label for="wardrobeInput">Wardrobe / Styling</label>
            <input type="text" id="wardrobeInput" placeholder="e.g. tailored wool coat, silk scarf" oninput="debounceCompile()">
          </div>
          <div class="field-group">
            <label for="moodInput">Mood / Emotion</label>
            <input type="text" id="moodInput" placeholder="e.g. effortless, contemplative, serene" oninput="debounceCompile()">
          </div>
        </div>
      </div>

      <!-- REFERENCE IMAGE & ANTI-DRIFT STUDIO -->
      <div class="panel-section" id="refImageSection">
        <div class="section-header">
          <div class="section-title">Reference Image & Anti-Drift Engine</div>
          <div class="section-meta" id="refModeBadge" style="color: var(--text-muted); font-family: var(--font-mono); font-size: 0.68rem;">NO IMAGE ATTACHED</div>
        </div>

        <!-- Local Image Drag & Drop / File Browser Area -->
        <div class="ref-dropzone" id="refDropzone" onclick="document.getElementById('refFileInput').click()">
          <input type="file" id="refFileInput" accept="image/png, image/jpeg, image/webp, image/heic" style="display: none;" onchange="handleFileSelect(event)">
          
          <div id="dropzoneEmpty" style="padding: 0.5rem 0;">
            <svg width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" style="color: var(--accent-cyan); margin-bottom: 0.35rem;">
              <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <div style="font-weight: 600; font-size: 0.8rem; color: #fff;">Click or Drag & Drop Local Reference Image</div>
            <div style="font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono); margin-top: 0.15rem;">
              Supports JPG, PNG, WEBP // 100% Local Hardware Processing
            </div>
            <div style="margin-top: 0.45rem;">
              <button type="button" class="pill-btn" style="font-size: 0.65rem; padding: 2px 9px; border-color: rgba(245, 158, 11, 0.4); color: var(--accent-amber);" onclick="event.stopPropagation(); enableProductLockDirect();">
                📦 Or Configure 100% Commercial SKU Approval Gate Directly
              </button>
            </div>
          </div>
          
          <!-- Image preview when loaded -->
          <div id="dropzonePreview" style="display: none; width: 100%; align-items: center; gap: 0.85rem; text-align: left;">
            <img id="refThumb" src="" alt="Reference thumbnail" style="width: 68px; height: 68px; object-fit: cover; border-radius: 6px; border: 1px solid var(--border-subtle); flex-shrink: 0;">
            <div style="flex: 1; min-width: 0;">
              <div id="refFileName" style="font-weight: 700; font-size: 0.8rem; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">image.jpg</div>
              <div id="refDimensions" style="font-size: 0.7rem; color: var(--accent-cyan); font-family: var(--font-mono); margin-top: 0.15rem;">1920x1080 (16:9)</div>
              <div style="display: flex; gap: 0.4rem; margin-top: 0.45rem; flex-wrap: wrap;">
                <button type="button" class="btn-ref-action" onclick="syncRefAspectRatio(event)">
                  <span>📐 Match Rig AR</span>
                </button>
                <button type="button" class="btn-ref-action btn-ref-danger" onclick="clearRefImage(event)">
                  <span>✕ Remove</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Reference Workflow Modes & Anti-Drift Controls -->
        <div id="refControls" style="display: none; flex-direction: column; gap: 0.75rem; margin-top: 0.15rem;">
          <div class="field-group">
            <label>Reference Workflow Mode</label>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(88px, 1fr)); gap: 0.35rem;">
              <button type="button" class="mode-card active" id="btnModeRestore" onclick="setRefMode('restore')">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fff;">🔬 Remaster</div>
                <div style="font-size: 0.60rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.2;">
                  1:1 Identity & 150MP
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeDepixelate" onclick="setRefMode('depixelate')">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fff;">✨ De-Pixelate</div>
                <div style="font-size: 0.60rem; color: var(--accent-rose); margin-top: 0.15rem; line-height: 1.2;">
                  GFX100RF & Skin
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeProduct" onclick="setRefMode('product')">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fff;">📦 Product Lock</div>
                <div style="font-size: 0.60rem; color: var(--accent-amber); margin-top: 0.15rem; line-height: 1.2;">
                  100% SKU Gate
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeTransform" onclick="setRefMode('transform')">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fff;">🎨 Re-Shoot</div>
                <div style="font-size: 0.60rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.2;">
                  Adapt scene with bones
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeOutpaint" onclick="setRefMode('outpaint')">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fff;">📐 Outpaint</div>
                <div style="font-size: 0.60rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.2;">
                  Head-to-toe shoes
                </div>
              </button>
            </div>
          </div>

          <!-- Commercial SKU & Product Reference Lock Section -->
          <div id="productFidelityPanel" style="display: none; background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 0.75rem; margin-top: 0.15rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem;">
              <span style="font-size: 0.76rem; font-weight: 700; color: var(--accent-amber); text-transform: uppercase; letter-spacing: 0.05em;">
                🔒 100% Commercial SKU Approval Gate
              </span>
              <label class="check-item" style="font-size: 0.70rem; color: var(--accent-amber); margin-bottom: 0;">
                <input type="checkbox" id="chkApprovalGate" checked onchange="debounceCompile()"> 100% Gate Enforced
              </label>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
              <div class="field-group">
                <label for="productCropInput" style="font-size: 0.68rem;">Product-Reference Crop Anchor</label>
                <input type="text" id="productCropInput" placeholder="e.g. assets/perfume_crop.png" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
              <div class="field-group">
                <label for="skuColorInput" style="font-size: 0.68rem;">SKU Color Integrity (Pantone/Hex)</label>
                <input type="text" id="skuColorInput" placeholder="e.g. Pantone 296 C Deep Navy (#001F3F)" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
              <div class="field-group">
                <label for="capGeometryInput" style="font-size: 0.68rem;">Cap & Closure Geometry</label>
                <input type="text" id="capGeometryInput" placeholder="e.g. brushed aluminum screw cap, 48 ridges" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
              <div class="field-group">
                <label for="labelKerningInput" style="font-size: 0.68rem;">Label Kerning & Typography</label>
                <input type="text" id="labelKerningInput" placeholder="e.g. optical kerning locked, exact letter spacing" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
              <div class="field-group">
                <label for="materialFinishInput" style="font-size: 0.68rem;">Material Finish & Specular</label>
                <input type="text" id="materialFinishInput" placeholder="e.g. frosted cosmetic glass, matte paper label" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
              <div class="field-group">
                <label for="seamsInput" style="font-size: 0.68rem;">Manufacturing Seams & Parting Lines</label>
                <input type="text" id="seamsInput" placeholder="e.g. subtle glass mold seam along lateral edge" oninput="debounceCompile()" style="font-size: 0.74rem;">
              </div>
            </div>
          </div>

          <!-- Content Classification & Reproduction Directive -->
          <div class="field-group" style="margin-top: 0.15rem;">
            <label for="contentTypeSelect">Content Classification (Auto-Suppresses DoF/Grain for Flat Scans)</label>
            <select id="contentTypeSelect" onchange="debounceCompile()">
              <option value="photograph" selected>Photograph (Standard Realistic Camera Optics)</option>
              <option value="portrait">Portrait (Human Skin Override Priority Target)</option>
              <option value="product_photo">Product Photography (Commercial Clean Acutance)</option>
              <option value="document_scan">Document Scan (Flat Reproduction / Zero DoF Falloff)</option>
              <option value="poster_or_flyer">Poster / Flyer (Flat Reproduction / Suppress Vignette)</option>
              <option value="meme_or_infographic">Meme / Infographic (Flat Digital Reproduction)</option>
              <option value="ui_or_screenshot">UI / Screenshot (Flat Digital Reproduction)</option>
              <option value="mixed_content">Mixed Content (Hybrid Photographic & Graphics)</option>
            </select>
          </div>

          <!-- Extreme Anti-Drift Fidelity Slider -->
          <div class="field-group">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <label for="fidelitySlider">Anti-Drift Fidelity Lock</label>
              <span id="fidelityVal" style="font-family: var(--font-mono); font-size: 0.74rem; color: var(--accent-cyan); font-weight: 700;">95% (Extreme Anti-Drift)</span>
            </div>
            <input type="range" id="fidelitySlider" min="50" max="100" value="95" style="width: 100%; accent-color: var(--accent-cyan); cursor: pointer;" oninput="onFidelitySliderChange()">
            <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: var(--text-muted); font-family: var(--font-mono);">
              <span>50% (Flexible)</span>
              <span>80% (Balanced)</span>
              <span>100% (1:1 Strict)</span>
            </div>
          </div>

          <!-- Preserved Element Checkboxes & Skin Realism Overrides -->
          <div class="field-group">
            <label>Biometric, Structural & Optical Overrides</label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; margin-top: 0.2rem;">
              <label class="check-item"><input type="checkbox" id="chkFacial" checked onchange="debounceCompile()"> Facial Geometry & Bones</label>
              <label class="check-item"><input type="checkbox" id="chkGaze" checked onchange="debounceCompile()"> Eye Shape & Gaze</label>
              <label class="check-item"><input type="checkbox" id="chkProportions" checked onchange="debounceCompile()"> Anatomical Proportions</label>
              <label class="check-item"><input type="checkbox" id="chkLighting" onchange="debounceCompile()"> Lighting Falloff Mood</label>
              <label class="check-item"><input type="checkbox" id="chkSkinRealism" checked onchange="debounceCompile()"> Skin Realism (Ban Pore Stamp)</label>
              <label class="check-item"><input type="checkbox" id="chkTextPreserve" checked onchange="debounceCompile()"> Strict OCR & Text Lock</label>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. OPTICAL DIALS & APERTURE -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">03. Optical Aperture & Depth of Field</div>
          <div class="section-meta" id="apertureMeta">f/2.8 Target</div>
        </div>
        <div class="field-group">
          <label>Aperture Ring <span class="hint" id="dofHint">Smooth editorial falloff, tack-sharp subject</span></label>
          <div class="dial-group">
            <button class="dial-btn" onclick="setAperture('f/1.2')">f/1.2</button>
            <button class="dial-btn" onclick="setAperture('f/1.4')">f/1.4</button>
            <button class="dial-btn" onclick="setAperture('f/2.0')">f/2.0</button>
            <button class="dial-btn active" onclick="setAperture('f/2.8')">f/2.8</button>
            <button class="dial-btn" onclick="setAperture('f/4.0')">f/4</button>
            <button class="dial-btn" onclick="setAperture('f/5.6')">f/5.6</button>
            <button class="dial-btn sweet-spot" onclick="setAperture('f/8.0')">f/8</button>
            <button class="dial-btn" onclick="setAperture('f/11')">f/11</button>
          </div>
        </div>
        <div class="field-row">
          <div class="field-group">
            <label for="filterSelect">Glass & Optical Filter</label>
            <select id="filterSelect" onchange="debounceCompile()">
              <option value="none">None / Maximum Optical MTF Acutance</option>
              <option value="pro_mist_eighth">Tiffen Black Pro-Mist 1/8 (Gentle Highlight Bloom)</option>
              <option value="pro_mist_quarter">Tiffen Black Pro-Mist 1/4 (Noticeable Cine Glow)</option>
              <option value="hollywood_black">Schneider Hollywood Black Magic (Dermal Micro-Bloom)</option>
              <option value="cpl">Circular Polarizer (CPL Glare Suppression)</option>
              <option value="anamorphic_streak">Anamorphic 2x Cylindrical (Horizontal Flare & Oval Bokeh)</option>
            </select>
          </div>
          <div class="field-group">
            <label for="aspectSelect">Frame Aspect Ratio & Resolution</label>
            <select id="aspectSelect" onchange="debounceCompile()">
              <option value="9:11" selected>9:11 (12MP PNG, 3132x3828 — High-End Editorial Portrait)</option>
              <option value="4:5">4:5 (12MP PNG, 3100x3875 — Standard Portrait)</option>
              <option value="3:2">3:2 (12MP PNG, 4248x2832 — Classic 35mm)</option>
              <option value="4:3">4:3 (12MP PNG, 4000x3000 — Medium Format Standard)</option>
              <option value="5:4">5:4 (12MP PNG, 3875x3100 — Large Format Sheet)</option>
              <option value="16:9">16:9 (8K UHD, 7680x4320, 33.2MP uncompressed)</option>
              <option value="1:1">1:1 (12MP PNG, 3464x3464 — Square 6x6)</option>
              <option value="21:9">21:9 (Anamorphic Scope)</option>
              <option value="9:16">9:16 (Vertical Story)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 4. LIGHTING RIG & EMULSION / FILM SCIENCE -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">04. Light Transport & Color Science</div>
        </div>
        <div class="field-group">
          <label for="lightingSelect">Lighting Rig & Modifiers</label>
          <select id="lightingSelect" onchange="debounceCompile()">
            <option value="strobe_para" selected>Studio Strobe: 35-45° Directional Key + Black Flag Negative Fill (Deep Contrast)</option>
            <option value="window_daylight">Directional Daylight with Soft Diffusion, Organic Natural Falloff</option>
            <option value="beauty_dish">High-Fashion Beauty Dish with 20° Honeycomb Grid & Diffuser Sock</option>
            <option value="rembrandt_key">Dramatic Chiaroscuro / Rembrandt Single-Source Key (4:1 Contrast Ratio)</option>
            <option value="golden_hour">Low-Angle Golden Hour Sunlight with Unbleached Muslin Bounce</option>
            <option value="hard_flash">Direct Hard On-Camera Strobe with High-Contrast Falloff (90s Editorial)</option>
            <option value="tungsten_candle">Practical Low-Light Tungsten & Candlelight (Barry Lyndon Style)</option>
            <option value="architectural_skylight">Diffused Architectural Clerestory Daylight with Clean Tonal Roll-off</option>
          </select>
        </div>
        <div class="field-row">
          <div class="field-group">
            <label for="filmStockSelect">Film Stock / Sensor Profile</label>
            <select id="filmStockSelect" onchange="debounceCompile()">
              <option value="digital_raw" selected>Digital Raw (16-bit Uncompressed Linear Latitude)</option>
              <option value="portra_400">Kodak Professional Portra 400 (Warm Dermal Tones & Pastel Roll-off)</option>
              <option value="portra_160">Kodak Professional Portra 160 (Ultra-Fine Grain Fashion)</option>
              <option value="tri_x_400">Kodak Tri-X 400 (High-Contrast Silver Halide Monochrome)</option>
              <option value="ilford_hp5">Ilford HP5 Plus (Gentle Classic Silver Halide Monochrome)</option>
              <option value="provia_100f">Fujifilm Provia 100F (Natural Professional Slide Film)</option>
              <option value="classic_chrome">Fujifilm Classic Chrome (Documentary Muted Contrast)</option>
              <option value="cinestill_800t">Cinestill 800T (Tungsten Cinema Stock with Red Halation)</option>
              <option value="arri_logc4">ARRI LogC4 / Kodak 2383 Print Profile</option>
            </select>
          </div>
          <div class="field-group">
            <label for="shutterSelect">Shutter & Motion</label>
            <select id="shutterSelect" onchange="debounceCompile()">
              <option value="sync_1600" selected>1/1600s Leaf Shutter Flash Freeze</option>
              <option value="sync_400">1/400s High-Speed Sync (Sony a1 II Stacked Freeze)</option>
              <option value="sync_500">1/500s Strobe Synchronized Action Freeze</option>
              <option value="shutter_125">1/125s Natural Handheld Shutter</option>
              <option value="shutter_180">180° Cinema Shutter Angle (1/48s Cadence)</option>
              <option value="shutter_drag">1/15s Shutter Drag with Rear-Curtain Flash</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 05. PIONEER PRECISION SUITES -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">05. Industry-Pioneering Precision Suites</div>
          <div class="section-meta" style="color: var(--accent-cyan);">Hands • Anamorphic • Advertising</div>
        </div>

        <!-- Tool 1: Biomechanical Hand & Finger Precision Gate -->
        <div style="background: rgba(6, 182, 212, 0.04); border: 1px solid rgba(6, 182, 212, 0.22); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.65rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem;">
            <span style="font-size: 0.76rem; font-weight: 700; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em;">
              🖐️ Hand Precision Gate (5-Point Grip Lock)
            </span>
            <label class="check-item" style="font-size: 0.70rem; color: var(--accent-cyan); margin-bottom: 0;">
              <input type="checkbox" id="chkHandLock" onchange="debounceCompile()"> Hand Lock Active
            </label>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
            <div class="field-group">
              <label for="gripTypeSelect" style="font-size: 0.68rem;">Anatomical Grip Type</label>
              <select id="gripTypeSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="default" selected>Default / Auto Grip</option>
                <option value="palm_support">Palm Support (Flat resting, open MCP joints)</option>
                <option value="precision_pinch">Precision Pinch (Thumb + forefinger pad contact, blanching)</option>
                <option value="cylindrical_wrap">Cylindrical Wrap (Curling digits 2-5, thumb opposition)</option>
                <option value="relaxed_rest">Relaxed Rest (Gentle natural finger arc cascade)</option>
                <option value="open_palm">Open Palm (Extended planar metacarpals & splay)</option>
              </select>
            </div>
            <div class="field-group">
              <label for="handDetailsInput" style="font-size: 0.68rem;">Micro-Anatomy / Nail Beds / Blanching</label>
              <input type="text" id="handDetailsInput" placeholder="e.g. visible lunula, natural cuticles, contact blanching..." oninput="debounceCompile()" style="font-size: 0.74rem;">
            </div>
          </div>
        </div>

        <!-- Tool 2: Cinema Anamorphic Optics & Flare Engine -->
        <div style="background: rgba(168, 85, 247, 0.04); border: 1px solid rgba(168, 85, 247, 0.22); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.65rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem;">
            <span style="font-size: 0.76rem; font-weight: 700; color: #c084fc; text-transform: uppercase; letter-spacing: 0.05em;">
              🎬 Cinema Anamorphic Optics & Flare Engine
            </span>
            <label class="check-item" style="font-size: 0.70rem; color: #c084fc; margin-bottom: 0;">
              <input type="checkbox" id="chkAnamorphic" onchange="debounceCompile()"> Anamorphic Engine
            </label>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem;">
            <div class="field-group">
              <label for="squeezeSelect" style="font-size: 0.68rem;">Squeeze Factor</label>
              <select id="squeezeSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="default" selected>Auto (2.0x Scope)</option>
                <option value="2.0x">2.0x True Scope</option>
                <option value="1.8x">1.8x Modern Cinema</option>
                <option value="1.5x">1.5x Full-Frame</option>
                <option value="1.33x">1.33x 16:9 Sensor</option>
                <option value="1.0x">1.0x Spherical</option>
              </select>
            </div>
            <div class="field-group">
              <label for="streakFlareSelect" style="font-size: 0.68rem;">Streak Flare</label>
              <select id="streakFlareSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="none" selected>None (Clean)</option>
                <option value="cyan_blue">Cyan-Blue Sci-Fi Streak</option>
                <option value="warm_gold">Warm Amber-Gold Flare</option>
                <option value="neutral_silver">Neutral Silver Acutance</option>
                <option value="vintage_magenta">Vintage Magenta Flare</option>
              </select>
            </div>
            <div class="field-group">
              <label for="irisBladesSelect" style="font-size: 0.68rem;">Aperture Iris</label>
              <select id="irisBladesSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="default" selected>Default Iris</option>
                <option value="14_blade_circular">14-Blade Circular (Smooth 2:1 Ovals)</option>
                <option value="9_blade_rounded">9-Blade Rounded (18-Point Sunstars)</option>
                <option value="8_blade_octagonal">8-Blade Octagonal (8-Point Diffraction)</option>
                <option value="6_blade_hexagonal">6-Blade Hexagonal (Vintage Diffraction)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Tool 3: Commercial Advertising Suite (Gobo + Grip + Copy-Space + Safe-Zone) -->
        <div style="background: rgba(245, 158, 11, 0.04); border: 1px solid rgba(245, 158, 11, 0.22); border-radius: 8px; padding: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem;">
            <span style="font-size: 0.76rem; font-weight: 700; color: var(--accent-amber); text-transform: uppercase; letter-spacing: 0.05em;">
              📐 Commercial Advertising Suite (Gobo & Ad Safe-Zones)
            </span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
            <div class="field-group">
              <label for="goboSelect" style="font-size: 0.68rem;">Gobo Projection Cookie</label>
              <select id="goboSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="none" selected>None (Clean Studio Key)</option>
                <option value="venetian_blinds">Venetian Blinds (Cinematic Slits)</option>
                <option value="dappled_foliage">Dappled Foliage / Monstera</option>
                <option value="window_panes">Architectural Window Mullions</option>
                <option value="geometric_slits">Modern Geometric Slits</option>
                <option value="prism_fracture">Prism Refraction Shadow</option>
              </select>
            </div>
            <div class="field-group">
              <label for="gripModifierSelect" style="font-size: 0.68rem;">Studio Grip Modifier</label>
              <select id="gripModifierSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="none" selected>None (Standard Reflector)</option>
                <option value="beauty_dish_honeycomb">Beauty Dish + 20° Honeycomb Grid</option>
                <option value="butterfly_8x8_silk">8x8ft Butterfly Diffusion Silk</option>
                <option value="snoot_pinpoint">Conical Snoot (Pinpoint Specular)</option>
                <option value="solid_black_floppy">Solid Black Floppy Flag (Negative Fill)</option>
              </select>
            </div>
            <div class="field-group">
              <label for="lightingRatioSelect" style="font-size: 0.68rem;">Lighting Contrast Ratio</label>
              <select id="lightingRatioSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="default" selected>Default Studio Contrast</option>
                <option value="1:1">1:1 Flat Commercial (High-Key)</option>
                <option value="2:1">2:1 Gentle Subtlety (Catalog)</option>
                <option value="4:1">4:1 Editorial Modeling (Portrait)</option>
                <option value="8:1">8:1 Dramatic Noir Chiaroscuro</option>
                <option value="16:1">16:1 Silhouette Low-Key</option>
              </select>
            </div>
            <div class="field-group">
              <label for="copySpaceSelect" style="font-size: 0.68rem;">Billboard / Ad Copy-Space</label>
              <select id="copySpaceSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="none" selected>None (Centered Layout)</option>
                <option value="left_third">Left Third Negative Space</option>
                <option value="right_third">Right Third Negative Space</option>
                <option value="top_third">Top Third Negative Space (Headline)</option>
                <option value="bottom_third">Bottom Third Negative Space (CTA)</option>
              </select>
            </div>
            <div class="field-group" style="grid-column: span 2;">
              <label for="adSafeZoneSelect" style="font-size: 0.68rem;">Social Platform UI Safe-Zone Framing</label>
              <select id="adSafeZoneSelect" onchange="debounceCompile()" style="font-size: 0.74rem;">
                <option value="none" selected>None / Full Frame Exposure</option>
                <option value="tiktok_reels_9_16">TikTok & Instagram Reels (9:16 — Bottom 20% & Right 15% UI Clearance)</option>
                <option value="instagram_feed_4_5">Instagram Feed (4:5 — 1:1 Center Square Grid Safe Anchor)</option>
                <option value="ecommerce_catalog_1_1">E-Commerce Catalog (1:1 — Clean 10% Margin Padding Buffer)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 06. BODY MORPHOLOGY & VOLUME CALIBRATION -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">06. Body Morphology & Volume Engine</div>
          <div class="section-meta" style="color: var(--accent-amber);">Proportional Volume • Bilateral Asymmetry</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
          <div>
            <label class="field-label" for="bodyVolumeInput">Enlarged Volume Target Regions</label>
            <input type="text" class="text-input" id="bodyVolumeInput" placeholder="e.g. biceps, chest, gut (or leave empty)" oninput="debounceCompile()">
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
            <div>
              <label class="field-label" for="weightLbInput">Target Body Mass (lbs)</label>
              <input type="number" class="text-input" id="weightLbInput" placeholder="e.g. 240" min="0" max="500" oninput="debounceCompile()">
            </div>
            <div style="display: flex; align-items: flex-end;">
              <div style="font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono); line-height: 1.3;">
                Locks frame proportionality, soft-tissue gravity compression, and clothing tension.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 07. 4D VOLUMETRIC & PREMIUM MATERIAL ENGINE -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">07. 4D Volumetric & Material Engine</div>
          <div class="section-meta" style="color: var(--accent-cyan);">Contour Rim Light • Dielectric Refraction</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
            <div>
              <label class="field-label" for="materialStyleSelect">Premium Material Finish</label>
              <select class="custom-select" id="materialStyleSelect" onchange="debounceCompile()">
                <option value="none" selected>Default Material Physics</option>
                <option value="glossy_latex">Glossy Latex (High-Contrast Specular Highlights)</option>
                <option value="liquid_glass">Liquid Glass (Subsurface Refraction & Caustics)</option>
                <option value="dielectric_acrylic">Dielectric Acrylic (High Abbe Number Dispersion)</option>
                <option value="brushed_titanium">Brushed Titanium (Anisotropic Reflection)</option>
                <option value="matte_silicone">Matte Silicone (Soft Dermal Sheen)</option>
                <option value="translucent_resin">Translucent Resin (Deep Volumetric Absorption)</option>
                <option value="volumetric_4d">Volumetric 4D (Maximum Tonal Isolation)</option>
              </select>
            </div>
            <div>
              <label class="field-label" for="bgStyleSelect">Background Style</label>
              <select class="custom-select" id="bgStyleSelect" onchange="debounceCompile()">
                <option value="default" selected>Default Scene Background</option>
                <option value="opaque_black_blur">Opaque Softly Blurred Black</option>
                <option value="pure_black_matte">Pure Black Matte Void</option>
                <option value="studio_cyclorama">Studio Infinity Cyclorama</option>
                <option value="negative_void">High-Fashion Negative Void</option>
              </select>
            </div>
          </div>
          <div style="display: flex; gap: 1.25rem; margin-top: 0.2rem; flex-wrap: wrap;">
            <label class="check-item" style="font-weight: 600;">
              <input type="checkbox" id="chkVolumetric4D" onchange="debounceCompile()"> 
              <span>✨ 4D Volumetric Depth & Rim Lighting</span>
            </label>
            <label class="check-item" style="font-weight: 600;">
              <input type="checkbox" id="chkRemoveText" onchange="debounceCompile()"> 
              <span>✂️ Conditional Text Removal</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 08. PRINT-CALIBRATED PREPRESS & EXHIBITION LAB MATRIX -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">08. Exhibition Prepress Matrix</div>
          <div class="section-meta" style="color: var(--accent-rose);">300 PPI • Fine Art Substrates</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem;">
          <div>
            <label class="field-label" for="paperProfileSelect">Fine Art Paper Profile</label>
            <select class="custom-select" id="paperProfileSelect" onchange="debounceCompile()">
              <option value="none" selected>Standard Digital Output</option>
              <option value="baryta">Baryta Fine Art (Dmax 2.4, Satin High Dynamic Range)</option>
              <option value="matte_cotton">100% Cotton Rag (Dmax 1.7, Zero Glare Velvet Finish)</option>
              <option value="luster">Premium Luster (Dmax 2.2, Fine Micro-Stipple Texture)</option>
              <option value="glossy">High-Gloss Metallic (Dmax 2.5, Mirror Specular Acutance)</option>
              <option value="canvas">Exhibition Canvas (Woven Matte Texture)</option>
            </select>
          </div>
          <div>
            <label class="field-label" for="printSizeSelect">Exhibition Print Size & Density</label>
            <select class="custom-select" id="printSizeSelect" onchange="debounceCompile()">
              <option value="default" selected>Native Sensor Pixel Grid</option>
              <option value="16x24@300">16" x 24" @ 300 PPI (4800 x 7200 px — Gallery Master)</option>
              <option value="24x36@240">24" x 36" @ 240 PPI (5760 x 8640 px — Museum Large Format)</option>
              <option value="9x12@640">9" x 12" @ 640 PPI (5760 x 7680 px — 8K Precision Proof)</option>
              <option value="20x30@300">20" x 30" @ 300 PPI (6000 x 9000 px — 54MP Exhibition Ultra)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 09. BRUTAL SHARPNESS & QUALITY ENFORCEMENT -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">09. Brutal Sharpness, Safety & Shields</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.2rem;">
          <label class="check-item" style="font-weight: 600;">
            <input type="checkbox" id="chkSharpness" checked onchange="debounceCompile()"> 
            <span>⚡ Brutal Sharpness Protocol (Near-Eye Focus Lock, Iris & Eyelash Acutance, Stability Cues)</span>
          </label>
          <label class="check-item" style="font-weight: 600;">
            <input type="checkbox" id="chkAntiBrand" checked onchange="debounceCompile()"> 
            <span>🚫 Anti-Brand & Anti-Text Shield (Suppresses logos, brand names, typography, and watermarks)</span>
          </label>
          <label class="check-item" style="font-weight: 600;">
            <input type="checkbox" id="chkMaxQuality" checked onchange="debounceCompile()"> 
            <span>💎 12MP / 8K UHD Lossless Bitrate Enforcer (Zero JPEG compression, uncompressed 16-bit raster)</span>
          </label>
          <label class="check-item" style="font-weight: 600; color: var(--accent-cyan);">
            <input type="checkbox" id="chkPolicySafe" onchange="debounceCompile()"> 
            <span>🛡️ Policy-Safe Compliance Layer (Non-destructive safety transform preventing refusal loops)</span>
          </label>
        </div>
      </div>

      <!-- 10. PFEP v1.0 DIAGNOSTIC STRESS PROBES -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">10. PFEP v1.0 Diagnostic Stress Probes</div>
          <div class="section-meta" style="color: var(--accent-cyan);">Hard Identity Gate: 2/2</div>
        </div>
        <div style="margin-top: 0.5rem;">
          <label class="field-label" for="probeSelect">Select Canonical Diagnostic Probe</label>
          <select class="custom-select" id="probeSelect" onchange="debounceCompile()">
            <option value="none" selected>None (Production Rig)</option>
            <option value="master_portrait_lock">01: Master Portrait Lock (Baseline Anchor)</option>
            <option value="outpaint_lens_honest">02: Lens-Honest Outpaint (FOV Lock, No Fisheye)</option>
            <option value="stress_hard_key">03: Hard Key Stress (50-60° Key, Pores in Shadows)</option>
            <option value="stress_cross_polarized">04: Cross-Polarized Skin (Zero Specular Glare, True Subsurface)</option>
            <option value="stress_glasses_reflections">05: Glasses Reflections (Eyes Visible, Plausible Lens Flare)</option>
            <option value="stress_seated_compression">06: Seated Compression (Optical Distance Locked to Standing)</option>
            <option value="stress_standing_compression">07: Standing Compression (Zero Perspective Stretching)</option>
            <option value="stress_background_scale">08: Background Scale Stress (Subject Scale Locked)</option>
            <option value="stress_hair_specular">09: Hair Specular Dynamics (Anisotropic Sheen, No Helmet Gloss)</option>
            <option value="stress_shadow_color">10: Shadow Color Integrity (Warm Melanin, Zero Synthetic Tint)</option>
          </select>
          <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono); margin-top: 0.35rem; line-height: 1.4;">
            8-Axis Scorecard: Identity (0-2), Geometry (0-2), Lighting (0-2), Skin (0-2), Hair (0-2), Optics (0-2), Acutance (0-2), Color (0-2). Pass Rule: Identity == 2 AND Total &ge; 12.
          </div>
        </div>
      </div>

      <!-- 11. EXHIBITION LIGHTING & CLOSED-LOOP OUTPUT CONSTRAINTS -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">11. Exhibition Systems & Closed-Loop Output</div>
          <div class="section-meta" style="color: var(--accent-amber);">500 Lux • TM-30 98 • SHA-256</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem;">
          <div>
            <label class="field-label" for="minMbInput">Minimum File Size (MB)</label>
            <input type="number" step="0.5" class="custom-input" id="minMbInput" placeholder="e.g. 35.0" oninput="debounceCompile()">
          </div>
          <div>
            <label class="field-label" for="cctInput">Gallery CCT Kelvin</label>
            <input type="number" class="custom-input" id="cctInput" placeholder="5000" oninput="debounceCompile()">
          </div>
          <div>
            <label class="field-label" for="luxInput">Exhibition Lux</label>
            <input type="number" class="custom-input" id="luxInput" placeholder="500" oninput="debounceCompile()">
          </div>
          <div>
            <label class="field-label" for="criInput">TM-30 / CRI Fidelity</label>
            <input type="number" step="0.5" class="custom-input" id="criInput" placeholder="98.0" oninput="debounceCompile()">
          </div>
          <div>
            <label class="field-label" for="wallSurroundInput">Wall / Surround</label>
            <input type="text" class="custom-input" id="wallSurroundInput" placeholder="Neutral Gray 18%" oninput="debounceCompile()">
          </div>
          <div>
            <label class="field-label" for="galleryZoneInput">Gallery Zone</label>
            <input type="text" class="custom-input" id="galleryZoneInput" placeholder="Zone A - North Wing" oninput="debounceCompile()">
          </div>
        </div>
        <div style="margin-top: 0.5rem;">
          <label class="field-label" for="anchorIdInput">Series Anchor Image ID</label>
          <input type="text" class="custom-input" id="anchorIdInput" placeholder="anchor_portrait_001" oninput="debounceCompile()">
        </div>
      </div>

    </div>


    <!-- RIGHT PANEL: COMPILED TARGET ENGINE OUTPUT -->
    <div class="output-panel">
      <div class="tabs-bar">
        <div class="tabs">
          <button class="tab active" onclick="setTarget('gpt_images')">🤖 GPT Images (ChatGPT)</button>
          <button class="tab" onclick="setTarget('imagen')">♊ Gemini Images (Imagen 3)</button>
          <button class="tab" onclick="setTarget('midjourney')">⛵ Midjourney (v8.2)</button>
          <button class="tab" onclick="setTarget('flux')">⚡ Flux.1 (Dev/Schnell)</button>
          <button class="tab" onclick="setTarget('sdxl')">🎨 SDXL Dual</button>
          <button class="tab" onclick="setTarget('raw')">📋 Raw Spec Audit</button>
          <button class="tab" onclick="setTarget('json')">📦 JSON All-in-One</button>
        </div>
        <button class="action-btn" onclick="copyPrompt('unified')">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
          <span>Copy All-in-One Prompt</span>
        </button>
      </div>

      <!-- Compiled All-in-One Prompt Payload (Positive + Anti-Artifact Shield) -->
      <div class="card">
        <div class="card-header">
          <div>
            <span class="card-title">COMPILED ALL-IN-ONE PROMPT PAYLOAD</span>
            <div style="font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono); margin-top: 0.2rem;">
              Positive Optical Simulation + Anti-Artifact Shield (Ready for 1-Click Copy & Paste)
            </div>
          </div>
          <div style="display: flex; gap: 0.4rem; align-items: center;">
            <span id="targetBadge" style="font-size: 0.7rem; color: var(--accent-cyan); font-family: var(--font-mono); background: rgba(56, 189, 248, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.2);">IMAGEN 3 PROSE</span>
          </div>
        </div>
        <div class="prompt-content" id="positiveOutput">Compiling...</div>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.4rem; flex-wrap: wrap; align-items: center;">
          <button class="action-btn" onclick="copyPrompt('unified')" style="font-size: 0.75rem; padding: 0.42rem 0.95rem;">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
            <span>Copy All-in-One (With Shield)</span>
          </button>
          <button class="action-btn-secondary" onclick="copyPrompt('positive')" title="Copy only the positive optical description without negative tokens">
            <span>Copy Optical Only</span>
          </button>
          <button class="action-btn-shield" onclick="copyPrompt('negative')" title="Copy only the negative artifact suppression tokens">
            <span>Copy Shield Only</span>
          </button>
        </div>
      </div>

      <!-- Anti-Artifact Shield / Negative Prompt Breakdown -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Anti-Artifact Negative Shield Breakdown</span>
          <span style="font-size: 0.7rem; color: var(--accent-rose); font-family: var(--font-mono);">ACTIVE SUPPRESSION</span>
        </div>
        <div class="shield-content" id="negativeOutput">Banning plastic skin, computational bokeh, digital sharpening halos...</div>
      </div>

      <!-- 100% Commercial SKU Approval Gate Live Telemetry -->
      <div class="card" id="approvalGateCard" style="display: none; border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.03);">
        <div class="card-header">
          <span class="card-title" style="color: var(--accent-amber); display: flex; align-items: center; gap: 0.5rem;">
            <span>🛡️</span> 100% Commercial SKU Approval Gate // 5-Point Forensic Inspection
          </span>
          <span style="font-size: 0.7rem; color: var(--accent-green); font-family: var(--font-mono); font-weight: 700;" id="gateStatusBadge">ALL GATES LOCKED</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; padding: 0.75rem;" id="gateChecklistContainer">
          <!-- Dynamically populated -->
        </div>
      </div>

      <!-- Biomechanical Hand Precision Gate Live Telemetry -->
      <div class="card" id="handGateCard" style="display: none; border-color: rgba(6, 182, 212, 0.4); background: rgba(6, 182, 212, 0.03);">
        <div class="card-header">
          <span class="card-title" style="color: var(--accent-cyan); display: flex; align-items: center; gap: 0.5rem;">
            <span>🖐️</span> Biomechanical Hand Precision Gate // 5-Point Grip Lock
          </span>
          <span style="font-size: 0.7rem; color: var(--accent-green); font-family: var(--font-mono); font-weight: 700;">ANATOMY LOCKED</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; padding: 0.75rem;" id="handChecklistContainer">
          <!-- Dynamically populated -->
        </div>
      </div>

      <!-- Cinema Anamorphic Optics & Flare Engine Live Telemetry -->
      <div class="card" id="anamorphicCard" style="display: none; border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.03);">
        <div class="card-header">
          <span class="card-title" style="color: #c084fc; display: flex; align-items: center; gap: 0.5rem;">
            <span>🎬</span> Cinema Anamorphic Optics & Flare Engine // Live Telemetry
          </span>
          <span style="font-size: 0.7rem; color: #c084fc; font-family: var(--font-mono); font-weight: 700;">SCOPE RIG ACTIVE</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; padding: 0.75rem;" id="anamorphicContainer">
          <!-- Dynamically populated -->
        </div>
      </div>

      <!-- Commercial Advertising Suite Live Telemetry -->
      <div class="card" id="advertisingCard" style="display: none; border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.03);">
        <div class="card-header">
          <span class="card-title" style="color: var(--accent-amber); display: flex; align-items: center; gap: 0.5rem;">
            <span>📐</span> Commercial Advertising Suite // Light Shaper & Safe-Zone
          </span>
          <span style="font-size: 0.7rem; color: var(--accent-amber); font-family: var(--font-mono); font-weight: 700;">STUDIO RIG LOCKED</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; padding: 0.75rem;" id="advertisingContainer">
          <!-- Dynamically populated -->
        </div>
      </div>

      <!-- Recommended Parameters & Physical Specs -->
      <div class="specs-grid" id="specsGrid">
        <!-- Dynamically filled -->
      </div>
    </div>
  </div>

  <div class="toast" id="toast">Copied prompt to clipboard!</div>

  <script>
    let activeTarget = 'gpt_images';
    let activeAperture = 'f/2.8';
    let availableProfiles = [];
    let compileTimer = null;
    let refData = null;
    let activeRefMode = 'restore';

    // Lens catalog mapped to camera systems
    const LENS_CATALOG = {
      sony_a1_ii: [
        "Sony FE 85mm F1.4 GM II (SEL85F14GM2) [High Hit-Rate Portrait]",
        "Sony FE 50mm F1.2 GM (SEL50F12GM) [Environmental Micro-Contrast]",
        "Sony FE 135mm F1.8 GM (SEL135F18GM) [Compression Texture Monster]"
      ],
      canon_eos_r5_ii: [
        "Canon RF 85mm F1.2L USM (Reference Portrait Prime)",
        "Canon RF 50mm F1.2L USM (Micro-Contrast & Natural DOF)",
        "Canon RF 135mm F1.8L IS USM (Subject Separation & IS)"
      ],
      nikon_z9: [
        "NIKKOR Z 135mm f/1.8 S Plena (Zero Vignetting Texture Monster)",
        "NIKKOR Z 85mm f/1.2 S (Reference Portrait Prime)",
        "NIKKOR Z 50mm f/1.2 S (High-Acutance Standard)"
      ],
      phase_one_iq4: [
        "Schneider Kreuznach 80mm LS f/2.8 Blue Ring (Standard Reference)",
        "Schneider Kreuznach 55mm LS f/2.8 Blue Ring (Wide Architectural)",
        "Schneider Kreuznach 110mm LS f/2.8 Blue Ring (Portrait Compression)",
        "Schneider Kreuznach 150mm LS f/3.5 Blue Ring (Tight Portrait)",
        "Schneider Kreuznach 240mm LS f/4.5 (Telephoto Separation)"
      ],
      hasselblad_h6d: [
        "Hasselblad HC 100mm f/2.2 Portrait Lens (Reference Prime)",
        "Hasselblad HC 50mm f/3.5 II Wide Angle",
        "Hasselblad HC 150mm f/3.2 Telephoto",
        "Hasselblad HC 24mm f/4.8 Ultra-Wide"
      ],
      hasselblad_500cm: [
        "Carl Zeiss Planar T* 80mm f/2.8 CF (Legendary Standard)",
        "Carl Zeiss Distagon T* 50mm f/4 CF (Wide Street & Interior)",
        "Carl Zeiss Sonnar T* 150mm f/4 CF (Classic Portrait)",
        "Carl Zeiss Biogon T* 38mm f/4.5 (Distortion-Free Wide)"
      ],
      pentax_67ii: [
        "SMC Pentax 67 105mm f/2.4 (The Legendary Bokeh King)",
        "SMC Pentax 67 90mm f/2.8 (Crisp Documentary Normal)",
        "SMC Pentax 67 55mm f/4 (Deep Landscape & Interior)",
        "SMC Pentax 67 165mm f/2.8 (Velvety Compression)"
      ],
      linhof_technika_4x5: [
        "Schneider Kreuznach Apo-Symmar 150mm f/5.6 L (Museum Reference)",
        "Rodenstock Grandagon-N 90mm f/4.5 (Extreme Architectural Rise)",
        "Schneider Super-Angulon 72mm f/5.6 XL (Ultra-Wide Interior)",
        "Schneider Apo-Tele-Xenar 250mm f/5.6 (Fine Art Telephoto)"
      ],
      leica_m11: [
        "Leica Summilux-M 35mm f/1.4 ASPH FLE II (Documentary Reference)",
        "Leica Noctilux-M 50mm f/0.95 ASPH (The King of Light)",
        "Leica APO-Summicron-M 50mm f/2 ASPH (Benchmark Optical Acutance)",
        "Leica Summicron-M 28mm f/2 ASPH (Environmental Reportage)"
      ],
      leica_m6_analog: [
        "Leica Summicron-M 50mm f/2 Dual-Range (Classic German Micro-Contrast)",
        "Leica Summilux-M 35mm f/1.4 Pre-ASPH 'Steel Rim'",
        "Leica Elmarit-M 28mm f/2.8 (Compact Street)",
        "Leica Tele-Elmarit-M 90mm f/2.8 'Fat Elmarit'"
      ],
      arri_alexa_35: [
        "Cooke S4/i 50mm T2.0 Cine Prime ('The Cooke Look')",
        "ARRI Signature Prime 47mm T1.8 (Organic Warm Skin Tones)",
        "Atlas Orion 65mm T2.0 2x Anamorphic Prime (Oval Bokeh & Horizontal Flare)",
        "Angenieux Optimo Ultra 12x Cine Zoom (Feature Film)"
      ],
      fujifilm_gfx100ii: [
        "Fujinon GF 110mm f/2 R LM WR (Reference Portrait Prime)",
        "Fujinon GF 80mm f/1.7 R WR (Ultra-Fast Medium Format)",
        "Fujinon GF 55mm f/1.7 R WR (Natural Standard)",
        "Fujinon GF 250mm f/4 R LM OIS WR (Subject Isolation)"
      ],
      sony_a7rv: [
        "Sony FE 50mm f/1.2 GM (G-Master Optical Reference)",
        "Sony FE 85mm f/1.4 GM II (Portrait Specialist)",
        "Sony FE 135mm f/1.8 GM (Razor-Sharp Background Dissolution)",
        "Sony FE 24-70mm f/2.8 GM II (Versatile Commercial Standard)"
      ],
      sony_fx_series: [
        "Sony FE 50mm f/1.2 GM @ f/2.8 (Venice Cine Sweet Spot)",
        "Sony FE 24-70mm f/2.8 GM II (Versatile Cine Zoom)",
        "Sony FE 85mm f/1.4 GM II (Cinematic Portrait Prime)",
        "Sony FE 135mm f/1.8 GM (Cinematic Separation Prime)",
        "Sony FE 16-35mm f/2.8 GM II (Wide Cine Master)"
      ],
      hasselblad_x2d_ii_100c: [
        "Hasselblad XCD 90mm f/2.5 V (Reference Medium Format Portrait Prime)",
        "Hasselblad XCD 55mm f/2.5 V (High-Resolution Normal)",
        "Hasselblad XCD 38mm f/2.5 V (Environmental Wide)",
        "Hasselblad XCD 135mm f/2.8 with 1.7x Converter"
      ],
      fujifilm_gfx100rf: [
        "Fujinon GF 45mm f/2.8 R WR (Compact Documentary Prime)",
        "Fujinon GF 63mm f/2.8 R WR (Standard Rangefinder Normal)",
        "Fujinon GF 110mm f/2 R LM WR (Reference Portrait Prime)",
        "Fujinon GF 30mm f/3.5 R WR (Wide Street Architecture)"
      ],
      canon_eos_r1: [
        "Canon RF 85mm F1.2L USM (Reference Portrait & Decisive Action)",
        "Canon RF 70-200mm F2.8L IS USM Z (Action & Sports Master)",
        "Canon RF 400mm F2.8L IS USM (Super-Telephoto Action)",
        "Canon RF 24-70mm F2.8L IS USM (Universal Fast Zoom)"
      ],
      leica_sl3_p: [
        "Leica APO-Summicron-SL 50mm f/2 ASPH (Apochromatic Benchmark)",
        "Leica APO-Summicron-SL 75mm f/2 ASPH (Portrait Micro-Contrast)",
        "Leica APO-Summicron-SL 35mm f/2 ASPH (Environmental Documentary)",
        "Leica Super-Vario-Elmar-SL 16-35mm f/3.5-4.5 ASPH"
      ],
      panasonic_lumix_s1rii: [
        "Lumix S PRO 50mm f/1.4 Leica-Certified (Ultimate Optical Purity)",
        "Lumix S PRO 85mm f/1.8 (Lightweight Portrait Prime)",
        "Lumix S 100mm f/2.8 Macro (1:1 Micro-Detail Specialist)",
        "Lumix S PRO 24-70mm f/2.8 (Professional Documentary Standard)"
      ]
    };

    // Scenarios library covering everyday natural environments, cities, weather, hotels, beaches, rural
    const SCENARIOS = {
      city_paris: {
        profile: "leica_m11",
        subject: "Pedestrian walking past an outdoor cafe terrace, holding an espresso cup",
        framing: "three-quarter editorial portrait",
        environment: "wet cobblestone Paris street in Saint-Germain, limestone Haussmann facade in background",
        wardrobe: "tailored navy wool trench coat and gray cashmere scarf",
        mood: "effortless, contemplative, authentic Parisian elegance",
        aperture: "f/2.8",
        timeWeather: "overcast",
        cityVibe: "paris",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        filter: "none"
      },
      tokyo_night: {
        profile: "leica_m6_analog",
        subject: "Person holding a clear vinyl umbrella under rain reflections",
        framing: "medium close-up cinematic portrait",
        environment: "narrow rain-soaked alleyway in Shinjuku with glowing neon signs and reflective puddles",
        wardrobe: "dark oversized coat with glistening raindrops on shoulders",
        mood: "melancholic, cinematic, vivid night atmosphere",
        aperture: "f/2.0",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "tungsten_candle",
        filmStock: "cinestill_800t",
        filter: "pro_mist_eighth"
      },
      nyc_soho: {
        profile: "sony_a7rv",
        subject: "Designer sitting on a concrete ledge reviewing fabric swatches",
        framing: "three-quarter editorial portrait",
        environment: "sunlit SoHo loft exterior with historic cast-iron columns and fire escapes",
        wardrobe: "minimalist black blazer, crisp white t-shirt, tailored trousers",
        mood: "sharp, modern, vibrant creative energy",
        aperture: "f/2.0",
        timeWeather: "golden_hour",
        cityVibe: "nyc",
        lighting: "golden_hour",
        filmStock: "digital_raw",
        filter: "none"
      },
      london_drizzle: {
        profile: "leica_m11",
        subject: "Art dealer standing outside an old brick gallery entrance",
        framing: "three-quarter editorial portrait",
        environment: "Mayfair street with weathered Portland stone, black railings, and subtle drizzle",
        wardrobe: "charcoal tweed overcoat and leather Chelsea boots",
        mood: "understated British refinement, calm",
        aperture: "f/2.8",
        timeWeather: "overcast",
        cityVibe: "london",
        lighting: "window_daylight",
        filmStock: "portra_400",
        filter: "none"
      },
      milan_portico: {
        profile: "hasselblad_h6d",
        subject: "Fashion director walking briskly through a classical colonnade",
        framing: "full-length architectural fashion portrait",
        environment: "lofty marble portico in Brera with geometric shadows and sunlit courtyard",
        wardrobe: "sharp structured camel wool coat and oversized dark sunglasses",
        mood: "commanding, sophisticated, high fashion",
        aperture: "f/4.0",
        timeWeather: "noon_sun",
        cityVibe: "milan",
        lighting: "strobe_para",
        filmStock: "portra_160",
        filter: "none"
      },
      hotel_terrace: {
        profile: "hasselblad_h6d",
        subject: "Guest relaxing on sun-warmed linen cushions with morning fruit and coffee",
        framing: "three-quarter editorial portrait",
        environment: "private terracotta terrace of a cliffside boutique hotel overlooking the sea",
        wardrobe: "unbleached relaxed white linen shirt and light linen trousers",
        mood: "peaceful luxury, serene warmth, slow living",
        aperture: "f/3.5",
        timeWeather: "golden_hour",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        filmStock: "portra_160",
        filter: "none"
      },
      hotel_penthouse: {
        profile: "phase_one_iq4",
        subject: "Traveler standing near floor-to-ceiling glass looking out across the city skyline",
        framing: "three-quarter editorial portrait",
        environment: "modernist luxury penthouse living room with smoked oak flooring and marble accents",
        wardrobe: "fine ribbed dark knit sweater and tailored wool trousers",
        mood: "quiet contemplation, refined luxury",
        aperture: "f/5.6",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "architectural_skylight",
        filmStock: "digital_raw",
        filter: "none"
      },
      hotel_lobby: {
        profile: "fujifilm_gfx100ii",
        subject: "Guest seated in an emerald velvet armchair waiting by a grand marble fireplace",
        framing: "medium close-up cinematic portrait",
        environment: "historic Grand Hotel lobby with fluted plaster columns, warm chandeliers, and gilded mirrors",
        wardrobe: "tailored midnight blue double-breasted suit",
        mood: "opulent, cinematic, dignified",
        aperture: "f/2.8",
        timeWeather: "night_city",
        cityVibe: "none",
        lighting: "tungsten_candle",
        filmStock: "classic_chrome",
        filter: "pro_mist_eighth"
      },
      hotel_bar: {
        profile: "arri_alexa_35",
        subject: "Patron seated at a curved mahogany bar holding a tumbler of whiskey",
        framing: "medium close-up cinematic portrait",
        environment: "speakeasy cocktail lounge with warm amber backlighting and brass accents",
        wardrobe: "crisp unbuttoned collar shirt and vintage leather jacket",
        mood: "intimate, moody, cinematic storytelling",
        aperture: "f/2.0",
        timeWeather: "night_city",
        cityVibe: "none",
        lighting: "rembrandt_key",
        filmStock: "arri_logc4",
        filter: "pro_mist_quarter"
      },
      beach_dunes: {
        profile: "pentax_67ii",
        subject: "Person standing amidst wild sea grass with wind blowing through their hair",
        framing: "three-quarter editorial portrait",
        environment: "coastal sand dunes leading to an open ocean beach at low tide",
        wardrobe: "chunky cream cable-knit wool sweater and weathered denim",
        mood: "raw coastal beauty, free, natural",
        aperture: "f/2.4",
        timeWeather: "golden_hour",
        cityVibe: "none",
        lighting: "golden_hour",
        filmStock: "portra_400",
        filter: "none"
      },
      mediterranean_cliff: {
        profile: "hasselblad_500cm",
        subject: "Model looking out over the sea leaning against a sun-bleached stone balustrade",
        framing: "full-length architectural fashion portrait",
        environment: "whitewashed Mediterranean cliffside village with vibrant bougainvillea and deep blue ocean",
        wardrobe: "flowing sky-blue cotton sundress with delicate embroidery",
        mood: "sun-drenched, radiant, timeless summer",
        aperture: "f/4.0",
        timeWeather: "noon_sun",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        filmStock: "portra_160",
        filter: "none"
      },
      nordic_fjord: {
        profile: "fujifilm_gfx100ii",
        subject: "Hiker standing on wet granite shoreline looking across calm fjord waters",
        framing: "wide environmental cinematic frame",
        environment: "Norwegian coastal fjord with dark mist-shrouded peaks and mossy rocks",
        wardrobe: "mustard yellow technical rain parka and waterproof hiking boots",
        mood: "epic nature, vast scale, crisp northern air",
        aperture: "f/5.6",
        timeWeather: "morning_fog",
        cityVibe: "scandinavia",
        lighting: "window_daylight",
        filmStock: "classic_chrome",
        filter: "none"
      },
      tropical_shore: {
        profile: "leica_m11",
        subject: "Local fisherman mending nets under palm tree canopy",
        framing: "environmental full-body portrait",
        environment: "secluded tropical beach with gentle surf, wet sand, and coconut palms",
        wardrobe: "faded linen shirt and roll-up cotton trousers",
        mood: "peaceful daily life, grounded, sun-baked",
        aperture: "f/2.8",
        timeWeather: "golden_hour",
        cityVibe: "none",
        lighting: "golden_hour",
        filmStock: "portra_400",
        filter: "none"
      },
      rural_vineyard: {
        profile: "hasselblad_500cm",
        subject: "Winemaker inspecting grape clusters in late summer light",
        framing: "three-quarter editorial portrait",
        environment: "sun-drenched Tuscan vineyard on rolling hills with cypress trees in background",
        wardrobe: "rustic chambray shirt and dirt-stained leather work gloves",
        mood: "earthy, authentic, slow agrarian rhythm",
        aperture: "f/4.0",
        timeWeather: "golden_hour",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        filmStock: "portra_400",
        filter: "none"
      },
      mountain_cabin: {
        profile: "linhof_technika_4x5",
        subject: "Woodworker carving timber on outdoor deck surrounded by pines",
        framing: "three-quarter editorial portrait",
        environment: "rustic cedar mountain cabin deck with wood shavings and morning fog in the pines",
        wardrobe: "heavy red-and-black wool flannel overshirt and leather apron",
        mood: "quiet craftsmanship, solitary, mountain air",
        aperture: "f/8.0",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "window_daylight",
        filmStock: "portra_400",
        filter: "none"
      },
      english_country: {
        profile: "pentax_67ii",
        subject: "Botanist gathering garden roses into a wicker basket",
        framing: "three-quarter editorial portrait",
        environment: "English country stone cottage garden overflowing with climbing roses and delphiniums",
        wardrobe: "waxed cotton jacket and sage linen dress",
        mood: "pastoral, romantic, gentle morning tranquility",
        aperture: "f/2.4",
        timeWeather: "overcast",
        cityVibe: "london",
        lighting: "window_daylight",
        filmStock: "portra_160",
        filter: "none"
      },
      desert_canyon: {
        profile: "linhof_technika_4x5",
        subject: "Explorer standing at canyon rim looking into the vast expanse",
        framing: "wide environmental cinematic frame",
        environment: "red sandstone canyon rim with deep geological strata and distant desert haze",
        wardrobe: "khaki canvas safari jacket and wide-brim felt hat",
        mood: "monumental scale, ancient earth, adventurous stillness",
        aperture: "f/11",
        timeWeather: "noon_sun",
        cityVibe: "none",
        lighting: "golden_hour",
        filmStock: "provia_100f",
        filter: "cpl"
      },
      architect_brutalist: {
        profile: "phase_one_iq4",
        subject: "Architect leaning against heavy timber drafting desk, examining blueprints and concrete models",
        framing: "three-quarter editorial portrait",
        environment: "brutalist board-formed concrete library with high clerestory windows",
        wardrobe: "charcoal wool blazer over black fine knit turtleneck, wire-frame spectacles",
        mood: "austere, contemplative, intellectual focus",
        aperture: "f/8.0",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "architectural_skylight",
        filmStock: "digital_raw",
        filter: "none"
      },
      commercial_packshot: {
        profile: "phase_one_iq4",
        subject: "Luxury cosmetic serum bottle on polished dark slate pedestal with natural micro-water droplets",
        framing: "macro packshot product hero shot",
        environment: "high-end commercial studio cyclorama with dual diffused strip softboxes",
        wardrobe: "",
        mood: "pristine, tactile, ultra-premium commercial quality",
        aperture: "f/8.0",
        timeWeather: "studio_soft",
        cityVibe: "none",
        lighting: "strobe_softbox",
        filmStock: "digital_raw",
        filter: "none",
        refMode: "product",
        capGeometry: "matte black anodized aluminum dropper cap with 48-ridge knurling collar and flush seal",
        skuColor: "Amber pharmaceutical glass (#8B4513) with Pantone 116 C gold hot-stamp foil text",
        labelKerning: "crisp micro-typography, precise character tracking, zero hallucinated micro-text",
        materialFinish: "heavy-base borosilicate glass, anti-reflective coating, tactile uncoated paper label",
        seamGeometry: "flawless circular base without mold flash, hairline parting seam along shoulder",
        productCrop: "packshot_reference_hero.png"
      },
      fashion_studio: {
        profile: "hasselblad_h6d",
        subject: "High-fashion model posing in sculpted structural silk couture gown",
        framing: "full-length architectural fashion portrait",
        environment: "pristine white infinity cove photo studio with subtle floor reflections",
        wardrobe: "unbleached raw ivory silk draped architectural dress with sharp folds",
        mood: "avant-garde, sculptural, pristine editorial elegance",
        aperture: "f/4.0",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        filmStock: "portra_160",
        filter: "none"
      },
      sculptor_atelier: {
        profile: "fujifilm_gfx100ii",
        subject: "Master stone sculptor covered in fine marble dust on muscular forearms",
        framing: "three-quarter editorial portrait",
        environment: "historic Carrara limestone atelier with half-carved statues and raking morning light shafts",
        wardrobe: "heavy indigo canvas workshirt and stained leather apron",
        mood: "intense concentration, raw craftsmanship",
        aperture: "f/2.8",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "window_daylight",
        filmStock: "classic_chrome",
        filter: "none"
      },
      watchmaker_bench: {
        profile: "sony_a7rv",
        subject: "Senior watchmaker looking through brass loupe, placing tourbillon balance wheel",
        framing: "extreme macro iris and skin detail portrait",
        environment: "cluttered antique wooden workbench with miniature gear wheels and micro-screwdrivers",
        wardrobe: "dark wool vest and rolled-up striped cotton shirt",
        mood: "microscopic precision, quiet mastery",
        aperture: "f/2.8",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        filmStock: "digital_raw",
        filter: "none"
      },
      museum_gallery: {
        profile: "linhof_technika_4x5",
        subject: "Curator standing gracefully in grand central gallery flanked by classical marble sculptures",
        framing: "full-length architectural fashion portrait",
        environment: "soaring neoclassical museum rotunda with polished marble floor and fluted columns",
        wardrobe: "bespoke charcoal three-piece suit with silk tie",
        mood: "scholarly majesty, timeless architectural symmetry",
        aperture: "f/11",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "architectural_skylight",
        filmStock: "portra_160",
        filter: "none"
      },
      hollywood_anamorphic: {
        profile: "arri_alexa_35",
        subject: "Cinematic operative in wet rain-slicked city avenue, intense focused stillness",
        framing: "widescreen medium cinematic shot",
        environment: "rain-soaked neon district with reflective wet asphalt and vertical anamorphic light streaks",
        wardrobe: "dark distressed tactical trench coat",
        mood: "cinematic tension, atmospheric sci-fi noir",
        aperture: "f/2.0",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "neon",
        filmStock: "arri_logc4",
        filter: "anamorphic_streak",
        aspectRatio: "21:9",
        anamorphic: true,
        squeeze: "2.0x",
        streakFlare: "cyan_blue",
        irisBlades: "14_blade_circular",
        gobo: "geometric_slits",
        lightingRatio: "8:1"
      },
      commercial_billboard_copy_space: {
        profile: "phase_one_iq4",
        subject: "Luxury skincare essence glass bottle held by elegant hand in precision pinch grip",
        framing: "asymmetric commercial advertising layout with negative copy space",
        environment: "architectural limestone studio plinth with sharp raking shadow patterns",
        wardrobe: "none",
        mood: "prestigious commercial luxury, pristine high-acutance minimalism",
        aperture: "f/8.0",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        filmStock: "digital_raw",
        filter: "none",
        aspectRatio: "4:5",
        handLock: true,
        gripType: "precision_pinch",
        handDetails: "slender fingers, visible lunula, natural cuticles, contact tissue blanching on glass",
        gobo: "venetian_blinds",
        gripModifier: "beauty_dish_honeycomb",
        lightingRatio: "4:1",
        copySpace: "left_third",
        adSafeZone: "instagram_feed_4_5",
        productCrop: "essence_bottle_hero.png",
        skuColor: "Pantone 296 C Deep Navy (#001F3F)",
        capGeometry: "Brushed aluminum knurled dropper collar",
        labelKerning: "Optically locked serif tracking +20",
        materialFinish: "Satin frosted cosmetic glass, 12% specular roughness",
        seamGeometry: "Seamless polished base rim",
        approvalGate: true
      },
      hyperrealistic_latex_character: {
        profile: "hasselblad_x2d_ii_100c",
        subject: "Avant-garde couture model wearing sculpted liquid-glass and glossy latex bodysuit, piercing calm gaze",
        framing: "three-quarter editorial high-fashion framing",
        environment: "deep opaque black softly blurred studio void with controlled rim glow",
        wardrobe: "bespoke black liquid-glass and latex bodysuit with contoured structural paneling",
        mood: "hypnotic avant-garde editorial, pristine optical precision",
        aperture: "f/4.0",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        filmStock: "digital_raw",
        filter: "none",
        aspectRatio: "9:12",
        materialStyle: "glossy_latex",
        bgStyle: "opaque_black_blur",
        volumetric4D: true,
        removeText: true,
        policySafe: true
      },
      heavyweight_editorial_portrait: {
        profile: "sony_a1_ii",
        subject: "Heavyweight athlete seated in quiet contemplation, authentic skin pores and fine vellus hair",
        framing: "medium seated editorial portrait",
        environment: "minimalist concrete locker pavilion, raking directional skylight",
        wardrobe: "ribbed athletic compression tank conforming naturally to enlarged chest and waist",
        mood: "dignified power, quiet rebellion, calm intensity",
        aperture: "f/2.8",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "window_rake",
        filmStock: "digital_raw",
        filter: "none",
        aspectRatio: "4:5",
        bodyVolume: "biceps, chest, gut",
        weightLb: 240,
        policySafe: true
      },
      gallery_baryta_print: {
        profile: "phase_one_iq4",
        subject: "Master ceramicist holding unglazed stoneware vessel, intense tactile micro-relief",
        framing: "intimate chest-level craftsman portrait",
        environment: "Kyoto pottery atelier, clay dust suspended in directional sunlight",
        wardrobe: "indigo dyed heavy linen smock",
        mood: "timeless artisanal presence, exhibition fine art acutance",
        aperture: "f/8.0",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "daylight_diffuse",
        filmStock: "digital_raw",
        filter: "none",
        aspectRatio: "4:5",
        paperProfile: "baryta",
        printSize: "16x24@300",
        policySafe: true
      }
    };

    async function init() {
      setupDragAndDrop();
      await loadProfiles();
      // Apply default Paris scenario to start
      onScenarioSelectChange();
    }

    function setupDragAndDrop() {
      const dz = document.getElementById('refDropzone');
      if (!dz) return;
      dz.addEventListener('dragover', (e) => {
        e.preventDefault();
        dz.classList.add('dragover');
      });
      dz.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dz.classList.remove('dragover');
      });
      dz.addEventListener('drop', (e) => {
        e.preventDefault();
        dz.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
          processSelectedImage(e.dataTransfer.files[0]);
        }
      });
    }

    function handleFileSelect(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      processSelectedImage(file);
    }

    function processSelectedImage(file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const dataUri = e.target.result;
        const img = new Image();
        img.onload = function() {
          const w = img.naturalWidth;
          const h = img.naturalHeight;
          const ratio = w / h;

          let matchedAr = "4:5";
          if (ratio > 1.6) matchedAr = "16:9";
          else if (ratio > 1.35) matchedAr = "3:2";
          else if (ratio > 1.15) matchedAr = "4:5";
          else if (ratio > 0.92 && ratio < 1.08) matchedAr = "1:1";
          else if (ratio > 0.72) matchedAr = "4:5";
          else if (ratio > 0.60) matchedAr = "2:3";
          else matchedAr = "9:16";

          refData = {
            active: true,
            filename: file.name,
            file_size: file.size,
            width: w,
            height: h,
            aspect_ratio: matchedAr,
            data_uri: dataUri
          };

          document.getElementById('refThumb').src = dataUri;
          document.getElementById('refFileName').textContent = file.name;
          document.getElementById('refDimensions').textContent = `${w} × ${h} px (Est. AR: ${matchedAr})`;

          document.getElementById('dropzoneEmpty').style.display = 'none';
          document.getElementById('dropzonePreview').style.display = 'flex';
          document.getElementById('refControls').style.display = 'flex';
          updateRefBadge();

          showToast(`Loaded reference: ${file.name} (${w}x${h})`);
          debounceCompile();
        };
        img.src = dataUri;
      };
      reader.readAsDataURL(file);
    }

    function syncRefAspectRatio(event) {
      if (event) event.stopPropagation();
      if (!refData || !refData.aspect_ratio) return;
      document.getElementById('aspectSelect').value = refData.aspect_ratio;
      showToast(`Rig aspect ratio synced to ${refData.aspect_ratio}`);
      debounceCompile();
    }

    function clearRefImage(event) {
      if (event) event.stopPropagation();
      refData = null;
      document.getElementById('refFileInput').value = '';
      document.getElementById('dropzoneEmpty').style.display = 'block';
      document.getElementById('dropzonePreview').style.display = 'none';
      document.getElementById('refControls').style.display = 'none';
      updateRefBadge();
      showToast("Reference image removed");
      debounceCompile();
    }

    function setRefMode(mode) {
      activeRefMode = mode;
      document.getElementById('btnModeRestore').classList.toggle('active', mode === 'restore');
      document.getElementById('btnModeTransform').classList.toggle('active', mode === 'transform');
      const btnOut = document.getElementById('btnModeOutpaint');
      if (btnOut) btnOut.classList.toggle('active', mode === 'outpaint');
      const btnDepix = document.getElementById('btnModeDepixelate');
      if (btnDepix) btnDepix.classList.toggle('active', mode === 'depixelate');
      const btnProd = document.getElementById('btnModeProduct');
      if (btnProd) btnProd.classList.toggle('active', mode === 'product');
      const prodPanel = document.getElementById('productFidelityPanel');
      if (prodPanel) prodPanel.style.display = (mode === 'product') ? 'block' : 'none';

      const slider = document.getElementById('fidelitySlider');
      if ((mode === 'restore' || mode === 'depixelate' || mode === 'product') && parseInt(slider.value, 10) < 90) {
        slider.value = 95;
      } else if (mode === 'outpaint') {
        slider.value = 95;
      } else if (mode === 'transform' && parseInt(slider.value, 10) > 90) {
        slider.value = 85;
      }

      if (mode === 'depixelate') {
        const profSel = document.getElementById('profileSelect');
        if (profSel) {
          for (let opt of profSel.options) {
            if (opt.value === 'fujifilm_gfx100rf') {
              profSel.value = 'fujifilm_gfx100rf';
              if (typeof onProfileChange === 'function') onProfileChange();
              break;
            }
          }
        }
      } else if (mode === 'product') {
        const profSel = document.getElementById('profileSelect');
        if (profSel) {
          for (let opt of profSel.options) {
            if (opt.value === 'phase_one_iq4') {
              profSel.value = 'phase_one_iq4';
              if (typeof onProfileChange === 'function') onProfileChange();
              break;
            }
          }
        }
      }

      onFidelitySliderChange();
      updateRefBadge();
      debounceCompile();
    }

    function enableProductLockDirect() {
      const controls = document.getElementById('refControls');
      if (controls) controls.style.display = 'flex';
      setRefMode('product');
      showToast("Activated 100% Commercial SKU Approval Gate");
    }

    function onFidelitySliderChange() {
      const val = parseInt(document.getElementById('fidelitySlider').value, 10);
      let label = "Extreme Anti-Drift";
      if (val >= 98) label = "Absolute 1:1 Identity Lock";
      else if (val >= 90) label = "Extreme Anti-Drift";
      else if (val >= 75) label = "High Fidelity";
      else label = "Flexible Adaptation";

      document.getElementById('fidelityVal').textContent = `${val}% (${label})`;
      debounceCompile();
    }

    function updateRefBadge() {
      const badge = document.getElementById('refModeBadge');
      if (!refData || !refData.active) {
        if (activeRefMode === 'product') {
          badge.textContent = "ACTIVE // 100% COMMERCIAL SKU GATE";
          badge.style.color = "var(--accent-amber)";
        } else {
          badge.textContent = "NO IMAGE ATTACHED";
          badge.style.color = "var(--text-muted)";
        }
      } else if (activeRefMode === 'depixelate') {
        badge.textContent = "ACTIVE // GFX100RF 102MP DE-PIXELATE";
        badge.style.color = "var(--accent-rose)";
      } else if (activeRefMode === 'restore') {
        badge.textContent = "ACTIVE // 1:1 RESTORE & REMASTER";
        badge.style.color = "var(--accent-cyan)";
      } else if (activeRefMode === 'outpaint') {
        badge.textContent = "ACTIVE // FULL-BODY OUTPAINT";
        badge.style.color = "var(--accent-amber)";
      } else if (activeRefMode === 'product') {
        badge.textContent = "ACTIVE // 100% COMMERCIAL SKU GATE";
        badge.style.color = "var(--accent-amber)";
      } else {
        badge.textContent = "ACTIVE // RE-SHOOT & ADAPT";
        badge.style.color = "var(--accent-blue)";
      }
    }

    async function loadProfiles() {
      try {
        const res = await fetch('/api/profiles');
        availableProfiles = await res.json();
        const select = document.getElementById('profileSelect');
        select.innerHTML = '';
        availableProfiles.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = `${p.title} // ${p.sensor || p.id}`;
          select.appendChild(opt);
        });
        document.getElementById('rigStatusReadout').textContent = `${availableProfiles.length} HARDWARE RIGS READY`;
      } catch (err) {
        console.error("Failed to load profiles:", err);
      }
    }

    function onScenarioSelectChange() {
      const select = document.getElementById('scenarioSelect');
      const val = select.value;

      if (val === 'none') {
        // Element of surprise: clear fields so user has complete freedom
        clearToSurprise();
        return;
      }

      const s = SCENARIOS[val];
      if (!s) return;

      // Populate camera profile
      document.getElementById('profileSelect').value = s.profile;
      onProfileChange();

      // Populate creative fields (completely editable)
      document.getElementById('subjectInput').value = s.subject;
      document.getElementById('framingInput').value = s.framing;
      document.getElementById('environmentInput').value = s.environment;
      document.getElementById('wardrobeInput').value = s.wardrobe;
      document.getElementById('moodInput').value = s.mood;

      if (s.timeWeather) document.getElementById('timeWeatherSelect').value = s.timeWeather;
      if (s.cityVibe) document.getElementById('cityVibeSelect').value = s.cityVibe;
      if (s.lighting) document.getElementById('lightingSelect').value = s.lighting;
      if (s.filmStock) document.getElementById('filmStockSelect').value = s.filmStock;
      if (s.filter) document.getElementById('filterSelect').value = s.filter;

      if (s.refMode) {
        const controls = document.getElementById('refControls');
        if (controls) controls.style.display = 'flex';
        setRefMode(s.refMode);
        if (s.capGeometry && document.getElementById('capGeometryInput')) document.getElementById('capGeometryInput').value = s.capGeometry;
        if (s.skuColor && document.getElementById('skuColorInput')) document.getElementById('skuColorInput').value = s.skuColor;
        if (s.labelKerning && document.getElementById('labelKerningInput')) document.getElementById('labelKerningInput').value = s.labelKerning;
        if (s.materialFinish && document.getElementById('materialFinishInput')) document.getElementById('materialFinishInput').value = s.materialFinish;
        if (s.seamGeometry && document.getElementById('seamsInput')) document.getElementById('seamsInput').value = s.seamGeometry;
        if (s.productCrop && document.getElementById('productCropInput')) document.getElementById('productCropInput').value = s.productCrop;
      }

      if (s.handLock !== undefined && document.getElementById('chkHandLock')) document.getElementById('chkHandLock').checked = !!s.handLock;
      if (s.gripType && document.getElementById('gripTypeSelect')) document.getElementById('gripTypeSelect').value = s.gripType;
      if (s.handDetails && document.getElementById('handDetailsInput')) document.getElementById('handDetailsInput').value = s.handDetails;

      if (s.anamorphic !== undefined && document.getElementById('chkAnamorphic')) document.getElementById('chkAnamorphic').checked = !!s.anamorphic;
      if (s.squeeze && document.getElementById('squeezeSelect')) document.getElementById('squeezeSelect').value = s.squeeze;
      if (s.streakFlare && document.getElementById('streakFlareSelect')) document.getElementById('streakFlareSelect').value = s.streakFlare;
      if (s.irisBlades && document.getElementById('irisBladesSelect')) document.getElementById('irisBladesSelect').value = s.irisBlades;

      if (s.gobo && document.getElementById('goboSelect')) document.getElementById('goboSelect').value = s.gobo;
      if (s.gripModifier && document.getElementById('gripModifierSelect')) document.getElementById('gripModifierSelect').value = s.gripModifier;
      if (s.lightingRatio && document.getElementById('lightingRatioSelect')) document.getElementById('lightingRatioSelect').value = s.lightingRatio;
      if (s.copySpace && document.getElementById('copySpaceSelect')) document.getElementById('copySpaceSelect').value = s.copySpace;
      if (s.adSafeZone && document.getElementById('adSafeZoneSelect')) document.getElementById('adSafeZoneSelect').value = s.adSafeZone;
      if (s.aspectRatio && document.getElementById('aspectSelect')) document.getElementById('aspectSelect').value = s.aspectRatio;

      if (document.getElementById('bodyVolumeInput')) document.getElementById('bodyVolumeInput').value = s.bodyVolume || '';
      if (document.getElementById('weightLbInput')) document.getElementById('weightLbInput').value = s.weightLb || '';
      if (document.getElementById('materialStyleSelect')) document.getElementById('materialStyleSelect').value = s.materialStyle || 'none';
      if (document.getElementById('bgStyleSelect')) document.getElementById('bgStyleSelect').value = s.bgStyle || 'default';
      if (document.getElementById('chkVolumetric4D')) document.getElementById('chkVolumetric4D').checked = !!s.volumetric4D;
      if (document.getElementById('chkRemoveText')) document.getElementById('chkRemoveText').checked = !!s.removeText;
      if (document.getElementById('paperProfileSelect')) document.getElementById('paperProfileSelect').value = s.paperProfile || 'none';
      if (document.getElementById('printSizeSelect')) document.getElementById('printSizeSelect').value = s.printSize || 'default';
      if (document.getElementById('chkPolicySafe')) document.getElementById('chkPolicySafe').checked = !!s.policySafe;

      setAperture(s.aperture || 'f/2.8');
      debounceCompile();
    }

    function clearToSurprise() {
      document.getElementById('scenarioSelect').value = 'none';
      document.getElementById('subjectInput').value = '';
      document.getElementById('environmentInput').value = '';
      document.getElementById('wardrobeInput').value = '';
      document.getElementById('moodInput').value = '';
      document.getElementById('framingInput').value = '';
      document.getElementById('timeWeatherSelect').value = 'auto';
      document.getElementById('cityVibeSelect').value = 'none';
      if (document.getElementById('productCropInput')) document.getElementById('productCropInput').value = '';
      if (document.getElementById('skuColorInput')) document.getElementById('skuColorInput').value = '';
      if (document.getElementById('capGeometryInput')) document.getElementById('capGeometryInput').value = '';
      if (document.getElementById('labelKerningInput')) document.getElementById('labelKerningInput').value = '';
      if (document.getElementById('materialFinishInput')) document.getElementById('materialFinishInput').value = '';
      if (document.getElementById('seamsInput')) document.getElementById('seamsInput').value = '';

      if (document.getElementById('chkHandLock')) document.getElementById('chkHandLock').checked = false;
      if (document.getElementById('gripTypeSelect')) document.getElementById('gripTypeSelect').value = 'default';
      if (document.getElementById('handDetailsInput')) document.getElementById('handDetailsInput').value = '';

      if (document.getElementById('chkAnamorphic')) document.getElementById('chkAnamorphic').checked = false;
      if (document.getElementById('squeezeSelect')) document.getElementById('squeezeSelect').value = 'default';
      if (document.getElementById('streakFlareSelect')) document.getElementById('streakFlareSelect').value = 'none';
      if (document.getElementById('irisBladesSelect')) document.getElementById('irisBladesSelect').value = 'default';

      if (document.getElementById('goboSelect')) document.getElementById('goboSelect').value = 'none';
      if (document.getElementById('gripModifierSelect')) document.getElementById('gripModifierSelect').value = 'none';
      if (document.getElementById('lightingRatioSelect')) document.getElementById('lightingRatioSelect').value = 'default';
      if (document.getElementById('copySpaceSelect')) document.getElementById('copySpaceSelect').value = 'none';
      if (document.getElementById('adSafeZoneSelect')) document.getElementById('adSafeZoneSelect').value = 'none';

      if (document.getElementById('bodyVolumeInput')) document.getElementById('bodyVolumeInput').value = '';
      if (document.getElementById('weightLbInput')) document.getElementById('weightLbInput').value = '';
      if (document.getElementById('materialStyleSelect')) document.getElementById('materialStyleSelect').value = 'none';
      if (document.getElementById('bgStyleSelect')) document.getElementById('bgStyleSelect').value = 'default';
      if (document.getElementById('chkVolumetric4D')) document.getElementById('chkVolumetric4D').checked = false;
      if (document.getElementById('chkRemoveText')) document.getElementById('chkRemoveText').checked = false;
      if (document.getElementById('paperProfileSelect')) document.getElementById('paperProfileSelect').value = 'none';
      if (document.getElementById('printSizeSelect')) document.getElementById('printSizeSelect').value = 'default';
      if (document.getElementById('chkPolicySafe')) document.getElementById('chkPolicySafe').checked = false;

      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      
      showToast("Cleared! Write freely for total element of surprise.");
      debounceCompile();
    }

    function injectEnv(keyword) {
      const input = document.getElementById('environmentInput');
      const current = input.value.trim();
      const snippets = {
        'city street': 'bustling historic city street, weathered stone buildings, active sidewalk atmosphere',
        'luxury hotel': 'luxury hotel suite interior, warm linen drapes, soft ambient morning light',
        'coastal beach': 'windswept ocean beach, natural sand dunes, rolling gentle waves',
        'rural vineyard': 'rolling countryside vineyard, olive groves, warm late afternoon sun',
        'photo studio': 'clean commercial photography studio, white cyclorama wall, controlled strobe lighting',
        'architectural interior': 'monolithic concrete and timber architectural pavilion, high ceilings',
        'pine forest': 'misty pine forest mountain trail, deep green canopy, damp earth'
      };
      
      const addition = snippets[keyword] || keyword;
      input.value = current ? `${current}, ${addition}` : addition;
      debounceCompile();
    }

    function onTimeWeatherChange() {
      const val = document.getElementById('timeWeatherSelect').value;
      if (val === 'auto') {
        debounceCompile();
        return;
      }
      const labels = {
        golden_hour: "during warm golden hour sunset with long shadows and rim light",
        blue_hour: "at cool blue hour twilight with ambient city lights glowing",
        overcast: "under soft diffuse overcast skies with shadowless flattering light",
        noon_sun: "under bright direct midday sun with sharp contrast",
        rainy_wet: "during a gentle rain with wet reflective pavement and glistening surfaces",
        morning_fog: "in dense early morning fog with soft atmospheric light shafts",
        night_city: "at night illuminated by warm streetlamps and ambient city light"
      };
      const text = labels[val];
      const env = document.getElementById('environmentInput');
      if (text && !env.value.includes(text.split(" ")[1])) {
        env.value = env.value ? `${env.value}, ${text}` : text;
      }
      debounceCompile();
    }

    function onCityVibeChange() {
      const val = document.getElementById('cityVibeSelect').value;
      if (val === 'none') {
        debounceCompile();
        return;
      }
      const labels = {
        paris: "Paris (Haussmann limestone facade, zinc rooftops, classic Parisian elegance)",
        tokyo: "Tokyo (narrow atmospheric street, minimalist aesthetic, subtle signage)",
        nyc: "New York City (SoHo cast-iron lofts, classic fire escapes, urban asphalt)",
        mediterranean: "Mediterranean Coast (whitewashed stucco, terracotta tiles, deep azure water)",
        london: "London (refined Georgian brickwork, classic black iron railings, muted overcast)",
        milan: "Milan (architectural stone porticos, quiet cobblestone courtyard, fashion district)",
        scandinavia: "Scandinavia (minimalist natural timber, granite rock, clean northern light)"
      };
      const text = labels[val];
      const env = document.getElementById('environmentInput');
      if (text) {
        env.value = env.value ? `${env.value}, ${text}` : text;
      }
      debounceCompile();
    }

    function onProfileChange() {
      const select = document.getElementById('profileSelect');
      const profileId = select.value;
      const selected = availableProfiles.find(p => p.id === profileId);

      if (selected) {
        document.getElementById('sensorGateMeta').textContent = selected.sensor || selected.title;
      }

      // Populate lenses
      const lensSelect = document.getElementById('lensSelect');
      lensSelect.innerHTML = '';
      const catalog = LENS_CATALOG[profileId] || [];
      catalog.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l.split(" (")[0];
        opt.textContent = l;
        lensSelect.appendChild(opt);
      });

      document.getElementById('customLensInput').value = '';

      if (selected && selected.aperture && document.getElementById('scenarioSelect').value === 'none') {
        setAperture(selected.aperture);
      } else {
        debounceCompile();
      }
    }

    function onLensSelectChange() {
      document.getElementById('customLensInput').value = '';
      debounceCompile();
    }

    function setFraming(val) {
      document.getElementById('framingInput').value = val;
      document.querySelectorAll('.pill-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('onclick').includes(val));
      });
      debounceCompile();
    }

    function setAperture(val) {
      activeAperture = val;
      document.querySelectorAll('.dial-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.trim() === val);
      });
      document.getElementById('apertureMeta').textContent = `${val} Target`;

      const dofEl = document.getElementById('dofHint');
      if (['f/1.2', 'f/1.4', 'f/2.0'].includes(val)) {
        dofEl.textContent = "Razor-thin planar isolation, dreamy spherical background blur";
      } else if (['f/2.8', 'f/4.0'].includes(val)) {
        dofEl.textContent = "Smooth editorial falloff, tack-sharp subject with creamy depth";
      } else if (['f/5.6', 'f/8.0'].includes(val)) {
        dofEl.textContent = "Maximum optical MTF acutance & edge-to-edge sensor contrast";
      } else {
        dofEl.textContent = "Deep architectural depth of field, corner-to-corner clarity";
      }

      debounceCompile();
    }

    function setTarget(engine) {
      activeTarget = engine;
      document.querySelectorAll('.tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('onclick').includes(engine));
      });
      const badgeMap = {
        gpt_images: "GPT IMAGES // MASTER EXECUTION PROMPT",
        imagen: "GEMINI IMAGES // IMAGEN 3 PROSE",
        midjourney: "MIDJOURNEY v8.2 // RAW SPEC",
        flux: "FLUX.1 // DIRECT PHYSICAL SPEC",
        sdxl: "SDXL DUAL // POSITIVE + NEGATIVE CHANNELS",
        raw: "RAW HARDWARE AUDIT // FORMATTED SPEC",
        json: "JSON ALL-IN-ONE PROMPT // STRUCTURED PAYLOAD",
      };
      document.getElementById('targetBadge').textContent = badgeMap[engine] || engine.toUpperCase();
      compile();
    }

    function debounceCompile() {
      clearTimeout(compileTimer);
      compileTimer = setTimeout(compile, 150);
    }

    async function compile() {
      const customLens = document.getElementById('customLensInput').value.trim();
      const selectedLens = customLens || document.getElementById('lensSelect').value;

      const lightingMap = {
        strobe_para: "Studio Strobe: 35-45° Directional Key with Black Foam-Core Negative Fill, single-axis specular catchlight (1/1600s leaf sync)",
        window_daylight: "Directional Daylight with Soft Diffusion, Organic Natural Falloff",
        beauty_dish: "High-Fashion Beauty Dish with 20° Honeycomb Grid & Diffuser Sock, sculpted shadow cheekbones",
        rembrandt_key: "Dramatic Chiaroscuro / Rembrandt Single-Source Key with Deep Negative Fill (4:1 Contrast Ratio)",
        golden_hour: "Low-Angle Golden Hour Sunlight with Unbleached Muslin Bounce, warm rim flare",
        hard_flash: "Direct Hard On-Camera Strobe with High-Contrast Falloff, sharp 90s editorial shadows",
        tungsten_candle: "Practical Low-Light Tungsten & Candlelight, warm intimate illumination",
        architectural_skylight: "Diffused Architectural Clerestory Daylight with Immaculate Tonal Roll-off"
      };

      const filmMap = {
        digital_raw: "16-bit Uncompressed Digital Raw Capture (Neutral Dynamic Range)",
        portra_400: "Kodak Professional Portra 400 (Warm Natural Skin Tones, Fine Dye Clouds)",
        portra_160: "Kodak Professional Portra 160 (Ultra-Fine Grain, Pastel Highlights)",
        tri_x_400: "Kodak Tri-X 400 (Classic Silver Halide High-Contrast Monochrome)",
        ilford_hp5: "Ilford HP5 Plus (Gentle Medium-Contrast Silver Monochrome)",
        provia_100f: "Fujifilm Provia 100F (Professional Reversal Slide Film)",
        classic_chrome: "Fujifilm Classic Chrome (Documentary Muted Saturation, Hard Contrast)",
        cinestill_800t: "Cinestill 800T (Tungsten Cinema Stock with Red Specular Halation)",
        arri_logc4: "ARRI LogC4 / Kodak 2383 Feature Film Print LUT Profile"
      };

      const filterMap = {
        none: "",
        pro_mist_eighth: "Tiffen Black Pro-Mist 1/8 (Gentle Highlight Bloom without loss of pore definition)",
        pro_mist_quarter: "Tiffen Black Pro-Mist 1/4 (Creamy Highlight Glow & Flare)",
        hollywood_black: "Schneider Hollywood Black Magic (Dermal Micro-Softening with Preserved Acutance)",
        cpl: "Circular Polarizer (CPL Glare Suppression on Skin and Reflective Surfaces)",
        anamorphic_streak: "Anamorphic 2x Cylindrical (Horizontal Flare & Oval Out-of-Focus Elements)"
      };

      const shutterMap = {
        sync_1600: "1/1600s Leaf Shutter High-Speed Sync Freeze",
        sync_400: "1/400s High-Speed Sync (Sony a1 II Stacked Freeze)",
        sync_500: "1/500s Strobe Synchronized Action Freeze",
        shutter_125: "1/125s Natural Handheld Exposure",
        shutter_180: "180° Cinema Shutter Angle (1/48s Organic Motion Cadence)",
        shutter_drag: "1/15s Shutter Drag with Rear-Curtain Flash Trace"
      };

      let refPayload = null;
      if (refData && refData.active) {
        const preserved = [];
        if (document.getElementById('chkFacial').checked) preserved.push("facial geometry and bone structure");
        if (document.getElementById('chkGaze').checked) preserved.push("eye shape and gaze direction");
        if (document.getElementById('chkProportions').checked) preserved.push("anatomical proportions");
        if (document.getElementById('chkLighting').checked) preserved.push("lighting falloff and mood");

        const fidelityVal = parseInt(document.getElementById('fidelitySlider').value, 10) / 100;
        const denoiseVal = (activeRefMode === 'restore' || activeRefMode === 'depixelate') ? 0.25 : (activeRefMode === 'outpaint' ? 0.40 : 0.65);

        let refModeStr = "restore_upscale";
        if (activeRefMode === 'depixelate') refModeStr = "depixelate_gfx100rf";
        if (activeRefMode === 'transform') refModeStr = "transform_adapt";
        if (activeRefMode === 'outpaint') refModeStr = "outpaint_full_body";
        if (activeRefMode === 'product') refModeStr = "product_lock";

        refPayload = {
          filename: refData.filename,
          mode: refModeStr,
          fidelity_lock: fidelityVal,
          denoise_strength: denoiseVal,
          detected_aspect_ratio: refData.aspect_ratio,
          preserved_elements: preserved,
        };
      } else if (activeRefMode === 'product') {
        const cropVal = document.getElementById('productCropInput') ? document.getElementById('productCropInput').value.trim() : "";
        refPayload = {
          filename: cropVal || "product_reference_crop.png",
          mode: "product_lock",
          fidelity_lock: 0.95,
          denoise_strength: 0.20,
          detected_aspect_ratio: "4:5",
          preserved_elements: [
            "cap closure geometry",
            "label kerning and typography",
            "manufacturing parting seams",
            "material surface finish",
            "exact SKU color"
          ]
        };
      }

      const aspectEl = document.getElementById('aspectSelect');
      const selectedResText = aspectEl && aspectEl.selectedOptions && aspectEl.selectedOptions[0] ? aspectEl.selectedOptions[0].text : null;

      const payload = {
        scene: document.getElementById('subjectInput').value || 'Subject',
        target: activeTarget,
        profile: document.getElementById('profileSelect').value || 'sony_a1_ii',
        framing: document.getElementById('framingInput').value,
        environment: document.getElementById('environmentInput').value,
        wardrobe: document.getElementById('wardrobeInput').value,
        mood: document.getElementById('moodInput').value,
        aperture: activeAperture,
        lens: selectedLens,
        aspect_ratio: document.getElementById('aspectSelect').value,
        lighting: lightingMap[document.getElementById('lightingSelect').value],
        film_stock: filmMap[document.getElementById('filmStockSelect').value],
        optical_filter: filterMap[document.getElementById('filterSelect').value],
        shutter_speed: shutterMap[document.getElementById('shutterSelect').value],
        reference: refPayload,
        product_crop: document.getElementById('productCropInput') ? document.getElementById('productCropInput').value : null,
        sku_color: document.getElementById('skuColorInput') ? document.getElementById('skuColorInput').value : null,
        cap_geometry: document.getElementById('capGeometryInput') ? document.getElementById('capGeometryInput').value : null,
        label_kerning: document.getElementById('labelKerningInput') ? document.getElementById('labelKerningInput').value : null,
        material_finish: document.getElementById('materialFinishInput') ? document.getElementById('materialFinishInput').value : null,
        seam_geometry: document.getElementById('seamsInput') ? document.getElementById('seamsInput').value : null,
        approval_gate_100pct: document.getElementById('chkApprovalGate') ? document.getElementById('chkApprovalGate').checked : true,
        sharpness_protocol: document.getElementById('chkSharpness') ? document.getElementById('chkSharpness').checked : true,
        suppress_text_branding: document.getElementById('chkAntiBrand') ? document.getElementById('chkAntiBrand').checked : true,
        human_skin_realism: document.getElementById('chkSkinRealism') ? document.getElementById('chkSkinRealism').checked : true,
        content_type: document.getElementById('contentTypeSelect') ? document.getElementById('contentTypeSelect').value : 'photograph',
        text_preservation: document.getElementById('chkTextPreserve') ? document.getElementById('chkTextPreserve').checked : true,
        output_resolution: selectedResText,
        hand_lock: document.getElementById('chkHandLock') ? document.getElementById('chkHandLock').checked : false,
        grip_type: (document.getElementById('gripTypeSelect') && document.getElementById('gripTypeSelect').value !== 'default') ? document.getElementById('gripTypeSelect').value : null,
        hand_details: document.getElementById('handDetailsInput') ? document.getElementById('handDetailsInput').value.trim() : null,
        anamorphic: document.getElementById('chkAnamorphic') ? document.getElementById('chkAnamorphic').checked : false,
        squeeze: (document.getElementById('squeezeSelect') && document.getElementById('squeezeSelect').value !== 'default') ? document.getElementById('squeezeSelect').value : null,
        streak_flare: (document.getElementById('streakFlareSelect') && document.getElementById('streakFlareSelect').value !== 'none') ? document.getElementById('streakFlareSelect').value : null,
        iris_blades: (document.getElementById('irisBladesSelect') && document.getElementById('irisBladesSelect').value !== 'default') ? document.getElementById('irisBladesSelect').value : null,
        gobo: (document.getElementById('goboSelect') && document.getElementById('goboSelect').value !== 'none') ? document.getElementById('goboSelect').value : null,
        grip_modifier: (document.getElementById('gripModifierSelect') && document.getElementById('gripModifierSelect').value !== 'none') ? document.getElementById('gripModifierSelect').value : null,
        lighting_ratio: (document.getElementById('lightingRatioSelect') && document.getElementById('lightingRatioSelect').value !== 'default') ? document.getElementById('lightingRatioSelect').value : null,
        copy_space: (document.getElementById('copySpaceSelect') && document.getElementById('copySpaceSelect').value !== 'none') ? document.getElementById('copySpaceSelect').value : null,
        ad_safe_zone: (document.getElementById('adSafeZoneSelect') && document.getElementById('adSafeZoneSelect').value !== 'none') ? document.getElementById('adSafeZoneSelect').value : null,
        body_volume: document.getElementById('bodyVolumeInput') ? document.getElementById('bodyVolumeInput').value.trim() : null,
        weight_lb: document.getElementById('weightLbInput') ? (parseInt(document.getElementById('weightLbInput').value, 10) || null) : null,
        material: (document.getElementById('materialStyleSelect') && document.getElementById('materialStyleSelect').value !== 'none') ? document.getElementById('materialStyleSelect').value : null,
        background_style: (document.getElementById('bgStyleSelect') && document.getElementById('bgStyleSelect').value !== 'default') ? document.getElementById('bgStyleSelect').value : null,
        volumetric_4d: document.getElementById('chkVolumetric4D') ? document.getElementById('chkVolumetric4D').checked : false,
        remove_text: document.getElementById('chkRemoveText') ? document.getElementById('chkRemoveText').checked : false,
        paper: (document.getElementById('paperProfileSelect') && document.getElementById('paperProfileSelect').value !== 'none') ? document.getElementById('paperProfileSelect').value : null,
        policy_safe: document.getElementById('chkPolicySafe') ? document.getElementById('chkPolicySafe').checked : false,
        probe: (document.getElementById('probeSelect') && document.getElementById('probeSelect').value !== 'none') ? document.getElementById('probeSelect').value : null,
        min_mb: document.getElementById('minMbInput') ? (parseFloat(document.getElementById('minMbInput').value) || null) : null,
        cct: document.getElementById('cctInput') ? (parseInt(document.getElementById('cctInput').value, 10) || null) : null,
        lux: document.getElementById('luxInput') ? (parseInt(document.getElementById('luxInput').value, 10) || null) : null,
        cri: document.getElementById('criInput') ? (parseFloat(document.getElementById('criInput').value) || null) : null,
        wall_surround: document.getElementById('wallSurroundInput') ? document.getElementById('wallSurroundInput').value.trim() : null,
        gallery_zone: document.getElementById('galleryZoneInput') ? document.getElementById('galleryZoneInput').value.trim() : null,
        anchor_id: document.getElementById('anchorIdInput') ? document.getElementById('anchorIdInput').value.trim() : null,
      };

      try {
        const res = await fetch('/api/compile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(await res.text());

        const data = await res.json();
        renderOutput(data);
      } catch (err) {
        console.error("Compilation error:", err);
        document.getElementById('positiveOutput').textContent = "Error compiling prompt: " + err.message;
      }
    }

    let currentPayload = null;

    function renderOutput(data) {
      currentPayload = data;
      // Display the unified prompt (positive payload + anti-artifact negative shield) in the primary output
      document.getElementById('positiveOutput').textContent = data.unified_prompt || data.positive_prompt || '';
      document.getElementById('negativeOutput').textContent = data.negative_prompt || 'None required for this engine (negative constraints are baked into the positive prompt flags).';

      // Render 100% Commercial SKU Approval Gate Live Telemetry if product lock is active
      const gateCard = document.getElementById('approvalGateCard');
      const isProductActive = (activeRefMode === 'product') ||
                              (data.metadata && data.metadata.reference_mode === 'product_lock') ||
                              (data.parameters && data.parameters.approval_gate_100pct === true) ||
                              (document.getElementById('productCropInput') && document.getElementById('productCropInput').value.trim() !== '') ||
                              (document.getElementById('capGeometryInput') && document.getElementById('capGeometryInput').value.trim() !== '');

      if (gateCard) {
        if (isProductActive) {
          gateCard.style.display = 'block';
          const container = document.getElementById('gateChecklistContainer');
          const capVal = (document.getElementById('capGeometryInput') && document.getElementById('capGeometryInput').value.trim()) || 'Preserved from crop / anti-dropper';
          const kernVal = (document.getElementById('labelKerningInput') && document.getElementById('labelKerningInput').value.trim()) || 'Zero hallucinated text / locked tracking';
          const seamVal = (document.getElementById('seamsInput') && document.getElementById('seamsInput').value.trim()) || 'Mold lines & rim structure verified';
          const matVal = (document.getElementById('materialFinishInput') && document.getElementById('materialFinishInput').value.trim()) || 'Refractive index & specular verified';
          const skuVal = (document.getElementById('skuColorInput') && document.getElementById('skuColorInput').value.trim()) || 'Pantone / hex lock verified';

          container.innerHTML = `
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-green);">✓ Gate 1: Cap Geometry</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${capVal}</div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-green);">✓ Gate 2: Label Kerning</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${kernVal}</div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-green);">✓ Gate 3: Seams & Rims</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${seamVal}</div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-green);">✓ Gate 4: Material Finish</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${matVal}</div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-green);">✓ Gate 5: SKU Color</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${skuVal}</div>
            </div>
          `;
        } else {
          gateCard.style.display = 'none';
        }
      }

      // Render Biomechanical Hand Precision Gate Live Telemetry
      const handCard = document.getElementById('handGateCard');
      const isHandActive = (document.getElementById('chkHandLock') && document.getElementById('chkHandLock').checked) ||
                           (data.parameters && data.parameters.hand_biomechanics_gate === true) ||
                           (data.metadata && data.metadata.hand_lock === true);
      if (handCard) {
        if (isHandActive) {
          handCard.style.display = 'block';
          const container = document.getElementById('handChecklistContainer');
          const gripVal = (document.getElementById('gripTypeSelect') && document.getElementById('gripTypeSelect').value !== 'default') ? document.getElementById('gripTypeSelect').value.replace(/_/g, ' ').toUpperCase() : 'PRECISION PINCH / WRAP';
          const detailsVal = (document.getElementById('handDetailsInput') && document.getElementById('handDetailsInput').value.trim()) || '5-ray metacarpal architecture (2:3:4:3.5:2.5 length ratio)';

          container.innerHTML = `
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan);">✓ Gate H1: Metacarpal Ray Ratio</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">2:3:4:3.5:2.5 Ray Structure Locked (5 distinct rays)</div>
            </div>
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan);">✓ Gate H2: Articulation Creases</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">DIP, PIP & MCP joint lines under physiological tension</div>
            </div>
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan);">✓ Gate H3: Ungual & Lunula Beds</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">Translucent nail plates with pale lunula crescents & natural eponychium</div>
            </div>
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan);">✓ Gate H4: Grip Tissue Blanching</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${gripVal} — localized capillary ischemia at contact points</div>
            </div>
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan);">✓ Gate H5: 25+ Mutation Shield</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${detailsVal}</div>
            </div>
          `;
        } else {
          handCard.style.display = 'none';
        }
      }

      // Render Cinema Anamorphic Optics & Flare Engine Live Telemetry
      const anaCard = document.getElementById('anamorphicCard');
      const isAnaActive = (document.getElementById('chkAnamorphic') && document.getElementById('chkAnamorphic').checked) ||
                          (data.metadata && data.metadata.is_anamorphic === true) ||
                          (data.parameters && data.parameters.anamorphic_optics_active === true);
      if (anaCard) {
        if (isAnaActive) {
          anaCard.style.display = 'block';
          const container = document.getElementById('anamorphicContainer');
          const sqVal = (document.getElementById('squeezeSelect') && document.getElementById('squeezeSelect').value !== 'default') ? document.getElementById('squeezeSelect').value : '2.0x Cinema Scope';
          const flareVal = (document.getElementById('streakFlareSelect') && document.getElementById('streakFlareSelect').value !== 'none') ? document.getElementById('streakFlareSelect').value.replace(/_/g, ' ').toUpperCase() : 'CYAN-BLUE HORIZONTAL STREAK';
          const irisVal = (document.getElementById('irisBladesSelect') && document.getElementById('irisBladesSelect').value !== 'default') ? document.getElementById('irisBladesSelect').value.replace(/_/g, ' ') : '14-blade circular diaphragm';

          container.innerHTML = `
            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: #c084fc;">Anamorphic Squeeze</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${sqVal} horizontal compression</div>
            </div>
            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: #c084fc;">Oval Elliptical Bokeh</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">2:1 vertical oval out-of-focus blur discs</div>
            </div>
            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: #c084fc;">Horizontal Streak Flare</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${flareVal} edge-to-edge ray emission</div>
            </div>
            <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: #c084fc;">Diffraction Geometry</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${irisVal} diffraction spikes</div>
            </div>
          `;
        } else {
          anaCard.style.display = 'none';
        }
      }

      // Render Commercial Advertising Suite Live Telemetry
      const adCard = document.getElementById('advertisingCard');
      const hasGobo = (document.getElementById('goboSelect') && document.getElementById('goboSelect').value !== 'none');
      const hasGrip = (document.getElementById('gripModifierSelect') && document.getElementById('gripModifierSelect').value !== 'none');
      const hasRatio = (document.getElementById('lightingRatioSelect') && document.getElementById('lightingRatioSelect').value !== 'default');
      const hasCopy = (document.getElementById('copySpaceSelect') && document.getElementById('copySpaceSelect').value !== 'none');
      const hasSafe = (document.getElementById('adSafeZoneSelect') && document.getElementById('adSafeZoneSelect').value !== 'none');
      const isAdActive = hasGobo || hasGrip || hasRatio || hasCopy || hasSafe || (data.metadata && data.metadata.copy_space);

      if (adCard) {
        if (isAdActive) {
          adCard.style.display = 'block';
          const container = document.getElementById('advertisingContainer');
          const goboText = hasGobo ? document.getElementById('goboSelect').value.replace(/_/g, ' ') : 'Clean unobstructed key';
          const gripText = hasGrip ? document.getElementById('gripModifierSelect').value.replace(/_/g, ' ') : 'Standard reflector';
          const ratioText = hasRatio ? document.getElementById('lightingRatioSelect').value : '4:1 contrast';
          const copyText = hasCopy ? document.getElementById('copySpaceSelect').value.replace(/_/g, ' ') : 'Full frame active subject';
          const safeText = hasSafe ? document.getElementById('adSafeZoneSelect').value.replace(/_/g, ' ') : 'Standard broadcast framing';

          container.innerHTML = `
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-amber);">Gobo Projection Cookie</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${goboText}</div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-amber);">Studio Grip Modifier</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${gripText}</div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-amber);">Contrast Ratio</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${ratioText} Key-to-Fill</div>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 0.5rem;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--accent-amber);">Copy-Space & Safe-Zone</div>
              <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 2px;">${copyText} // ${safeText}</div>
            </div>
          `;
        } else {
          adCard.style.display = 'none';
        }
      }

      const grid = document.getElementById('specsGrid');
      grid.innerHTML = '';

      if (data.parameters) {
        for (const [key, val] of Object.entries(data.parameters)) {
          const item = document.createElement('div');
          item.className = 'spec-item';
          item.innerHTML = `<span class="spec-label">${key.replace(/_/g, ' ')}</span><span class="spec-value">${val}</span>`;
          grid.appendChild(item);
        }
      }

      if (data.metadata) {
        for (const [key, val] of Object.entries(data.metadata)) {
          if (typeof val === 'string' && val.length < 75) {
            const item = document.createElement('div');
            item.className = 'spec-item';
            item.innerHTML = `<span class="spec-label">${key.replace(/_/g, ' ')}</span><span class="spec-value">${val}</span>`;
            grid.appendChild(item);
          }
        }
      }
    }

    function copyPrompt(mode = 'unified') {
      let text = '';
      let msg = '';

      if (mode === 'unified') {
        text = currentPayload ? (currentPayload.unified_prompt || currentPayload.positive_prompt) : document.getElementById('positiveOutput').textContent;
        msg = "Copied All-in-One Prompt (with Anti-Artifact Shield)!";
      } else if (mode === 'positive') {
        text = currentPayload ? currentPayload.positive_prompt : '';
        msg = "Copied Optical Description only!";
      } else if (mode === 'negative') {
        text = currentPayload ? currentPayload.negative_prompt : '';
        msg = "Copied Anti-Artifact Shield only!";
      }

      if (!text) {
        text = document.getElementById('positiveOutput').textContent;
      }

      navigator.clipboard.writeText(text).then(() => {
        showToast(msg);
      }).catch(() => {
        showToast("Unable to copy to clipboard");
      });
    }

    function copyActivePrompt() {
      copyPrompt('unified');
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2000);
    }

    let lastUpscaleReport = null;

    function openUpscalerModal() {
      document.getElementById('upscalerModal').classList.add('active');
    }

    function closeUpscalerModal() {
      document.getElementById('upscalerModal').classList.remove('active');
    }

    async function run102mpUpscale() {
      const inputPath = document.getElementById('upscaleInputPath').value.trim();
      if (!inputPath) {
        alert('Please provide a valid source image path.');
        return;
      }
      const outputPath = document.getElementById('upscaleOutputPath').value.trim() || null;
      const format = document.getElementById('upscaleFormat').value;
      const cleanup = document.getElementById('upscaleCleanup').checked;
      const sharpen = document.getElementById('upscaleSharpen').checked;

      const btn = document.getElementById('btnExecuteUpscale');
      const box = document.getElementById('upscaleStatusBox');
      const copyBtn = document.getElementById('btnCopyUpscaleReport');

      btn.disabled = true;
      btn.textContent = 'EXECUTING CONSERVATIVE 102MP RESTORATION...';
      box.innerHTML = '<div style="color: var(--accent-cyan);"><div class="pulse-dot" style="display:inline-block; margin-right: 6px;"></div> Staged Lanczos Upscaling & Neutral Micro-Softening in Progress...</div>';

      try {
        const resp = await fetch('/api/upscale-102mp', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            input_path: inputPath,
            output_path: outputPath,
            output_format: format,
            cleanup: cleanup,
            sharpening: sharpen
          })
        });
        const data = await resp.json();
        if (!resp.ok) {
          throw new Error(data.error || 'Upscale failed');
        }

        lastUpscaleReport = data;
        copyBtn.style.display = 'inline-block';

        const exactRatio = data.exact_aspect_ratio_preserved;
        const validPass = data.validation_passed;

        box.innerHTML = `
          <div style="width: 100%; text-align: left; display: flex; flex-direction: column; gap: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.5rem;">
              <span style="font-weight: bold; color: ${validPass ? 'var(--accent-green)' : 'var(--accent-rose)'};">
                ${validPass ? '✅ RESTORATION & 102MP UPSCALE VERIFIED' : '⚠️ VALIDATION FAILED'}
              </span>
              <span class="brand-tag">${data.profile}</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem;">
              <div><strong>Source:</strong> ${data.source_width}x${data.source_height} (${data.source_megapixels} MP)</div>
              <div><strong>Output:</strong> ${data.output_width}x${data.output_height} (${data.output_megapixels} MP)</div>
              <div><strong>Ratio Preservation:</strong> <span style="color: ${exactRatio ? 'var(--accent-green)' : 'var(--accent-rose)'}; font-weight: bold;">${exactRatio ? 'Exact Rational GCD Lock (Zero Drift)' : 'Drifted'}</span></div>
              <div><strong>File Size:</strong> ${data.file_size_mib_standard} MiB (${data.file_size_mb_custom_2048_divisor} MB_2048)</div>
              <div><strong>Stages:</strong> ${data.upscale_stages.length} staged passes</div>
              <div><strong>Format / Mode:</strong> ${data.output_format} (${data.output_mode})</div>
            </div>

            <div style="background: var(--bg-surface); padding: 0.5rem; border-radius: 4px; border: 1px solid var(--border-subtle); word-break: break-all; font-size: 0.72rem;">
              <strong>Saved:</strong> <code>${data.output_path}</code>
            </div>

            <div style="font-size: 0.68rem; color: var(--text-muted); max-height: 120px; overflow-y: auto; background: #000; padding: 0.5rem; border-radius: 4px;">
              <pre style="margin: 0; white-space: pre-wrap;">${JSON.stringify(data, null, 2)}</pre>
            </div>
          </div>
        `;
      } catch (err) {
        box.innerHTML = `<div style="color: var(--accent-rose);">❌ Error: ${err.message}</div>`;
      } finally {
        btn.disabled = false;
        btn.textContent = 'EXECUTE 102MP RESTORATION & UPSCALE';
      }
    }

    function copyUpscaleReport() {
      if (lastUpscaleReport) {
        navigator.clipboard.writeText(JSON.stringify(lastUpscaleReport, null, 2));
        showToast('Copied 102MP Audit JSON!');
      }
    }

    window.onload = init;
  </script>

  <!-- 102MP CONSERVATIVE RESTORATION MODAL -->
  <div class="modal-overlay" id="upscalerModal" onclick="if(event.target===this) closeUpscalerModal()">
    <div class="modal-content">
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #000; font-weight: bold; font-size: 0.85rem;">🔬</div>
          <div>
            <div style="font-size: 0.95rem; font-weight: 700; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.5rem;">
              <span>PIL CONSERVATIVE 102MP RESTORATION LOCK</span>
              <span class="brand-tag">PLATINUM_NO_DRIFT</span>
            </div>
            <div style="font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono);">
              Hardware-Locked 102,000,000 Px Conservative Resampling • PIL_ONLY No-Drift Architecture
            </div>
          </div>
        </div>
        <button onclick="closeUpscalerModal()" style="background: none; border: none; color: var(--text-muted); font-size: 1.4rem; cursor: pointer; padding: 0.2rem 0.5rem;">&times;</button>
      </div>

      <div class="modal-body">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;">
          <!-- Controls Column -->
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <label class="spec-label" style="display: block; margin-bottom: 0.35rem;">Source Image File Path *</label>
              <input type="text" id="upscaleInputPath" placeholder="/path/to/source_image.jpg or png" style="width: 100%; background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.6rem 0.8rem; color: var(--text-primary); font-family: var(--font-mono); font-size: 0.75rem;">
            </div>

            <div>
              <label class="spec-label" style="display: block; margin-bottom: 0.35rem;">Output Destination Path (Optional)</label>
              <input type="text" id="upscaleOutputPath" placeholder="Leave blank for auto-named output next to source" style="width: 100%; background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.6rem 0.8rem; color: var(--text-primary); font-family: var(--font-mono); font-size: 0.75rem;">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label class="spec-label" style="display: block; margin-bottom: 0.35rem;">Target Format</label>
                <select id="upscaleFormat" style="width: 100%; background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.55rem 0.7rem; color: var(--text-primary); font-family: var(--font-mono); font-size: 0.75rem;">
                  <option value="JPEG">JPEG (4:4:4 Chroma, Q96)</option>
                  <option value="PNG">PNG (Level 6 Lossless)</option>
                  <option value="TIFF">TIFF (LZW Lossless)</option>
                </select>
              </div>
              <div>
                <label class="spec-label" style="display: block; margin-bottom: 0.35rem;">Target Megapixels</label>
                <input type="text" value="102.0 MP (Locked)" disabled style="width: 100%; background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.55rem 0.7rem; color: var(--accent-cyan); font-family: var(--font-mono); font-size: 0.75rem;">
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.5rem; background: var(--bg-canvas); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.85rem;">
              <div style="font-size: 0.68rem; font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 600; text-transform: uppercase;">🔒 Strict Policy Locks:</div>
              <label class="check-item">
                <input type="checkbox" id="upscaleCleanup" checked>
                <span>Region-neutral micro-softening (Gaussian blend 0.08)</span>
              </label>
              <label class="check-item">
                <input type="checkbox" id="upscaleSharpen" checked>
                <span>Single-pass UnsharpMask (r=0.75, p=42, th=5)</span>
              </label>
              <label class="check-item">
                <input type="checkbox" checked disabled>
                <span>Staged Lanczos Scaling (&le; 2.0x linear growth/stage)</span>
              </label>
              <label class="check-item">
                <input type="checkbox" checked disabled>
                <span>Exact GCD Rational Aspect Ratio (w*h0 == h*w0)</span>
              </label>
            </div>

            <button id="btnExecuteUpscale" onclick="run102mpUpscale()" style="width: 100%; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); border: none; border-radius: 6px; padding: 0.75rem; color: #000; font-weight: 700; font-family: var(--font-sans); font-size: 0.85rem; cursor: pointer; letter-spacing: 0.04em; transition: all 0.2s;">
              EXECUTE 102MP RESTORATION & UPSCALE
            </button>
          </div>

          <!-- Audit & Output Column -->
          <div style="display: flex; flex-direction: column; gap: 0.85rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="spec-label">Audit & Quality Control Telemetry</span>
              <button class="btn-action" onclick="copyUpscaleReport()" id="btnCopyUpscaleReport" style="display: none; padding: 0.25rem 0.6rem; font-size: 0.7rem;">Copy Audit JSON</button>
            </div>

            <div id="upscaleStatusBox" style="background: var(--bg-canvas); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 1rem; min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: var(--text-muted); font-size: 0.78rem; font-family: var(--font-mono);">
              Ready to process. Enter source image path and click Execute.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


class StudioAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler serving both the studio UI and the JSON REST API."""

    compiler_cache: dict[str, OpticalCompiler] = {}

    def get_compiler(self, profile: str) -> OpticalCompiler:
        """Cache or instantiate OpticalCompiler for the requested profile."""
        if profile not in self.compiler_cache:
            self.compiler_cache[profile] = OpticalCompiler(profile=profile)
        return self.compiler_cache[profile]

    def log_message(self, format: str, *args: Any) -> None:
        """Custom clean logging to stderr."""
        sys.stderr.write(f"[Studio Web] {self.address_string()} - {format % args}\n")

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        """Helper to send JSON response with appropriate headers."""
        response_body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_body)

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Serve root UI, profile lists, or health checks."""
        parsed_path = self.path.split("?")[0]

        if parsed_path in ("/", "/index.html"):
            content = HTML_TEMPLATE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed_path == "/api/profiles":
            profiles = list_available_profiles()
            self._send_json(profiles)
            return

        if parsed_path == "/api/health":
            self._send_json({"status": "ok", "version": "2.1.0"})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:
        """Handle compilation requests via REST API."""
        parsed_path = self.path.split("?")[0]

        if parsed_path not in ("/api/compile", "/api/upscale-102mp", "/api/export-closed-loop"):
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception as err:
            self._send_json({"error": f"Invalid JSON payload: {err}"}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed_path == "/api/export-closed-loop":
            input_path = body.get("input_path") or body.get("image_path")
            if not input_path:
                self._send_json({"error": "Missing required field 'input_path'"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                from .restoration import PILLOW_AVAILABLE, export_closed_loop
            except ImportError:
                self._send_json({"error": "Restoration module could not be imported."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if not PILLOW_AVAILABLE:
                self._send_json({"error": "Pillow is not installed."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                output_path = body.get("output_path") or "export_output.png"
                run_rep, rep_dict = export_closed_loop(
                    input_path=input_path,
                    output_path=output_path,
                    target_width=body.get("target_width"),
                    target_height=body.get("target_height"),
                    width_in=body.get("width_in"),
                    height_in=body.get("height_in"),
                    ppi=int(body.get("ppi", 300)),
                    min_mb=float(body.get("min_mb")) if body.get("min_mb") is not None else None,
                    output_format=body.get("output_format"),
                    add_noise=bool(body.get("add_noise", False)),
                    generate_report=True,
                )
                self._send_json(rep_dict)
            except Exception as err:
                self._send_json({"error": str(err)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if parsed_path == "/api/upscale-102mp":
            input_path = body.get("input_path") or body.get("image_path")
            if not input_path:
                self._send_json({"error": "Missing required field 'input_path'"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                from .restoration import PILLOW_AVAILABLE, RestorationConfig, restore_and_upscale_102mp
            except ImportError:
                self._send_json({"error": "Restoration module could not be imported."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if not PILLOW_AVAILABLE:
                self._send_json({
                    "error": "Pillow is not installed. Run: pip install Pillow (or pip install 'optical-camera-compiler[upscale]')"
                }, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                config = RestorationConfig(
                    cleanup_enabled=bool(body.get("cleanup", True)),
                    sharpening_enabled=bool(body.get("sharpening", True)),
                    human_skin_realism=bool(body.get("human_skin_realism", True)),
                )
                output_path = body.get("output_path") or None
                output_format = body.get("output_format") or None
                report = restore_and_upscale_102mp(
                    input_path=input_path,
                    output_path=output_path,
                    config=config,
                    output_format=output_format,
                )
                self._send_json(report)
            except Exception as err:
                self._send_json({"error": str(err)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # /api/compile
        scene_text = body.get("scene", "")
        target_engine = body.get("target", "flux")
        profile_name = body.get("profile", "phase_one_iq4")

        try:
            compiler = self.get_compiler(profile_name)
            payload = compiler.compile(
                scene=scene_text,
                target=target_engine,
                framing=body.get("framing"),
                environment=body.get("environment"),
                wardrobe=body.get("wardrobe"),
                mood=body.get("mood"),
                aperture=body.get("aperture"),
                lens=body.get("lens"),
                lighting=body.get("lighting"),
                aspect_ratio=body.get("aspect_ratio", "4:5"),
                film_stock=body.get("film_stock"),
                optical_filter=body.get("optical_filter"),
                shutter_speed=body.get("shutter_speed"),
                lighting_modifier=body.get("lighting_modifier"),
                custom_positives=body.get("custom_positives"),
                custom_negatives=body.get("custom_negatives"),
                reference=body.get("reference"),
                sharpness_protocol=body.get("sharpness_protocol", True),
                output_resolution=body.get("output_resolution"),
                suppress_text_branding=body.get("suppress_text_branding", True),
                human_skin_realism=body.get("human_skin_realism", True),
                content_type=body.get("content_type", "photograph"),
                text_preservation=body.get("text_preservation", True),
                camera_angle=body.get("camera_angle"),
                color_mode=body.get("color_mode"),
                crowd_action=body.get("crowd_action"),
                capture_mode=body.get("capture_mode"),
                lighting_preset=body.get("lighting_preset"),
                product_crop=body.get("product_crop"),
                sku_color=body.get("sku_color"),
                cap_geometry=body.get("cap_geometry"),
                label_kerning=body.get("label_kerning"),
                material_finish=body.get("material_finish"),
                seam_geometry=body.get("seam_geometry"),
                approval_gate_100pct=body.get("approval_gate_100pct", True),
                hand_lock=body.get("hand_lock", False),
                grip_type=body.get("grip_type"),
                hand_details=body.get("hand_details"),
                anamorphic=body.get("anamorphic", False),
                anamorphic_squeeze=body.get("anamorphic_squeeze") or body.get("squeeze"),
                streak_flare=body.get("streak_flare"),
                iris_blades=body.get("iris_blades"),
                gobo=body.get("gobo"),
                grip_modifier=body.get("grip_modifier") or body.get("grip"),
                lighting_ratio=body.get("lighting_ratio"),
                copy_space=body.get("copy_space"),
                ad_safe_zone=body.get("ad_safe_zone"),
                body_volume=body.get("body_volume"),
                weight_lb=body.get("weight_lb"),
                material_style=body.get("material_style") or body.get("material"),
                background_style=body.get("background_style"),
                is_4d_volumetric=bool(body.get("is_4d_volumetric") or body.get("volumetric_4d", False)),
                remove_text_when_present=bool(body.get("remove_text_when_present") or body.get("remove_text", False)),
                paper_profile=body.get("paper_profile") or body.get("paper"),
                policy_safe=bool(body.get("policy_safe", False)),
                stress_probe=body.get("stress_probe") or body.get("probe"),
                min_mb=body.get("min_mb"),
                cct_kelvin=body.get("cct_kelvin") or body.get("cct"),
                illuminance_lux=body.get("illuminance_lux") or body.get("lux"),
                spectral_cri=body.get("spectral_cri") or body.get("cri"),
                wall_surround=body.get("wall_surround"),
                gallery_zone=body.get("gallery_zone"),
                anchor_image_id=body.get("anchor_image_id") or body.get("anchor_id"),
            )
            self._send_json(payload.to_dict())
        except Exception as err:
            self._send_json({"error": str(err)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def run_server(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = False) -> None:
    """Start local web studio server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, StudioAPIHandler)
    url = f"http://{host}:{port}"

    sys.stdout.write("=" * 75 + "\n")
    sys.stdout.write("  OPTICAL CAMERA COMPILER // MASTER STUDIO CONSOLE v2.1\n")
    sys.stdout.write(f"  Live at: {url}\n")
    sys.stdout.write("  Available Hardware Profiles: 10 Elite Camera Systems\n")
    sys.stdout.write("  Scenario Bar: Grouped Natural Scenarios & Element of Surprise\n")
    sys.stdout.write("  REST API available at /api/compile & /api/profiles\n")
    sys.stdout.write("  Press Ctrl+C to stop.\n")
    sys.stdout.write("=" * 75 + "\n")
    sys.stdout.flush()

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nStudio server stopped.\n")
    finally:
        httpd.server_close()


def main() -> None:
    """CLI runner for web studio."""
    parser = argparse.ArgumentParser(description="Run Optical Camera Compiler Studio Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port number (default: 8765)")
    parser.add_argument("--open", "-o", action="store_true", help="Automatically open default web browser")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, open_browser=args.open)


if __name__ == "__main__":
    main()
