document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    
    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', () => {
            adminSidebar.classList.toggle('show');
        });
    }

    // 2. Alert Toast Disappear
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // 3. Dynamic Timeline Editors (Education & Experience JSON handler)
    const eduContainer = document.getElementById('education-fields-container');
    const expContainer = document.getElementById('experience-fields-container');
    const eduHidden = document.getElementById('education_hidden'); // Textarea containing JSON
    const expHidden = document.getElementById('experience_hidden'); // Textarea containing JSON

    if (eduContainer && eduHidden) {
        setupJSONTimelineEditor(eduContainer, eduHidden, 'education');
    }

    if (expContainer && expHidden) {
        setupJSONTimelineEditor(expContainer, expHidden, 'experience');
    }

    function setupJSONTimelineEditor(container, hiddenTextarea, type) {
        let items = [];
        try {
            items = JSON.parse(hiddenTextarea.value || '[]');
        } catch (e) {
            items = [];
        }

        // Render initial items
        renderTimelineItems(container, items, type);

        // Add item button click handler
        const addBtn = document.getElementById(`add-${type}-btn`);
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                if (type === 'education') {
                    items.push({ institution: '', degree: '', years: '', details: '' });
                } else {
                    items.push({ company: '', role: '', years: '', details: '' });
                }
                renderTimelineItems(container, items, type);
                serializeAndSave(hiddenTextarea, items);
            });
        }
    }

    function renderTimelineItems(container, items, type) {
        container.innerHTML = '';
        if (items.length === 0) {
            container.innerHTML = `<p class="text-muted small">No items added yet. Click the add button to begin.</p>`;
            return;
        }

        items.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'timeline-entry-editor shadow-sm border p-3 mb-3 rounded position-relative';
            
            if (type === 'education') {
                card.innerHTML = `
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <label class="small fw-bold">Institution</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="institution" value="${item.institution || ''}">
                        </div>
                        <div class="col-md-6 mb-2">
                            <label class="small fw-bold">Degree / Certification</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="degree" value="${item.degree || ''}">
                        </div>
                        <div class="col-md-4 mb-2">
                            <label class="small fw-bold">Years (e.g. 2018 - 2022)</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="years" value="${item.years || ''}">
                        </div>
                        <div class="col-md-8 mb-2">
                            <label class="small fw-bold">Details</label>
                            <textarea class="form-control form-control-sm item-input" data-field="details" rows="2">${item.details || ''}</textarea>
                        </div>
                    </div>
                    <button type="button" class="btn btn-danger btn-sm delete-entry-btn position-absolute top-0 end-0 m-2" style="padding: 2px 8px;">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                `;
            } else {
                card.innerHTML = `
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <label class="small fw-bold">Company</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="company" value="${item.company || ''}">
                        </div>
                        <div class="col-md-6 mb-2">
                            <label class="small fw-bold">Role / Job Title</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="role" value="${item.role || ''}">
                        </div>
                        <div class="col-md-4 mb-2">
                            <label class="small fw-bold">Years (e.g. 2022 - Present)</label>
                            <input type="text" class="form-control form-control-sm item-input" data-field="years" value="${item.years || ''}">
                        </div>
                        <div class="col-md-8 mb-2">
                            <label class="small fw-bold">Responsibilities / Achievements</label>
                            <textarea class="form-control form-control-sm item-input" data-field="details" rows="2">${item.details || ''}</textarea>
                        </div>
                    </div>
                    <button type="button" class="btn btn-danger btn-sm delete-entry-btn position-absolute top-0 end-0 m-2" style="padding: 2px 8px;">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                `;
            }

            // Hook input edits
            const inputs = card.querySelectorAll('.item-input');
            inputs.forEach(input => {
                input.addEventListener('input', (e) => {
                    const field = e.target.getAttribute('data-field');
                    items[index][field] = e.target.value;
                    const hiddenTextarea = type === 'education' ? 
                        document.getElementById('education_hidden') : 
                        document.getElementById('experience_hidden');
                    serializeAndSave(hiddenTextarea, items);
                });
            });

            // Hook delete button
            const delBtn = card.querySelector('.delete-entry-btn');
            delBtn.addEventListener('click', () => {
                items.splice(index, 1);
                renderTimelineItems(container, items, type);
                const hiddenTextarea = type === 'education' ? 
                    document.getElementById('education_hidden') : 
                    document.getElementById('experience_hidden');
                serializeAndSave(hiddenTextarea, items);
            });

            container.appendChild(card);
        });
    }

    function serializeAndSave(hiddenTextarea, items) {
        hiddenTextarea.value = JSON.stringify(items);
    }
    
    // 4. File uploads validation and preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Size validation (Max 16MB)
                const maxSize = 16 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('File size exceeds the 16MB limit.');
                    e.target.value = '';
                    return;
                }
                
                // Show simple text notification or file details
                const parent = e.target.closest('.mb-3');
                if (parent) {
                    let helperText = parent.querySelector('.file-preview-helper');
                    if (!helperText) {
                        helperText = document.createElement('div');
                        helperText.className = 'file-preview-helper text-success small mt-1';
                        parent.appendChild(helperText);
                    }
                    helperText.innerHTML = `<i class="fas fa-file-alt"></i> Selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
                }
            }
        });
    });
});
