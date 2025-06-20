let alterTrackerToken = null;
let alteredToken = null;
let collection = [];
let step = 1;

// Ecoute les messages de la popup ou d'autres scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getStep') {
    sendResponse({ step: step });
  }

  if (request.action === 'setAlterTrackerToken') {
    alterTrackerToken = request.token;
    step = 2;
    sendResponse({ success: true });
  }

  if (request.action === 'getAlterTrackerToken') {
    sendResponse({ token: alterTrackerToken });
  }

  if (request.action === 'setAlteredToken') {
    alteredToken = request.token;
    step = 3;
    sendResponse({ success: true });
  }

  if (request.action === 'getAlteredToken') {
    sendResponse({ token: alteredToken });
  }

  if (request.action === 'setCollection') {
    collection = request.collection;
    sendResponse({ success: true });
  }

  if (request.action === 'getCollection') {
    sendResponse({ collection });
  }

  if (request.action === 'importCollection') {
    fetch('https://altertracker.com/api/user/collection', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${alterTrackerToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ collection })
    })
      .then(res => res.json())
      .then(data => sendResponse({ success: true, data }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    // Indique qu'on répondra de façon asynchrone
    return true;
  }
});