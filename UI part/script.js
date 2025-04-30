function fetchCurrentLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(position => {
        document.getElementById('latitude').value = position.coords.latitude;
        document.getElementById('longitude').value = position.coords.longitude;
      }, error => {
        alert('Unable to retrieve location. Please allow location access.');
      });
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  }

  function searchSpots() {
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;
    const radius = document.getElementById('radius').value;
    const category = document.getElementById('category').value;

    // // Simulated API call for recommendations
    // const sampleRecommendations = [
    //   { name: "Central Park", category: "parks" }
    // ];

    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '<h3>Recommendations</h3><ul>' +
      sampleRecommendations.map(rec => `<li>${rec.name} (${rec.category})</li>`).join('') +
      '</ul>';
  }