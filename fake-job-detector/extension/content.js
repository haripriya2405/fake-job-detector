// JobScamScore Browser Extension - Content Script
// Extracts job details from active web pages (LinkedIn, Indeed, Glassdoor, Greenhouse, Lever, Workday)

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'GET_JOB_DETAILS') {
    const jobData = extractJobDataFromDOM();
    sendResponse(jobData);
  }
  return true;
});

function extractJobDataFromDOM() {
  const host = window.location.hostname.toLowerCase();
  let title = '';
  let company = '';
  let text = '';

  // 1. LinkedIn Job Details
  if (host.includes('linkedin.com')) {
    const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title') ||
                    document.querySelector('.jobs-unified-top-card__job-title') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('.job-details-jobs-unified-top-card__company-name') ||
                      document.querySelector('.jobs-unified-top-card__company-name');
    const descEl = document.querySelector('.jobs-description__content') ||
                   document.querySelector('.jobs-box__html-content') ||
                   document.querySelector('#job-details');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 5000);
  }
  // 2. Indeed Job Details
  else if (host.includes('indeed.com')) {
    const titleEl = document.querySelector('[data-testid="jobsearch-JobInfoHeader-title"]') ||
                    document.querySelector('.jobsearch-JobInfoHeader-title') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('[data-testid="inlineHeader-companyName"]') ||
                      document.querySelector('.jobsearch-InlineCompanyRating-companyHeader');
    const descEl = document.querySelector('#jobDescriptionText') || document.querySelector('.jobsearch-jobDescriptionText');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 5000);
  }
  // 3. Greenhouse ATS
  else if (host.includes('greenhouse.io')) {
    const titleEl = document.querySelector('.app-title') || document.querySelector('h1');
    const companyEl = document.querySelector('.company-name') || document.querySelector('.header__logo-text');
    const descEl = document.querySelector('#content') || document.querySelector('.body');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 5000);
  }
  // 4. Lever ATS
  else if (host.includes('lever.co')) {
    const titleEl = document.querySelector('.posting-headline h2') || document.querySelector('h2');
    const companyEl = document.querySelector('.main-header-logo img') || document.querySelector('.posting-headline');
    const descEl = document.querySelector('.section-wrapper') || document.querySelector('.posting-sections');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? (companyEl.getAttribute('alt') || '') : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 5000);
  }
  // 5. General / Workday / Other Fallback
  else {
    const h1 = document.querySelector('h1');
    title = h1 ? h1.innerText.trim() : document.title;
    text = document.body ? document.body.innerText.slice(0, 5000) : '';
  }

  return {
    title: title || document.title || 'Job Listing',
    company: company || 'Employer',
    text: text || document.body?.innerText?.slice(0, 3000) || '',
    url: window.location.href
  };
}
