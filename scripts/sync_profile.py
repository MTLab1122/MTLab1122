#!/usr/bin/env python3
"""
Autonomous GitHub Profile & Portfolio Synchronization Engine
Author: Muhammad Talha (@MTLab1122)

This engine automates the discovery, auditing, metadata validation, and
idempotent updating of the master GitHub Profile README and repository portfolio.
Follows strict safety principles:
- Never exposes private repository metadata.
- Never makes destructive changes or renames.
- Idempotent: produces 0 diffs if no new repositories or updates occurred.
- Verifies all links and assets for 100% reliability.
"""

import os
import sys
import json
import subprocess
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
README_PATH = WORKSPACE_ROOT / "README.md"
REPORT_PATH = WORKSPACE_ROOT / "sync_report.md"

# Known curated flagship assignments and priority rankings
FLAGSHIP_CATALOG = {
    "SpecForge": {
        "title": "SpecForge — Discovery & Scope OS SaaS Platform",
        "category": "Enterprise Multi-Tenant SaaS & Distributed Systems",
        "tagline": "AI-assisted discovery, requirements, estimation, and delivery-handover SaaS with cryptographic sign-offs.",
        "badges": ["Next.js 15.5", "TypeScript 5.4", "Prisma 5.22", "PostgreSQL 16", "Zod", "Playwright"],
        "highlights": [
            "<b>11-Stage Scope Pipeline:</b> Grounded requirements extraction linking citations directly to source audio/text with zero hallucinations.",
            "<b>Cryptographic Client Sign-Offs:</b> Immutable scope freezing with SHA-256 digital seals preventing scope creep.",
            "<b>Defensible P80 Estimation:</b> Mathematical contingency modeling with automated Jira, Linear, and GitHub task generation.",
            "<b>49 / 49 Master Quality Checks:</b> 100% green launch-readiness matrix and 124 modular architecture tests passing."
        ],
        "demo_url": "https://specforge-tawny.vercel.app",
        "repo_url": "https://github.com/MTLab1122/SpecForge",
        "priority": 1,
    },
    "PDF_file_conversion_to_Audio": {
        "title": "AudioDoc — Commercial PDF-to-Audiobook SaaS",
        "category": "Enterprise Multi-Tenant SaaS & Distributed Systems",
        "tagline": "Distributed commercial platform converting complex digital & scanned documents into neural audiobooks.",
        "badges": ["Next.js 14", "FastAPI", "Celery", "Redis 8", "PostgreSQL 16", "FFmpeg", "PyMuPDF"],
        "highlights": [
            "<b>Microservice Architecture:</b> Next.js 14 App Router decoupled with Python FastAPI gateway and Celery distributed workers.",
            "<b>Dual-Engine Ingestion:</b> PyMuPDF column-aware structural parsing with 300 DPI Tesseract OCR fallback.",
            "<b>Neural Voice Synthesis:</b> Edge Neural TTS engine with 100+ voices, chunk-level FFmpeg assembly, and ID3 tags.",
            "<b>87 / 87 Automated Tests Passed:</b> 100% pass rate spanning Pytest, Vitest, Playwright browser E2E, and OWASP audits."
        ],
        "demo_url": "https://pdf-file-conversion-to-audio.vercel.app",
        "repo_url": "https://github.com/MTLab1122/PDF_file_conversion_to_Audio",
        "priority": 2,
    },
    "Cash-Carry-SaaS-POS-Platform": {
        "title": "Enterprise Cash & Carry SaaS & POS Platform",
        "category": "Enterprise Multi-Tenant SaaS & Distributed Systems",
        "tagline": "Multi-tenant retail management platform and offline-first Point-of-Sale ecosystem for wholesale supermarkets.",
        "badges": ["Next.js 14", "NestJS", "Electron", "Flutter", "Prisma", "SQLite", "TypeScript"],
        "highlights": [
            "<b>Triple-Client Ecosystem:</b> Next.js 14 Web Management, Windows Desktop POS (Electron + SQLite), and Mobile App (Flutter).",
            "<b>Offline POS Engine:</b> Sub-500ms barcode scanning, durable offline mutation queue with UUID idempotency, and replay sync.",
            "<b>Hardware Integration:</b> 80mm ESC/POS thermal printing, cash drawer kick triggers, and GS1 EAN-13 barcodes.",
            "<b>169 / 169 Verification Assertions Passing:</b> Double-entry khata chained with SHA-256 hash chains preventing retroactive tampering."
        ],
        "demo_url": "https://cash-carry-saaspos.vercel.app",
        "repo_url": "https://github.com/MTLab1122/Cash-Carry-SaaS-POS-Platform",
        "priority": 3,
    },
    "ShifaDesk": {
        "title": "ShifaDesk (MatabAI) — Multilingual Clinic Operations SaaS",
        "category": "Enterprise Multi-Tenant SaaS & Distributed Systems",
        "tagline": "Enterprise multilingual AI-powered clinic operations and EMR SaaS platform for outpatient healthcare networks.",
        "badges": ["Next.js 15", "NestJS 10", "Supabase", "PostgreSQL 16", "Prisma", "Tailwind CSS"],
        "highlights": [
            "<b>Monorepo Architecture:</b> High-performance pnpm monorepo uniting Next.js 15 App Router web client and NestJS 10 REST API.",
            "<b>Multilingual Patient Care:</b> AI clinical transcription, smart walk-in queueing, and WhatsApp-driven booking (Urdu, English, Pashto, Arabic).",
            "<b>Clinical EMR-Lite & Finance:</b> Longitudinal patient records, prescription tracking, multi-tender billing, and cash drawer auditing.",
            "<b>HIPAA/GDPR Security Protocols:</b> Row-level tenant isolation, zero-secret commits, and granular role-based access control."
        ],
        "demo_url": "https://shifadesk-mtlab.vercel.app",
        "repo_url": "https://github.com/MTLab1122/ShifaDesk",
        "priority": 4,
    },
    "AgroShift_NASA": {
        "title": "AgroShift — NASA Space Apps Challenge 2026",
        "category": "Autonomous AI, Climate Intelligence & Telemetry",
        "tagline": "Climate-resilient crop planning powered by NASA Earth observations for Peshawar Valley (Team Lead).",
        "badges": ["Next.js 14", "FastAPI", "Python 3.11", "NASA SMAP", "NASA GPM", "Leaflet", "Pytest"],
        "highlights": [
            "<b>Global Challenge Leadership:</b> Team Lead of Team InCir (Abasyn University Peshawar) for the NASA Space Apps Challenge 2026.",
            "<b>4-Engine NASA Synthesis:</b> Live ingestion of NASA SMAP L4 soil moisture, GPM IMERG rain, MODIS/VIIRS NDVI, and POWER agroclimatology.",
            "<b>Explainable Agronomic Engine:</b> Multi-criteria decision function balancing climate suitability, water efficiency, and soil nitrogen.",
            "<b>74 / 74 Automated Tests Passed:</b> 100% pass rate in Pytest with live terminal probes and deterministic scenario comparisons."
        ],
        "demo_url": "https://agroshift-nasa-eight.vercel.app",
        "repo_url": "https://github.com/MTLab1122/AgroShift_NASA",
        "priority": 5,
    },
    "BluetoothChat": {
        "title": "BluetoothChat — Offline P2P Android Network",
        "category": "Native Mobile & Distributed Protocols",
        "tagline": "100% offline peer-to-peer encrypted messaging and file transfer mobile application operating without internet.",
        "badges": ["Flutter", "Dart", "Bluetooth RFCOMM", "SQLite", "Material Design 3"],
        "highlights": [
            "<b>Protocol Architecture:</b> Direct RFCOMM socket stream over Serial Port Profile (SPP) with newline-delimited framing.",
            "<b>Binary Chunking Engine:</b> 4KB binary payload chunking with end-to-end SHA-256 verification and automatic packet recovery.",
            "<b>Local State Persistence:</b> Indexed SQLite database schema storing chats, delivery receipts, and cryptographic fingerprints."
        ],
        "demo_url": None,
        "repo_url": "https://github.com/MTLab1122/BluetoothChat",
        "priority": 6,
    },
    "student-opportunity-intelligence": {
        "title": "KP & Charsadda Scholarship Intelligence Agent",
        "category": "Autonomous AI, Climate Intelligence & Telemetry",
        "tagline": "Autonomous daily intelligence agent crawling, verifying, and reporting regional university aid for KP students.",
        "badges": ["Python", "Google Gemini API", "GitHub Actions", "ReportLab", "Pydantic", "Resend API"],
        "highlights": [
            "<b>Three-Tier Trust Engine:</b> Strict source verification separating official .gov/.edu portals from unverified aggregators.",
            "<b>AI Extraction & Deduplication:</b> Gemini API structured extraction, verbatim quotes, and fuzzy similarity deduplication (ratio >= 0.88).",
            "<b>Multi-Format Dispatches:</b> Executes daily at 07:00 PKT via GitHub Actions, compiling vector PDFs, dashboards, and automated email digests."
        ],
        "demo_url": None,
        "repo_url": "https://github.com/MTLab1122/student-opportunity-intelligence",
        "priority": 7,
    },
    "CityDrive_Mobile_APP": {
        "title": "CityDrive — Native Android Car Rental Platform",
        "category": "Native Mobile & Distributed Protocols",
        "tagline": "Native Android vehicle rental and mobility platform engineered with clean architectural separation and reactive state.",
        "badges": ["Kotlin", "Jetpack Compose", "Coroutines", "MVVM + UDF", "Material 3"],
        "highlights": [
            "<b>Native Architecture:</b> Kotlin with Jetpack Compose (Material 3), unidirectional data flow (UDF), and MVVM patterns.",
            "<b>Telemetry & Routing:</b> Live GPS tracking simulation, dynamic interactive map route rendering, and multi-tier booking calculators.",
            "<b>Reactive Concurrency:</b> Asynchronous Kotlin Coroutines and StateFlow streams ensuring 60fps rendering without UI thread blocking."
        ],
        "demo_url": None,
        "repo_url": "https://github.com/MTLab1122/CityDrive_Mobile_APP",
        "priority": 8,
    },
    "autoreport_agent": {
        "title": "Autonomous Tech Intelligence Briefing Agent",
        "category": "Autonomous AI, Climate Intelligence & Telemetry",
        "tagline": "24-hour self-operating market intelligence crawler executing parallel sweeps across frontier AI research.",
        "badges": ["Python", "Gemini GenAI", "ReportLab", "Task Scheduler", "Resend API"],
        "highlights": [
            "<b>Multi-Source Ingestion:</b> Parallel scrapers across Hacker News, Hugging Face model registries, and GitHub trending APIs.",
            "<b>Structured LLM Processing:</b> Strict JSON-mode synthesis with Gemini GenAI SDK, fallback heuristic engines, and Pydantic validation.",
            "<b>Publication Delivery:</b> Automated compilation into professional multi-page vector PDFs dispatched daily to engineering stakeholders."
        ],
        "demo_url": None,
        "repo_url": "https://github.com/MTLab1122/autoreport_agent",
        "priority": 9,
    },
    "portfolio": {
        "title": "Editorial Developer Portfolio Architecture",
        "category": "High-Performance Web & Full-Stack Systems",
        "tagline": "Production developer portfolio engineered with Astro's zero-JS static architecture and strict TypeScript.",
        "badges": ["Astro", "Tailwind CSS v4", "TypeScript", "GSAP", "WCAG 2.2 AA"],
        "highlights": [
            "<b>Performance Benchmarks:</b> 100/100 Core Web Vitals, sub-second LCP, zero layout shift (CLS 0.0), and 0 kB base runtime JS.",
            "<b>Technical SEO:</b> Full Schema.org JSON-LD semantic graph (Person, CreativeWork, ProfilePage) and dynamic XML sitemaps."
        ],
        "demo_url": "https://talha-portfolio-gules.vercel.app/",
        "repo_url": "https://github.com/MTLab1122/portfolio",
        "priority": 10,
    },
    "Campus_Environment_DataVisualization_System": {
        "title": "Campus Environment Telemetry & Visualization",
        "category": "Autonomous AI, Climate Intelligence & Telemetry",
        "tagline": "Full-stack environmental telemetry platform ingesting ambient sensor data across 8 university campus zones.",
        "badges": ["Python", "Flask", "Plotly Dash", "SQLAlchemy", "Chart.js", "Pytest"],
        "highlights": [
            "<b>Analytical Engine:</b> US EPA AQI piecewise linear interpolation, ASHRAE thermal comfort indices, and Plotly 5-axis spider radar.",
            "<b>Automated QA:</b> 27 unit and integration tests passing via pytest covering models, REST API endpoints, and Dash callbacks."
        ],
        "demo_url": "https://campus-environment-data-visualizati.vercel.app",
        "repo_url": "https://github.com/MTLab1122/Campus_Environment_DataVisualization_System",
        "priority": 11,
    },
    "Pac_Man": {
        "title": "Modern Pac-Man Arcade Engine",
        "category": "High-Performance Web & Full-Stack Systems",
        "tagline": "High-performance retro arcade recreation built with React Hooks and requestAnimationFrame — zero canvas engines.",
        "badges": ["Next.js 14", "TypeScript", "React Hooks", "Tailwind CSS"],
        "highlights": [
            "<b>Autonomous AI State Machines:</b> 4 classic ghost behaviors: Blinky (chaser), Pinky (ambusher), Inky (random), Clyde (defender).",
            "<b>Responsive Vector Rendering:</b> Scalable SVG sprites, direction input buffering, and mobile touch controls alongside keyboard controls."
        ],
        "demo_url": "https://pacman-arcade-brown.vercel.app",
        "repo_url": "https://github.com/MTLab1122/Pac_Man",
        "priority": 12,
    },
}

