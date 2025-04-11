document.addEventListener('DOMContentLoaded', () => {
    const categoryButtons = document.querySelectorAll('.category-button');
    const categoryContentDivs = document.querySelectorAll('.category-content');
    const projectDisplay = document.querySelector('.project-display'); // Container for delegation

    // --- Hauptkategorie-Filter ---
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedCategory = button.getAttribute('data-category');
            const targetContentId = `content-${selectedCategory}`;

            // Buttons aktivieren/deaktivieren
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Content-Divs ein-/ausblenden
            categoryContentDivs.forEach(div => {
                if (div.id === targetContentId) {
                    div.style.display = 'block'; // Ziel-Div anzeigen
                } else {
                    div.style.display = 'none'; // Alle anderen ausblenden
                }
            });

            // Wichtig: Beim Wechsel der Hauptkategorie alle Unterkategorie-Bilder ausblenden
            // und ggf. aktive Unterkategorie-Buttons zurücksetzen
            const targetContentDiv = document.getElementById(targetContentId);
            if (targetContentDiv) {
                const subcategoryFigures = targetContentDiv.querySelectorAll('.subcategory-display figure');
                subcategoryFigures.forEach(figure => figure.style.display = 'none');

                const subcategoryButtons = targetContentDiv.querySelectorAll('.subcategory-button');
                subcategoryButtons.forEach(subBtn => subBtn.classList.remove('active'));
            }
        });
    });

    // --- Unterkategorie- und Projekt-Filter (Event Delegation) ---
    if (projectDisplay) {
        projectDisplay.addEventListener('click', (event) => {
            const target = event.target;

            // --- Klick auf Unterkategorie-Button ---
            if (target.matches('.subcategory-button')) {
                const clickedSubButton = target;
                const selectedSubcategory = clickedSubButton.getAttribute('data-subcategory');
                const targetSubContentId = `content-${selectedSubcategory}`;

                // Finde das übergeordnete category-content
                const parentCategoryContent = clickedSubButton.closest('.category-content');
                if (!parentCategoryContent) return;

                // Alle Unterkategorie-Buttons und -Inhalte innerhalb dieser Hauptkategorie holen
                const currentSubButtons = parentCategoryContent.querySelectorAll('.subcategory-button');
                const currentSubContents = parentCategoryContent.querySelectorAll('.subcategory-content');

                // Aktiven Status für Unterkategorie-Buttons setzen
                currentSubButtons.forEach(btn => btn.classList.remove('active'));
                clickedSubButton.classList.add('active');

                // Unterkategorie-Inhalte ein-/ausblenden
                currentSubContents.forEach(contentDiv => {
                    if (contentDiv.id === targetSubContentId) {
                        contentDiv.style.display = 'block'; // Ziel-Div anzeigen
                        // Beim Anzeigen einer Unterkategorie: Projektfilter zurücksetzen
                        const projectButtons = contentDiv.querySelectorAll('.project-button');
                        const projectFigures = contentDiv.querySelectorAll('.project-gallery-display figure');
                        projectButtons.forEach(btn => btn.classList.remove('active'));
                        projectFigures.forEach(fig => fig.style.display = 'none'); // Alle Projektbilder ausblenden
                    } else {
                        contentDiv.style.display = 'none'; // Andere ausblenden
                    }
                });
            }

            // --- Klick auf Projekt-Button ---
            else if (target.matches('.project-button')) {
                const clickedProjectButton = target;
                const selectedProject = clickedProjectButton.getAttribute('data-project');
                    console.log(`[DEBUG] Project button clicked: ${selectedProject}`);

                // Finde das übergeordnete subcategory-content
                const parentSubcategoryContent = clickedProjectButton.closest('.subcategory-content');
                if (!parentSubcategoryContent) return;

                // Finde die Projekt-Buttons und -Bilder innerhalb dieses Unterkategorie-Inhalts
                const currentProjectButtons = parentSubcategoryContent.querySelectorAll('.project-button');
                const galleryDisplay = parentSubcategoryContent.querySelector('.project-gallery-display');
                if (!galleryDisplay) return;
                const currentProjectFigures = galleryDisplay.querySelectorAll('figure');
                const currentProjectDescriptions = parentSubcategoryContent.querySelectorAll('.project-description'); // NEU: Beschreibungen finden

                    console.log(`[DEBUG] Found ${currentProjectFigures.length} figures and ${currentProjectDescriptions.length} descriptions.`);
                // Aktiven Status für Projekt-Buttons setzen
                currentProjectButtons.forEach(btn => btn.classList.remove('active'));
                clickedProjectButton.classList.add('active');

                // Projekt-Bilder filtern
                currentProjectFigures.forEach(figure => {
                    const figureProject = figure.getAttribute('data-project');
                    if (figureProject === selectedProject) {
                        figure.style.display = ''; // Passende anzeigen (CSS kümmert sich um Layout)
                    } else {
                        console.log(`[DEBUG] Figure data-project="${figureProject}": Showing`);
                        figure.style.display = 'none'; // Nicht passende ausblenden
                    }
                        console.log(`[DEBUG] Figure data-project="${figureProject}": Hiding`);
                });

                // NEU: Projekt-Beschreibungen filtern
                currentProjectDescriptions.forEach(description => {
                    const descriptionProject = description.getAttribute('data-project');
                    if (descriptionProject === selectedProject) {
                        description.style.display = 'block'; // Passende anzeigen
                    } else {
                        console.log(`[DEBUG] Description data-project="${descriptionProject}": Showing`);
                        description.style.display = 'none'; // Nicht passende ausblenden
                    }
                        console.log(`[DEBUG] Description data-project="${descriptionProject}": Hiding`);
                });
            }
        });
    }

    // Initialisierung:
    // Das HTML sorgt bereits dafür, dass das richtige category-content-Div angezeigt wird
    // und die figures darin initial ausgeblendet sind.
    // Es ist keine explizite Filterung beim Laden mehr nötig.
    // Der alte Initialisierungscode wurde entfernt.

});