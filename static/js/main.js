// SkillBridge JavaScript Utilities

document.addEventListener('DOMContentLoaded', function() {
  // Auto-dismiss alert messages after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });

  // Dynamic Radio toggle for Skill Addition (Existing vs Custom New Skill)
  const radioExisting = document.getElementById('id_add_type_0');
  const radioNew = document.getElementById('id_add_type_1');
  const existingSection = document.getElementById('existing-skill-section');
  const newSection = document.getElementById('new-skill-section');

  function toggleSkillSections() {
    if (radioExisting && radioNew && existingSection && newSection) {
      if (radioExisting.checked) {
        existingSection.style.display = 'block';
        newSection.style.display = 'none';
      } else {
        existingSection.style.display = 'none';
        newSection.style.display = 'block';
      }
    }
  }

  if (radioExisting && radioNew) {
    radioExisting.addEventListener('change', toggleSkillSections);
    radioNew.addEventListener('change', toggleSkillSections);
    toggleSkillSections(); // Initial state check
  }
});