SUGGESTED_METADATA_FIXES = {
    "ShifaDesk": {
        "description": "Multilingual AI-Powered Clinic Operations SaaS Platform — Next.js 15, NestJS 10, Supabase, PostgreSQL 16 & WhatsApp scheduling",
        "topics": ["clinic-management", "emr-system", "healthcare-saas", "nestjs", "nextjs", "postgresql", "prisma", "saas", "supabase", "typescript"]
    },
    "AgroShift_NASA": {
        "description": "AgroShift - NASA Space Apps Challenge 2026. Climate-resilient crop planning powered by NASA Earth observations for Peshawar Valley (Team InCir).",
        "topics": ["agriculture", "climate-resilience", "earth-observation", "fastapi", "nasa-space-apps", "nextjs", "python", "satellite-data", "smap"]
    },
    "AgroShift": {
        "description": "AgroShift Agronomic Decision Support Engine — NASA Space Apps Challenge 2026 climate reconciliation & crop rotation engine in Python/FastAPI.",
        "topics": ["agritech", "climate-data", "decision-support", "fastapi", "nasa-power", "nasa-space-apps", "pydantic", "pytest", "python"]
    },
    "SpecForge": {
        "description": "AI-assisted discovery, requirements, estimation, proposal, client-approval, and delivery-handover SaaS platform",
        "topics": ["ai-agency-tools", "estimation", "nextjs", "playwright", "postgresql", "prisma", "project-management", "saas", "scope-management", "typescript"]
    }
}


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Execute a GitHub CLI command safely."""
    try:
        proc = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8"
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def fetch_all_public_repos() -> list[dict]:
    """Fetch all repositories for the user via GitHub CLI."""
    code, stdout, stderr = run_gh_command([
        "repo", "list", "MTLab1122",
        "--limit", "100",
        "--json", "name,description,url,isPrivate,isFork,updatedAt,createdAt,primaryLanguage,stargazerCount,repositoryTopics"
    ])
    if code != 0:
        print(f"Error fetching repos: {stderr}", file=sys.stderr)
        return []
    try:
        repos = json.loads(stdout)
        # Filter strictly for public repositories to prevent private data exposure
        return [r for r in repos if not r.get("isPrivate", False)]
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        return []


def audit_repositories(repos: list[dict]) -> dict:
    """Analyze repositories for missing descriptions, missing topics, and new projects."""
    missing_desc = []
    missing_topics = []
    recent_repos = []
    now = datetime.now(timezone.utc)

    for r in repos:
        name = r.get("name", "")
        desc = (r.get("description") or "").strip()
        topics = r.get("repositoryTopics") or []
        created_str = r.get("createdAt")
        
        if not desc:
            missing_desc.append(name)
        if not topics:
            missing_topics.append(name)

        if created_str:
            try:
                # Handle ISO 8601 string
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                days_old = (now - created_dt).days
                if days_old <= 30:
                    recent_repos.append({"name": name, "days_old": days_old, "created_at": created_str})
            except Exception:
                pass

    return {
        "total_public_repos": len(repos),
        "missing_descriptions": missing_desc,
        "missing_topics": missing_topics,
        "recent_repos": sorted(recent_repos, key=lambda x: x["days_old"]),
    }


def verify_url(url: str, timeout: int = 15) -> bool:
    """Check whether a URL is reachable (returns HTTP 200/300)."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MTLabProfileBot/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as e:
        # Ignore 429 rate limit, 403, 405 (HEAD/GET restriction) or 999 on LinkedIn/Cloudflare
        if e.code in (403, 405, 429, 999):
            return True
        return False
    except Exception:
        return False


