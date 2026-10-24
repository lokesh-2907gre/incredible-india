let cities = [];
let autoSearchTimer = null;
let isDiscovering = false;

// Fetch destinations dynamically from Python + MySQL
async function loadCities() {
  try {
    const res = await fetch('/api/cities');
    const data = await res.json();
    // Only load items with valid images
    cities = data.filter(x => x.image && x.image.trim() !== '');
    renderCities();
  } catch (error) {
    console.error('Failed to load cities from backend:', error);
  }
}

loadCities();

function renderCities(query = '') {
  const match = query.toLowerCase().trim();
  
  // Filter destinations matching query and having an image
  const visible = cities.filter(x => 
    x.image && x.image.trim() !== '' &&
    `${x.city} ${x.state} ${x.monument} ${x.category || ''}`.toLowerCase().includes(match)
  );
  
  if (visible.length > 0) {
    clearTimeout(autoSearchTimer);
    cityGrid.innerHTML = visible.map(x => `
      <article class="card" data-index="${cities.indexOf(x)}">
        <img src="${x.image}" alt="${x.monument}, ${x.city}" loading="lazy" onerror="handleImageError(this)">
        <div class="card-info">
          <small>${x.category ? x.category.toUpperCase() + ' · ' : ''}${x.monument}</small>
          <h3>${x.city}</h3>
        </div>
      </article>
    `).join('');
  } else if (match.length >= 2) {
    // Show animated discovering card directly under search bar
    cityGrid.innerHTML = `
      <article class="card card-discovering">
        <div class="discovering-spinner"></div>
        <div class="card-info">
          <small>Searching across India...</small>
          <h3>Discovering ${escapeHtml(query)}</h3>
        </div>
      </article>
    `;

    // Automatically search location across India after brief pause
    clearTimeout(autoSearchTimer);
    autoSearchTimer = setTimeout(() => {
      autoDiscoverLocation(query);
    }, 600);
  } else {
    cityGrid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:#8a6d4b;padding:30px 0;">No matching city found.</p>';
  }
}

function handleImageError(img) {
  // If an image URL fails to load in browser, remove the card from view
  const card = img.closest('.card');
  if (card) {
    card.remove();
  }
}

function escapeHtml(text) {
  return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function autoDiscoverLocation(query) {
  const q = (query || document.querySelector('#citySearch').value).trim();
  if (!q || isDiscovering) return;

  isDiscovering = true;
  try {
    const res = await fetch('/api/discover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q })
    });

    const data = await res.json();
    if (data.destination && data.destination.image) {
      const dest = data.destination;
      const existingIdx = cities.findIndex(c => c.city.toLowerCase() === dest.city.toLowerCase());
      if (existingIdx !== -1) {
        cities[existingIdx] = dest;
      } else {
        // Place newly discovered card right at the top
        cities.unshift(dest);
      }

      // Re-render and show the new card immediately under the search bar
      const visible = cities.filter(x => 
        x.image && x.image.trim() !== '' &&
        `${x.city} ${x.state} ${x.monument} ${x.category || ''}`.toLowerCase().includes(q.toLowerCase())
      );
      
      const toShow = visible.length ? visible : [dest];
      cityGrid.innerHTML = toShow.map(x => `
        <article class="card" data-index="${cities.indexOf(x)}">
          <img src="${x.image}" alt="${x.monument}, ${x.city}" loading="lazy" onerror="handleImageError(this)">
          <div class="card-info">
            <small>${x.category ? x.category.toUpperCase() + ' · ' : ''}${x.monument}</small>
            <h3>${x.city}</h3>
          </div>
        </article>
      `).join('');
    } else {
      cityGrid.innerHTML = `
        <p style="grid-column:1/-1;text-align:center;color:#8a6d4b;padding:30px 0;">
          No secret trails found for "${escapeHtml(q)}". Try searching another town or landmark.
        </p>
      `;
    }
  } catch (err) {
    console.error('Discovery error:', err);
    cityGrid.innerHTML = `
      <p style="grid-column:1/-1;text-align:center;color:#8a6d4b;padding:30px 0;">
        Could not explore "${escapeHtml(q)}". Please try again.
      </p>
    `;
  } finally {
    isDiscovering = false;
  }
}
