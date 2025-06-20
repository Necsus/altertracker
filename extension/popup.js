function showStep(stepId) {
  ['step1', 'step2', 'step3', 'success', 'error', 'loading'].forEach(id => {
    document.getElementById(id).classList.add('hidden');
  });
  document.getElementById(stepId).classList.remove('hidden');
}

function getTabIdByUrlPart(urlPart, callback) {
  chrome.tabs.query({}, function (tabs) {
    const tab = tabs.find(t => t.url && t.url.includes(urlPart));
    if (tab) {
      callback(tab.id);
    } else {
      alert("Onglet du site non trouvé !");
    }
  });
}

const getAccessTokenFromAPI = async () => {
  try {
    const response = await fetch("https://www.altered.gg/api/auth/session", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      showStep('step2');
      console.log('Err03 : Invalid API response ! Please reload the page and try again.');
    }

    const data = await response.json();

    if (!data.accessToken) {
      showStep('step2');
      console.log("Err04 : Please login into your account !");
    }

    return data.accessToken;
  } catch (error) {
    showStep('step2');
    console.error(error);
    throw error;
  }
};

const getCollection = async (token, page = 1, collection = []) => {
  console.log(`https://api.altered.gg/cards?cardType%5B%5D=CHARACTER&collection=true&rarity%5B%5D=UNIQUE&itemsPerPage=36&page=${page}&locale=fr-fr`);
  const postRes = await fetch(`https://api.altered.gg/cards?cardType%5B%5D=CHARACTER&collection=true&rarity%5B%5D=UNIQUE&itemsPerPage=36&page=${page}&locale=fr-fr`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (!postRes.ok) throw new Error("Erreur lors de l'import.");
  const result = await postRes.json();
  result['hydra:member'].forEach(card => {
    collection.push(card['reference']);
  });
  if (result['hydra:totalItems'] > collection.length) {
    return getCollection(token, page + 1, collection);
  }
  return collection;
};

document.addEventListener('DOMContentLoaded', () => {
  chrome.runtime.sendMessage({ action: 'getStep' }, async (response) => {
    const step = response.step || 1;
    if (step === 1) {
      showStep('loading');
      getTabIdByUrlPart('altertracker.com', function (tabIdOfSite1) {
        chrome.scripting.executeScript({
          target: { tabId: tabIdOfSite1 },
          func: () => localStorage.getItem('access_token')
        }, (results) => {
          const alterTrackerToken = results[0].result;
          console.log(alterTrackerToken);
          if (alterTrackerToken) {
            chrome.runtime.sendMessage({ action: 'setAlterTrackerToken', token: alterTrackerToken }, () => {
              showStep('step2');
            });
          } else {
            showStep('step1');
          }
        });
      });
    }
    else if (step === 2) {
      showStep('loading');
      chrome.runtime.sendMessage({ action: 'setAlteredToken', token: await getAccessTokenFromAPI() }, () => {
        showStep('step3');
      });
    } else if (step === 3) {
      showStep('step3');
    }
  });

  // Step 1 : Récupération du token AlterTracker
  document.getElementById('go-altertracker').onclick = () => {
    chrome.tabs.create({ url: 'https://altertracker.com/login', active: true });
  };

  // Step 2 : Récupération du token Altered
  document.getElementById('go-altered').onclick = () => {
    chrome.tabs.create({ url: 'https://www.altered.gg', active: true });
  };

  // Step 3 : Import de la collection
  document.getElementById('start-import').onclick = async () => {
    showStep('loading');
    chrome.runtime.sendMessage({ action: 'getAlteredToken' }, async (response) => {
      console.log(response.token);
      const collection = await getCollection(response.token);
      // Stocke la collection dans le background
      chrome.runtime.sendMessage({ action: 'setCollection', collection }, () => {
        // Lance l'import côté background
        chrome.runtime.sendMessage({ action: 'importCollection' }, (importRes) => {
          if (importRes && importRes.success) {
            showStep('success');
          } else {
            showStep('error');
            console.log(importRes.error || "Erreur lors de l'import.");
          }
        });
      });
    });
  };
});