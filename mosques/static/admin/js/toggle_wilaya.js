// static/admin/js/toggle_wilaya.js
document.addEventListener('DOMContentLoaded', function() {
    // 1. On cible les champs par leurs IDs générés par Django
    const countryField = document.querySelector('#id_country_link');
    // On cible la ligne entière de la Wilaya (le conteneur div)
    const wilayaRow = document.querySelector('.field-wilaya');

    function checkCountry() {
        if (!countryField || !wilayaRow) return;

        const selectedText = countryField.options[countryField.selectedIndex].text.trim();

        // Affiche la Wilaya uniquement si le pays sélectionné contient "Algérie"
        if (selectedText.includes("Algérie") || selectedText.includes("Algerie")) {
            wilayaRow.style.display = 'block';
        } else {
            wilayaRow.style.display = 'none';
        }
    }

    // Écouter les changements sur le champ Pays
    if (countryField) {
        countryField.addEventListener('change', checkCountry);
        // Exécuter une fois au chargement pour les fiches existantes
        checkCountry();
    }
});
