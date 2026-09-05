// JobScamScore Browser Extension - Background Service Worker (Manifest V3)

chrome.runtime.onInstalled.addListener(() => {
  console.log('[JobScamScore] Threat Detection Extension installed successfully.');
});
