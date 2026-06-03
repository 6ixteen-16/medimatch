// MediMatch — main.js

// Dropdown toggle
document.addEventListener('click', function(e) {
  const dropdown = e.target.closest('.dropdown');
  document.querySelectorAll('.dropdown.open').forEach(d => {
    if (d !== dropdown) d.classList.remove('open');
  });
  if (dropdown) dropdown.classList.toggle('open');
});

// Mobile hamburger
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
}

// Alert dismiss
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('alert-close')) {
    e.target.closest('.alert').remove();
  }
});

// Role selector (register page)
document.querySelectorAll('.role-card').forEach(card => {
  card.addEventListener('click', function() {
    document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
    this.classList.add('selected');
    const roleInput = document.getElementById('id_role');
    if (roleInput) roleInput.value = this.dataset.role;
  });
});

// SOS urgency selector
document.querySelectorAll('.urgency-option').forEach(opt => {
  opt.addEventListener('click', function() {
    document.querySelectorAll('.urgency-option').forEach(o => o.classList.remove('selected'));
    this.classList.add('selected');
    const input = document.getElementById('id_urgency');
    if (input) input.value = this.dataset.urgency;
  });
});

// Blood type grid selector (SOS create)
document.querySelectorAll('.bt-option').forEach(opt => {
  opt.addEventListener('click', function() {
    document.querySelectorAll('.bt-option').forEach(o => o.classList.remove('selected'));
    this.classList.add('selected');
    const input = document.getElementById('id_blood_type_needed');
    if (input) input.value = this.dataset.bt;
  });
});

// Profile photo preview
const photoInput = document.getElementById('id_profile_photo');
const photoPreview = document.getElementById('photo-preview');
if (photoInput && photoPreview) {
  photoInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => { photoPreview.src = e.target.result; photoPreview.style.display = 'block'; };
      reader.readAsDataURL(file);
    }
  });
}

// Transport toggle
const transportToggle = document.getElementById('id_needs_transport');
const transportDetails = document.getElementById('transport-details');
if (transportToggle && transportDetails) {
  function toggleTransport() {
    transportDetails.style.display = transportToggle.checked ? 'block' : 'none';
  }
  transportToggle.addEventListener('change', toggleTransport);
  toggleTransport();
}

// Auto-dismiss success alerts after 5s
setTimeout(() => {
  document.querySelectorAll('.alert-success').forEach(a => {
    a.style.transition = 'opacity 0.5s';
    a.style.opacity = '0';
    setTimeout(() => a.remove(), 500);
  });
}, 5000);
