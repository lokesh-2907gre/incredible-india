const landing = document.querySelector('#landing');
const citiesPage = document.querySelector('#cities');
const spotPage = document.querySelector('#spot');
const cityGrid = document.querySelector('#cityGrid');
const citySearch = document.querySelector('#citySearch');

function show(page) {
  [landing, citiesPage, spotPage].forEach(x => x.classList.add('hidden'));
  page.classList.remove('hidden');
  window.scrollTo(0, 0);
}

function openSpotDetails(place) {
  if (!place) return;

  // Header Details
  document.querySelector('#spotCategory').textContent = place.category || 'Heritage';
  document.querySelector('#spotState').textContent = place.state || 'India';
  document.querySelector('#spotCity').textContent = place.city === 'Delhi' ? 'IIIT-Delhi' : place.city;
  document.querySelector('#spotMonument').textContent = place.monument || '';
  
  // Hero Image & Story
  const heroImg = document.querySelector('#spotHeroImage');
  heroImg.src = place.image;
  heroImg.alt = `${place.monument}, ${place.city}`;
  document.querySelector('#spotText').textContent = place.hiddenSpot;

  // Travel Guide Info Grid
  document.querySelector('#spotBestTime').textContent = place.bestTime || 'October to March';
  document.querySelector('#spotTimings').textContent = place.timingsEntry || 'Open Daily · Free Exploration';
  document.querySelector('#spotTransit').textContent = place.howToReach || 'Connected via Road, Rail & Airport';
  // Top 3 Must-Visit Places Grid
  const mustVisitContainer = document.querySelector('#spotMustVisit');
  let spots = [];
  if (place.mustVisit && place.mustVisit.includes('|')) {
    spots = place.mustVisit.split('|').map(s => s.trim()).filter(Boolean);
  } else if (place.mustVisit) {
    spots = [place.mustVisit];
  } else {
    spots = [
      `Historic Citadel & Heritage Landmarks of ${place.city}`,
      `Scenic Valley & Panoramic Sunset Viewpoint`,
      `Old Town Cultural Bazaar & Sacred Trail`
    ];
  }

  spots = spots.slice(0, 3);
  mustVisitContainer.innerHTML = spots.map((spot, i) => `
    <div class="must-visit-card">
      <span class="must-visit-num">0${i + 1} MUST-VISIT</span>
      <p class="must-visit-text">${escapeHtml(spot)}</p>
    </div>
  `).join('');

  // Google Maps Live Link
  const query = encodeURIComponent(`${place.monument} ${place.city} ${place.state}`);
  document.querySelector('#mapsLink').href = `https://www.google.com/maps/search/?api=1&query=${query}`;

  // Wishlist Button Logic
  const wishlistBtn = document.querySelector('#wishlistBtn');
  let wishlist = JSON.parse(localStorage.getItem('india_wishlist') || '[]');
  const isSaved = wishlist.includes(place.city);
  wishlistBtn.textContent = isSaved ? '❤️ Saved to Wishlist' : '🤍 Save to Wishlist';
  wishlistBtn.classList.toggle('saved', isSaved);

  wishlistBtn.onclick = () => {
    wishlist = JSON.parse(localStorage.getItem('india_wishlist') || '[]');
    if (wishlist.includes(place.city)) {
      wishlist = wishlist.filter(c => c !== place.city);
      wishlistBtn.textContent = '🤍 Save to Wishlist';
      wishlistBtn.classList.remove('saved');
    } else {
      wishlist.push(place.city);
      wishlistBtn.textContent = '❤️ Saved to Wishlist';
      wishlistBtn.classList.add('saved');
    }
    localStorage.setItem('india_wishlist', JSON.stringify(wishlist));
  };

  // Special IIIT-Delhi Campus Showcase
  const isDelhi = place.city === 'Delhi';
  document.querySelector('#iiitGallery').classList.toggle('show', isDelhi);
  document.querySelector('#iiitCopy').classList.toggle('show', isDelhi);
  document.querySelector('#placementStats').classList.toggle('show', isDelhi);
  document.querySelector('#statSource').classList.toggle('show', isDelhi);

  show(spotPage);
}

document.querySelector('#startExploring').addEventListener('click', () => show(citiesPage));
document.querySelector('#homeButton').addEventListener('click', () => show(landing));
document.querySelector('#citiesButton').addEventListener('click', () => show(citiesPage));

citySearch.addEventListener('input', e => renderCities(e.target.value));
citySearch.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    e.preventDefault();
    if (autoSearchTimer) clearTimeout(autoSearchTimer);
    autoDiscoverLocation(e.target.value);
  }
});

cityGrid.addEventListener('click', event => {
  const card = event.target.closest('.card');
  if (!card || card.classList.contains('card-discovering')) return;
  const place = cities[card.dataset.index];
  openSpotDetails(place);
});
