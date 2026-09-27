const GA_MEASUREMENT_ID = "G-C05BBNRKXV";

const banner = document.getElementById("cookie-banner");
const aceptar = document.getElementById("aceptar-analytics");
const rechazar = document.getElementById("rechazar-analytics");
const modificar = document.getElementById("modificar-preferencias");

const CLAVE_CONSENTIMIENTO = "zstars_analytics_consent";

function cargarGoogleAnalytics() {
    if (document.getElementById("ga4-script")) {
        return;
    }

    const script = document.createElement("script");
    script.id = "ga4-script";
    script.async = true;
    script.src =
        `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;

    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];

    function gtag() {
        dataLayer.push(arguments);
    }

    window.gtag = gtag;

    gtag("js", new Date());
    gtag("config", GA_MEASUREMENT_ID);
}

if (banner && aceptar && rechazar) {
    const preferencia = localStorage.getItem(CLAVE_CONSENTIMIENTO);

    if (preferencia === null) {
        banner.hidden = false;
    }

    if (preferencia === "accepted") {
        cargarGoogleAnalytics();
    }

    aceptar.addEventListener("click", () => {
        localStorage.setItem(
            CLAVE_CONSENTIMIENTO,
            "accepted"
        );

        banner.hidden = true;

        cargarGoogleAnalytics();
    });

    rechazar.addEventListener("click", () => {
        localStorage.setItem(
            CLAVE_CONSENTIMIENTO,
            "rejected"
        );

        banner.hidden = true;
    });

    if (modificar) {
        modificar.addEventListener("click", () => {
            banner.hidden = false;
        });
    }
}