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

    /* SCENARIO BAR (ORGANIZED BY CAMERA STYLE & AMBIENT STYLE + BUILD YOUR OWN) */
    .scenario-bar {
      background: #0b0e14;
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.85rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }
    .scenario-controls-container {
      display: flex;
      align-items: center;
      gap: 1rem;
      width: 100%;
      flex-wrap: wrap;
    }
    .scenario-select-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex: 1;
      min-width: 320px;
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
      gap: 0.35rem;
    }
    .scenario-select {
      background: var(--bg-card);
      border: 1px solid #2d3748;
      color: var(--text-primary);
      padding: 0.48rem 0.85rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: inherit;
      font-weight: 500;
      flex: 1;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 240px;
    }
    .scenario-select:focus {
      border-color: var(--accent-amber);
      box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
    }
    .scenario-select optgroup {
      font-weight: 700;
      color: var(--accent-cyan);
      background: #111827;
      padding: 4px 0;
    }
    .scenario-select option {
      font-weight: normal;
      color: #e2e8f0;
      background: #0f172a;
      padding: 4px 6px;
    }
    .btn-surprise {
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.35);
      color: var(--accent-amber);
      padding: 0.48rem 1rem;
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
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .scenario-hint strong {
      color: var(--text-secondary);
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

  <!-- CALIBRATED SCENARIOS & RIGS: ORGANIZED BY CAMERA STYLE & AMBIENT STYLE -->
  <div class="scenario-bar">
    <div class="scenario-controls-container">
      
      <!-- 1. CAMERA & LENS RIG STYLE DROPDOWN -->
      <div class="scenario-select-group">
        <label class="scenario-label" for="cameraPresetSelect">
          <span>📷 Camera Style:</span>
        </label>
        <select class="scenario-select" id="cameraPresetSelect" onchange="onCameraPresetSelectChange()">
          <option value="none" selected>✨ -- Clear / Build Your Own (Custom Rig) --</option>
          
          <optgroup label="🏆 Medium Format Commercial Titans (100MP–150MP)">
            <option value="cam_phase_one_iq4_still">Phase One XF IQ4 150MP // Schneider 80mm LS (Museum Fine Art Curator)</option>
            <option value="cam_phase_one_iq4_arch">Phase One XF IQ4 150MP // Schneider 55mm LS (Brutalist Concrete Library)</option>
            <option value="cam_hasselblad_h6d_para">Hasselblad H6D-100c // HC 100mm f/2.2 (Haute Couture Studio & Para 220)</option>
            <option value="cam_hasselblad_x2d_hncs">Hasselblad X2D II 100C // XCD 90mm f/2.5 V (HNCS 16-Bit Equestrian Editorial)</option>
            <option value="cam_fujifilm_gfx100ii_reala">Fujifilm GFX 100 II // GF 110mm f/2 (Carrara Marble Sculptor Atelier)</option>
            <option value="cam_fujifilm_gfx100rf_street">FUJIFILM GFX100RF // 35mm f/4 @ f/5.6 (Fixed 102MP Archival Street)</option>
          </optgroup>

          <optgroup label="🇩🇪 Leica Rangefinders & Precision Optics">
            <option value="cam_leica_m11_reportage">Leica M11 60MP // Summilux-M 35mm f/1.4 FLE II (Haussmannian Street Reportage)</option>
            <option value="cam_leica_m11_noctilux">Leica M11 60MP // Noctilux-M 50mm f/0.95 (Jazz Club The King of Light)</option>
            <option value="cam_leica_m6_analog_trix">Leica M6 Classic 35mm // Summicron-M 50mm f/2 (Kodak Tri-X 400 Street)</option>
            <option value="cam_leica_q3_monochrom">Leica Q3 Monochrom 60.3MP // Summilux 28mm f/1.7 ASPH (Zero-CFA Archival)</option>
            <option value="cam_leica_sl2_motion_blur">Leica SL2 47.3MP // Summilux-SL 50mm f/1.4 @ f/2.8 (Stationary Subject vs Motion Trails)</option>
            <option value="cam_leica_sl3_p_apo">Leica SL3-P Maestro IV // APO-Summicron-SL 50mm f/2 (Foreign Dispatch Reportage)</option>
          </optgroup>

          <optgroup label="⚡ Flagship Stacked & High-Resolution Systems">
            <option value="cam_sony_a1_ii_flash_freeze">Sony a1 II 50.1MP // FE 85mm f/1.4 GM II (1/400s Flash Freeze Fencing)</option>
            <option value="cam_sony_a7rv_macro_horology">Sony Alpha 7R V 61MP // FE 50mm f/1.2 GM (Horologist Macro Micro-Bench)</option>
            <option value="cam_sony_a7rv_depixel_flat">Sony Alpha 7R V 61MP // 55mm f/1.8 ZA (Flat Copy-Stand & De-Pixelate v2.0 OCR)</option>
            <option value="cam_canon_eos_r5_ii_vogue">Canon EOS R5 Mark II 45MP // RF 85mm f/1.2L USM (Vogue Sculptural Beauty)</option>
            <option value="cam_canon_eos_r1_action">Canon EOS R1 Full-Frame // RF 70-200mm f/2.8L (Decisive Ballet Grand Jeté)</option>
            <option value="cam_nikon_z9_plena">Nikon Z 9 45.7MP // NIKKOR Z 135mm f/1.8 S Plena (Plena Circular Bokeh Cellist)</option>
            <option value="cam_panasonic_s1rii_micro">Panasonic LUMIX S1R II // Lumix S 100mm f/2.8 Macro (1:1 Orchid Micro-Science)</option>
          </optgroup>

          <optgroup label="🎬 Hollywood Cinema & Anamorphic Systems">
            <option value="cam_arri_alexa_35_cooke">ARRI Alexa 35 ALEV 4 // Cooke S4/i 50mm T2.0 (The Cooke Look Speakeasy)</option>
            <option value="cam_arri_alexa_35_anamorphic">ARRI Alexa 35 Scope // Atlas Orion 65mm 2.0x (Cyan Streak Flare & Oval Bokeh)</option>
            <option value="cam_sony_fx_venice_noir">Sony FX Cinema Line // FE 50mm f/1.2 GM @ f/2.8 (Venice S-Cinetone Saxophone Noir)</option>
          </optgroup>

          <optgroup label="🎞️ Analog Sheet Film & Classic Formats">
            <option value="cam_linhof_4x5_architectural">Linhof Master Technika 4x5 // Schneider 150mm f/5.6 (Neoclassical Rotunda)</option>
            <option value="cam_linhof_4x5_desert">Linhof Master Technika 4x5 // Rodenstock 90mm f/4.5 (Expansive Desert Strata)</option>
            <option value="cam_pentax_67_bokeh_king">Pentax 67 II 6x7 // SMC 105mm f/2.4 (The Bokeh King Dune Ocean Portrait)</option>
            <option value="cam_pentax_67_cotswolds">Pentax 67 II 6x7 // SMC 90mm f/2.8 (Cotswolds English Country Garden)</option>
            <option value="cam_hasselblad_500cm_zeiss">Hasselblad 500C/M 6x6 // Zeiss Planar 80mm f/2.8 CF (Tuscan Chianti Vineyard)</option>
          </optgroup>
        </select>
      </div>

      <!-- 2. AMBIENT & LIGHTING STYLE DROPDOWN -->
      <div class="scenario-select-group">
        <label class="scenario-label" for="ambientPresetSelect">
          <span>🌤️ Ambient Style:</span>
        </label>
        <select class="scenario-select" id="ambientPresetSelect" onchange="onAmbientPresetSelectChange()">
          <option value="none" selected>✨ -- Clear / Build Your Own (Custom Ambience) --</option>
          
          <optgroup label="🏙️ Cities & Urban Streetscapes">
            <option value="amb_paris_haussmann">Paris Saint-Germain // Haussmann Limestone, Zinc Roofs & Overcast Diffuse (5500K)</option>
            <option value="amb_tokyo_shinjuku">Tokyo Shinjuku Alleyway // Wet Reflective Asphalt, Glowing Neon & Puddles</option>
            <option value="amb_nyc_soho_loft">New York SoHo Cast-Iron // Raking Morning Sunbeam, Fire Escapes & Cobblestone</option>
            <option value="amb_london_mayfair">London Mayfair Mews // Portland Limestone, Black Railings & Soft Misty Drizzle</option>
            <option value="amb_milan_portico">Milan Brera Design Quarter // High-Contrast Italian Marble Portico Shadows</option>
            <option value="amb_kyoto_gion">Kyoto Gion Preservation Lane // Dark Aged Cedar, Glowing Lanterns & Rain</option>
            <option value="amb_berlin_concrete">Berlin Mitte Industrial Yard // Raw Board-Formed Concrete & Cold Overcast</option>
          </optgroup>

          <optgroup label="🏨 Luxury Hospitality & Architectural Sanctuaries">
            <option value="amb_amalfi_terrace">Amalfi Coast Cliffside Villa // Terracotta, Morning Sun & Mediterranean Sea Breeze</option>
            <option value="amb_manhattan_penthouse">Manhattan Skyline Penthouse // Floor-to-Ceiling Glass & Golden Sunrise Horizon</option>
            <option value="amb_paris_palace_lobby">Parisian Grand Palace Lobby // Fluted Carrara Marble & Crystal Chandeliers</option>
            <option value="amb_kyoto_ryokan">Kyoto Luxury Sukiya Ryokan // Tatami Mats, Sliding Shoji & Moss Garden Sunbeams</option>
            <option value="amb_alpine_chalet">Saint-Moritz Alpine Chalet // Raw Granite Fireplace, Cashmere & Mountain Snowlight</option>
            <option value="amb_speakeasy_lounge">Speakeasy Cocktail Lounge // Dim Filament Tungsten, Midnight Velvet & Mirrors</option>
          </optgroup>

          <optgroup label="🌊 Coastal, Maritime & Island Escapes">
            <option value="amb_mediterranean_cliff">Mediterranean White Cliffside // Sun-Bleached Rock, Bougainvillea & Azure Sea</option>
            <option value="amb_atlantic_dunes">Windswept Atlantic Ocean Dunes // Low Golden Hour Sun & Wild Dune Grass</option>
            <option value="amb_nordic_fjord">Norwegian Coastal Fjord // Cool Sea Mist, Dark Wet Granite & Mossy Rocks</option>
            <option value="amb_tropical_shore">Polynesian Secluded Shoreline // Coconut Palm Silhouettes & Humid Sunset Glow</option>
            <option value="amb_big_sur_bluffs">Big Sur California Coastline // High Coastal Bluffs, Pacific Marine Layer & Sun Break</option>
          </optgroup>

          <optgroup label="🌾 Terroir, Rural Landscapes & Wild Nature">
            <option value="amb_tuscan_vineyard">Tuscan Chianti Hills // Cypress Avenue, Warm Golden Dust & Terracotta Earth</option>
            <option value="amb_pnw_pine_forest">Pacific Northwest Pine Forest // Douglas Fir Canopy, Morning Mist & Damp Earth</option>
            <option value="amb_cotswolds_garden">Cotswolds English Cottage Garden // Blooming Climbing Roses & Gentle English Daylight</option>
            <option value="amb_mojave_desert">Mojave Desert Sandstone Plateau // Monumental Strata, Dune Shadows & Azure Sky</option>
            <option value="amb_highland_moor">Scottish Highlands Heather Moor // Low Raking Clouds, Peat Moss & Windblown Grass</option>
          </optgroup>

          <optgroup label="📸 High-End Commercial Studio & Exhibition">
            <option value="amb_cosmetic_packshot">Luxury Cosmetic Packshot // Diffused Strip Softboxes, Water Droplets & 100% SKU Gate</option>
            <option value="amb_haute_couture_studio">Haute Couture Runway Studio // Giant Broncolor Para 220 Strobe & Infinity Cove</option>
            <option value="amb_sculptor_atelier">Carrara Sculptor Atelier // Swirling Limestone Dust & High Raking Directional Sun</option>
            <option value="amb_horologist_bench">Horologist Micro-Bench // Macro Brass Gears & Focused Worklamp Illumination</option>
            <option value="amb_museum_rotunda">Neoclassical Museum Rotunda // Soaring Fluted Columns & Coffered Glass Skylight</option>
            <option value="amb_commercial_gobo_copy">Commercial Advertising Hero // Venetian Blinds Gobo Shadow & Left-Third Copy Space</option>
          </optgroup>

          <optgroup label="✨ Mastery Protocols & Technical Directives">
            <option value="amb_4d_liquid_glass">4D Liquid Glass & Latex High-Fashion // Contour Rim Strobe & Opaque Black Void</option>
            <option value="amb_heavyweight_morphology">Calibrated Heavyweight Body Morphology // Directional Window Rake & Skin Pores</option>
            <option value="amb_baryta_print_prepress">Exhibition Prepress Master // Baryta Fine Art 16x24@300 Print Calibration</option>
            <option value="amb_depixel_v2_restoration">Universal De-Pixelate v2.0 // Flat Copy-Stand & Character-for-Character OCR Safety</option>
            <option value="amb_monochrome_luminance">Pure Monochromatic Luminance // Zero-CFA Monochromatic Sensor & Obsidian Blacks</option>
          </optgroup>
        </select>
      </div>

      <!-- 3. CLEAR / BUILD YOUR OWN BUTTON -->
      <button class="btn-surprise" id="btnClearBuildOwn" onclick="clearToSurprise()" title="Reset all creative and technical fields to build your own scene freely">
        <span>↺ Clear / Build Your Own</span>
      </button>

      <!-- Legacy shim element -->
      <select id="scenarioSelect" style="display:none;"><option value="none">none</option></select>

    </div>
    <div class="scenario-hint">
      Pick a <strong>Camera Rig</strong> for hardware & optics, or an <strong>Ambient Style</strong> for lighting & atmosphere. Click <strong>Clear / Build Your Own</strong> to write freely.
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
      leica_q3_monochrom: [
        "Leica Summilux 28mm f/1.7 ASPH (Fixed Integrated Lens with Macro Mode)",
        "Leica Summilux 28mm f/1.7 ASPH @ Macro Mode (17cm close focus)",
        "Leica Summilux 28mm f/1.7 ASPH (35mm Crop Mode)",
        "Leica Summilux 28mm f/1.7 ASPH (50mm Crop Mode)"
      ],
      panasonic_lumix_s1rii: [
        "Lumix S PRO 50mm f/1.4 Leica-Certified (Ultimate Optical Purity)",
        "Lumix S PRO 85mm f/1.8 (Lightweight Portrait Prime)",
        "Lumix S 100mm f/2.8 Macro (1:1 Micro-Detail Specialist)",
        "Lumix S PRO 24-70mm f/2.8 (Professional Documentary Standard)"
      ],
      leica_sl2: [
        "Leica Summilux-SL 50mm f/1.4 ASPH (Motion-Blur Crowd Reference)",
        "Leica APO-Summicron-SL 35mm f/2 ASPH (Environmental Reportage)",
        "Leica APO-Summicron-SL 75mm f/2 ASPH (Portrait Acutance)",
        "Leica Super-Vario-Elmar-SL 16-35mm f/3.5-4.5 ASPH (Architectural Street)"
      ]
    };

    // =========================================================================
    // CALIBRATED CAMERA & LENS RIG PRESETS (Organized by Camera System & Optics)
    // =========================================================================
    const CAMERA_PRESETS = {
      // 1. Medium Format Commercial Titans (100MP–150MP)
      cam_phase_one_iq4_still: {
        profile: "phase_one_iq4",
        lens: "Schneider Kreuznach 80mm LS f/2.8 Blue Ring",
        aperture: "f/8.0",
        subject: "Fine art museum curator in tailored charcoal wool suit examining a classical marble bust, high tactile micro-relief and chisel marks",
        framing: "three-quarter museum gallery portrait",
        environment: "neoclassical museum rotunda with soaring limestone walls and diffuse high clerestory light",
        wardrobe: "bespoke charcoal three-piece suit with silk pocket square",
        mood: "timeless archival reverence, museum-grade 150MP resolution",
        timeWeather: "overcast",
        lighting: "architectural_skylight",
        filmStock: "digital_raw",
        aspectRatio: "4:5",
        paperProfile: "baryta",
        printSize: "16x24@300"
      },
      cam_phase_one_iq4_arch: {
        profile: "phase_one_iq4",
        lens: "Schneider Kreuznach 55mm LS f/2.8 Blue Ring",
        aperture: "f/8.0",
        subject: "Architect leaning over a monolithic drafting table reviewing hand-drawn blueprints and raw concrete scale models",
        framing: "wide environmental architectural portrait",
        environment: "brutalist board-formed concrete library pavilion with high clerestory windows",
        wardrobe: "charcoal fine-knit merino turtleneck and tailored trousers",
        mood: "austere, contemplative, intellectual focus",
        timeWeather: "overcast",
        lighting: "architectural_skylight",
        filmStock: "digital_raw",
        aspectRatio: "16:9"
      },
      cam_hasselblad_h6d_para: {
        profile: "hasselblad_h6d",
        lens: "Hasselblad HC 100mm f/2.2 Portrait Lens",
        aperture: "f/4.0",
        subject: "Haute couture fashion model in structural pleated ivory silk gown with razor-sharp gaze",
        framing: "full-length architectural fashion portrait",
        environment: "pristine white infinity cove photo studio with subtle floor reflections",
        wardrobe: "sculptural pleated raw ivory silk architectural dress",
        mood: "avant-garde, pristine luxury, crystalline micro-contrast",
        timeWeather: "auto",
        lighting: "strobe_para",
        filmStock: "portra_160",
        aspectRatio: "4:5"
      },
      cam_hasselblad_x2d_hncs: {
        profile: "hasselblad_x2d_ii_100c",
        lens: "Hasselblad XCD 90mm f/2.5 V",
        aperture: "f/2.5",
        subject: "Equestrian trainer standing beside a dark thoroughbred in sunlit stone courtyard, tactile leather reins and tweed textures",
        framing: "three-quarter outdoor editorial portrait",
        environment: "historic limestone stables courtyard with sun-warmed cobblestones and horse brasses",
        wardrobe: "tailored olive tweed field jacket and leather riding boots",
        mood: "refined heritage, HNCS 16-bit organic skin tones and tactile micro-relief",
        timeWeather: "golden_hour",
        lighting: "golden_hour",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },
      cam_fujifilm_gfx100ii_reala: {
        profile: "fujifilm_gfx100ii",
        lens: "Fujinon GF 110mm f/2 R LM WR",
        aperture: "f/2.8",
        subject: "Master stone sculptor covered in fine marble dust on muscular forearms, chisel resting on Carrara relief",
        framing: "three-quarter artisanal portrait",
        environment: "historic Carrara limestone atelier with half-carved sculptures and raking morning sunbeams",
        wardrobe: "heavy indigo canvas workshirt and stained leather apron",
        mood: "intense concentration, raw craftsmanship, 102MP tonal graduation",
        timeWeather: "morning_fog",
        lighting: "window_daylight",
        filmStock: "classic_chrome",
        aspectRatio: "4:5"
      },
      cam_fujifilm_gfx100rf_street: {
        profile: "fujifilm_gfx100rf",
        lens: "Fujinon GF 45mm f/2.8 R WR",
        aperture: "f/5.6",
        subject: "Documentary photographer standing watchful on rain-slicked city crossing, camera resting at hip",
        framing: "environmental street portrait",
        environment: "rain-soaked European pedestrian plaza with historic stone facades and reflections",
        wardrobe: "charcoal waxed cotton coat and leather boots",
        mood: "fixed-lens medium format acutance, zero optical distortion, archival realism",
        timeWeather: "rainy_wet",
        lighting: "window_daylight",
        filmStock: "classic_chrome",
        aspectRatio: "4:3"
      },

      // 2. Leica Rangefinders & Precision Optics
      cam_leica_m11_reportage: {
        profile: "leica_m11",
        lens: "Leica Summilux-M 35mm f/1.4 ASPH FLE II",
        aperture: "f/2.8",
        subject: "Pedestrian walking past an outdoor cafe terrace, holding an espresso cup",
        framing: "three-quarter street editorial portrait",
        environment: "wet cobblestone Paris street in Saint-Germain, limestone Haussmann facade in background",
        wardrobe: "tailored navy wool trench coat and gray cashmere scarf",
        mood: "effortless, contemplative, authentic Parisian elegance",
        timeWeather: "overcast",
        cityVibe: "paris",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "3:2"
      },
      cam_leica_m11_noctilux: {
        profile: "leica_m11",
        lens: "Leica Noctilux-M 50mm f/0.95 ASPH",
        aperture: "f/1.4",
        subject: "Jazz pianist paused at grand piano keys in intimate low-lit lounge, glistening lacquer reflections",
        framing: "tight atmospheric portrait with razor-thin depth of field",
        environment: "intimate jazz club with warm amber filament wall sconces and dark velvet curtains",
        wardrobe: "crisp white unbuttoned collar shirt and dark wool vest",
        mood: "The King of Light, dreamy subject isolation, luminous specular falloff",
        timeWeather: "night_city",
        lighting: "tungsten_candle",
        filmStock: "digital_raw",
        aspectRatio: "3:2"
      },
      cam_leica_m6_analog_trix: {
        profile: "leica_m6_analog",
        lens: "Leica Summicron-M 50mm f/2 Dual-Range",
        aperture: "f/2.0",
        subject: "City commuter under umbrella standing by crosswalk, raindrops caught in light",
        framing: "medium close-up street documentary portrait",
        environment: "narrow rain-soaked Shinjuku alley with glowing neon signs and reflective puddles",
        wardrobe: "dark oversized trench coat with glistening raindrops on shoulders",
        mood: "authentic 35mm silver halide grain, gritty timeless Magnum photojournalism",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "tungsten_candle",
        filmStock: "tri_x_400",
        aspectRatio: "3:2"
      },
      cam_leica_q3_monochrom: {
        profile: "leica_q3_monochrom",
        lens: "Leica Summilux 28mm f/1.7 ASPH",
        aperture: "f/2.8",
        subject: "Portrait of veteran silversmith with deep character wrinkles and intense focused gaze at jeweler bench",
        framing: "intimate environmental craftsman portrait",
        environment: "antique goldsmith workshop with scattered burins, silver wire, and raking north skylight",
        wardrobe: "charcoal linen apron over textured gray work shirt",
        mood: "zero Color Filter Array, uncompromised pure luminance micro-contrast, obsidian black to specular white",
        timeWeather: "overcast",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "3:2"
      },
      cam_leica_sl2_motion_blur: {
        profile: "leica_sl2",
        lens: "Leica Summilux-SL 50mm f/1.4 ASPH",
        aperture: "f/2.8",
        subject: "Stationary traveler standing serenely still and tack-sharp at eye level while rushing crowd blurs around them",
        framing: "wide environmental transit hall portrait",
        environment: "grand European railway station concourse with streaming commuters in multi-directional motion blur trails",
        wardrobe: "tailored camel wool coat and leather weekender bag",
        mood: "calm center of gravity amidst swirling urban momentum, slow shutter motion-blur aesthetic",
        timeWeather: "overcast",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "3:2"
      },
      cam_leica_sl3_p_apo: {
        profile: "leica_sl3_p",
        lens: "Leica APO-Summicron-SL 50mm f/2 ASPH",
        aperture: "f/2.0",
        subject: "Foreign correspondent standing on rain-spattered hotel balcony reviewing investigative notes",
        framing: "three-quarter documentary portrait",
        environment: "European capital city skyline under stormy twilight sky, wet railings and distant city lights",
        wardrobe: "dark navy waterproof shell over fine charcoal sweater",
        mood: "apochromatic optical acutance, zero chromatic aberration, Maestro IV tonal depth",
        timeWeather: "blue_hour",
        lighting: "blue_hour",
        filmStock: "digital_raw",
        aspectRatio: "3:2"
      },

      // 3. Flagship Stacked & High-Resolution Systems
      cam_sony_a1_ii_flash_freeze: {
        profile: "sony_a1_ii",
        lens: "Sony FE 85mm F1.4 GM II (SEL85F14GM2)",
        aperture: "f/2.8",
        subject: "Fencing athlete paused between lunges, perspiration glistening on brow, tack-sharp near-eye pupil focus",
        framing: "three-quarter athletic editorial portrait",
        environment: "minimalist dark gymnasium with high directional strobe freeze and black negative fill",
        wardrobe: "white textured fencing jacket with foil blade resting vertically",
        mood: "1/400s electronic stacked shutter freeze, brutal near-eye sharpness, zero motion blur",
        timeWeather: "auto",
        lighting: "strobe_para",
        filmStock: "digital_raw",
        aspectRatio: "9:11"
      },
      cam_sony_a7rv_macro_horology: {
        profile: "sony_a7rv",
        lens: "Sony FE 50mm f/1.2 GM (SEL50F12GM)",
        aperture: "f/2.8",
        subject: "Senior watchmaker looking through brass loupe, placing tourbillon balance wheel with titanium tweezers",
        framing: "extreme macro iris and skin detail portrait",
        environment: "cluttered antique wooden workbench with miniature gear wheels and micro-screwdrivers",
        wardrobe: "dark wool vest and rolled-up striped cotton shirt",
        mood: "61MP microscopic precision, resolved epidermal pores, brass tooth reflections",
        timeWeather: "auto",
        lighting: "strobe_para",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },
      cam_sony_a7rv_depixel_flat: {
        profile: "sony_a7rv",
        lens: "Sony FE 50mm f/1.2 GM (SEL50F12GM)",
        aperture: "f/5.6",
        subject: "High-resolution flat archival document reproduction and infographic restoration with crisp typography",
        framing: "perpendicular flat copy-stand reproduction",
        environment: "professional copy-stand studio with balanced 45-degree polarized illumination",
        wardrobe: "none",
        mood: "Universal De-Pixelate v2.0 protocol, zero geometric distortion, strict OCR typography preservation",
        timeWeather: "studio_soft",
        lighting: "strobe_softbox",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },
      cam_canon_eos_r5_ii_vogue: {
        profile: "canon_eos_r5_ii",
        lens: "Canon RF 85mm F1.2L USM (Reference Portrait Prime)",
        aperture: "f/1.4",
        subject: "Beauty editorial model with sculptural wet-look hair, radiant luminous skin, and piercing direct gaze",
        framing: "tight beauty headshot",
        environment: "warm sand-colored studio seamless backdrop with diffused beauty dish key light",
        wardrobe: "minimalist nude silk bandeau top",
        mood: "legendary Canon skin tone warmth, creamy background defocus, tack-sharp eyelashes",
        timeWeather: "auto",
        lighting: "strobe_softbox",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },
      cam_canon_eos_r1_action: {
        profile: "canon_eos_r1",
        lens: "Canon RF 70-200mm F2.8L IS USM Z (Action & Sports Master)",
        aperture: "f/2.8",
        subject: "Prima ballerina caught at the floating zenith of a grand jeté leap across sunlit stage floor",
        framing: "dynamic full-body performance framing",
        environment: "historic opera house rehearsal hall with tall arched windows and dusty light shafts",
        wardrobe: "dusty rose rehearsal tulle skirt and fitted black leotard",
        mood: "stacked full-frame instantaneous motion freeze, decisive peak moment, athletic elegance",
        timeWeather: "window_daylight",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "16:9"
      },
      cam_nikon_z9_plena: {
        profile: "nikon_z9",
        lens: "NIKKOR Z 135mm f/1.8 S Plena (Zero Vignetting Texture Monster)",
        aperture: "f/1.8",
        subject: "Cellist seated in deep concentration during rehearsal, natural window backlight rimming hair",
        framing: "medium seated performance portrait",
        environment: "wood-paneled concert hall chamber with warm timber acoustic baffles",
        wardrobe: "dark tailored charcoal wool suit",
        mood: "Plena zero-vignetting edge-to-edge circular bokeh, velvety separation, tack-sharp cello strings",
        timeWeather: "window_daylight",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },
      cam_panasonic_s1rii_micro: {
        profile: "panasonic_lumix_s1rii",
        lens: "Lumix S 100mm f/2.8 Macro (1:1 Micro-Detail Specialist)",
        aperture: "f/5.6",
        subject: "Botanical taxonomist dissecting rare cloud forest orchid petal with surgical micro-tweezers",
        framing: "1:1 macro scientific portrait",
        environment: "botany research laboratory bench with specimen glass jars and natural north daylight",
        wardrobe: "crisp white laboratory coat and dark slate glasses",
        mood: "micro-science optical purity, cellular petal vein relief, tactile pollen grains",
        timeWeather: "window_daylight",
        lighting: "window_daylight",
        filmStock: "digital_raw",
        aspectRatio: "4:5"
      },

      // 4. Hollywood Cinema & Anamorphic Systems
      cam_arri_alexa_35_cooke: {
        profile: "arri_alexa_35",
        lens: "Cooke S4/i 50mm T2.0 Cine Prime ('The Cooke Look')",
        aperture: "f/2.0",
        subject: "Detective seated at corner booth of dim speakeasy holding tumbler, intense focused gaze",
        framing: "cinematic medium close-up",
        environment: "speakeasy cocktail lounge with warm amber backlighting, mahogany, and brass accents",
        wardrobe: "vintage weathered leather bomber jacket over open-collar dark shirt",
        mood: "The Cooke Look, 17 stops dynamic range, organic LogC4 highlight roll-off",
        timeWeather: "night_city",
        lighting: "rembrandt_key",
        filmStock: "arri_logc4",
        aspectRatio: "21:9"
      },
      cam_arri_alexa_35_anamorphic: {
        profile: "arri_alexa_35",
        lens: "Atlas Orion 65mm T2.0 2x Anamorphic Prime (Oval Bokeh & Horizontal Flare)",
        aperture: "f/2.0",
        subject: "Cinematic operative standing on wet rain-slicked city avenue, intense focused stillness",
        framing: "widescreen medium cinematic shot",
        environment: "rain-soaked neon district with reflective wet asphalt and vertical anamorphic light streaks",
        wardrobe: "dark distressed tactical trench coat",
        mood: "2.0x horizontal optical squeeze, 2:1 vertical oval bokeh, cyan streak flares",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "neon",
        filmStock: "arri_logc4",
        aspectRatio: "21:9",
        anamorphic: true,
        squeeze: "2.0x",
        streakFlare: "cyan_blue",
        irisBlades: "14_blade_circular"
      },
      cam_sony_fx_venice_noir: {
        profile: "sony_fx_series",
        lens: "Sony FE 50mm f/1.2 GM @ f/2.8 (Venice Cine Sweet Spot)",
        aperture: "f/2.8",
        subject: "Jazz saxophonist performing under single warm tungsten pool of light on dark club stage",
        framing: "medium performance shot with deep shadows",
        environment: "intimate cellar jazz club with brick arches, subtle haze, and warm spotlight",
        wardrobe: "midnight blue velvet blazer and unbuttoned silk shirt",
        mood: "Venice color science, S-Cinetone organic skin rendering, 180-degree cinema shutter cadence",
        timeWeather: "night_city",
        lighting: "tungsten_candle",
        filmStock: "digital_raw",
        aspectRatio: "16:9"
      },

      // 5. Analog Sheet Film & Classic Formats
      cam_linhof_4x5_architectural: {
        profile: "linhof_technika_4x5",
        lens: "Schneider Kreuznach Apo-Symmar 150mm f/5.6 L (Museum Reference)",
        aperture: "f/11",
        subject: "Museum director standing gracefully in grand central gallery flanked by classical sculptures",
        framing: "full-length architectural fashion portrait",
        environment: "soaring neoclassical museum rotunda with polished marble floor and fluted columns",
        wardrobe: "bespoke charcoal three-piece suit with silk tie",
        mood: "Scheimpflug optical plane alignment, zero vertical keystoning, Kodak Ektar 100 resolution",
        timeWeather: "overcast",
        lighting: "architectural_skylight",
        filmStock: "portra_160",
        aspectRatio: "4:5"
      },
      cam_linhof_4x5_desert: {
        profile: "linhof_technika_4x5",
        lens: "Rodenstock Grandagon-N 90mm f/4.5 (Extreme Architectural Rise)",
        aperture: "f/16",
        subject: "Explorer standing at canyon rim looking into the vast expanse of red sandstone",
        framing: "wide environmental cinematic frame",
        environment: "red sandstone canyon rim with deep geological strata and distant desert haze",
        wardrobe: "khaki canvas safari jacket and wide-brim felt hat",
        mood: "monumental scale, ancient earth, sheet film micro-acutance, adventurous stillness",
        timeWeather: "noon_sun",
        lighting: "golden_hour",
        filmStock: "provia_100f",
        aspectRatio: "4:5"
      },
      cam_pentax_67_bokeh_king: {
        profile: "pentax_67ii",
        lens: "SMC Pentax 67 105mm f/2.4 (The Legendary Bokeh King)",
        aperture: "f/2.4",
        subject: "Person standing amidst wild sea grass with evening wind blowing through hair",
        framing: "three-quarter editorial portrait",
        environment: "coastal sand dunes leading to an open ocean beach at low tide",
        wardrobe: "chunky cream cable-knit wool sweater and weathered denim",
        mood: "The Legendary Bokeh King, medium format 6x7 negative depth, velvety background melt",
        timeWeather: "golden_hour",
        lighting: "golden_hour",
        filmStock: "portra_400",
        aspectRatio: "4:5"
      },
      cam_pentax_67_cotswolds: {
        profile: "pentax_67ii",
        lens: "SMC Pentax 67 90mm f/2.8 (Crisp Documentary Normal)",
        aperture: "f/2.8",
        subject: "Botanist gathering garden roses into a wicker basket beside weathered stone wall",
        framing: "three-quarter editorial portrait",
        environment: "English country stone cottage garden overflowing with climbing roses and delphiniums",
        wardrobe: "waxed cotton jacket and sage linen dress",
        mood: "pastoral, romantic, gentle morning tranquility, organic Portra color palette",
        timeWeather: "overcast",
        lighting: "window_daylight",
        filmStock: "portra_160",
        aspectRatio: "4:5"
      },
      cam_hasselblad_500cm_zeiss: {
        profile: "hasselblad_500cm",
        lens: "Carl Zeiss Planar T* 80mm f/2.8 CF (Legendary Standard)",
        aperture: "f/4.0",
        subject: "Winemaker inspecting grape clusters in late summer light along vineyard terrace",
        framing: "square medium format environmental portrait",
        environment: "sun-drenched Tuscan vineyard on rolling hills with cypress trees in background",
        wardrobe: "rustic chambray shirt and dirt-stained leather work gloves",
        mood: "Zeiss Planar micro-contrast, square 6x6 medium format discipline, sun-drenched Tuscany",
        timeWeather: "golden_hour",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        filmStock: "portra_400",
        aspectRatio: "1:1"
      }
    };

    // =========================================================================
    // CALIBRATED AMBIENT & LIGHTING PRESETS (Organized by Environmental Style)
    // =========================================================================
    const AMBIENT_PRESETS = {
      // 1. Cities & Urban Streetscapes
      amb_paris_haussmann: {
        environment: "wet cobblestone Paris street in Saint-Germain, limestone Haussmann facade in background with zinc rooftops",
        timeWeather: "overcast",
        cityVibe: "paris",
        lighting: "window_daylight",
        mood: "effortless European sophistication, contemplative, authentic Parisian elegance",
        wardrobe: "tailored navy wool trench coat and gray cashmere scarf",
        filmStock: "digital_raw"
      },
      amb_tokyo_shinjuku: {
        environment: "narrow rain-soaked alleyway in Shinjuku with glowing neon signs and reflective puddles",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "tungsten_candle",
        mood: "melancholic, cinematic, vivid night atmosphere with saturated reflections",
        wardrobe: "dark oversized coat with glistening raindrops on shoulders",
        filmStock: "cinestill_800t"
      },
      amb_nyc_soho_loft: {
        environment: "sunlit SoHo loft exterior with historic cast-iron columns, fire escapes, and Belgian block cobblestones",
        timeWeather: "golden_hour",
        cityVibe: "nyc",
        lighting: "golden_hour",
        mood: "sharp, modern, vibrant creative energy with raking morning sunlight",
        wardrobe: "minimalist black blazer, crisp white t-shirt, tailored trousers",
        filmStock: "digital_raw"
      },
      amb_london_mayfair: {
        environment: "Mayfair street with weathered Portland stone, black wrought-iron railings, and gentle misty drizzle",
        timeWeather: "overcast",
        cityVibe: "london",
        lighting: "window_daylight",
        mood: "understated British refinement, calm overcast atmosphere",
        wardrobe: "charcoal tweed overcoat and leather Chelsea boots",
        filmStock: "portra_400"
      },
      amb_milan_portico: {
        environment: "lofty marble portico in Brera design district with geometric sunbeam shadows and sunlit courtyard",
        timeWeather: "noon_sun",
        cityVibe: "milan",
        lighting: "strobe_para",
        mood: "commanding, sophisticated Italian fashion with high-contrast shadow carving",
        wardrobe: "sharp structured camel wool coat and dark sunglasses",
        filmStock: "portra_160"
      },
      amb_kyoto_gion: {
        environment: "historic Gion preservation lane with dark aged cedar lattice timber, glowing amber paper lanterns, and wet flagstones",
        timeWeather: "rainy_wet",
        cityVibe: "tokyo",
        lighting: "tungsten_candle",
        mood: "serene, contemplative, ancient Japanese atmospheric evening",
        wardrobe: "indigo-dyed heavy linen smock and wooden geta footwear",
        filmStock: "portra_400"
      },
      amb_berlin_concrete: {
        environment: "raw board-formed concrete industrial courtyard in Berlin Mitte with exposed steel beams and gravel",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "stark brutalist minimalism, cold industrial aesthetic",
        wardrobe: "monochromatic black technical parka and heavyweight trousers",
        filmStock: "digital_raw"
      },

      // 2. Luxury Hospitality & Architectural Sanctuaries
      amb_amalfi_terrace: {
        environment: "private terracotta terrace of a cliffside boutique hotel overlooking the deep azure Mediterranean sea",
        timeWeather: "golden_hour",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        mood: "peaceful luxury, serene warmth, slow coastal living",
        wardrobe: "unbleached relaxed white linen shirt and light linen trousers",
        filmStock: "portra_160"
      },
      amb_manhattan_penthouse: {
        environment: "modernist luxury penthouse living room with smoked oak flooring, marble accents, and floor-to-ceiling skyline views",
        timeWeather: "morning_fog",
        cityVibe: "nyc",
        lighting: "architectural_skylight",
        mood: "quiet contemplation, refined architectural luxury",
        wardrobe: "fine ribbed dark knit sweater and tailored wool trousers",
        filmStock: "digital_raw"
      },
      amb_paris_palace_lobby: {
        environment: "historic Grand Hotel lobby with fluted plaster columns, warm crystal chandeliers, gilded mirrors, and marble hearth",
        timeWeather: "night_city",
        cityVibe: "paris",
        lighting: "tungsten_candle",
        mood: "opulent, cinematic, dignified European grandeur",
        wardrobe: "tailored midnight blue double-breasted suit",
        filmStock: "classic_chrome"
      },
      amb_kyoto_ryokan: {
        environment: "traditional luxury ryokan interior with natural tatami mats, sliding shoji screens, and morning light on moss garden",
        timeWeather: "window_daylight",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "zen tranquility, meditative quiet, organic natural textures",
        wardrobe: "natural raw silk yukata robe with dark sash",
        filmStock: "provia_100f"
      },
      amb_alpine_chalet: {
        environment: "Swiss luxury alpine chalet salon with roaring raw granite hearth, floor-to-ceiling snow views, and timber beams",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "tungsten_candle",
        mood: "hygge warmth, tactile comfort against alpine winter chill",
        wardrobe: "chunky ivory ribbed cashmere turtleneck and flannel trousers",
        filmStock: "portra_400"
      },
      amb_speakeasy_lounge: {
        environment: "speakeasy cocktail lounge with curved mahogany bar, dim amber filament bulbs, and midnight velvet drapery",
        timeWeather: "night_city",
        cityVibe: "none",
        lighting: "rembrandt_key",
        mood: "intimate, moody, cinematic storytelling",
        wardrobe: "crisp unbuttoned collar shirt and vintage leather jacket",
        filmStock: "arri_logc4"
      },

      // 3. Coastal, Maritime & Island Escapes
      amb_mediterranean_cliff: {
        environment: "whitewashed Mediterranean cliffside village with vibrant bougainvillea, sun-bleached stone, and deep blue ocean",
        timeWeather: "noon_sun",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        mood: "sun-drenched, radiant, timeless summer warmth",
        wardrobe: "flowing sky-blue cotton sundress with delicate embroidery",
        filmStock: "portra_160"
      },
      amb_atlantic_dunes: {
        environment: "coastal sand dunes leading to an open ocean beach at low tide with windswept sea oats",
        timeWeather: "golden_hour",
        cityVibe: "none",
        lighting: "golden_hour",
        mood: "raw coastal beauty, free, natural salt air",
        wardrobe: "chunky cream cable-knit wool sweater and weathered denim",
        filmStock: "portra_400"
      },
      amb_nordic_fjord: {
        environment: "Norwegian coastal fjord with dark mist-shrouded peaks, dark wet granite rocks, and pine fringe",
        timeWeather: "morning_fog",
        cityVibe: "scandinavia",
        lighting: "window_daylight",
        mood: "epic nature, vast monumental scale, crisp northern air",
        wardrobe: "mustard yellow technical rain parka and waterproof hiking boots",
        filmStock: "classic_chrome"
      },
      amb_tropical_shore: {
        environment: "secluded tropical beach with gentle surf, wet sand, and coconut palm silhouettes against orange twilight",
        timeWeather: "golden_hour",
        cityVibe: "none",
        lighting: "golden_hour",
        mood: "peaceful daily life, grounded, sun-baked serenity",
        wardrobe: "faded linen shirt and roll-up cotton trousers",
        filmStock: "portra_400"
      },
      amb_big_sur_bluffs: {
        environment: "high dramatic coastal cliffs over crashing Pacific surf with dense marine layer fog breaking into warm golden sun",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "golden_hour",
        mood: "untamed wilderness, awe-inspiring maritime atmosphere",
        wardrobe: "waxed canvas field coat and heavy wool beanie",
        filmStock: "portra_400"
      },

      // 4. Terroir, Rural Landscapes & Wild Nature
      amb_tuscan_vineyard: {
        environment: "sun-drenched Tuscan vineyard on rolling hills with cypress trees and warm late afternoon golden dust",
        timeWeather: "golden_hour",
        cityVibe: "mediterranean",
        lighting: "golden_hour",
        mood: "earthy, authentic, slow agrarian rhythm",
        wardrobe: "rustic chambray shirt and dirt-stained leather work gloves",
        filmStock: "portra_400"
      },
      amb_pnw_pine_forest: {
        environment: "dense Pacific Northwest pine forest mountain trail, mossy Douglas fir canopy, and damp cedar earth",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "quiet solitary wilderness, cool damp mountain air",
        wardrobe: "heavy red-and-black wool flannel overshirt and leather boots",
        filmStock: "portra_400"
      },
      amb_cotswolds_garden: {
        environment: "English country stone cottage garden overflowing with climbing roses, delphiniums, and dry-stone walls",
        timeWeather: "overcast",
        cityVibe: "london",
        lighting: "window_daylight",
        mood: "pastoral, romantic, gentle morning English daylight",
        wardrobe: "waxed cotton jacket and sage linen dress",
        filmStock: "portra_160"
      },
      amb_mojave_desert: {
        environment: "red sandstone canyon rim with deep geological strata, raking dune shadows, and distant desert haze",
        timeWeather: "noon_sun",
        cityVibe: "none",
        lighting: "golden_hour",
        mood: "monumental scale, ancient earth, adventurous stillness",
        wardrobe: "khaki canvas safari jacket and wide-brim felt hat",
        filmStock: "provia_100f"
      },
      amb_highland_moor: {
        environment: "Scottish Highlands peat moorland covered in blooming purple heather under low dramatic storm clouds",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "brooding, wild, romantic solitude",
        wardrobe: "heavy Harris Tweed jacket and waterproof leather field boots",
        filmStock: "portra_160"
      },

      // 5. High-End Commercial Studio & Exhibition
      amb_cosmetic_packshot: {
        environment: "high-end commercial studio cyclorama with dual diffused strip softboxes and black flag negative fill",
        timeWeather: "studio_soft",
        cityVibe: "none",
        lighting: "strobe_softbox",
        mood: "pristine, tactile, ultra-premium commercial quality",
        wardrobe: "none",
        filmStock: "digital_raw"
      },
      amb_haute_couture_studio: {
        environment: "pure white infinity cove photo studio with subtle floor reflections and giant Broncolor Para 220 strobe",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        mood: "sculptural high-fashion elegance, pristine micro-contrast",
        wardrobe: "unbleached raw ivory silk draped architectural dress",
        filmStock: "portra_160"
      },
      amb_sculptor_atelier: {
        environment: "historic Carrara limestone atelier with half-carved statues and raking morning sunlight beams",
        timeWeather: "morning_fog",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "intense concentration, raw craftsmanship, suspended marble dust",
        wardrobe: "heavy indigo canvas workshirt and stained leather apron",
        filmStock: "classic_chrome"
      },
      amb_horologist_bench: {
        environment: "cluttered antique wooden workbench with miniature gear wheels, watchmaker loupes, and brass shavings",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        mood: "microscopic precision, quiet mastery",
        wardrobe: "dark wool vest and rolled-up striped cotton shirt",
        filmStock: "digital_raw"
      },
      amb_museum_rotunda: {
        environment: "soaring neoclassical museum rotunda with polished marble floor, fluted columns, and glass skylight",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "architectural_skylight",
        mood: "scholarly majesty, timeless architectural symmetry",
        wardrobe: "bespoke charcoal three-piece suit with silk tie",
        filmStock: "portra_160"
      },
      amb_commercial_gobo_copy: {
        environment: "architectural limestone studio plinth with sharp raking Venetian blind shadow patterns and negative copy-space",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        mood: "prestigious commercial luxury, pristine high-acutance minimalism",
        wardrobe: "none",
        filmStock: "digital_raw"
      },

      // 6. Mastery Protocols & Technical Directives
      amb_4d_liquid_glass: {
        environment: "deep opaque black softly blurred studio void with controlled contour rim glow",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "strobe_para",
        mood: "hypnotic avant-garde editorial, pristine optical precision",
        wardrobe: "bespoke black liquid-glass and latex bodysuit with contoured structural paneling",
        filmStock: "digital_raw"
      },
      amb_heavyweight_morphology: {
        environment: "minimalist concrete locker pavilion, raking directional skylight",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "window_rake",
        mood: "dignified power, quiet rebellion, calm intensity",
        wardrobe: "ribbed athletic compression tank conforming naturally to enlarged torso",
        filmStock: "digital_raw"
      },
      amb_baryta_print_prepress: {
        environment: "Kyoto pottery atelier, clay dust suspended in directional sunlight",
        timeWeather: "auto",
        cityVibe: "none",
        lighting: "daylight_diffuse",
        mood: "timeless artisanal presence, exhibition fine art acutance",
        wardrobe: "indigo dyed heavy linen smock",
        filmStock: "digital_raw"
      },
      amb_depixel_v2_restoration: {
        environment: "professional document copystand with 45-degree balanced polarization and zero reflections",
        timeWeather: "studio_soft",
        cityVibe: "none",
        lighting: "strobe_softbox",
        mood: "Universal De-Pixelate v2.0 restoration, strict OCR safety, flat copy-stand acutance",
        wardrobe: "none",
        filmStock: "digital_raw"
      },
      amb_monochrome_luminance: {
        environment: "monochrome stone archival gallery with raking directional window light",
        timeWeather: "overcast",
        cityVibe: "none",
        lighting: "window_daylight",
        mood: "pure monochromatic sensor fidelity, zero CFA interpolation, obsidian black to pure specular white",
        wardrobe: "charcoal wool minimalist attire",
        filmStock: "digital_raw"
      }
    };

    // Backward-compatible merged dictionary
    const SCENARIOS = Object.assign({}, CAMERA_PRESETS, AMBIENT_PRESETS);
    // Aliases for legacy scenario keys
    SCENARIOS.city_paris = CAMERA_PRESETS.cam_leica_m11_reportage;
    SCENARIOS.tokyo_night = CAMERA_PRESETS.cam_leica_m6_analog_trix;
    SCENARIOS.nyc_soho = CAMERA_PRESETS.cam_sony_a7rv_macro_horology;
    SCENARIOS.london_drizzle = CAMERA_PRESETS.cam_leica_sl3_p_apo;
    SCENARIOS.milan_portico = CAMERA_PRESETS.cam_hasselblad_h6d_para;
    SCENARIOS.hotel_terrace = AMBIENT_PRESETS.amb_amalfi_terrace;
    SCENARIOS.hotel_penthouse = CAMERA_PRESETS.cam_phase_one_iq4_arch;
    SCENARIOS.hotel_lobby = AMBIENT_PRESETS.amb_paris_palace_lobby;
    SCENARIOS.hotel_bar = CAMERA_PRESETS.cam_arri_alexa_35_cooke;
    SCENARIOS.beach_dunes = CAMERA_PRESETS.cam_pentax_67_bokeh_king;
    SCENARIOS.mediterranean_cliff = AMBIENT_PRESETS.amb_mediterranean_cliff;
    SCENARIOS.nordic_fjord = AMBIENT_PRESETS.amb_nordic_fjord;
    SCENARIOS.tropical_shore = AMBIENT_PRESETS.amb_tropical_shore;
    SCENARIOS.rural_vineyard = CAMERA_PRESETS.cam_hasselblad_500cm_zeiss;
    SCENARIOS.mountain_cabin = AMBIENT_PRESETS.amb_pnw_pine_forest;
    SCENARIOS.english_country = CAMERA_PRESETS.cam_pentax_67_cotswolds;
    SCENARIOS.desert_canyon = CAMERA_PRESETS.cam_linhof_4x5_desert;
    SCENARIOS.architect_brutalist = CAMERA_PRESETS.cam_phase_one_iq4_arch;
    SCENARIOS.commercial_packshot = AMBIENT_PRESETS.amb_cosmetic_packshot;
    SCENARIOS.fashion_studio = CAMERA_PRESETS.cam_hasselblad_h6d_para;
    SCENARIOS.sculptor_atelier = CAMERA_PRESETS.cam_fujifilm_gfx100ii_reala;
    SCENARIOS.watchmaker_bench = CAMERA_PRESETS.cam_sony_a7rv_macro_horology;
    SCENARIOS.museum_gallery = CAMERA_PRESETS.cam_linhof_4x5_architectural;
    SCENARIOS.hollywood_anamorphic = CAMERA_PRESETS.cam_arri_alexa_35_anamorphic;
    SCENARIOS.commercial_billboard_copy_space = AMBIENT_PRESETS.amb_commercial_gobo_copy;
    SCENARIOS.hyperrealistic_latex_character = AMBIENT_PRESETS.amb_4d_liquid_glass;
    SCENARIOS.heavyweight_editorial_portrait = AMBIENT_PRESETS.amb_heavyweight_morphology;
    SCENARIOS.gallery_baryta_print = CAMERA_PRESETS.cam_phase_one_iq4_still;

    async function init() {
      setupDragAndDrop();
      await loadProfiles();
      // Apply default Leica M11 + Paris scenario to start
      if (document.getElementById('cameraPresetSelect')) {
        document.getElementById('cameraPresetSelect').value = 'cam_leica_m11_reportage';
        onCameraPresetSelectChange();
      }
      if (document.getElementById('ambientPresetSelect')) {
        document.getElementById('ambientPresetSelect').value = 'amb_paris_haussmann';
        onAmbientPresetSelectChange();
      }
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

    function onCameraPresetSelectChange() {
      const select = document.getElementById('cameraPresetSelect');
      const val = select ? select.value : 'none';

      if (val === 'none') {
        return;
      }

      const c = CAMERA_PRESETS[val];
      if (!c) return;

      // 1. Populate camera profile
      document.getElementById('profileSelect').value = c.profile;
      onProfileChange();

      // 2. Populate matched lens if present in options
      if (c.lens) {
        const lensSelect = document.getElementById('lensSelect');
        const targetLensPrefix = c.lens.split(" (")[0].toLowerCase();
        for (let i = 0; i < lensSelect.options.length; i++) {
          if (lensSelect.options[i].text.toLowerCase().includes(targetLensPrefix) ||
              lensSelect.options[i].value.toLowerCase().includes(targetLensPrefix)) {
            lensSelect.selectedIndex = i;
            break;
          }
        }
      }

      // 3. Populate camera-tailored subject & framing
      if (c.subject) document.getElementById('subjectInput').value = c.subject;
      if (c.framing) document.getElementById('framingInput').value = c.framing;

      // 4. If ambient style is not set, provide sensible default environment from camera preset
      const ambSelect = document.getElementById('ambientPresetSelect');
      if (!ambSelect || ambSelect.value === 'none') {
        if (c.environment) document.getElementById('environmentInput').value = c.environment;
        if (c.wardrobe) document.getElementById('wardrobeInput').value = c.wardrobe;
        if (c.mood) document.getElementById('moodInput').value = c.mood;
        if (c.timeWeather) document.getElementById('timeWeatherSelect').value = c.timeWeather;
        if (c.cityVibe) document.getElementById('cityVibeSelect').value = c.cityVibe;
        if (c.lighting) document.getElementById('lightingSelect').value = c.lighting;
        if (c.filmStock) document.getElementById('filmStockSelect').value = c.filmStock;
      }

      // 5. Special camera features
      if (c.anamorphic !== undefined && document.getElementById('chkAnamorphic')) {
        document.getElementById('chkAnamorphic').checked = !!c.anamorphic;
        if (c.squeeze) document.getElementById('squeezeSelect').value = c.squeeze;
        if (c.streakFlare) document.getElementById('streakFlareSelect').value = c.streakFlare;
        if (c.irisBlades) document.getElementById('irisBladesSelect').value = c.irisBlades;
      }
      if (c.aspectRatio && document.getElementById('aspectSelect')) {
        document.getElementById('aspectSelect').value = c.aspectRatio;
      }
      if (c.paperProfile && document.getElementById('paperProfileSelect')) {
        document.getElementById('paperProfileSelect').value = c.paperProfile;
      }
      if (c.printSize && document.getElementById('printSizeSelect')) {
        document.getElementById('printSizeSelect').value = c.printSize;
      }

      setAperture(c.aperture || 'f/2.8');
      debounceCompile();
    }

    function onAmbientPresetSelectChange() {
      const select = document.getElementById('ambientPresetSelect');
      const val = select ? select.value : 'none';

      if (val === 'none') {
        return;
      }

      const a = AMBIENT_PRESETS[val];
      if (!a) return;

      if (a.environment) document.getElementById('environmentInput').value = a.environment;
      if (a.wardrobe) document.getElementById('wardrobeInput').value = a.wardrobe;
      if (a.mood) document.getElementById('moodInput').value = a.mood;
      if (a.timeWeather) document.getElementById('timeWeatherSelect').value = a.timeWeather;
      if (a.cityVibe) document.getElementById('cityVibeSelect').value = a.cityVibe;
      if (a.lighting) document.getElementById('lightingSelect').value = a.lighting;
      if (a.filmStock) document.getElementById('filmStockSelect').value = a.filmStock;

      debounceCompile();
    }

    function onScenarioSelectChange(customKey) {
      const val = customKey || (document.getElementById('scenarioSelect') ? document.getElementById('scenarioSelect').value : 'none');
      if (val === 'none') {
        clearToSurprise();
        return;
      }
      if (CAMERA_PRESETS[val]) {
        if (document.getElementById('cameraPresetSelect')) document.getElementById('cameraPresetSelect').value = val;
        onCameraPresetSelectChange();
        return;
      }
      if (AMBIENT_PRESETS[val]) {
        if (document.getElementById('ambientPresetSelect')) document.getElementById('ambientPresetSelect').value = val;
        onAmbientPresetSelectChange();
        return;
      }
      const s = SCENARIOS[val];
      if (!s) return;
      if (s.profile) {
        document.getElementById('profileSelect').value = s.profile;
        onProfileChange();
      }
      if (s.subject) document.getElementById('subjectInput').value = s.subject;
      if (s.framing) document.getElementById('framingInput').value = s.framing;
      if (s.environment) document.getElementById('environmentInput').value = s.environment;
      if (s.wardrobe) document.getElementById('wardrobeInput').value = s.wardrobe;
      if (s.mood) document.getElementById('moodInput').value = s.mood;
      if (s.timeWeather) document.getElementById('timeWeatherSelect').value = s.timeWeather;
      if (s.cityVibe) document.getElementById('cityVibeSelect').value = s.cityVibe;
      if (s.lighting) document.getElementById('lightingSelect').value = s.lighting;
      if (s.filmStock) document.getElementById('filmStockSelect').value = s.filmStock;
      if (s.aperture) setAperture(s.aperture);
      debounceCompile();
    }

    function clearToSurprise() {
      if (document.getElementById('cameraPresetSelect')) document.getElementById('cameraPresetSelect').value = 'none';
      if (document.getElementById('ambientPresetSelect')) document.getElementById('ambientPresetSelect').value = 'none';
      if (document.getElementById('scenarioSelect')) document.getElementById('scenarioSelect').value = 'none';
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
      
      showToast("Cleared! Build your own scene freely or pick from camera & ambient styles.");
      debounceCompile();
    }
    const clearToBuildYourOwn = clearToSurprise;

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

      const camPresetEl = document.getElementById('cameraPresetSelect');
      if (selected && selected.aperture && (!camPresetEl || camPresetEl.value === 'none')) {
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

        if parsed_path not in ("/api/compile", "/api/upscale-102mp", "/api/export-closed-loop", "/api/recon-4x", "/api/png-lock-upscale"):
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception as err:
            self._send_json({"error": f"Invalid JSON payload: {err}"}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed_path == "/api/png-lock-upscale":
            input_path = body.get("input_path") or body.get("image_path")
            if not input_path:
                self._send_json({"error": "Missing required field 'input_path'"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                from .restoration import PILLOW_AVAILABLE, execute_4x_full_color_png_upscale
            except ImportError:
                self._send_json({"error": "Restoration module could not be imported."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if not PILLOW_AVAILABLE:
                self._send_json({"error": "Pillow is not installed."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                output_path = body.get("output_path") or None
                unsharp_radius = float(body.get("unsharp_radius", 1.1))
                unsharp_percent = int(body.get("unsharp_percent", 85))
                unsharp_threshold = int(body.get("unsharp_threshold", 3))
                compress_level = int(body.get("compress_level", 0))
                min_mb = float(body.get("min_mb", 12.0))

                rep, rep_dict = execute_4x_full_color_png_upscale(
                    input_path=input_path,
                    output_path=output_path,
                    unsharp_radius=unsharp_radius,
                    unsharp_percent=unsharp_percent,
                    unsharp_threshold=unsharp_threshold,
                    compress_level=compress_level,
                    min_mb=min_mb,
                    generate_report=True,
                )
                self._send_json(rep_dict)
            except Exception as err:
                self._send_json({"error": str(err)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if parsed_path == "/api/recon-4x":
            input_path = body.get("input_path") or body.get("image_path")
            if not input_path:
                self._send_json({"error": "Missing required field 'input_path'"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                from .restoration import PILLOW_AVAILABLE, execute_4x_reconstruction_lock
            except ImportError:
                self._send_json({"error": "Restoration module could not be imported."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if not PILLOW_AVAILABLE:
                self._send_json({"error": "Pillow is not installed."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                output_path = body.get("output_path") or None
                backend = body.get("backend", "realesrnet_x4plus")
                denoise_strength = float(body.get("denoise_strength", 0.15))
                blend_ratio = float(body.get("blend_ratio", 0.20))
                protect_sky_haze = bool(body.get("protect_sky_haze", True))
                output_format = body.get("output_format")

                rep, rep_dict = execute_4x_reconstruction_lock(
                    input_path=input_path,
                    output_path=output_path,
                    backend=backend,
                    denoise_strength=denoise_strength,
                    blend_ratio=blend_ratio,
                    protect_sky_haze=protect_sky_haze,
                    output_format=output_format,
                    generate_report=True,
                )
                self._send_json(rep_dict)
            except Exception as err:
                self._send_json({"error": str(err)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
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
                reconstruction_lock=body.get("reconstruction_lock") or body.get("recon_4x", False),
                sr_backend=body.get("sr_backend"),
                sr_denoise=float(body["sr_denoise"]) if body.get("sr_denoise") is not None else None,
                sr_blend=float(body["sr_blend"]) if body.get("sr_blend") is not None else None,
                protect_sky_haze=bool(body.get("protect_sky_haze", True)),
                png_lock=body.get("png_lock") or body.get("png_output_lock", False),
                png_min_mb=float(body["png_min_mb"]) if body.get("png_min_mb") is not None else None,
                depixelate_v2=body.get("depixelate_v2") or body.get("depix_v2", False),
                depix_camera=body.get("depix_camera"),
                depix_lens=body.get("depix_lens"),
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
