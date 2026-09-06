// SentinelJob AI Browser Extension - Content Script
// Extracts job details across Indian & Global job portals:
// (Naukri, Internshala, Foundit/Monster, Shine, Apna, LinkedIn, Indeed, Glassdoor, ZipRecruiter, Greenhouse, Lever, Workday)

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

  // 🇮🇳 1. Naukri.com
  if (host.includes('naukri.com')) {
    const titleEl = document.querySelector('.styles_jd-header-title__rZwM1') ||
                    document.querySelector('.jd-header-title') ||
                    document.querySelector('h1.title') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('.styles_jd-header-comp-name__MvqAI a') ||
                      document.querySelector('.jd-header-comp-name') ||
                      document.querySelector('.company-name');
    const descEl = document.querySelector('.styles_JDC__dang-inner-html__h0K4t') ||
                   document.querySelector('.job-desc-section') ||
                   document.querySelector('.dang-inner-html');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🇮🇳 2. Internshala.com
  else if (host.includes('internshala.com')) {
    const titleEl = document.querySelector('.profile') ||
                    document.querySelector('.heading_4_5') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('.link_display_like_text') ||
                      document.querySelector('.company_name');
    const descEl = document.querySelector('.text-container') ||
                   document.querySelector('.internship_details');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🇮🇳 3. Foundit.in (formerly Monster India)
  else if (host.includes('foundit.in') || host.includes('monsterindia.com')) {
    const titleEl = document.querySelector('.jobTitle') ||
                    document.querySelector('.header__title') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('.companyName') ||
                      document.querySelector('.header__company');
    const descEl = document.querySelector('.jobDesc') ||
                   document.querySelector('.job-description');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🇮🇳 4. Shine.com
  else if (host.includes('shine.com')) {
    const titleEl = document.querySelector('.JobDetailWidget_jobCard_title__sK__y') ||
                    document.querySelector('.job-title') ||
                    document.querySelector('h1');
    const companyEl = document.querySelector('.JobDetailWidget_jobCard_company__r_rFp') ||
                      document.querySelector('.company-name');
    const descEl = document.querySelector('.JobDetailWidget_jobDetail__r_1lK') ||
                   document.querySelector('.job-description');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🇮🇳 5. Apna.co
  else if (host.includes('apna.co')) {
    const titleEl = document.querySelector('h1') || document.querySelector('.job-title');
    const companyEl = document.querySelector('.company-name') || document.querySelector('h2');
    const descEl = document.querySelector('.job-description') || document.querySelector('.details-container');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🌐 6. LinkedIn Job Details
  else if (host.includes('linkedin.com')) {
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
  // 🌐 7. Indeed Job Details
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
  // 🌐 8. Glassdoor
  else if (host.includes('glassdoor.com')) {
    const titleEl = document.querySelector('[data-test="job-title"]') || document.querySelector('h1');
    const companyEl = document.querySelector('[data-test="employer-name"]') || document.querySelector('.EmployerProfile_employerName');
    const descEl = document.querySelector('.JobDetails_jobDescription') || document.querySelector('#JobDescriptionContainer');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🌐 9. Greenhouse ATS
  else if (host.includes('greenhouse.io')) {
    const titleEl = document.querySelector('.app-title') || document.querySelector('h1');
    const companyEl = document.querySelector('.company-name') || document.querySelector('.header__logo-text');
    const descEl = document.querySelector('#content') || document.querySelector('.body');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? companyEl.innerText.trim() : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🌐 10. Lever ATS
  else if (host.includes('lever.co')) {
    const titleEl = document.querySelector('.posting-headline h2') || document.querySelector('h2');
    const companyEl = document.querySelector('.main-header-logo img') || document.querySelector('.posting-headline');
    const descEl = document.querySelector('.section-wrapper') || document.querySelector('.posting-sections');

    title = titleEl ? titleEl.innerText.trim() : '';
    company = companyEl ? (companyEl.getAttribute('alt') || '') : '';
    text = descEl ? descEl.innerText.trim() : document.body.innerText.slice(0, 6000);
  }
  // 🌐 11. General / Fallback
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
