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
          <option value="fashion_studio">Haute Couture Studio Editorial // Giant Broncolor Para 220 Strobe (Hasselblad H6D)</option>
          <option value="sculptor_atelier">Carrara Marble Sculptor Atelier // Limestone Dust & Directional Sun (Fujifilm GFX)</option>
          <option value="watchmaker_bench">Horologist Micro-Bench // Macro Brass Gears & Focus (Sony A7R V)</option>
          <option value="museum_gallery">Neoclassical Museum Rotunda // Soaring Marble Fluted Columns (Linhof 4x5)</option>
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
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.4rem;">
              <button type="button" class="mode-card active" id="btnModeRestore" onclick="setRefMode('restore')">
                <div style="font-size: 0.73rem; font-weight: 700; color: #fff;">🔬 Remaster</div>
                <div style="font-size: 0.63rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.3;">
                  1:1 Identity lock & 150MP upscale
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeTransform" onclick="setRefMode('transform')">
                <div style="font-size: 0.73rem; font-weight: 700; color: #fff;">🎨 Re-Shoot</div>
                <div style="font-size: 0.63rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.3;">
                  Adapt scene while locking bones & gaze
                </div>
              </button>
              <button type="button" class="mode-card" id="btnModeOutpaint" onclick="setRefMode('outpaint')">
                <div style="font-size: 0.73rem; font-weight: 700; color: #fff;">📐 Outpaint</div>
                <div style="font-size: 0.63rem; color: var(--text-muted); margin-top: 0.15rem; line-height: 1.3;">
                  Extend down head-to-toe with shoes
                </div>
              </button>
            </div>
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

          <!-- Preserved Element Checkboxes -->
          <div class="field-group">
            <label>Biometric & Structural Anchors</label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; margin-top: 0.2rem;">
              <label class="check-item"><input type="checkbox" id="chkFacial" checked onchange="debounceCompile()"> Facial Geometry & Bones</label>
              <label class="check-item"><input type="checkbox" id="chkGaze" checked onchange="debounceCompile()"> Eye Shape & Gaze</label>
              <label class="check-item"><input type="checkbox" id="chkProportions" checked onchange="debounceCompile()"> Anatomical Proportions</label>
              <label class="check-item"><input type="checkbox" id="chkLighting" onchange="debounceCompile()"> Lighting Falloff Mood</label>
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

      <!-- 05. BRUTAL SHARPNESS & QUALITY ENFORCEMENT -->
      <div class="panel-section">
        <div class="section-header">
          <div class="section-title">05. Brutal Sharpness & Quality Shields</div>
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

      const slider = document.getElementById('fidelitySlider');
      if (mode === 'restore' && parseInt(slider.value, 10) < 90) {
        slider.value = 95;
      } else if (mode === 'outpaint') {
        slider.value = 95;
      } else if (mode === 'transform' && parseInt(slider.value, 10) > 90) {
        slider.value = 85;
      }
      onFidelitySliderChange();
      updateRefBadge();
      debounceCompile();
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
        badge.textContent = "NO IMAGE ATTACHED";
        badge.style.color = "var(--text-muted)";
      } else if (activeRefMode === 'restore') {
        badge.textContent = "ACTIVE // 1:1 RESTORE & REMASTER";
        badge.style.color = "var(--accent-cyan)";
      } else if (activeRefMode === 'outpaint') {
        badge.textContent = "ACTIVE // FULL-BODY OUTPAINT";
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
        const denoiseVal = activeRefMode === 'restore' ? 0.35 : (activeRefMode === 'outpaint' ? 0.40 : 0.65);

        let refModeStr = "restore_upscale";
        if (activeRefMode === 'transform') refModeStr = "transform_adapt";
        if (activeRefMode === 'outpaint') refModeStr = "outpaint_full_body";

        refPayload = {
          filename: refData.filename,
          mode: refModeStr,
          fidelity_lock: fidelityVal,
          denoise_strength: denoiseVal,
          detected_aspect_ratio: refData.aspect_ratio,
          preserved_elements: preserved,
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
        sharpness_protocol: document.getElementById('chkSharpness') ? document.getElementById('chkSharpness').checked : true,
        suppress_text_branding: document.getElementById('chkAntiBrand') ? document.getElementById('chkAntiBrand').checked : true,
        output_resolution: selectedResText,
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

    window.onload = init;
  </script>
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

        if parsed_path != "/api/compile":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception as err:
            self._send_json({"error": f"Invalid JSON payload: {err}"}, status=HTTPStatus.BAD_REQUEST)
            return

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
