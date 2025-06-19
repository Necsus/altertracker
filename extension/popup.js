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
      throw new Error('Err03 : Invalid API response ! Please reload the page and try again.');
    }

    const data = await response.json();

    if (!data.accessToken) {
      throw new Error("Err04 : Please login into your account !");
    }

    return data.accessToken;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const getCollection = async (token, page) => {
  const collection = [];
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
    page++; // Passer à la page suivante
    fetchPage(); // Récursivité pour récupérer la page suivante
  }
  return collection;
}


document.getElementById('step2').addEventListener('click', async () => {
  getTabIdByUrlPart('altertracker.com', function (tabIdOfSite1) {
    try {
      chrome.scripting.executeScript({
        target: { tabId: tabIdOfSite1 },
        func: () => localStorage.getItem('access_token')
      }, (results) => {
        const alterTrackerToken = results[0].result;
        (async () => {
          const accessToken = await getAccessTokenFromAPI();

          await fetchCollectionPage(accessToken);

          const postRes = await fetch('https://altertracker.com/user/collection', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${alterTrackerToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(collection)
          });

          if (!postRes.ok) throw new Error("Erreur lors de l'import.");

          const result = await postRes.json();
          document.getElementById('success').classList.remove('hidden');
          document.getElementById('collection-link').href = result.collectionUrl ?? 'https://altertracker.com/my-collection';
        })();

      });
    }
    catch (err) {
      alert("Erreur pendant l'import : " + err.message);
    }
  });
});