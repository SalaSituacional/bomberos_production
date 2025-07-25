
const weatherInfoDiv = document.getElementById("weather-info");


function getFormattedDateTime() {
    const now = new Date();

    const optionsTime = { hour: '2-digit', minute: '2-digit', hour12: true };
    let timeString = now.toLocaleTimeString('es-ES', optionsTime);

    timeString = timeString.replace('a. m.', 'AM').replace('p. m.', 'PM');

    // Formato de fecha (ej. 22 de Septiembre del 2025)
    const optionsDate = { day: 'numeric', month: 'long', year: 'numeric' };
    const dateString = now.toLocaleDateString('es-ES', optionsDate);

    // Combinar: 12:27 AM - 22 de Septiembre del 2025
    return `${timeString} - ${dateString}`;
}

// --- Nueva lógica para iniciar automáticamente el clima ---
function initWeatherApp() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                fetchWeatherData(lat, lon);
            }
        );
    }
}

async function fetchWeatherData(lat, lon) {
    const proxyUrl = `/api/weather-proxy/?lat=${lat}&lon=${lon}`;

    try {
        const response = await fetch(proxyUrl);
        
        const data = await response.json();
        displayWeather(data);
    } catch (error) {
    }
}

// --- FUNCIÓN PRINCIPAL DE VISUALIZACIÓN AHORA CON FECHA Y HORA ---
function displayWeather(data) {
    if (data.main && data.weather && data.name) {
        const temp = data.main.temp;
        const feelsLike = data.main.feels_like;
        const city = data.name;
        const humidity = data.main.humidity;
        const windSpeed = data.wind.speed; // m/s

        // Obtiene la fecha y hora actual formateada
        const currentDateTime = getFormattedDateTime(); 

        document.getElementById("fecha-clima").textContent = currentDateTime
        document.getElementById("ubicacion-clima").textContent = city
        document.getElementById("temperatura-clima").textContent = `${temp}°C`
        document.getElementById("sensacion-clima").textContent = `${feelsLike}°C`
        document.getElementById("humedad-clima").textContent = `${humidity}%`
        document.getElementById("viento-clima").textContent = `${windSpeed}m/s`
    }
}

// --- Inicio de la aplicación al cargar el DOM ---
document.addEventListener('DOMContentLoaded', () => {
    initWeatherApp();

    setInterval(() => {
        const dateTimeElement = document.getElementById('fecha-clima');
        if (dateTimeElement) {
            dateTimeElement.textContent = getFormattedDateTime();
        }
    }, 1000); 
});