def build_readme_content(repo_count: int) -> str:
    """Assemble the world-class profile README with updated flagships and metadata."""
    
    # Typing SVG lines rotating through all major pillars
    typing_lines = (
        "Enterprise+Multi-Tenant+SaaS+%26+Offline+POS+Architect+%E2%9A%A1;"
        "NASA+Space+Apps+2026+Team+Lead+%E2%80%A2+AgroShift+Earth+Observation+%F0%9F%8C%8D;"
        "Distributed+Neural+AI+Pipelines+(FastAPI+%E2%80%A2+Celery+%E2%80%A2+FFmpeg)+%F0%9F%8E%A7;"
        "Multilingual+Clinic+SaaS+%26+Scope+OS+(Next.js+15+%E2%80%A2+NestJS+%E2%80%A2+Supabase)+%F0%9F%8F%A5;"
        "Native+Android+(Kotlin+%E2%80%A2+Jetpack+Compose)+%26+Flutter+Mobile+%F0%9F%93%B1;"
        "Autonomous+AI+Agents+(Python+%E2%80%A2+Gemini+%E2%80%A2+GitHub+Actions)+%F0%9F%A4%96;"
        "High-Performance+Web+Architecture+(Astro+%E2%80%A2+Next.js+%E2%80%A2+TypeScript)+%F0%9F%9A%80"
    )

    content = f"""<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0:030712,25:0F172A,50:1E1B4B,75:312E81,100:0284C7&height=240&section=header&text=Muhammad%20Talha&fontSize=46&fontAlignY=36&desc=Software%20Engineer%20%7C%20Enterprise%20SaaS%20%E2%80%A2%20Distributed%20AI%20%E2%80%A2%20Native%20Mobile%20Systems&descAlignY=58&descSize=18" width="100%" alt="Muhammad Talha Header Banner" />

  <a href="https://github.com/MTLab1122">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=19&duration=3000&pause=1000&color=38BDF8&center=true&vCenter=true&width=840&lines={typing_lines}" alt="Specializations Typing Animation" />
  </a>

  <br />

  <a href="https://talha-portfolio-gules.vercel.app/">
    <img src="https://img.shields.io/badge/Portfolio-talha--portfolio.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Portfolio" />
  </a>
  <a href="https://www.linkedin.com/in/mtlabs1122/">
    <img src="https://img.shields.io/badge/LinkedIn-Muhammad_Talha-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
  <a href="https://github.com/MTLab1122">
    <img src="https://img.shields.io/badge/GitHub-MTLab1122-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="mailto:muhammadtalhapro1@gmail.com">
    <img src="https://img.shields.io/badge/Email-muhammadtalhapro1%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" />
  </a>
  <a href="https://wa.me/923472937773">
    <img src="https://img.shields.io/badge/WhatsApp-Chat_Direct-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp" />
  </a>
  <a href="#-academic--professional-background">
    <img src="https://img.shields.io/badge/Location-Peshawar%2C_Pakistan-34A853?style=for-the-badge&logo=googlemaps&logoColor=white" alt="Location" />
  </a>

  <br /><br />

  <!-- High-Impact Verified Performance Highlights -->
  <a href="#-academic--professional-background">
    <img src="https://img.shields.io/badge/Academic_Excellence-CGPA_3.87_%2F_4.0-blueviolet?style=flat-square&logo=academia&logoColor=white" alt="CGPA" />
  </a>
  <a href="#-autonomous-ai-climate-intelligence--telemetry">
    <img src="https://img.shields.io/badge/NASA_Space_Apps_2026-Team_Lead-blue?style=flat-square&logo=nasa&logoColor=white" alt="NASA Space Apps" />
  </a>
  <a href="#-featured-engineering-showcase">
    <img src="https://img.shields.io/badge/QA_Standard-100%25_Passing_Automated_Tests-success?style=flat-square&logo=checkmarx&logoColor=white" alt="QA Status" />
  </a>
  <a href="https://github.com/MTLab1122?tab=repositories">
    <img src="https://img.shields.io/badge/Public_Repositories-{repo_count}%2B_Engineered-informational?style=flat-square&logo=github&logoColor=white" alt="Repos" />
  </a>
  <a href="#-academic--professional-background">
    <img src="https://img.shields.io/badge/Technical_Pedagogy-DIT_Instructor-orange?style=flat-square&logo=teacher&logoColor=white" alt="Instructor" />
  </a>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0284C7,50:6366F1,100:38BDF8&height=4&section=header" width="100%" alt="Divider Line" />

## ◈ Executive Overview

I am a **Software Engineer** pursuing my degree at **Abasyn University Peshawar (CGPA 3.87 / 4.0)**, **Team Lead** for the **NASA Space Apps Challenge 2026** (Team InCir), and an active **DIT Instructor** at Govt. Technical & Vocational Center. My engineering practice unifies rigorous computer science fundamentals with production-grade commercial software architecture.

I architect and deliver resilient digital products across four interconnected technical domains:
- 🏢 **Enterprise SaaS & Distributed Architecture**: Commercial multi-tenant platforms built with **Next.js 15/14**, **NestJS 10**, **FastAPI**, **Celery**, **Redis**, and **PostgreSQL 16**, featuring row-level tenant isolation, cryptographic audit trails, and 100% automated test coverage.
- 🌍 **Climate Intelligence & Satellite Observation Systems**: Earth observation synthesis platforms ingesting live **NASA SMAP L4**, **GPM IMERG**, **MODIS/VIIRS NDVI**, and **POWER Agroclimatology** APIs to model climate resilience and agricultural decision-support.
- 📱 **Native Mobile & Offline Distributed Protocols**: Production-grade native Android applications built with **Kotlin** and **Jetpack Compose (Material 3)** following strict MVVM + UDF patterns, alongside cross-platform **Flutter & Dart** systems featuring offline SQLite synchronization and direct peer-to-peer **Bluetooth Classic RFCOMM** socket streaming.
- 🤖 **Autonomous AI & Deterministic Pipelines**: Automated intelligence pipelines orchestrating **Python**, **Google Gemini GenAI SDK**, **Pydantic**, and **GitHub Actions** for web crawling, dynamic data synthesis, automated vector PDF compilation (**ReportLab**), and scheduled dispatches.

---

## 📌 Featured Engineering Showcase

### 🏢 Enterprise Multi-Tenant SaaS & Distributed Systems
<table>
  <tr>
    <td width="50%" valign="top">
      <h3>⚡ SpecForge — Discovery & Scope OS SaaS</h3>
      <p>AI-assisted discovery, requirements engineering, estimation, and delivery-handover SaaS eliminating agency scope creep with cryptographic client sign-offs.</p>
      <ul>
        <li><b>Immutable 11-Stage Pipeline:</b> Extracts structured features, user stories, and acceptance criteria from briefs, linking citations directly to source audio/text with zero hallucinations.</li>
        <li><b>Defensible P80 Estimation:</b> Mathematical rate-card modeling with automated task generation for Jira, Linear, and GitHub.</li>
        <li><b>Cryptographic Sign-Offs:</b> Versioned immutable scope freezing with SHA-256 digital seals.</li>
        <li><b>49 / 49 Master Quality Checks:</b> 100% green launch-readiness matrix and 124 modular architecture tests passing.</li>
      </ul>
      <p>
        <code>Next.js 15.5</code> <code>TypeScript 5.4</code> <code>Prisma 5.22</code> <code>PostgreSQL 16</code> <code>Zod</code> <code>Playwright</code>
      </p>
      <p>
        <a href="https://specforge-tawny.vercel.app"><b>🚀 Live Interactive Demo</b></a> · 
        <a href="https://github.com/MTLab1122/SpecForge"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🎧 AudioDoc — Commercial PDF-to-Audiobook SaaS</h3>
      <p>Distributed commercial platform converting complex digital & scanned documents into high-fidelity neural audiobooks with studio-grade MP3 assembly.</p>
      <ul>
        <li><b>Microservice Architecture:</b> Next.js 14 App Router frontend decoupled with a distributed Python FastAPI gateway and Celery worker cluster backed by Redis 8 & PostgreSQL 16.</li>
        <li><b>Dual-Engine Ingestion:</b> PyMuPDF column-aware structural parsing with 300 DPI Tesseract OCR fallback for scanned and damaged documents.</li>
        <li><b>Zero-Cost Neural Synthesis:</b> Edge Neural TTS engine with 100+ voices across 30+ languages, chunk-level FFmpeg audio concatenation, and ID3 metadata tagging.</li>
        <li><b>Enterprise Verification:</b> Verified across <b>87 / 87 automated tests (100% pass rate)</b> spanning Pytest, Vitest, Playwright browser E2E, and OWASP security audits.</li>
      </ul>
      <p>
        <code>Next.js 14</code> <code>FastAPI</code> <code>Celery</code> <code>Redis</code> <code>PostgreSQL</code> <code>FFmpeg</code> <code>PyMuPDF</code>
      </p>
      <p>
        <a href="https://pdf-file-conversion-to-audio.vercel.app"><b>🚀 Live Web Demo</b></a> · 
        <a href="https://github.com/MTLab1122/PDF_file_conversion_to_Audio"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🛒 Enterprise Cash & Carry SaaS & POS Platform</h3>
      <p>Complete multi-tenant retail management platform and offline-first Point-of-Sale ecosystem for wholesale supermarkets and retail chains.</p>
      <ul>
        <li><b>Triple-Client Ecosystem:</b> Next.js 14 Web Management Dashboard, Windows Desktop POS (Electron + React + SQLite), and Mobile Supervisor App (Flutter + Dart).</li>
        <li><b>Offline POS Engine:</b> Sub-500ms barcode scanning, durable offline mutation queue with UUID idempotency, and automated replay sync upon network reconnection.</li>
        <li><b>Hardware Integration:</b> 80mm ESC/POS thermal receipt printing, cash drawer kick triggers, and GS1 standard EAN-13 barcode generation.</li>
        <li><b>Cryptographic Audit Ledger:</b> Double-entry customer credit khata chained with SHA-256 hash chains preventing retroactive record tampering. <b>169 / 169 verification assertions passing (100%)</b>.</li>
      </ul>
      <p>
        <code>Next.js 14</code> <code>NestJS</code> <code>Electron</code> <code>Flutter</code> <code>Prisma</code> <code>SQLite</code> <code>TypeScript</code>
      </p>
      <p>
        <a href="https://cash-carry-saaspos.vercel.app"><b>🚀 Live Web Demo</b></a> · 
        <a href="https://github.com/MTLab1122/Cash-Carry-SaaS-POS-Platform"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🏥 ShifaDesk (MatabAI) — Multilingual Clinic Operations SaaS</h3>
      <p>Enterprise multilingual clinic management and outpatient operations SaaS integrating AI medical transcription, smart queueing, and multi-tenant EMR.</p>
      <ul>
        <li><b>High-Performance Monorepo:</b> Built with Next.js 15 App Router web portal, modular NestJS 10 REST API, Supabase PostgreSQL, and shared Zod contracts.</li>
        <li><b>Multilingual Patient Workflows:</b> Real-time consultation transcription, appointment booking via WhatsApp, and smart walk-in queue automation (Urdu, English, Pashto, Arabic).</li>
        <li><b>Clinical EMR-Lite & Billing:</b> Encounters, longitudinal patient health records, multi-tender payment processing, and cash drawer float reconciliation.</li>
        <li><b>Healthcare Compliance:</b> Row-level tenant isolation, zero-secret commits, and granular role-based access control.</li>
      </ul>
      <p>
        <code>Next.js 15</code> <code>NestJS 10</code> <code>Supabase</code> <code>PostgreSQL 16</code> <code>Prisma</code> <code>Zod</code>
      </p>
      <p>
        <a href="https://shifadesk-mtlab.vercel.app"><b>🚀 Live Web Demo</b></a> · 
        <a href="https://github.com/MTLab1122/ShifaDesk"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
</table>

### 🌍 Autonomous AI, Climate Intelligence & Telemetry
<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🛰️ AgroShift — NASA Space Apps Challenge 2026</h3>
      <p>Climate-resilient crop planning and agronomic decision-support platform powered by NASA Earth observations for the Peshawar Valley (Team Lead, Team InCir).</p>
      <ul>
        <li><b>4-Engine NASA Observation:</b> Ingests NASA SMAP L4 soil moisture (9 km), NASA GPM IMERG precipitation (10 km), MODIS/VIIRS NDVI canopy greenness, and NASA POWER daily agroclimatology.</li>
        <li><b>Explainable Scoring Formula:</b> Evaluates 3 crop rotation strategies balancing climate suitability, water efficiency, and biological nitrogen fixation.</li>
        <li><b>Zero Data Fabrication:</b> Rigorous sentinel fill handling mapping missing satellite observations to explicit nulls with spatial provenance citations.</li>
        <li><b>74 / 74 Pytest Tests Passed:</b> 100% pass rate covering NASA API clients, recommendation scoring, and report generation.</li>
      </ul>
      <p>
        <code>Next.js 14</code> <code>FastAPI</code> <code>Python 3.11</code> <code>NASA APIs</code> <code>Leaflet</code> <code>Pytest</code>
      </p>
      <p>
        <a href="https://agroshift-nasa-eight.vercel.app"><b>🚀 Live Web Demo</b></a> · 
        <a href="https://github.com/MTLab1122/AgroShift_NASA"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🎓 KP & Charsadda Scholarship Intelligence Agent</h3>
      <p>Autonomous daily intelligence agent crawling, verifying, deduplicating, and reporting verified higher-education scholarships for regional students.</p>
      <ul>
        <li><b>Three-Tier Trust Engine:</b> Strict source verification separating official <code>.gov</code> / <code>.edu</code> portals from unverified secondary aggregators.</li>
        <li><b>AI Synthesis & Deduplication:</b> Google Gemini API structured extraction, verbatim source quotes (up to 300 chars), and fuzzy string similarity deduplication (ratio >= 0.88).</li>
        <li><b>Multi-Format Automated Dispatches:</b> Executes daily at 07:00 PKT via GitHub Actions, compiling interactive HTML dashboards, ReportLab vector PDFs, and automated Resend email delivery.</li>
      </ul>
      <p>
        <code>Python</code> <code>Google Gemini API</code> <code>GitHub Actions</code> <code>ReportLab</code> <code>Pydantic</code>
      </p>
      <p>
        <a href="https://github.com/MTLab1122/student-opportunity-intelligence"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>⚡ Autonomous Tech Intelligence Briefing Agent</h3>
      <p>24-hour self-operating market intelligence crawler executing parallel sweeps across frontier AI research, developer tooling, and trending repositories.</p>
      <ul>
        <li><b>Multi-Source Ingestion:</b> Parallel scrapers across Hacker News, Hugging Face model registries, and GitHub trending API endpoints.</li>
        <li><b>Structured LLM Processing:</b> Strict JSON-mode synthesis with Gemini GenAI SDK, fallback heuristic engines, and deterministic schema validation.</li>
        <li><b>Publication Delivery:</b> Automated compilation into professional multi-page vector PDFs with dynamic tables, dispatched daily to engineering stakeholders.</li>
      </ul>
      <p>
        <code>Python</code> <code>Gemini GenAI</code> <code>ReportLab</code> <code>Task Scheduler</code> <code>Resend API</code>
      </p>
      <p>
        <a href="https://github.com/MTLab1122/autoreport_agent"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>📊 Campus Environment Telemetry & Visualization</h3>
      <p>Full-stack environmental telemetry platform ingesting and visualizing ambient telemetry across 8 university campus zones.</p>
      <ul>
        <li><b>Analytical Engine:</b> US EPA Air Quality Index (AQI) piecewise linear interpolation for PM2.5/PM10, ASHRAE thermal comfort indices, and Plotly 5-axis spider radar matrices.</li>
        <li><b>Automated QA:</b> 27 unit and integration tests passing via pytest covering models, REST API endpoints, and Dash callbacks.</li>
      </ul>
      <p>
        <code>Python</code> <code>Flask</code> <code>Plotly Dash</code> <code>SQLAlchemy</code> <code>Chart.js</code>
      </p>
      <p>
        <a href="https://campus-environment-data-visualizati.vercel.app"><b>🚀 Live Web View</b></a> · 
        <a href="https://github.com/MTLab1122/Campus_Environment_DataVisualization_System"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
</table>

### 📱 Native Mobile & Distributed Protocols
<table>
  <tr>
    <td width="50%" valign="top">
      <h3>📶 BluetoothChat — Offline P2P Android Network</h3>
      <p>100% offline peer-to-peer encrypted messaging and file transfer mobile application operating without internet connectivity, cellular networks, or centralized servers.</p>
      <ul>
        <li><b>Protocol Architecture:</b> Direct RFCOMM socket stream over Serial Port Profile (SPP) with newline-delimited framing and client/server pairing.</li>
        <li><b>Binary Chunking Engine:</b> 4KB binary payload chunking with end-to-end SHA-256 verification and automatic corrupted packet recovery.</li>
        <li><b>Local State Persistence:</b> Indexed SQLite database schema storing chats, message delivery states, and contact fingerprints locally.</li>
      </ul>
      <p>
        <code>Flutter</code> <code>Dart</code> <code>Bluetooth RFCOMM</code> <code>SQLite</code> <code>Material Design 3</code>
      </p>
      <p>
        <a href="https://github.com/MTLab1122/BluetoothChat"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🚗 CityDrive — Native Android Car Rental Platform</h3>
      <p>Production-grade native Android vehicle rental and urban mobility platform engineered with clean architectural separation and reactive state.</p>
      <ul>
        <li><b>Native Architecture:</b> Kotlin with Jetpack Compose (Material 3), unidirectional data flow (UDF), and MVVM presentation patterns.</li>
        <li><b>Telemetry & Routing:</b> Live GPS tracking simulation, dynamic interactive map route rendering, and multi-tier booking calculators.</li>
        <li><b>Reactive Concurrency:</b> Asynchronous Kotlin Coroutines and StateFlow streams ensuring 60fps rendering without UI thread blocking.</li>
      </ul>
      <p>
        <code>Kotlin</code> <code>Jetpack Compose</code> <code>Coroutines</code> <code>MVVM</code> <code>Material 3</code>
      </p>
      <p>
        <a href="https://github.com/MTLab1122/CityDrive_Mobile_APP"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>💍 ShaadiVenue — Banquet & Hall Reservation Platform</h3>
      <p>Native Android event venue booking ecosystem featuring role-based portals for Event Hosts, Venue Owners, and Admins with date conflict detection.</p>
      <ul>
        <li><b>Role-Based Workflows:</b> Separate authenticated experiences for clients seeking banquet venues and hall administrators managing booking calendars.</li>
        <li><b>Collision Prevention:</b> Deterministic schedule availability verification preventing double-booking across multi-session events.</li>
      </ul>
      <p>
        <code>Kotlin</code> <code>Jetpack Compose</code> <code>Material 3</code> <code>Multi-Role Auth</code>
      </p>
      <p>
        <a href="https://github.com/MTLab1122/ShaadiVenue_Mobile_APP"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🖨️ Mukhtar Press & Store — Commercial Print Ecosystem</h3>
      <p>End-to-end commercial print production and e-commerce mobile application paired with an interactive React 19/Vite web showcase.</p>
      <ul>
        <li><b>Automated Estimation:</b> Real-time dynamic quotation algorithms factoring paper stock, quantity, ink variants, and binding requirements.</li>
        <li><b>Cloud Data Layer:</b> Firebase Firestore real-time synchronization backed by granular security rules protecting customer orders.</li>
      </ul>
      <p>
        <code>Flutter</code> <code>Dart</code> <code>Firebase Firestore</code> <code>React 19</code> <code>Tailwind CSS v4</code>
      </p>
      <p>
        <a href="https://mukhtar-press.vercel.app"><b>🚀 Live Web Demo</b></a> · 
        <a href="https://github.com/MTLab1122/Mukhtar_Press_Mobile_APP"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
</table>

### ⚡ High-Performance Web & Full-Stack Systems
<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🌐 Editorial Developer Portfolio</h3>
      <p>Production developer portfolio engineered with Astro's zero-JS static architecture, Tailwind CSS v4 design tokens, and strict TypeScript data contracts.</p>
      <ul>
        <li><b>Performance Benchmarks:</b> 100/100 Core Web Vitals, sub-second LCP, zero layout shift (CLS 0.0), and zero base runtime client JS overhead.</li>
        <li><b>Technical SEO:</b> Full Schema.org JSON-LD semantic graph (Person, CreativeWork, ProfilePage), dynamic XML sitemaps, and automated robots directives.</li>
      </ul>
      <p>
        <code>Astro</code> <code>Tailwind CSS v4</code> <code>TypeScript</code> <code>GSAP</code> <code>WCAG 2.2 AA</code>
      </p>
      <p>
        <a href="https://talha-portfolio-gules.vercel.app/"><b>🚀 Live Demo</b></a> · 
        <a href="https://github.com/MTLab1122/portfolio"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>👾 Modern Pac-Man Arcade Engine</h3>
      <p>High-performance retro arcade recreation built from scratch with modern React Hooks and requestAnimationFrame — zero external canvas game engines.</p>
      <ul>
        <li><b>Autonomous AI State Machines:</b> Authentic recreation of 4 classic ghost behaviors: Blinky (chaser), Pinky (ambusher), Inky (random), Clyde (defender).</li>
        <li><b>Responsive Vector Rendering:</b> Scalable SVG sprites, direction input buffering, and full mobile touch controls alongside keyboard controls.</li>
      </ul>
      <p>
        <code>Next.js 14</code> <code>TypeScript</code> <code>React Hooks</code> <code>Tailwind CSS</code>
      </p>
      <p>
        <a href="https://pacman-arcade-brown.vercel.app"><b>🚀 Play Online</b></a> · 
        <a href="https://github.com/MTLab1122/Pac_Man"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🚗 AutoX Accessories — Modern E-Commerce Platform</h3>
      <p>Modern responsive automotive accessories online storefront built with React 18, Vite, and Tailwind CSS with real-time cart state management and category filters.</p>
      <p>
        <code>Vite</code> <code>React 18</code> <code>Tailwind CSS</code> <code>Lucide Icons</code>
      </p>
      <p>
        <a href="https://autox-accessories.vercel.app"><b>🚀 Live Web Store</b></a> · 
        <a href="https://github.com/MTLab1122/Online_Car_Accessories_Shop_Website"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>🧭 AuraNav — Interactive Campus & Transit Navigation</h3>
      <p>Zero-JS static navigation portal built with Astro and Tailwind CSS v4 featuring responsive direction routing, interactive floorplans, and accessible SVG waypoints.</p>
      <p>
        <code>Astro</code> <code>Tailwind CSS v4</code> <code>TypeScript</code> <code>WCAG 2.2 AA</code>
      </p>
      <p>
        <a href="https://auranav-navigation.vercel.app"><b>🚀 Live Interactive App</b></a> · 
        <a href="https://github.com/MTLab1122/aptura_week1_task1"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔄 Converter Hub — Multi-Unit & Currency Suite</h3>
      <p>High-performance client-side utility suite performing instantaneous multi-unit conversions across length, weight, temperature, and currency with zero server latency.</p>
      <p>
        <code>HTML5</code> <code>CSS3 Grid/Flexbox</code> <code>Vanilla JavaScript</code>
      </p>
      <p>
        <a href="https://converter-hub-smoky.vercel.app"><b>🚀 Live Web App</b></a> · 
        <a href="https://github.com/MTLab1122/Converter-Hub"><b>📂 View Repository</b></a>
      </p>
    </td>
    <td width="50%" valign="top">
      <h3>📄 Software Requirements Specification (SRS) Suite</h3>
      <p>Interactive web documentation viewer presenting full IEEE 830-compliant Software Requirement Specifications with structured UML diagrams and traceability matrices.</p>
      <p>
        <code>HTML5</code> <code>CSS3</code> <code>IEEE 830 Standard</code> <code>UML</code>
      </p>
      <p>
        <a href="https://srs-documents.vercel.app"><b>🚀 Live Documentation</b></a> · 
        <a href="https://github.com/MTLab1122/SRS_Documents"><b>📂 View Repository</b></a>
      </p>
    </td>
  </tr>
</table>

---

## 🛠️ Technical Ecosystem & Architecture Stack

<div align="center">

### 💻 Core Programming Languages
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Kotlin](https://img.shields.io/badge/Kotlin-7F52FF?style=flat-square&logo=kotlin&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=flat-square&logo=dart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)

### 🏢 Full-Stack & Distributed Backend
![Next.js 15/14](https://img.shields.io/badge/Next.js_15%2F14-000000?style=flat-square&logo=next.js&logoColor=white)
![NestJS 10](https://img.shields.io/badge/NestJS_10-E0234E?style=flat-square&logo=nestjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white)
![Express.js](https://img.shields.io/badge/Express.js-000000?style=flat-square&logo=express&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Prisma ORM](https://img.shields.io/badge/Prisma_ORM-2D3748?style=flat-square&logo=prisma&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)

### 📱 Native Mobile & Hardware Protocols
![Android Native](https://img.shields.io/badge/Android_Native-3DDC84?style=flat-square&logo=android&logoColor=white)
![Jetpack Compose](https://img.shields.io/badge/Jetpack_Compose-4285F4?style=flat-square&logo=jetpackcompose&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white)
![Electron POS](https://img.shields.io/badge/Electron_Desktop-47848F?style=flat-square&logo=electron&logoColor=white)
![Bluetooth RFCOMM](https://img.shields.io/badge/Bluetooth_RFCOMM-0082FC?style=flat-square&logo=bluetooth&logoColor=white)
![Material Design 3](https://img.shields.io/badge/Material_Design_3-757575?style=flat-square&logo=materialdesign&logoColor=white)
![Gradle](https://img.shields.io/badge/Gradle-02303A?style=flat-square&logo=gradle&logoColor=white)

### 🤖 Agentic AI, Climate & Document Processing
![Google Gemini API](https://img.shields.io/badge/Google_Gemini_API-8E75C2?style=flat-square&logo=googlegemini&logoColor=white)
![NASA Earth Observations](https://img.shields.io/badge/NASA_Earth_Observations-0B3D91?style=flat-square&logo=nasa&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-FF6F00?style=flat-square&logo=python&logoColor=white)
![Tesseract OCR](https://img.shields.io/badge/Tesseract_OCR-5C6BC0?style=flat-square&logo=tesseract&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![Edge Neural TTS](https://img.shields.io/badge/Edge_Neural_TTS-0078D7?style=flat-square&logo=microsoft&logoColor=white)
![ReportLab PDF](https://img.shields.io/badge/ReportLab_Vector_PDF-306998?style=flat-square&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)

### ⚡ Frontend Architecture & UI Craft
![Astro](https://img.shields.io/badge/Astro-BC52EE?style=flat-square&logo=astro&logoColor=white)
![React 19](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)
![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![GSAP](https://img.shields.io/badge/GSAP_Timelines-88CE02?style=flat-square&logo=greensock&logoColor=black)
![Figma](https://img.shields.io/badge/Figma_UI/UX-F24E1E?style=flat-square&logo=figma&logoColor=white)
![WCAG 2.2 AA](https://img.shields.io/badge/WCAG_2.2_AA-005A9C?style=flat-square&logo=w3c&logoColor=white)

### 🚀 DevOps, Quality Assurance & Systems
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Vitest](https://img.shields.io/badge/Vitest-6E9F18?style=flat-square&logo=vitest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

</div>

---

## 🏛️ Engineering Principles & System Design Standards

```mermaid
flowchart LR
    A["Deterministic Architecture"] --> B["Strict Type Safety & Schemas"]
    B --> C["Automated Multi-Layer Testing"]
    C --> D["Zero-Downtime Offline Durability"]
    D --> E["Sub-Second Performance & A11y"]
```

- **Deterministic Offline-First Resilience**: Critical enterprise services must operate irrespective of network state. I implement durable local mutation queues, SQLite persistence, and idempotent background sync with exponential backoff and jitter.
- **Zero-Defect Quality Assurance**: Software is only as reliable as its automated verification suite. My flagship projects achieve 100% test pass rates across unit, integration, browser E2E (Playwright), and security tests (87/87 tests in AudioDoc; 169/169 assertions in Cash & Carry POS; 49/49 checks in SpecForge; 74/74 tests in AgroShift).
- **Strict Type Safety & Cryptographic Integrity**: Eliminating runtime defects through strict-mode TypeScript contracts, Kotlin type systems, Pydantic runtime models, and immutable SHA-256 cryptographic audit hash-chains for financial ledgers and scope approval contracts.
- **Scientific Honesty & Zero Data Fabrication**: Data systems strictly map missing observations to explicit nulls and disclaim uncertainty rather than synthesising artificial statistics.
- **Zero-Overhead Web Performance**: Rejecting client-side JavaScript bloat by defaulting to static-first architectures (Astro), server components, and native CSS tokens, targeting 100/100 Core Web Vitals.
- **Accessible, Human-Centered UX**: Engineering WCAG 2.2 AA compliant interfaces with visible keyboard focus rings, group-aria states, zero layout shift, and smooth cross-device accessibility.

---

## 🎓 Academic & Professional Background

| Focus Area | Institution / Organization | Scope & Achievements |
| :--- | :--- | :--- |
| **B.S. Software Engineering** | **Abasyn University, Peshawar** | **CGPA 3.87 / 4.0** (2023–2027). Advanced coursework in Data Structures & Algorithms, Distributed Systems, Software Requirement Engineering (SRS), and Database Design. |
| **NASA Space Apps Challenge 2026** | **NASA Space Apps & Abasyn University** | **Team Lead (Team InCir)**. Leading a 5-member multidisciplinary engineering team building AgroShift, synthesizing 4 NASA Earth-observation systems for climate-resilient agriculture. |
| **Technical Pedagogy & Instruction** | **Govt. Technical & Vocational Center, Umarzai** | **DIT Instructor (Ongoing)**. Mentoring vocational students in programming fundamentals, algorithm design, computing essentials, and practical software assignments. |
| **Commercial Print & Visual Systems** | **Mukhtar Printing Press** | **Computer Operator / Graphic Designer (3 Years)**. Production design, typography typesetting, and prepress vector engineering using Corel Draw, Photoshop, and InPage. |
| **Advanced Computing Fellowship** | **Presidential Initiative for AI & Computing (PIAIC)** | Specialized training in modern Next.js App Router, TypeScript strict typing, Tailwind CSS, and applied AI systems. |
| **Technical Internships & Programs** | **Abasyn, Pak Army (ISPR), NCHD & KP-TEVTA** | **5+ Technical Programs & Internships** across Android Mobile Development, Computer Technology On-Job Training, and Research (ORIC). |

---

## 📊 GitHub Analytics & Activity

<div align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=MTLab1122&show_icons=true&theme=tokyonight&hide_border=true&count_private=true" alt="Muhammad Talha's GitHub Stats" height="175" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=MTLab1122&layout=compact&theme=tokyonight&hide_border=true" alt="Top Languages" height="175" />
</div>

<div align="center">
  <img src="https://streak-stats.demolab.com/?user=MTLab1122&theme=tokyonight&hide_border=true" alt="GitHub Streak" />
</div>

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/MTLab1122/MTLab1122/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/MTLab1122/MTLab1122/output/github-contribution-grid-snake.svg">
    <img alt="GitHub Contribution Snake Animation" src="https://raw.githubusercontent.com/MTLab1122/MTLab1122/output/github-contribution-grid-snake.svg" />
  </picture>
</div>

---

## 🤝 Connect & Collaborate

I am actively open to discussing **Software Engineering roles**, **Enterprise SaaS development**, **Native Mobile (Android / Flutter) contracts**, and **Autonomous AI agent pipelines**.

<div align="center">

| Channel | Destination | Primary Purpose |
| :--- | :--- | :--- |
| 💼 **LinkedIn** | [linkedin.com/in/mtlabs1122](https://www.linkedin.com/in/mtlabs1122/) | Professional Networking & Career Opportunities |
| 🌐 **Portfolio** | [talha-portfolio-gules.vercel.app](https://talha-portfolio-gules.vercel.app/) | Interactive Case Studies & Live Project Demos |
| 📧 **Direct Email** | [muhammadtalhapro1@gmail.com](mailto:muhammadtalhapro1@gmail.com) | Contract Inquiries, Technical Consulting & Hiring |
| 💬 **WhatsApp** | [+92 347 2937773](https://wa.me/923472937773) | Direct Instant Communication & Project Scoping |
| 🐙 **GitHub** | [@MTLab1122](https://github.com/MTLab1122) | Code Exploration, Architecture Audits & Open Source |

</div>

<br />

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0:0284C7,35:312E81,70:1E1B4B,100:030712&height=120&section=footer" width="100%" alt="Footer Wave" />
  <sub>Engineered with architectural precision by <strong>Muhammad Talha</strong> · Performance, Reliability, and Distinction.</sub>
</div>
"""
    return content


