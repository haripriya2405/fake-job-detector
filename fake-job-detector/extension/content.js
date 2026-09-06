// SentinelJob AI Browser Extension - Content Script
// Extracts job details across LinkedIn, Indeed, Glassdoor, ZipRecruiter, Handshake, Greenhouse, Lever, Workday, Dice

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
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
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
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 3. ZipRecruiter
  else if (host.includes('ziprecruiter.com')) {
    const titleEl = document.querySelector('.job_title') || document.querySelector('h1');
    const companyEl = document.querySelector('.hiring_company_text') || document.querySelector('.company_name');
    const descEl = document.querySelector('.jobDescriptionSection') || document.querySelector('.job_description');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 4. Glassdoor
  else if (host.includes('glassdoor.com')) {
    const titleEl = document.querySelector('[data-test="job-title"]') || document.querySelector('h1');
    const companyEl = document.querySelector('[data-test="employer-name"]') || document.querySelector('.EmployerProfile_employerName');
    const descEl = document.querySelector('.JobDetails_jobDescription') || document.querySelector('#JobDescriptionContainer');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 5. Handshake
  else if (host.includes('joinhandshake.com')) {
    const titleEl = document.querySelector('[data-hook="job-title"]') || document.querySelector('h1');
    const companyEl = document.querySelector('[data-hook="employer-name"]');
    const descEl = document.querySelector('[data-hook="job-description"]') || document.querySelector('.style__description');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 6. Greenhouse ATS
  else if (host.includes('greenhouse.io')) {
    const titleEl = document.querySelector('.app-title') || document.querySelector('h1');
    const companyEl = document.querySelector('.company-name') || document.querySelector('.header__logo-text');
    const descEl = document.querySelector('#content') || document.querySelector('.body');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 7. Lever ATS
  else if (host.includes('lever.co')) {
    const titleEl = document.querySelector('.posting-headline h2') || document.querySelector('h2');
    const companyEl = document.querySelector('.main-header-logo img') || document.querySelector('.posting-headline');
    const descEl = document.querySelector('.section-wrapper') || document.querySelector('.posting-sections');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? (companyEl.getAttribute('alt') || '') : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 8. General / Fallback
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
