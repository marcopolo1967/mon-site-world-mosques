document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('#header');
    if (!header) return;

    let badge = document.createElement('a');
    badge.id = 'proposition-badge';
    badge.href = '/admin/mosques/proposition/'; // Lien direct
    badge.style.display = 'none';
    header.appendChild(badge);

    function updateBadge() {
        fetch('/admin/mosques/api/pending-count/')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    let message = "";

                    if (data.count === 1) {
                        // Règle 1 : Nom de la mosquée si c'est la seule
                        message = `🔔 Mosquée : ${data.names[0]}`;
                    } else {
                        // Règle 2 : Chiffre si > 1
                        message = `🔔 ${data.count} PROPOSITIONS EN ATTENTE`;
                    }

                    badge.innerHTML = message;
                    badge.title = "Cliquez pour voir la liste : " + data.names.join(', ');
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            })
    }

    updateBadge();
    setInterval(updateBadge, 30000);
});