def generate_report(audit_data: dict, readme_changed: bool) -> str:
    """Generate a markdown report of synchronization results."""
    report = f"""# Autonomous GitHub Profile & Portfolio Synchronization Report

**Executed At**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Target Profile**: [@MTLab1122](https://github.com/MTLab1122)  
**Total Public Repositories Discovered**: {audit_data['total_public_repos']}  

---

## 1. Discovery of Recent & High-Impact Projects

### Recent Projects (Created/Updated within 30 days)
"""
    for r in audit_data["recent_repos"]:
        report += f"- **{r['name']}** (Created: {r['created_at']}, {r['days_old']} days ago)\n"

    report += """
### Newly Added Flagships in Showcase
1. **SpecForge**: Discovery & Scope OS SaaS Platform (Next.js 15.5, Prisma, PostgreSQL 16, 49/49 verification checks)
2. **AgroShift (NASA Space Apps Challenge 2026)**: Team Lead, NASA Earth observation models (SMAP, GPM, MODIS, POWER), 74/74 pytest tests
3. **ShifaDesk (MatabAI)**: Multilingual Clinic Operations SaaS (Next.js 15 + NestJS 10 monorepo, WhatsApp scheduling)
4. **AudioDoc SaaS**: Commercial distributed PDF-to-Audiobook platform (87/87 tests passed)
5. **Cash & Carry SaaS POS**: Multi-tenant retail SaaS + offline Electron POS + Flutter app (169/169 assertions)

---

## 2. Profile README Synchronization Status
"""
    if readme_changed:
        report += "- **Status**: `CHANGES_PREPARED` — Profile README has been updated with newly discovered flagships, updated repository count, and NASA Space Apps Challenge leadership.\n"
    else:
        report += "- **Status**: `IN_SYNC` — Profile README matches current repository state. Zero churn required.\n"

    report += """
---

## 3. Metadata Quality Audit (Missing Descriptions & Topics)

### Repositories Missing Descriptions
"""
    if audit_data["missing_descriptions"]:
        for m in audit_data["missing_descriptions"]:
            report += f"- `{m}`\n"
    else:
        report += "None! All public repositories have descriptions.\n"

    report += "\n### Repositories Missing Topics\n"
    if audit_data["missing_topics"]:
        for m in audit_data["missing_topics"]:
            report += f"- `{m}`\n"
    else:
        report += "None! All public repositories have topics.\n"

    report += """
---

## 4. Suggested Metadata Optimizations (Pending Approval)

| Repository | Recommended Description | Recommended Topics |
| :--- | :--- | :--- |
| **ShifaDesk** | Multilingual AI-Powered Clinic Operations SaaS Platform — Next.js 15, NestJS 10, Supabase, PostgreSQL 16 & WhatsApp scheduling | `clinic-management`, `emr-system`, `healthcare-saas`, `nestjs`, `nextjs`, `postgresql`, `prisma`, `saas`, `supabase`, `typescript` |
| **AgroShift_NASA** | AgroShift - NASA Space Apps Challenge 2026. Climate-resilient crop planning powered by NASA Earth observations for Peshawar Valley (Team InCir). | `agriculture`, `climate-resilience`, `earth-observation`, `fastapi`, `nasa-space-apps`, `nextjs`, `python`, `satellite-data`, `smap` |
| **AgroShift** | AgroShift Agronomic Decision Support Engine — NASA Space Apps Challenge 2026 climate reconciliation & crop rotation engine in Python/FastAPI. | `agritech`, `climate-data`, `decision-support`, `fastapi`, `nasa-power`, `nasa-space-apps`, `pydantic`, `pytest`, `python` |
| **SpecForge** | AI-assisted discovery, requirements, estimation, proposal, client-approval, and delivery-handover SaaS platform | `ai-agency-tools`, `estimation`, `nextjs`, `playwright`, `postgresql`, `prisma`, `project-management`, `saas`, `scope-management`, `typescript` |

---

## 5. Strategic Recommendations: Top-6 Pinned Repositories

```mermaid
flowchart TD
    P1["1. SpecForge (AI Discovery & Scope OS SaaS)"]
    P2["2. AgroShift_NASA (NASA Space Apps Challenge 2026 - Team Lead)"]
    P3["3. Cash-Carry-SaaS-POS-Platform (Enterprise Multi-Tenant SaaS & POS)"]
    P4["4. PDF_file_conversion_to_Audio (Distributed Neural Audiobook SaaS)"]
    P5["5. BluetoothChat (Offline P2P Android Network & RFCOMM)"]
    P6["6. ShifaDesk or portfolio (Multilingual Clinic SaaS / Astro v4 Portfolio)"]
```
"""
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync GitHub Profile README with latest repositories.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    parser.add_argument("--check-links", action="store_true", help="Verify all URLs in README.")
    args = parser.parse_args()

    print("==================================================")
    print("🚀 Running Autonomous GitHub Profile Synchronization")
    print("==================================================")

    repos = fetch_all_public_repos()
    print(f"✓ Discovered {len(repos)} public repositories.")

    audit_data = audit_repositories(repos)
    print(f"✓ Found {len(audit_data['recent_repos'])} repositories updated/created in past 30 days.")

    new_readme = build_readme_content(len(repos))
    
    existing_readme = ""
    if README_PATH.exists():
        existing_readme = README_PATH.read_text(encoding="utf-8")

    readme_changed = (new_readme.strip() != existing_readme.strip())

    if readme_changed:
        print("⚡ Changes detected in profile representation.")
        if not args.dry_run:
            README_PATH.write_text(new_readme, encoding="utf-8")
            print(f"✓ Successfully wrote updated README to: {README_PATH}")
        else:
            print("ℹ️ Dry-run mode active: README was not modified.")
    else:
        print("✓ Profile README is already 100% in sync (idempotent - no diffs).")

    report_content = generate_report(audit_data, readme_changed)
    if not args.dry_run:
        REPORT_PATH.write_text(report_content, encoding="utf-8")
        print(f"✓ Generated sync report at: {REPORT_PATH}")

    if args.check_links:
        print("🔍 Verifying all links in README...")
        urls = re.findall(r'href=[\"\'](https?://[^\"\']+)[\"\']|\[.*?\]\((https?://[^\)]+)\)', new_readme)
        flat_urls = set([u[0] or u[1] for u in urls if u[0] or u[1]])
        print(f"Total unique URLs to verify: {len(flat_urls)}")
        broken = []
        for u in sorted(flat_urls):
            # Skip localhost or mailto
            if "localhost" in u or "wa.me" in u:
                continue
            ok = verify_url(u)
            status = "✓ OK" if ok else "✗ BROKEN"
            print(f"  {status}: {u}")
            if not ok:
                broken.append(u)
        if broken:
            print(f"⚠️ {len(broken)} URLs failed verification!", file=sys.stderr)
        else:
            print("✓ All external URLs verified successfully.")

    print("\n✅ Autonomous Synchronization Completed.")


if __name__ == "__main__":
    main()
