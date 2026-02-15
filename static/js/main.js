
document.addEventListener("DOMContentLoaded", () => {
  function setUser(u){ localStorage.setItem("traffic_user", JSON.stringify(u)); }
  function getUser(){ try{ return JSON.parse(localStorage.getItem("traffic_user")); } catch(e){ return null; } }
  function logout(){ localStorage.removeItem("traffic_user"); window.location="index.html"; }

  const uForm = document.getElementById("loginUserForm");
  if(uForm){ uForm.addEventListener("submit", (e) => { e.preventDefault(); const u=document.getElementById("u_user").value.trim(); const p=document.getElementById("u_pass").value; if(u==="user" && p==="user123"){ setUser({name:u,role:"user"}); window.location="user-dashboard.html"; } else { document.getElementById("u_msg").textContent="Invalid credentials"; } }); }

  const aForm = document.getElementById("loginAdminForm");
  if(aForm){ aForm.addEventListener("submit", (e) => { e.preventDefault(); const u=document.getElementById("a_user").value.trim(); const p=document.getElementById("a_pass").value; if(u==="admin" && p==="admin123"){ setUser({name:u,role:"admin"}); window.location="admin-dashboard.html"; } else { document.getElementById("a_msg").textContent="Invalid credentials"; } }); }

  const u = getUser();
  if(u){ const userLabel = document.getElementById("userLabel") || document.getElementById("adminLabel"); if(userLabel) userLabel.textContent = u.name; }

  document.querySelectorAll(".logoutBtn").forEach(btn => {
    btn.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  // upload demo
  const uploadForm = document.getElementById("uploadForm");
  if(uploadForm){ uploadForm.addEventListener("submit",(e)=>{ e.preventDefault(); alert("Demo upload captured. Connect to backend to persist & analyze."); uploadForm.reset(); }); }

  // sample complaints listing
  const compWrap = document.getElementById("complaintsList");
  if(compWrap){
    const demo = [{id:1,user:"Ravi",type:"No Helmet",loc:"Sector 12, Delhi",time:"2025-10-22 08:37"},{id:2,user:"Ujjwal",type:"Triple Riding",loc:"NH9, Ghaziabad",time:"2025-10-21 15:12"}];
    demo.forEach(d => {
      const div = document.createElement("div"); div.className="card card-glass mb-3 p-3";
      div.innerHTML = `<div class="d-flex justify-content-between"><div><strong>${d.user}</strong><div class="small text-muted">${d.time} • ${d.loc}</div><div class="mt-2 text-danger">${d.type}</div></div><div><button class="btn btn-ti" onclick="alert('Review ${d.id} - backend should return media & plate')">Review</button></div></div>`;
      compWrap.appendChild(div);
    });
  }
});



/* --- Camera & FIR enhancements --- */
let _cameraStream = null;
function openCameraModal() {
  const modal = document.getElementById('cameraModal');
  if(!modal) return alert('Camera modal not found.');
  modal.style.display = 'block';
  const video = document.getElementById('camVideo');
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('Camera API not supported in this browser.');
    return;
  }
  navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then(stream => {
      _cameraStream = stream;
      video.srcObject = stream;
      video.play();
    }).catch(err => {
      console.error(err);
      alert('Could not access camera: ' + err.message);
    });
}

function capturePhotoFromCamera() {
  const video = document.getElementById('camVideo');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
  // set preview and put into FIR form input
  const imgPreview = document.getElementById('cameraPreview');
  if(imgPreview) imgPreview.src = dataUrl;
  const hidden = document.getElementById('fir_camera_image');
  if(hidden) hidden.value = dataUrl;
  closeCameraModal();
}

function closeCameraModal() {
  const modal = document.getElementById('cameraModal');
  if(modal) modal.style.display = 'none';
  const video = document.getElementById('camVideo');
  if(video && video.srcObject){
    const tracks = video.srcObject.getTracks();
    tracks.forEach(t => t.stop());
    video.srcObject = null;
  }
  _cameraStream = null;
}

function getLocationForFIR() {
  const locField = document.getElementById('fir_location');
  const locStatus = document.getElementById('fir_location_status');
  if(!navigator.geolocation) {
    locStatus.textContent = 'Geolocation not supported.';
    return;
  }
  locStatus.textContent = 'Fetching location...';
  navigator.geolocation.getCurrentPosition(function(pos){
    const lat = pos.coords.latitude.toFixed(6);
    const lon = pos.coords.longitude.toFixed(6);
    locField.value = lat + ',' + lon;
    locStatus.textContent = 'Location captured';
  }, function(err){
    locStatus.textContent = 'Permission denied or unavailable.';
    console.error(err);
  }, { enableHighAccuracy:true, timeout:10000 });
}

// nearest police station (mock list)
const POLICE_STATIONS = [
  { name:'Central Police Station - Sector 12', lat:28.7045, lon:77.1025, phone:'+91-1122334455' },
  { name:'North Police Station - NH9', lat:28.7450, lon:77.4330, phone:'+91-9988776655' },
  { name:'East Police Station - City Center', lat:28.6700, lon:77.2300, phone:'+91-8877665544' }
];

function haversineDistance(lat1, lon1, lat2, lon2){
  function toRad(x){ return x * Math.PI / 180; }
  const R = 6371; // km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)*Math.sin(dLat/2) + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)*Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function findNearestPoliceStation(lat, lon){
  let best = null; let bestD = 1e9;
  POLICE_STATIONS.forEach(s => {
    const d = haversineDistance(lat, lon, s.lat, s.lon);
    if(d < bestD){ bestD = d; best = {...s, distance_km: d.toFixed(2)}; }
  });
  return best;
}

// FIR submit -> generate PDF and show assigned police station (mock)
function submitFIRForm(e) {
  e.preventDefault();
  const name = document.getElementById('fir_name').value || 'Unknown';
  const phone = document.getElementById('fir_phone').value || '';
  const type = document.getElementById('fir_type').value || '';
  const desc = document.getElementById('fir_desc').value || '';
  const loc = document.getElementById('fir_location').value || '';
  const imgData = document.getElementById('fir_camera_image').value || '';
  const submitStatus = document.getElementById('fir_submit_status');
  submitStatus.textContent = 'Processing...';

  let lat = null, lon = null;
  if(loc.includes(',')) { const parts = loc.split(','); lat = parseFloat(parts[0]); lon = parseFloat(parts[1]); }

  let assigned = null;
  if(lat !== null && lon !== null){ assigned = findNearestPoliceStation(lat, lon); }
  else { assigned = POLICE_STATIONS[0]; }

  // generate PDF via jsPDF (we expect jsPDF loaded in FIR page)
  try {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.setTextColor('#ff1b1b');
    doc.text('TrafficIQ - FIR Report', 14, 20);
    doc.setFontSize(11);
    doc.setTextColor(20,20,20);
    doc.text('Name: ' + name, 14, 36);
    doc.text('Phone: ' + phone, 14, 44);
    doc.text('Type: ' + type, 14, 52);
    doc.text('Location: ' + (loc || 'N/A'), 14, 60);
    doc.text('Assigned Police Station: ' + (assigned ? assigned.name + ' ('+assigned.distance_km+' km)': 'N/A'), 14, 68);
    doc.text('Description:', 14, 82);
    // wrap description
    const splitted = doc.splitTextToSize(desc || '-', 180);
    doc.text(splitted, 14, 88);

    if(imgData) {
      // add image scaled
      doc.addPage();
      doc.setFontSize(14);
      doc.text('Attached Photo', 14, 20);
      doc.addImage(imgData, 'JPEG', 14, 28, 180, 120);
    }

    const pdfName = 'FIR_' + (new Date()).toISOString().replace(/[:.]/g,'-') + '.pdf';
    doc.save(pdfName);
    submitStatus.textContent = 'FIR submitted (mock). PDF downloaded: ' + pdfName + '. Assigned: ' + (assigned ? assigned.name : 'N/A');
    // mock: show assigned details in UI
    const assignedBox = document.getElementById('fir_assigned');
    if(assignedBox){
      assignedBox.innerHTML = '<div class="card card-glass p-2 mt-2"><strong>Assigned Station:</strong><div>' + assigned.name + '</div><div class="small text-muted">Distance: ' + assigned.distance_km + ' km</div><div class="small text-muted">Phone: ' + assigned.phone + '</div></div>';
    }
  } catch(err){
    console.error(err);
    submitStatus.textContent = 'Error generating PDF: ' + err.message;
    alert('Error: ' + err.message + '. Make sure jspdf is loaded.');
  }
}
/* end camera & FIR enhancements */
