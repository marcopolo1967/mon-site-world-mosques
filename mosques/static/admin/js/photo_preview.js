// static/admin/js/photo_preview.js
document.addEventListener('DOMContentLoaded', function() {
    // 1. Trouver tous les inputs file dans l'admin
    const fileInputs = document.querySelectorAll('input[type="file"][multiple]');

    fileInputs.forEach(input => {
        // Vérifier si c'est un champ de photos (par nom ou ID)
        if (input.name.includes('photo') || input.id.includes('photo') ||
            input.name === 'bulk_photos' || input.name === 'photos') {

            console.log('✅ Initialisation miniatures pour:', input.name);
            initPhotoPreview(input);
        }
    });

    function initPhotoPreview(input) {
        // Trouver la ligne du champ
        const fieldRow = input.closest('.form-row');
        if (!fieldRow) return;

        // Créer le conteneur de prévisualisation
        const previewContainer = document.createElement('div');
        previewContainer.className = 'photo-preview-admin';
        previewContainer.style.marginTop = '15px';

        // Insérer après le champ
        fieldRow.appendChild(previewContainer);

        // Fonction de mise à jour
        function updatePreviews() {
            previewContainer.innerHTML = '';

            if (!input.files || input.files.length === 0) {
                previewContainer.innerHTML = `
                    <div class="empty-preview">
                        <i class="bi bi-images"></i>
                        <span>Aucune photo sélectionnée. Les miniatures apparaîtront ici.</span>
                    </div>
                `;
                return;
            }

            // Créer une grille de miniatures
            const grid = document.createElement('div');
            grid.className = 'photo-grid-admin';

            Array.from(input.files).forEach((file, index) => {
                if (!file.type.startsWith('image/')) return;

                const reader = new FileReader();

                reader.onload = function(e) {
                    const previewItem = document.createElement('div');
                    previewItem.className = 'photo-item-admin';

                    previewItem.innerHTML = `
                        <div class="photo-thumbnail">
                            <img src="${e.target.result}" alt="${file.name}">
                            <button type="button" class="remove-thumbnail" data-index="${index}">
                                &times;
                            </button>
                        </div>
                        <div class="photo-info">
                            <span class="photo-name">${file.name.length > 20 ? file.name.substring(0, 18) + '...' : file.name}</span>
                            <span class="photo-size">${(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                    `;

                    grid.appendChild(previewItem);

                    // Bouton de suppression
                    previewItem.querySelector('.remove-thumbnail').addEventListener('click', function() {
                        removeFile(index, input);
                    });
                };

                reader.readAsDataURL(file);
            });

            previewContainer.appendChild(grid);
        }

        // Fonction pour supprimer un fichier
        function removeFile(index, inputElement) {
            const newFiles = new DataTransfer();
            Array.from(inputElement.files).forEach((file, i) => {
                if (i !== index) {
                    newFiles.items.add(file);
                }
            });
            inputElement.files = newFiles.files;
            updatePreviews();
        }

        // Initialiser
        input.addEventListener('change', updatePreviews);
        updatePreviews();
    }
});