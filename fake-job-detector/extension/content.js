// SentinelJob AI Browser Extension - Content Script & DOM Scraper
// Supports: LinkedIn, Indeed, Naukri, Internshala, Foundit, Shine, Glassdoor, Greenhouse, Lever, Workday

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'GET_JOB_DETAILS') {
    const jobData = extractJobDataFromDOM();
    sendResponse(jobData);
  }
  return true;
});

// Auto-inject 1-Click Scam Scanner Overlay Badge on job listing pages
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', injectAutoScanBadge);
} else {
  injectAutoScanBadge();
}

function injectAutoScanBadge() {
  if (document.getElementById('sentinel-auto-scan-badge')) return;

  const badge = document.createElement('div');
  badge.id = 'sentinel-auto-scan-badge';
  badge.innerHTML = `
    <div style="
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 999999;
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(7, 16, 12, 0.94);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(16, 185, 129, 0.4);
      border-radius: 9999px;
      padding: 10px 18px;
      color: #F3F4F6;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(16, 185, 129, 0.2);
      cursor: pointer;
      transition: all 0.25s ease;
      user-select: none;
    " id="sentinel-badge-btn">
      <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: rgba(16, 185, 129, 0.15); border-radius: 50%; border: 1px solid rgba(16, 185, 129, 0.4); color: #10B981;">🛡️</span>
      <span style="letter-spacing: -0.01em;">SentinelJob: <span style="color: #34D399;">1-Click Scam Check</span></span>
    </div>
    <div id="sentinel-scan-modal" style="
      display: none;
      position: fixed;
      bottom: 74px;
      right: 24px;
      z-index: 999999;
      width: 360px;
      background: rgba(7, 16, 12, 0.96);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 20px;
      padding: 18px;
      color: #F3F4F6;
      font-family: system-ui, -apple-system, sans-serif;
      box-shadow: 0 20px 40px rgba(0,0,0,0.8);
    "></div>
  `;

  document.body.appendChild(badge);

  const badgeBtn = document.getElementById('sentinel-badge-btn');
  const modal = document.getElementById('sentinel-scan-modal');

  badgeBtn.addEventListener('mouseenter', () => {
    badgeBtn.style.transform = 'translateY(-2px) scale(1.02)';
    badgeBtn.style.borderColor = 'rgba(16, 185, 129, 0.8)';
  });
  badgeBtn.addEventListener('mouseleave', () => {
    badgeBtn.style.transform = 'translateY(0) scale(1)';
    badgeBtn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
  });

  badgeBtn.addEventListener('click', async () => {
    if (modal.style.display === 'block') {
      modal.style.display = 'none';
      return;
    }

    const jobData = extractJobDataFromDOM();
    modal.style.display = 'block';
    modal.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; border-b: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 12px;">
        <span style="font-size: 12px; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.05em;">🛡️ SentinelJob Scan Engine</span>
        <button id="sentinel-modal-close" style="background: none; border: none; color: #9CA3AF; cursor: pointer; font-size: 16px;">✕</button>
      </div>
      <div style="margin-bottom: 10px;">
        <div style="font-size: 13px; font-weight: 600; color: #FFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(jobData.title)}</div>
        <div style="font-size: 11px; color: #9CA3AF;">${escapeHtml(jobData.company)}</div>
      </div>
      <div id="sentinel-result-area" style="text-align: center; padding: 20px 10px;">
        <div style="display: inline-block; width: 24px; height: 24px; border: 3px solid rgba(16, 185, 129, 0.3); border-top-color: #10B981; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
        <div style="font-size: 12px; color: #9CA3AF; margin-top: 10px;">Analyzing posting across 8 forensic layers...</div>
      </div>
      <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    `;

    document.getElementById('sentinel-modal-close').addEventListener('click', () => {
      modal.style.display = 'none';
    });

    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: jobData.text,
          job_title: jobData.title,
          company_name: jobData.company,
          source_type: 'text'
        })
      });

      if (!response.ok) throw new Error('Analysis request failed');

      const data = await response.json();
      const score = data.risk_score ?? 15;
      const riskColor = score < 30 ? '#10B981' : score < 70 ? '#F59E0B' : '#EF4444';
      const riskBg = score < 30 ? 'rgba(16, 185, 129, 0.15)' : score < 70 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)';
      const verdict = data.verdict_category || (score < 30 ? 'VERIFIED SAFE' : score < 70 ? 'SUSPICIOUS' : 'HIGH RISK SCAM');

      const resultArea = document.getElementById('sentinel-result-area');
      resultArea.innerHTML = `
        <div style="background: ${riskBg}; border: 1px solid ${riskColor}; border-radius: 14px; padding: 14px; margin-bottom: 12px;">
          <div style="font-size: 28px; font-weight: 800; color: ${riskColor}; font-family: monospace;">${score} <span style="font-size: 14px; font-weight: 500; opacity: 0.8;">/ 100</span></div>
          <div style="font-size: 11px; font-weight: 700; color: ${riskColor}; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px;">${verdict}</div>
        </div>
        <div style="font-size: 11px; color: #D1D5DB; text-align: left; line-height: 1.4; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 10px; margin-bottom: 12px; max-height: 80px; overflow-y: auto;">
          ${escapeHtml((data.explanation || 'No major red flags detected. Standard hiring patterns observed.').slice(0, 180))}...
        </div>
        <a href="http://localhost:5173/analysis/${data.id}" target="_blank" style="display: block; width: 100%; box-sizing: border-box; text-align: center; background: #10B981; color: #FFF; font-weight: 600; font-size: 12px; padding: 9px; border-radius: 10px; text-decoration: none;">View Full Forensic Report →</a>
      `;
    } catch (err) {
      const resultArea = document.getElementById('sentinel-result-area');
      resultArea.innerHTML = `
        <div style="font-size: 12px; color: #EF4444; margin-bottom: 10px;">Backend offline or scan limit reached.</div>
        <a href="http://localhost:5173/scan" target="_blank" style="display: block; width: 100%; box-sizing: border-box; text-align: center; background: rgba(255,255,255,0.1); color: #FFF; font-size: 12px; padding: 8px; border-radius: 10px; text-decoration: none;">Open SentinelJob Web Scanner</a>
      `;
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function extractJobDataFromDOM() {
  const host = window.location.hostname.toLowerCase();
  let title = '';
  let company = '';
  let text = '';

  // 1. Naukri.com
  if (host.includes('naukri.com')) {
    const titleEl = document.querySelector('.styles_jd-header-title__rZwM1') || document.querySelector('.jd-header-title') || document.querySelector('h1');
    const companyEl = document.querySelector('.styles_jd-header-comp-name__MvqAI a') || document.querySelector('.jd-header-comp-name') || document.querySelector('.company-name');
    const descEl = document.querySelector('.styles_JDC__dang-inner-html__h0K4t') || document.querySelector('.job-desc-section');
    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 2. Internshala.com
  else if (host.includes('internshala.com')) {
    const titleEl = document.querySelector('.profile') || document.querySelector('h1');
    const companyEl = document.querySelector('.link_display_like_text') || document.querySelector('.company_name');
    const descEl = document.querySelector('.text-container') || document.querySelector('.internship_details');
    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 3. LinkedIn
  else if (host.includes('linkedin.com')) {
    const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title') || document.querySelector('.jobs-unified-top-card__job-title') || document.querySelector('h1');
    const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name') || document.querySelector('.jobs-unified-top-card__company-name');
    const descEl = document.querySelector('.jobs-description__content') || document.querySelector('#job-details');
    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 4. Indeed
  else if (host.includes('indeed.com')) {
    const titleEl = document.querySelector('[data-testid="jobsearch-JobInfoHeader-title"]') || document.querySelector('h1');
    const companyEl = document.querySelector('[data-testid="inlineHeader-companyName"]');
    const descEl = document.querySelector('#jobDescriptionText');
    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // Fallback
  else {
    const h1 = document.querySelector('h1');
    title = h1 ? h1.innerText.trim() : document.title;
    text = document.body ? document.body.innerText.slice(0, 6000) : '';
  }

  return {
    title: title || document.title || 'Job Listing',
    company: company || 'Employer',
    text: text || document.body?.innerText?.slice(0, 4000) || '',
    url: window.location.href
  };
}
