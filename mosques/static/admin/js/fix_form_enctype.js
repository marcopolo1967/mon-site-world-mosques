// Force enctype sur tous les formulaires admin avec upload
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Vérifier si le formulaire a des champs fichier
        const fileInputs = form.querySelectorAll('input[type="file"]');
        if (fileInputs.length > 0) {
            form.setAttribute('enctype', 'multipart/form-data');
            console.log('✅ enctype ajouté à:', form.id || 'form');
        }
    });
});