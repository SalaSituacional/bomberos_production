// Información de estaciones
const stations = {
  0: {
    address:
      "Cuartel Central, Coronel (B) Justo Pastor Daza P Av. 19 de Abril. 📞(0276-3534344)",
    map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d494.150335348621!2d-72.21435923777214!3d7.768319283748523!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e666cbf9c23cba1%3A0xb510c881c0b32597!2sCuerpo%20de%20Bomberos%20de%20San%20Crist%C3%B3bal!5e0!3m2!1ses-419!2sus!4v1731684840657!5m2!1ses-419!2sus",
  },
  1: {
    address: "El terminal: DTGdo (F) Jose Luis Buitrago. 📞(0276-3410633)",
    map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d494.17427373401506!2d-72.23660161060488!3d7.747946626524347!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e6614aa78b16275%3A0x70d3838611fe538c!2sSud%20Estaci%C3%B3n%20De%20Bomberos%20El%20Terminal!5e0!3m2!1ses-419!2sus!4v1731687969643!5m2!1ses-419!2sus",
  },
  2: {
    address: "La Ermita, Sgto.Aydte(F) Baltazar Augusto Echeverria. 📞(0276-3465393)",
    map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d494.1504257466089!2d-72.23608734557061!3d7.768242450824334!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e666ca09a65eecb%3A0x92f3175dbe55559a!2sSud%20Estacion%20La%20Ermita%20Bomberos!5e0!3m2!1ses-419!2sve!4v1731945492800!5m2!1ses-419!2sve",
  },
  3: {
    address: "Pueblo Nuevo, Mayor (B) Bernardo Daza P. 📞(0276-3532160)",
    map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d932.7767617208882!2d-72.20323729881532!3d7.792975119706162!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e666c584446a3ab%3A0x6f41bcb0610c598c!2sSub%20Estaci%C3%B3n%20De%20Bomberos%20Paramillo!5e0!3m2!1ses-419!2sve!4v1731946167660!5m2!1ses-419!2sve",
  },
};

// Elementos DOM
const select = document.getElementById("stationSelect");
const addressSpan = document.getElementById("stationAddress");
const mapIframe = document.getElementById("mapIframe");
mapIframe.src =
  "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d494.150335348621!2d-72.21435923777214!3d7.768319283748523!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e666cbf9c23cba1%3A0xb510c881c0b32597!2sCuerpo%20de%20Bomberos%20de%20San%20Crist%C3%B3bal!5e0!3m2!1ses-419!2sus!4v1731684840657!5m2!1ses-419!2sus";
addressSpan.textContent =
  "Cuartel Central, Coronel (B) Justo Pastor Daza Av. 19 de Abril. 📞(0276-3534344)";

// Evento para cambiar de estación
select.addEventListener("change", (event) => {
  const stationId = event.target.value;
  if (stations[stationId]) {
    const { address, map } = stations[stationId];
    addressSpan.textContent = address;
    mapIframe.src = map;
  }
});
